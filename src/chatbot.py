import json
from openai import OpenAI
from openai import (
    RateLimitError, 
    APIConnectionError, 
    AuthenticationError,
    APIError,
    APITimeoutError
)
from src.config import MODEL, SYSTEM_MESSAGE, GEMINI_API_KEY, GEMINI_BASE_URL
from src.tools import (TOOLS, search_products, get_product_details, check_stock, get_budget_recommendations)

client = OpenAI(
    api_key=GEMINI_API_KEY,
    base_url=GEMINI_BASE_URL
)

def handle_tool_calls(message):
    responses = []
    
    for tool_call in message.tool_calls:
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)

        if function_name == "search_products":
            result = search_products(**arguments)
        elif function_name == "get_product_details":
            result = get_product_details(**arguments)
        elif function_name == "check_stock":
            result = check_stock(**arguments)
        elif function_name == "get_budget_recommendations":
            result = get_budget_recommendations(**arguments)
        else:
            result = f"Unknown function called"
        
        responses.append({
            "role": "tool",
            "content": result,
            "tool_call_id": tool_call.id
        })
    
    return responses


def chat(message, history):
    try:
        history = [{"role":h["role"], "content":h["content"]} for h in history]

        messages = [{"role":"system", "content": SYSTEM_MESSAGE}] + history + [{"role":"user", "content": message}]

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS
        )

        while response.choices[0].finish_reason == "tool_calls":
            message_with_tools = response.choices[0].message
            tool_responses = handle_tool_calls(message_with_tools)

            messages.append(message_with_tools)
            messages.extend(tool_responses)

            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=TOOLS
            )
        
        content = response.choices[0].message.content
        return content if content else "I'm sorry, I couldn't generate a response."
    
    except RateLimitError as e:
        error_msg = "Rate limit exceeded. Please wait a moment and try again."
        if "retry" in str(e).lower():
            error_msg += " The service is temporarily busy."
        print(f"Rate limit error: {e}")
        return error_msg
    
    except AuthenticationError as e:
        error_msg = "Authentication error. Please check your API credentials."
        print(f"Authentication error: {e}")
        return error_msg
    
    except APIConnectionError as e:
        error_msg = "Connection error. Please check your internet connection and try again."
        print(f"Connection error: {e}")
        return error_msg
    
    except APITimeoutError as e:
        error_msg = "Request timed out. Please try again."
        print(f"Timeout error: {e}")
        return error_msg
    
    except APIError as e:
        error_msg = f"API error occurred: {e.message if hasattr(e, 'message') else str(e)}"
        print(f"API error: {e}")
        return error_msg
    
    except Exception as e:
        error_msg = f"An unexpected error occurred. Please try again."
        print(f"Unexpected error in chat: {type(e).__name__}: {e}")
        return error_msg