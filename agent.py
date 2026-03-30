import json
import os
from groq import Groq
from stock_db import check_stock
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

sessions = {}
carts = {}
finalized_orders = {}

SYSTEM_PROMPT = """You are a highly efficient conversational AI voice assistant for a supermarket.
Speak in natural, plain Indian English without ANY markdown. NEVER use asterisks, code blocks, JSON, or backticks!

Your conversation flow MUST be EXACTLY as follows:
1. Welcome the customer and ask for their order.
2. When the customer asks for items (e.g. "I need 1 kg of potato and 2 kg of tomato"):
   - Immediately use `add_to_cart_tool` for ALL requested items in parallel (make multiple tool calls at once).
   - DO NOT wait for confirmation. Automatically add them.
   - For items successfully added, tell the customer their prices in Indian Rupees (₹) and confirm what was added.
   - Then immediately ask: "Do you need anything else?"
   - If `add_to_cart_tool` returns insufficient stock, tell them what is available and ask if they want that.
3. If the customer just asks "Do you have [item]?", use `check_stock_tool` to check availability without adding.
4. If the customer wants to remove an item or reduce its quantity (e.g., "remove 1 kg of tomato"), use `remove_from_cart_tool`.
5. Once they say they don't need anything else ("No") or say "Checkout":
   - Read out their entire order list.
   - State the grand total price in Rupees.
   - Ask: "Is this order correct?" and WAIT for them to confirm.
6. Once they confirm it is correct:
   - Ask: "Would you like pickup or delivery?"
   - For delivery, ask for their full address.
7. Use `finalize_order_tool` to finalize. Say EXACTLY: "Thank you. Your order has been placed successfully." and end the call.

CRITICAL RULES:
- The currency is Indian Rupees (₹).
- Do not announce your background actions. Just process it.
- If they ask for multiple items, process them all simultaneously!
"""

tools = [
    {
        "type": "function",
        "function": {
            "name": "check_stock_tool",
            "description": "Check if a product is in stock and its price without adding it to the cart.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": "string",
                        "description": "The English name of the product",
                    }
                },
                "required": ["product_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_to_cart_tool",
            "description": "Directly check stock and add a product to the cart. Use this when the user says they want an item.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": "string",
                        "description": "The English name of the product",
                    },
                    "requested_quantity": {
                        "type": "number",
                        "description": "The quantity the user requested",
                    }
                },
                "required": ["product_name", "requested_quantity"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "remove_from_cart_tool",
            "description": "Remove or reduce the quantity of an item currently in the cart.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": "string",
                        "description": "The English name of the product to remove",
                    },
                    "quantity_to_remove": {
                        "type": "number",
                        "description": "The quantity to deduct from the cart",
                    }
                },
                "required": ["product_name", "quantity_to_remove"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "finalize_order_tool",
            "description": "Confirm the order and delivery mode.",
            "parameters": {
                "type": "object",
                "properties": {
                    "delivery_mode": {
                        "type": "string",
                        "description": "'pickup' or 'delivery'",
                    },
                    "delivery_address": {
                        "type": "string",
                        "description": "Full delivery address, empty if pickup",
                    }
                },
                "required": ["delivery_mode", "delivery_address"],
            },
        },
    }
]

caller_numbers = {}
call_statuses = {}

def init_session(call_sid: str, caller_number: str = None):
    carts[call_sid] = []
    finalized_orders[call_sid] = None
    caller_numbers[call_sid] = caller_number or "Unknown Caller"
    call_statuses[call_sid] = "in-progress"
    sessions[call_sid] = [{"role": "system", "content": SYSTEM_PROMPT}]

def set_status(call_sid: str, status: str):
    if call_sid in call_statuses:
        call_statuses[call_sid] = status

def get_cart(call_sid: str):
    return carts.get(call_sid, [])

def process_message(call_sid: str, user_text: str, caller_number: str = None):
    if call_sid not in sessions:
        init_session(call_sid, caller_number)
        
    messages = sessions[call_sid]
    messages.append({"role": "user", "content": user_text})
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            tools=tools,
            tool_choice="auto",
            max_tokens=1024,
            temperature=0.3
        )
        response_message = response.choices[0].message
        
        tool_calls = response_message.tool_calls
        if tool_calls:
            messages.append(response_message)
            replies = []
            
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                try:
                    function_args = json.loads(tool_call.function.arguments)
                except Exception:
                    function_args = {}
                    
                print(f"[{call_sid}] Tool call: {function_name}({function_args})")
                
                prod = str(function_args.get("product_name", "item"))
                
                if function_name == "check_stock_tool":
                    res = check_stock(prod, 0)
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": json.dumps({"found": res["found"], "price_per_unit": res.get("price_per_unit", 0)})
                    })
                    if res["found"]:
                        replies.append(f"Yes, we have {prod} for {res.get('price_per_unit', 0)} rupees.")
                    else:
                        replies.append(f"Sorry, we don't have {prod}.")
                        
                elif function_name == "add_to_cart_tool":
                    try:
                        qty = float(function_args.get("requested_quantity", 1.0))
                    except (ValueError, TypeError):
                        qty = 1.0
                        
                    res = check_stock(prod, qty)
                    if res["found"] and res["can_fulfill"]:
                        carts[call_sid].append({"product": prod, "quantity": qty, "price": float(res.get("price_per_unit", 0))})
                        total = qty * float(res.get("price_per_unit", 0))
                        messages.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": '{"status": "success"}'
                        })
                        replies.append(f"I've added {qty} {prod}. That's {total} rupees.")
                    elif res["found"]:
                        messages.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": '{"status": "insufficient_stock"}'
                        })
                        replies.append(f"Sorry, we only have {res.get('available_quantity', 0)} {prod} left.")
                    else:
                        messages.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": '{"status": "not_found"}'
                        })
                        replies.append(f"Sorry, we do not carry {prod}.")
                        
                elif function_name == "remove_from_cart_tool":
                    try:
                        qty_to_remove = float(function_args.get("quantity_to_remove", 1.0))
                    except (ValueError, TypeError):
                        qty_to_remove = 1.0
                        
                    removed = False
                    current_cart = carts.get(call_sid, [])
                    for i in range(len(current_cart) - 1, -1, -1):
                        item = current_cart[i]
                        if str(item["product"]).lower() == prod.lower():
                            if float(item["quantity"]) <= qty_to_remove:
                                current_cart.pop(i)
                                messages.append({"tool_call_id": tool_call.id, "role": "tool", "name": function_name, "content": '{"status":"removed"}'})
                                replies.append(f"I have completely removed {prod} from your list.")
                            else:
                                item["quantity"] = float(item["quantity"]) - qty_to_remove
                                messages.append({"tool_call_id": tool_call.id, "role": "tool", "name": function_name, "content": '{"status":"reduced"}'})
                                replies.append(f"I reduced {prod} by {qty_to_remove}. You now have {item['quantity']} left.")
                            removed = True
                            break
                    if not removed:
                        messages.append({"tool_call_id": tool_call.id, "role": "tool", "name": function_name, "content": '{"status":"not_found"}'})
                        replies.append(f"Hmm, you don't have any {prod} in your cart.")
                        
                elif function_name == "finalize_order_tool":
                    finalized_orders[call_sid] = {
                        "delivery_mode": str(function_args.get("delivery_mode", "pickup")),
                        "delivery_address": str(function_args.get("delivery_address", ""))
                    }
                    messages.append({"tool_call_id": tool_call.id, "role": "tool", "name": function_name, "content": '{"status":"finalized"}'})
                    replies.append("Thank you. Your order has been placed successfully.")

            final_text = " ".join(replies)
            if "placed successfully" not in final_text and len(replies) > 0:
                final_text += " Do you need anything else?"
                
            # Manually append the generated response so Groq retains memory context perfectly without burning an extra API call!
            if final_text:
                messages.append({"role": "assistant", "content": final_text})
                return final_text
        
        # If no tool calls (general conversation, reading the cart back), return text!
        if getattr(response_message, "content", None):
            messages.append(response_message)
            return response_message.content
            
        return "I am here. Do you need anything else?"
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Groq Error: {e}")
        return "Sorry, I had a brief technical glitch. Could you repeat that?"

def is_finalized(call_sid: str):
    return finalized_orders.get(call_sid, None)
