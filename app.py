import gradio as gr
import logging
from src.database import initialize_database
from src.chatbot import chat

logger = logging.getLogger(__name__)

initialize_database()


demo = gr.ChatInterface(
    fn=chat,
    title="Computer Store AI Assistant",
    description=("Welcome to a Computer Store! I can help you find the perfect computer."
                 "Ask me about products, prices, specifications, or ger personalized recommendations based on your budget!"),
    examples=[
        "What gaming laptops do you have?",
        "I need a laptop under $1000",
        "Tell me about the MacBook Pro 14",
        "Do you have any desktops with RTX 4090?",
        "What's in stock from Dell?",
        "Show me computers with at least 4.5 star rating"
    ],
)

if __name__ == "__main__":
    logger.info("="*60)
    logger.info("Computer Store AI Assistant")
    logger.info("="*60)
    demo.launch(
        inbrowser=True,
        share=False
    )