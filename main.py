import os
import traceback
from typing import Optional
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from agent import ECommerceAgent
from services import (
    user_login, user_register, get_all_products, get_all_coupons, 
    get_user_orders, create_order, get_user_by_email
)
from database import init_db
from dotenv import load_dotenv

load_dotenv()

# Initialize Startup
init_db()

# --- Config ---
API_KEY = os.getenv("GOOGLE_API_KEY")

app = FastAPI()

# Session Storage
agents_store = {}

def get_user_agent(session_id: str):
    global agents_store
    if session_id not in agents_store:
        agents_store[session_id] = ECommerceAgent(api_key=API_KEY)
    return agents_store[session_id]

# --- Models (More flexible for Pydantic V2) ---

class LoginRequest(BaseModel):
    email: str
    password: str

class SignupRequest(BaseModel):
    name: str
    email: str
    password: str
    address: str = ""

class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None
    session_id: Optional[str] = "guest_default"

class OrderRequest(BaseModel):
    user_id: str
    product_id: str
    delivery_address: str
    quantity: int = 1

# --- API Endpoints ---

@app.post("/api/chat")
async def chat(req: ChatRequest):
    try:
        # Determine the unique session key
        session_key = req.user_id if req.user_id else req.session_id
        if not session_key: session_key = "anonymous_guest"

        print(f"[CHAT] Message from {session_key}: {req.message}")
        
        agent = get_user_agent(session_key)
        response = agent.handle_message(req.message, user_id=req.user_id)
        
        if not response:
            return {"response": "The AI is currently formulating a response. Please re-state your query."}
            
        return {"response": response}
    except Exception as e:
        print(f"[ERROR] Chat failure: {e}")
        traceback.print_exc()
        return {"response": f"I'm sorry, I'm having trouble connecting to the cloud. Please check if your Project ID and API Key are valid."}

@app.post("/api/login")
async def login(req: LoginRequest):
    user = user_login(req.email, req.password)
    return {"success": True, "user": user} if user else {"success": False, "message": "Invalid Login."}

@app.post("/api/signup")
async def signup(req: SignupRequest):
    res = user_register(req.name, req.email, req.password, req.address)
    return {"success": "registered" in res, "message": res}

@app.get("/api/products")
async def products(): return get_all_products()

@app.get("/api/coupons")
async def coupons(): return get_all_coupons()

@app.get("/api/orders/{user_id}")
async def orders(user_id: str): return get_user_orders(user_id)

@app.post("/api/place_order")
async def place_order(req: OrderRequest):
    res = create_order(req.user_id, req.product_id, req.delivery_address, req.quantity)
    return {"success": True, "message": res}

@app.get("/")
async def root(): return FileResponse("index.html")

@app.get("/style.css")
async def css(): return FileResponse("style.css")

@app.get("/script.js")
async def js(): return FileResponse("script.js")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
