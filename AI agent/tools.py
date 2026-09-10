from datetime import datetime
import urllib.request
import urllib.parse
from google import genai
from config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)

def calculator(expression: str) -> str:
    """
    Calculate a mathematical expression.
    
    Args:
        expression: The math expression to evaluate, e.g. "45 * 12"
    """
    print(f"\n[DEBUG] 🛠️ Tool 'calculator' called with expression: {expression}")
    try:
        result = eval(expression)
        print(f"[DEBUG] ✅ Tool result: {result}")
        return str(result)
    except Exception as e:
        print(f"[DEBUG] ❌ Tool error: {e}")
        return "Unable to calculate the expression"


def get_current_time() -> str:
    """
    Returns the current date and time.
    """    
    print("\n[DEBUG] 🛠️ Tool 'get_current_time' called")
    try:
        current_time = datetime.now()
        time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[DEBUG] ✅ Tool result: {time_str}")
        return time_str
    except Exception as e:
        print(f"[DEBUG] ❌ Tool error: {e}")
        return "Unable to fetch current time"


def get_weather(city: str) -> str:
    """
    Get the current weather for a specified city.
    
    Args:
        city: The name of the city, e.g. "Mumbai", "London", or "New York"
    """
    print(f"\n[DEBUG] 🛠️ Tool 'get_weather' called for city: {city}")
    try:
        encoded_city = urllib.parse.quote(city)
        # Using format=3 provides a clean preformatted string like "Mumbai: ⛅️ +32°C"
        url = f"https://wttr.in/{encoded_city}?format=3"
        req = urllib.request.Request(url, headers={'User-Agent': 'curl/7.68.0'})
        
        with urllib.request.urlopen(req, timeout=5) as response:
            result = response.read().decode('utf-8').strip()
            print(f"[DEBUG] ✅ Tool result: {result}")
            return result
    except Exception as e:
        print(f"[DEBUG] ❌ Tool error: {e}")
        return f"Unable to fetch weather for {city}"