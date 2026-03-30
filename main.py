from fastapi import FastAPI, Form, Request, BackgroundTasks
from fastapi.responses import Response, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from twilio.twiml.voice_response import VoiceResponse
from twilio.request_validator import RequestValidator
import os
from dotenv import load_dotenv
import agent
import csv
from stock_db import init_db

load_dotenv()
app = FastAPI()
init_db()

from fastapi.responses import RedirectResponse
@app.get("/")
async def root():
    return RedirectResponse(url="/dashboard/index.html")

# Create static directory if not exists
if not os.path.exists("static"):
    os.makedirs("static")
    
app.mount("/dashboard", StaticFiles(directory="static", html=True), name="static")

@app.get("/api/live-carts")
async def api_live_carts():
    """API Endpoint for the Admin Dashboard to poll live cart data"""
    calls_data = []
    for sid, cart in agent.carts.items():
        calls_data.append({
            "call_sid": sid,
            "caller_number": agent.caller_numbers.get(sid, "Unknown Caller"),
            "status": agent.call_statuses.get(sid, "in-progress"),
            "cart": cart,
            "finalized": agent.finalized_orders.get(sid)
        })
    return {"calls": calls_data}

WHATSAPP_NUMBER = "+919092922592"

def respond(text: str):
    vr = VoiceResponse()
    # Adding status_callback to track hangups even if no speech matches
    gather = vr.gather(input="speech", action="/process-speech", timeout=5, speech_timeout="1", enhanced=True, language="en-IN", bargeIn=True)
    gather.say(text, language="en-IN", voice="Google.en-IN-Standard-A")
    vr.redirect("/empty-speech")
    return Response(content=str(vr), media_type="text/xml")

@app.post("/status-callback")
async def status_callback(CallSid: str = Form(...), CallStatus: str = Form(...)):
    """Twilio calls this when the call ends or changes state"""
    print(f"[{CallSid}] Status Update: {CallStatus}")
    if CallStatus in ["completed", "failed", "busy", "no-answer", "canceled"]:
        # If the call was already finalized, keep it as finalized for display
        # Otherwise, mark as ended
        current_status = agent.call_statuses.get(CallSid)
        if current_status != "finalized":
            agent.set_status(CallSid, "ended")
    return Response(content="OK", media_type="text/plain")

@app.post("/empty-speech")
async def empty_speech(CallSid: str = Form(None)):
    # Simple reprompt if silence was detected
    return respond("I didn't quite catch that. Could you please repeat your order?")

def finalize_call(text: str, call_sid: str):
    vr = VoiceResponse()
    vr.say(text)
    # The call will end naturally after saying the final text
    vr.hangup()
    return Response(content=str(vr), media_type="text/xml")

@app.post("/incoming-call")
async def incoming_call(CallSid: str = Form(...), From: str = Form(None)):
    agent.init_session(CallSid, From)
    greeting = agent.process_message(CallSid, "The user has answered the call. Greet them.", From)
    
    # Send a response that includes the status_callback
    vr = VoiceResponse()
    gather = vr.gather(input="speech", action="/process-speech", timeout=5, speech_timeout="1", enhanced=True, language="en-IN", bargeIn=True)
    gather.say(greeting, language="en-IN", voice="Google.en-IN-Standard-A")
    vr.redirect("/empty-speech")
    
    # We set status callback on the initial response
    # Twilio will use this for the duration of the call
    response_xml = str(vr).replace('<Response>', f'<Response statusCallback="/status-callback" statusCallbackEvent="completed">')
    return Response(content=response_xml, media_type="text/xml")

@app.post("/process-speech")
async def process_speech(CallSid: str = Form(...), SpeechResult: str = Form(None), From: str = Form(None), background_tasks: BackgroundTasks = BackgroundTasks()):
    if not SpeechResult:
        # Prompt them again if nothing was heard
        return respond("I didn't quite catch that. Could you please repeat your order?")
        
    print(f"[{CallSid}] Heard: {SpeechResult}")
    
    agent_reply = agent.process_message(CallSid, SpeechResult, From)
    finalized_info = agent.is_finalized(CallSid)
    
    if finalized_info:
        # The agent decided to finalize the order.
        # Run sheet creation and whatsapp sending in background so call ends quickly.
        cart = agent.get_cart(CallSid)
        delivery_mode = finalized_info.get("delivery_mode", "pickup")
        delivery_address = finalized_info.get("delivery_address", "")
        # The call ID is the unique order ID
        order_number = CallSid
        
        background_tasks.add_task(process_final_order, order_number, cart, delivery_mode, delivery_address)
        agent.set_status(CallSid, "finalized")
        
        return finalize_call(agent_reply, CallSid)
    
    return respond(agent_reply)

import csv

def export_to_admin_dashboard(order_number: str, cart: list, delivery_mode: str, delivery_address: str):
    # TODO: Export logic for the admin dashboard
    print(f"[{order_number}] Exporting order to the admin dashboard...")

def process_final_order(order_number: str, cart: list, delivery_mode: str, delivery_address: str):
    print(f"Processing background order {order_number}...")
    
    # New Hook: Export to Admin Dashboard
    export_to_admin_dashboard(order_number, cart, delivery_mode, delivery_address)
    
    # 1. Save local CSV file immediately
    csv_file = f"Order_{order_number}.csv"
    try:
        with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Product Name", "Quantity", "Price", "Total Price"])
            grand_total = 0
            for item in cart:
                total_price = item["quantity"] * item["price"]
                grand_total += total_price
                writer.writerow([item["product"], item["quantity"], item["price"], total_price])
            writer.writerow(["", "", "GRAND TOTAL", grand_total])
            writer.writerow(["Delivery Mode", delivery_mode, "", ""])
            writer.writerow(["Address", delivery_address, "", ""])
        print(f"Successfully saved {csv_file} locally!")
    except Exception as e:
        print(f"Failed to save CSV: {e}")

    print(f"Order #{order_number} completely finalized.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
