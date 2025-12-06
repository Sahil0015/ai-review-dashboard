from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("❌ GROQ_API_KEY not found in environment variables!")

# Initialize Groq client with fixed version compatibility
try:
    client = Groq(api_key=GROQ_API_KEY)
    print("✓ Groq client initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize Groq client: {e}")
    raise

# Model configuration
model = "llama-3.1-8b-instant"

print(f"✓ Using model: {model}")
