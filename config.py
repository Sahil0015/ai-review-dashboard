from groq import Groq
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("❌ GROQ_API_KEY not found in .env file!")

# Configure native Groq client
client = Groq(api_key=GROQ_API_KEY)

model = "llama-3.1-8b-instant"  

print(f"✓ Groq configured successfully")
print(f"✓ Using model: {model}")
