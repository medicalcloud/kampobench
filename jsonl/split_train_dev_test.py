#!/usr/bin/env python3
import argparse, json, random, pathlib

def read_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line=line.strip()
            if line:
                yield json.loads(line)

def write_jsonl(path, items):
    with open(path, "w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--train", default="data/train.jsonl")
    ap.add_argument("--dev", default="data/dev.jsonl")
    ap.add_argument("--test", default="data/test.jsonl")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    items = list(read_jsonl(args.input))
    random.Random(args.seed).shuffle(items)
    n = len(items)
    t = int(n*0.8); d = int(n*0.1)
    write_jsonl(args.train, items[:t])
    write_jsonl(args.dev, items[t:t+d])
    write_jsonl(args.test, items[t+d:])
    print(f"train/dev/test = {t}/{d}/{n-t-d}")
