from collections import defaultdict, deque
import time
from google.adk.plugins import base_plugin
from google.genai import types

class RateLimitPlugin(base_plugin.BasePlugin):
    """
    Rate Limiter Plugin (Sliding Window).
    Prevents abuse by blocking users who send too many requests in a short time.
    """
    def __init__(self, max_requests=10, window_seconds=60):
        super().__init__(name="rate_limiter")
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.user_windows = defaultdict(deque)
        self.blocked_hits = 0

    async def on_user_message_callback(self, *, invocation_context, user_message):
        # Default user_id if context is missing
        user_id = "default_user"
        if hasattr(invocation_context, "user_id") and invocation_context.user_id:
            user_id = invocation_context.user_id
        
        now = time.time()
        window = self.user_windows[user_id]

        # Remove expired timestamps (older than the window_seconds)
        while window and window[0] < now - self.window_seconds:
            window.popleft()

        # Check if user reached limit
        if len(window) >= self.max_requests:
            self.blocked_hits += 1
            wait_time = int(self.window_seconds - (now - window[0]))
            return types.Content(
                role="model",
                parts=[types.Part.from_text(
                    text=f"[RATE_LIMIT] You have exceeded the request limit. Please wait {wait_time} seconds."
                )]
            )

        # Allow request and record timestamp
        window.append(now)
        return None
