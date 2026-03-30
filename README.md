# Supermarket AI Voice Agent

A RAG-like conversational Voice AI for a supermarket built using FastAPI, Twilio Voice, OpenAI, and Google Sheets.

## Features
- **Phone Calls:** Customers can call the Twilio number and an AI voice agent will answer.
- **Multilingual:** The AI greets the customer, asks for their language, and smoothly switches to it.
- **Inventory Check:** The AI checks a local stock database (`stock.db`) to see if a requested item is available and its price.
- **Order Cart:** The AI manages the customer's cart during the call, checking availability limits dynamically.
- **Checkout & Finalization:** The AI reads out the entire order, the total price, and asks whether pickup or delivery is needed (taking an address if needed).
- **Google Sheets Integration:** Automatically creates a Google Sheet with the order details, total, and delivery address.
- **WhatsApp Notification:** Sends the Google Sheet link to a designated WhatsApp number (`+91 9092922592`).

## Prerequisites

1. **Python 3.9+** and `pip`
2. **OpenAI API Key** with access to `gpt-4o`
3. **Twilio Account** with a purchased phone number and WhatsApp Sender access.
4. **Google Cloud Project** with Google Sheets and Google Drive APIs enabled, and a **Service Account JSON key**.
5. **Ngrok** (to expose your local FastAPI server to Twilio webhooks).

## Setup & Configuration

1. **Install Dependencies:**
   ```cmd
   pip install -r requirements.txt
   ```

2. **Environment Variables:**
   Create a `.env` file in the root directory (you can copy `.env.example`) and fill in your keys:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   TWILIO_ACCOUNT_SID=your_twilio_account_sid
   TWILIO_AUTH_TOKEN=your_twilio_auth_token
   # If you are using the Twilio WhatsApp Sandbox, enter your sandbox number below:
   TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
   ```

3. **Google Sheets Credentials:**
   Place your Google Service Account JSON file in the project root folder and name it `credentials.json`. This service account will be used to automatically generate the spreadsheets.

4. **Initialize Database:**
   The SQLite database (`stock.db`) will be created and populated with sample data the first time you run the server.

## Running the Application

1. **Start the FastAPI Server:**
   ```cmd
   uvicorn main:app --reload
   ```
   *The server will start on port 8000.*

2. **Expose Local Server to the Internet:**
   In a new terminal window, start ngrok:
   ```cmd
   ngrok http 8000
   ```

3. **Configure Twilio Webhooks:**
   - Go to your Twilio Console -> Phone Numbers -> Manage -> Active Numbers.
   - Click on your purchased phone number `+1 260 319 3542`.
   - Scroll down to "Voice & Fax".
   - Under **A CALL COMES IN**, set it to **Webhook** and paste your ngrok URL followed by `/incoming-call`:
     `https://<your-ngrok-url>.ngrok-free.app/incoming-call`
   - Set the HTTP method to `POST`.
   - Save the configuration.

4. **Add WhatsApp Sandbox Participant:**
   If you are testing using the Twilio WhatsApp sandbox, you must send a WhatsApp message to your Twilio Sandbox number to opt-in from `+91 9092922592` before Twilio can send messages to it.

## Testing

1. Call `+1 260 319 3542` from your phone.
2. The AI will answer and greet you.
3. Converse with it:
   - "I want to speak in Spanish"
   - "I would like 2kg of potatoes and 1 liter of milk"
   - Note: The initial mock database has `potato (10kg)`, `tomato (5kg)`, `onion (20kg)`, `milk (15 liter)`, `bread (30 pack)`.
4. Finalize the order and say you want delivery to "123 Main Street".
5. Hang up when it says goodbye.
6. Check your WhatsApp for the message containing the newly created Google Sheet!
