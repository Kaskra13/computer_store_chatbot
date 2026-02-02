import os
import logging
from dotenv import load_dotenv

load_dotenv(override=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = "gemini-2.5-flash"
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "computer_store"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
}


SYSTEM_MESSAGE = """
You are a helpful AI assistant for a Computer Store, an online computer retailer.

Your role:
- Help customers find the perfect computer based on their needs and budget
- Provide accurate product information, pricing, and availability
- Offer recommendations based on customer requirements
- Be friendly, concise, and professional

Guidelines:
- Keep responses clear and to the point (2-3 sentences max unless detailed info is requested)
- Always verify information using your tools before responding
- If you don't have specific information, say so and offer to help differently
- Highlight products that are in stock and have good ratings
- When comparing products, focus on key differences that matter to the customer
"""

if GEMINI_API_KEY:
    logger.info("Gemini API key loaded successfully.")
else:
    logger.warning("Gemini API key is not set.")


if DB_CONFIG["password"]:
    logger.info(f"Database config loaded. Host: {DB_CONFIG['host']}, DB Name: {DB_CONFIG['database']}")
else:
    logger.warning("Database password is not set.")