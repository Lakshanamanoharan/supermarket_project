import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

def send_whatsapp_message(to_number: str, message_body: str):
    """
    Sends a WhatsApp message using Twilio API.
    to_number must be in format 'whatsapp:+91909292...'.
    """
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_whatsapp_number = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
    if not from_whatsapp_number.startswith("whatsapp:"):
        from_whatsapp_number = f"whatsapp:{from_whatsapp_number}"
    
    if not account_sid or not auth_token:
        print("Warning: Twilio credentials not set. WhatsApp message not sent.")
        return False
        
    client = Client(account_sid, auth_token)
    
    try:
        message = client.messages.create(
            body=message_body,
            from_=from_whatsapp_number,
            to=f"whatsapp:{to_number.replace('whatsapp:', '')}"
        )
        print(f"WhatsApp message sent! SID: {message.sid}")
        return True
    except Exception as e:
        print(f"Failed to send WhatsApp message: {str(e)}")
        return False
