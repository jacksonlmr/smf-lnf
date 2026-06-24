import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is missing from the environment variables.")

if not GEMINI_MODEL:
    raise ValueError("GEMINI_MODEL is missing from the environment variables")