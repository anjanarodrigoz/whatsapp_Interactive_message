from flask import Flask, request
import requests

app = Flask(__name__)

# Replace these with your actual WhatsApp Cloud API details
ACCESS_TOKEN = "EAAP4m2NZCKpQBO9J9J5CmOGeLPFCjzPxsQowZCEABqBc8niwFZAkTC0h6Nj7GWku4hZAU79UoiEWB7DHmlsP19AHZC9brSDca2spYvjDJvbGMXsZBCSoo75SJl2TNIO9MLAZCg60vkwGtG3qJb3sU0MxIa4qSZBLWZAXZCpSekSaVTE67gY4L0nP2xYrnq1oShphZAV5RniToduWZAnxgl3qUt7mdcoCDrgw"
PHONE_NUMBER_ID = "508530822343719"  # Replace with your phone number ID
VERIFY_TOKEN = "12345678"  # Your chosen verify token

# In-memory user state to track language preference
user_states = {}

def send_message(to, message_body):
    """Send a plain text message."""
    url = f"https://graph.facebook.com/v16.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message_body}
    }
    response = requests.post(url, json=payload, headers=headers)
    print("Send message response:", response.json())  # Debug log
    return response.json()


def send_button_message(to, header_text, buttons):
    """Send a button message."""
    url = f"https://graph.facebook.com/v16.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "header": {"type": "text", "text": header_text},
            "body": {"text": "Please select an option:"},
            "action": {
                "buttons": [{"type": "reply", "reply": {"id": f"lang_{btn}", "title": btn}} for btn in buttons]
            }
        }
    }
    response = requests.post(url, json=payload, headers=headers)
    print("Send button response:", response.json())  # Debug log
    return response.json()


@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        # Webhook verification
        token_sent = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        return challenge, 200
        # if token_sent == VERIFY_TOKEN:
        #     print("Webhook verified successfully!")
           
        # print(f"Invalid verify token received: {token_sent}")
        # return "Invalid verification token", 403

    elif request.method == "POST":
        # Handle incoming messages from WhatsApp
        data = request.get_json()
        print("Webhook received:", data)

        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                messages = value.get("messages", [])

                for message in messages:
                    from_number = message["from"]  # Sender's phone number
                    incoming_msg = message["text"]["body"]  # Incoming message text

                    # Handle language selection or options
                    if from_number not in user_states:
                        # Send language selection menu
                        buttons = ["English", "සිංහල", "தமிழ்"]
                        send_button_message(from_number, "Select your language", buttons)
                        user_states[from_number] = None
                    elif user_states[from_number] in ["English", "සිංහල", "தமிழ்"]:
                        # Handle user-selected options
                        handle_request(from_number, incoming_msg)
                    else:
                        send_message(from_number, "Invalid request. Please restart the conversation.")

        return "OK", 200


def handle_request(user_number, incoming_msg):
    """Handle user message based on language selection."""
    selected_language = user_states.get(user_number)

    # Provide responses based on language and options
    if selected_language == "English":
        options = {
            "1": "About BIT: The Bachelor of Information Technology (BIT) is a degree offered by the University of Moratuwa.",
            "2": "How to Apply: Visit https://bit.uom.lk.",
            "3": "Fees: The total fee for the BIT program is approximately Rs. 200,000."
        }
    elif selected_language == "සිංහල":
        options = {
            "1": "BIT මොරටුව ගැන: අභිඥාපත්‍රය BIT මොරටුව විශ්වවිද්‍යාලය විසින් සපයනු ලබයි.",
            "2": "අයදුම් කිරීමේ ක්‍රමය: https://bit.uom.lk වෙත පිවිසෙන්න.",
            "3": "ගාස්තු: BIT වැඩසටහන සඳහා සමස්ත ගාස්තුව රු. 200,000ක් පමණ වේ."
        }
    elif selected_language == "தமிழ்":
        options = {
            "1": "BIT பற்றி: BIT பட்டம் மொரட்டுவா பல்கலைக்கழகம் வழங்குகிறது.",
            "2": "விண்ணப்பிக்க: https://bit.uom.lk.",
            "3": "கட்டணம்: BIT திட்டத்தின் மொத்த கட்டணம் சுமார் Rs. 200,000 ஆகும்."
        }
    else:
        send_message(user_number, "Invalid input. Please restart the conversation.")
        return

    if incoming_msg in options:
        send_message(user_number, options[incoming_msg])
    else:
        send_message(user_number, "Invalid option. Please reply with 1, 2, or 3.")


if __name__ == "__main__":
    # Start the Flask server
    app.run(port=5000, debug=True)