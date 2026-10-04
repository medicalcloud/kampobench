import time
import abc
from ..types import SamplerBase, MessageList, SamplerResponse

class SamplerWithRetry(SamplerBase, abc.ABC):
    """
    Base class for samplers that implements exponential backoff retry logic.
    Subclasses only need to implement the _sample method.
    """

    def __call__(self, message_list: MessageList) -> SamplerResponse:
        trial = 0
        while True:
            try:
                return self._sample(message_list)
            except Exception as e:
                # Max retries
                if trial >= 5:
                    print(f"Max retries reached. Error: {e}")
                    raise e

                # Check if it's a specific API error that should NOT be retried (Optional)
                # For now, we retry on all exceptions as per the existing pattern.
                
                exception_backoff = 2**trial
                print(
                    f"Exception occurred, so wait and retry {trial} after {exception_backoff} sec: {e}"
                )
                time.sleep(exception_backoff)
                trial += 1

    @abc.abstractmethod
    def _sample(self, message_list: MessageList) -> SamplerResponse:
        """
        Implementation-specific sampling logic.
        """
        pass
