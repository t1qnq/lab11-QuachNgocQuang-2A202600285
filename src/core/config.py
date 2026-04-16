"""
Lab 11 — Configuration & API Key Setup
"""
import os
from dotenv import load_dotenv


def setup_api_key():
    """Load API keys from environment or .env file."""
    load_dotenv()
    # google-adk uses GOOGLE_API_KEY for native Gemini/Gemma models.
    
    if "GOOGLE_API_KEY" not in os.environ:
        key = os.getenv("GOOGLE_API_KEY")
        if key:
            os.environ["GOOGLE_API_KEY"] = key
        else:
            print("WARNING: GOOGLE_API_KEY not found in environment or .env")

    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "0"
    print("API configuration initialized.")


# Allowed banking topics (used by topic_filter)
ALLOWED_TOPICS = [
    "banking", "account", "transaction", "transfer",
    "loan", "interest", "savings", "credit",
    "deposit", "withdrawal", "balance", "payment",
    "tai khoan", "giao dich", "tiet kiem", "lai suat",
    "chuyen tien", "the tin dung", "so du", "vay",
    "ngan hang", "atm",
]

# Blocked topics (immediate reject)
BLOCKED_TOPICS = [
    "hack", "exploit", "weapon", "drug", "illegal",
    "violence", "gambling", "bomb", "kill", "steal",
]
