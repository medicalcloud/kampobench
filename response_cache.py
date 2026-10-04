# -*- coding: utf-8 -*-
"""API 呼び出しの結果をディスクに残し、再実行時に使い回す。

課金枠を使い切って測定が落ちても、次回は済んだ分を呼び直さずに再開できる。
`SamplerWithRetry` は5回の再試行で諦めて例外を投げ、それが `map_with_progress` の
スレッドプールを抜けて実行全体を落とす。そのときすでに払ったトークンを無駄にしないための仕組み。

回答の生成にも採点にも同じ仕組みが効く。どちらも `SamplerBase.__call__` だからである。

**キャッシュは設定ごとに分かれる。** モデル名だけでなく、システムメッセージ・温度・
出力上限も鍵に含める。設定を変えれば別の鍵になり、古い結果が混ざることはない。

**再実行が独立の試行にならない点に注意。** 実行ごとのばらつきを測りたいときは
`--no-cache` を付けること。
"""
import hashlib
import json
import os
import threading

from .types import MessageList, SamplerBase, SamplerResponse

CACHE_ROOT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tmp", "api_cache"
)


def _fingerprint(sampler: SamplerBase) -> str:
    """サンプラーの設定を表す文字列。設定が違えば別のキャッシュになる。"""
    parts = [type(sampler).__name__]
    # GeminiCompletionSampler はモデル名を model_name に持つ。取りこぼすと
    # 別モデルの応答を同じ鍵で共有してしまうので、両方を見る。
    for attr in ("model", "model_name", "system_message", "temperature",
                 "max_tokens", "reasoning_effort"):
        if hasattr(sampler, attr):
            parts.append(f"{attr}={getattr(sampler, attr)!r}")
    return "|".join(parts)


class CachingSampler(SamplerBase):
    """内側のサンプラーを包み、同じ入力への応答をディスクから返す。"""

    def __init__(self, inner: SamplerBase, label: str, cache_root: str = CACHE_ROOT):
        self.inner = inner
        self.label = label
        self.fingerprint = _fingerprint(inner)
        # 設定の指紋を短縮してディレクトリ名にする。設定を変えれば別の置き場になる。
        cfg = hashlib.sha256(self.fingerprint.encode("utf-8")).hexdigest()[:12]
        safe = "".join(c if c.isalnum() or c in "-._" else "_" for c in label)
        self.dir = os.path.join(cache_root, f"{safe}_{cfg}")
        os.makedirs(self.dir, exist_ok=True)
        self._lock = threading.Lock()
        self.hits = 0
        self.misses = 0
        # どの設定のキャッシュかを人が読めるように残す
        meta = os.path.join(self.dir, "_fingerprint.txt")
        if not os.path.exists(meta):
            with open(meta, "w", encoding="utf-8") as fh:
                fh.write(self.fingerprint + "\n")

    def _path(self, message_list: MessageList) -> str:
        key = hashlib.sha256(
            (self.fingerprint + json.dumps(message_list, ensure_ascii=False, sort_keys=True))
            .encode("utf-8")
        ).hexdigest()
        # 1ディレクトリにファイルを集中させない
        sub = os.path.join(self.dir, key[:2])
        os.makedirs(sub, exist_ok=True)
        return os.path.join(sub, key + ".json")

    def _pack_message(self, role, content):
        return {"role": str(role), "content": content}

    def __call__(self, message_list: MessageList) -> SamplerResponse:
        p = self._path(message_list)
        if os.path.exists(p):
            try:
                with open(p, encoding="utf-8") as fh:
                    d = json.load(fh)
                with self._lock:
                    self.hits += 1
                return SamplerResponse(
                    response_text=d["response_text"],
                    actual_queried_message_list=d["actual_queried_message_list"],
                    response_metadata=d.get("response_metadata") or {},
                )
            except Exception:
                # 壊れた行があっても止めない。呼び直して上書きする。
                pass

        r = self.inner(message_list)
        with self._lock:
            self.misses += 1
        # usage 等はそのままでは JSON にできないことがあるので、書ける形に落とす
        meta = {}
        for k, v in (r.response_metadata or {}).items():
            try:
                json.dumps(v)
                meta[k] = v
            except TypeError:
                meta[k] = _to_plain(v)
        tmp = p + f".{os.getpid()}.{threading.get_ident()}.part"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(
                {
                    "response_text": r.response_text,
                    "actual_queried_message_list": r.actual_queried_message_list,
                    "response_metadata": meta,
                },
                fh, ensure_ascii=False,
            )
        os.replace(tmp, p)   # 書き途中のファイルを読ませない
        return r


def _to_plain(v):
    """usage オブジェクト等を JSON にできる形へ。"""
    for attr in ("model_dump", "dict", "to_dict"):
        if hasattr(v, attr):
            try:
                return getattr(v, attr)()
            except Exception:
                pass
    if hasattr(v, "__dict__"):
        return {k: str(x) for k, x in vars(v).items()}
    return str(v)


def wrap(sampler: SamplerBase, label: str, enabled: bool = True) -> SamplerBase:
    return CachingSampler(sampler, label) if enabled else sampler


def report(samplers) -> str:
    """キャッシュの使われ方をまとめる。再開が効いたかの確認に使う。"""
    lines = []
    for s in samplers:
        if isinstance(s, CachingSampler):
            tot = s.hits + s.misses
            if tot:
                lines.append(f"  {s.label:34s} 再利用 {s.hits:5d} / 新規 {s.misses:5d}"
                             f"（{s.hits/tot*100:.0f}% を再利用）")
    return "\n".join(lines)
