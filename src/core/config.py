import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Validate critical secrets on startup
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is missing from the environment variables.")