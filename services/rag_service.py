import json
import os
import  re
import google.generativeai as genai
import  requests
from jinja2.utils import missing

from  models.models import FitnessClass,Booking
from  dotenv import load_dotenv

try:
    if not load_dotenv():
        print("Warning: .env file not found or could not be loaded.")
except Exception as e:
    print(f"Error loading .env file: {e}")


api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables.")

try:
    genai.configure(api_key=api_key)
    print("✅ genai configured successfully.")
except Exception as e:
    print(f"Failed to configure genai: {e}")






model = genai.GenerativeModel("gemini-2.0-flash")

# def fetch_context_from_db():
#
#     classes = FitnessClass.query.filter_by(is_cancelled = False).all()
#
#     if not classes:
#         return  "No upcoming fitness classes available"
#
#     context = "\n".join([
#
#         f"Class : {c.name}, Time: {c.datetime}, Instructor: {c.instructor_name}, Slots: {c.available_slots}"
#         for c in classes
#     ])
#
#     return context
#
#
# def answer_user_query(query):
#
#     context = fetch_context_from_db()
#     prompt = f"""
#
#     You are a fitness booking customer service assistant. Use the following context to answer:
#
#     Context : {context}
#
#     User Query : {query}
#
#     """
#
#     try:
#
#         response = model.generate_content(prompt, stream=True)
#         for chunk in response:
#             if chunk.text:
#                 yield chunk.text
#
#     except Exception as e:
#         yield f"Failed to get response: {str(e)}"
#
#


BACKEND_URL = "http://localhost:5000"  # Adjust if deployed elsewhere

session = {"booking": {}}
CLASS_NAME_TO_ID = {
    "yoga": 1,
    "zumba": 2,
    "hiit": 3,
}
def extract_class_info(text):
    for name in CLASS_NAME_TO_ID:
        if name in text.lower():
            return name.capitalize(), CLASS_NAME_TO_ID[name]
    return None, None

def extract_json(text):
    try:
        json_str = re.search(r"\{.*\}", text, re.DOTALL).group()
        return json.loads(json_str)
    except Exception as e:
        print("JSON parsing failed. Raw LLM response:", text)
        raise e

def fetch_context_from_db():
    classes = FitnessClass.query.filter_by(is_cancelled=False).all()
    if not classes:
        return "No upcoming fitness classes available."

    context = "\n".join([
        f"Class: {c.name}, Time: {c.datetime}, Instructor: {c.instructor_name}, Slots: {c.available_slots}"
        for c in classes
    ])
    return context

def chat_with_context(query):
    context = fetch_context_from_db()
    prompt = f"""
You are a friendly fitness studio assistant. Answer based on the following class schedule:
Context: {context}
User Query: {query}
"""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Failed to respond: {str(e)}"

EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
def detect_intent_and_collect(query, session):
    intent = None
    collected = session.get("booking", {})

    if "cancel" in query.lower():
        intent = "cancel_booking"

        name, cid = extract_class_info(query)
        if name and cid:
            collected["class_name"] = name
            collected["class_id"] = cid



    elif "book" in query.lower() and any(x in query.lower() for x in CLASS_NAME_TO_ID):
        intent = "book_class"
        name, cid = extract_class_info(query)
        collected["class_name"] = name
        collected["class_id"] = cid

    match = re.search(EMAIL_REGEX, query)
    if match:
        collected["email"] = match.group()

    # Try to extract customer name if user types: "my name is John"
    name_match = re.search(r"my name is ([a-zA-Z\s]+)", query.lower())
    if name_match:
        collected["customer_name"] = name_match.group(1).strip().title()

    session["booking"] = collected
    return intent, collected

def detect_intent_and_call_api(query):
    system_prompt = """
You are an AI fitness assistant. Analyze the user query and identify if it matches one of the following actions:
1. View available fitness classes (intent: get_classes)
2. Book a class (intent: book_class) – Required: class_id, customer_email
3. Cancel a booking (intent: cancel_booking) – Required: class_id, customer_email
4. View my bookings (intent: get_bookings) – Required: customer_email

Return JSON: 
{
  "intent": "one of the above",
  "data": { ... any required parameters ... }
}
If nothing matches, respond with {"intent": "chat"}.
"""
    try:
        intent_response = model.generate_content(
            f"{system_prompt}\nUser Query: {query}"
        )
        response_text = intent_response.text.strip()
        parsed = extract_json(response_text)
        intent = parsed.get("intent")
        data = parsed.get("data", {})
    except Exception as e:
        return f"Sorry, I couldn't understand that. Error: {e}"

    try:
        if intent == "get_classes":
            res = requests.get(f"{BACKEND_URL}/classes")
            return res.json()

        elif intent == "book_class":
            res = requests.post(f"{BACKEND_URL}/book", json=data)
            return res.json()

        elif intent == "cancel_booking":
            res = requests.delete(f"{BACKEND_URL}/cancel-booking", json=data)
            return res.json()

        elif intent == "get_bookings":
            email = data.get("customer_email")
            if not email:
                return "Please provide your email."
            res = requests.get(f"{BACKEND_URL}/bookings?email={email}")
            return res.json()

        else:
            return chat_with_context(query)

    except Exception as e:
        return f"API call failed: {str(e)}"

def format_response(result):
    if isinstance(result, str):
        return result

    elif isinstance(result, list):
        # Handle list of classes or bookings
        if all("name" in item and "instructor" in item and "datetime" in item for item in result):
            lines = ["Here are the available fitness classes:\n"]
            emoji_map = {"Yoga": "🧘‍♂️", "Zumba": "💃", "HIIT": "🏋️", "Pilates": "🧎"}
            for cls in result:
                emoji = emoji_map.get(cls["name"], "🏋️")
                lines.append(
                    f"{emoji} **{cls['name']}** by {cls['instructor']} at {cls['datetime']} ({cls['available_slots']} slots available)"
                )
            return "\n".join(lines)

        elif all("booking_id" in item and "email" in item for item in result):
            lines = ["Here are your current bookings:\n"]
            for b in result:
                lines.append(
                    f"✅ Booking ID: {b['booking_id']} | Class: {b['class_name']} at {b['datetime']} | Email: {b['email']}"
                )
            return "\n".join(lines)

        else:
            return json.dumps(result, indent=2)

    elif isinstance(result, dict):

        if "message" in result:
            return f"✅ {result['message']}"
        elif "booking_id" in result:
            return (
                f"✅ Booking confirmed!\n"
                f"Class: {result.get('class_name')}\n"
                f"Date: {result.get('datetime')}\n"
                f"Booking ID: {result.get('booking_id')}"
            )
        else:
            return json.dumps(result, indent=2)

    else:
        return f"⚠️ Unrecognized response format:\n{str(result)}"

SAMPLE_BOOKING_FORMAT = """
Here's how you can book a class:

📍 I want to book a [Class Name] class  
📧 My email is [your-email@example.com]  
🙋‍♂️ My name is [Your Name]

✅ Example:
I want to book a Yoga class  
My email is user212@gmail.com  
My name is userrname
"""

def answer_user_query(query):
    intent, data = detect_intent_and_collect(query, session)

    if intent == "book_class":
        missing = []
        if "email" not in data:
            missing.append("email")
        if "class_id" not in data:
            missing.append("class_id")

        if "customer_name" not in data:
            missing.append("customer_name")

        if missing:
            if "email" in missing:
                yield "📧 Please provide your email to complete the booking."
            if "class_id" in missing:
                yield "📌 Which class would you like to book? (e.g., Yoga, Zumba, HIIT)"

            if "customer_name" in missing:
                yield "🙋‍♂️ Please tell me your name (e.g., 'My name is Aniket')"
            yield SAMPLE_BOOKING_FORMAT

        else:
            try:
                payload = {
                    "class_id": data["class_id"],
                    "customer_email": data["email"],
                    "customer_name": data["customer_name"]
                }
                res = requests.post(f"{BACKEND_URL}/book", json=payload)
                session["booking"] = {}  # reset session after success
                if res.status_code == 201:
                    yield f"✅ Booking confirmed for {data['class_name']}!"
                else:
                    yield f" Failed to book: {res.text}"
            except Exception as e:
                yield f" Error while booking: {e}"


    elif intent == "cancel_booking":
        missing = []
        if "email" not in data:
            missing.append("email")
        if "class_id" not in data:
            missing.append("class_id")

        if missing:
            if "email" in missing:
                yield "📧 Please provide your email to cancel the booking."
            if "class_id" in missing:
                yield "📌 Which class would you like to cancel? (e.g., Zumba, Yoga)"
        else:
            try:
                res = requests.delete(f"{BACKEND_URL}/cancel", params={
                    "email": data["email"],
                    "class_id": data["class_id"]
                })
                session["booking"] = {}  # reset
                if res.status_code == 200:
                    yield f"✅ Your booking for {data['class_name']} has been canceled."
                else:
                    yield f"❌ Failed to cancel: {res.text}"
            except Exception as e:
                yield f"⚠️ Error while cancelling: {e}"

    elif intent in ["get_classes", "get_bookings"]:
        # use RAG + API-based intent detection
        result = detect_intent_and_call_api(query)
        yield format_response(result)

    else:
        # only fallback to RAG if no valid intent
        response = chat_with_context(query)
        if response.strip():
            yield response.strip()
        else:
            yield "🤖 I can help you with booking, cancellations, or viewing your classes. Try asking something like 'book a yoga class'."