import time
import random
from typing import List

class RequestThrottler:
    """Class to handle request delays and throttling to avoid overloading servers."""
    
    def __init__(self, min_delay: float = 2.0, max_delay: float = 5.0):
        """Initialize the throttler with delay settings.
        
        Args:
            min_delay: Minimum delay between requests in seconds
            max_delay: Maximum delay between requests in seconds
        """
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.last_request_time = 0
    
    def throttle(self):
        """Wait an appropriate amount of time since the last request."""
        # Calculate time elapsed since last request
        elapsed = time.time() - self.last_request_time
        
        # Determine delay based on settings
        delay = random.uniform(self.min_delay, self.max_delay)
        
        # If enough time hasn't passed, sleep
        if elapsed < delay:
            time_to_sleep = delay - elapsed
            print(f"Throttling request for {time_to_sleep:.2f} seconds...")
            time.sleep(time_to_sleep)
        
        # Update last request time
        self.last_request_time = time.time()


def get_random_user_agent() -> str:
    """Return a random user agent string to avoid detection."""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36 Edg/92.0.902.78",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
    ]
    return random.choice(user_agents) 