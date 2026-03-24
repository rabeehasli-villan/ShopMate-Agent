import os
import vertexai
from vertexai.generative_models import (
    GenerativeModel, Tool, FunctionDeclaration, Content, Part, GenerationConfig
)
from services import (
    get_all_products, get_all_coupons, get_coupon_by_code, create_order, 
    get_user_orders, get_order_by_id, update_order_status_cancel, 
    update_order_address, update_order_quantity, user_register, 
    get_user_by_email, reset_user_password, get_platform_info
)
from dotenv import load_dotenv

load_dotenv()

# --- Config ---
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "ecommerce-ass")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

vertexai.init(project=PROJECT_ID, location=LOCATION)

# --- Standard E-Commerce Tools ---
retail_tools = Tool(
    function_declarations=[
        FunctionDeclaration(name="list_products", description="Show shop products and prices.", parameters={"type": "object", "properties": {}}),
        FunctionDeclaration(name="list_coupons", description="View all active/expired shop coupons.", parameters={"type": "object", "properties": {}}),
        FunctionDeclaration(name="check_coupon", description="Get description/discount for a code.", parameters={"type": "object", "properties": {"code": {"type": "string"}}, "required": ["code"]}),
        FunctionDeclaration(name="place_order", description="New order for product. Needs user_email.", parameters={"type": "object", "properties": {"user_id": {"type": "string"}, "product_id": {"type": "string"}, "delivery_address": {"type": "string"}, "quantity": {"type": "number"}}, "required": ["user_id", "product_id", "delivery_address"]}),
        FunctionDeclaration(name="check_order", description="Status/details for order ID.", parameters={"type": "object", "properties": {"order_id": {"type": "string"}}, "required": ["order_id"]}),
        FunctionDeclaration(name="cancel_order", description="Cancel if not shipped.", parameters={"type": "object", "properties": {"order_id": {"type": "string"}}, "required": ["order_id"]}),
        FunctionDeclaration(name="update_address", description="Update address for order.", parameters={"type": "object", "properties": {"order_id": {"type": "string"}, "new_address": {"type": "string"}}, "required": ["order_id", "new_address"]}),
        FunctionDeclaration(name="change_quantity", description="Modify quantity only if Pending.", parameters={"type": "object", "properties": {"order_id": {"type": "string"}, "new_quantity": {"type": "number"}}, "required": ["order_id", "new_quantity"]}),
        FunctionDeclaration(name="get_profile", description="Retrieve user profile details. Automatically redacts the password field.", parameters={"type": "object", "properties": {"email": {"type": "string"}}, "required": ["email"]}),
        FunctionDeclaration(name="reset_password", description="Update a user's password in Firestore given their email.", parameters={"type": "object", "properties": {"email": {"type": "string"}, "new_password": {"type": "string"}}, "required": ["email", "new_password"]}),
        FunctionDeclaration(name="faq_info", description="General shop usage / how-to info.", parameters={"type": "object", "properties": {}})
    ]
)

class ECommerceAgent:
    def __init__(self, api_key: str = None):
        self.model = GenerativeModel(
            "gemini-2.5-flash",
            tools=[retail_tools],
            system_instruction="You are a warm, helpful E-Commerce Assistant. "
                               "GUEST MODE: Greeting users and helping with general info. "
                               "AUTHENTICATED: Help with orders and profiles. "
                               "PASSWORD SECURITY: If a user asks for their password or profile, you must NEVER show the password field since it is redacted. If they want to change it, use the reset_password tool."
        )
        self.chat = self.model.start_chat()

    def handle_message(self, message: str, user_id=None):
        try:
            ctx = f"Login Status: {'ID ' + user_id if user_id else 'GUEST'}. "
            response = self.chat.send_message(ctx + message)
            
            for _ in range(8):
                if not response.candidates or not response.candidates[0].content.parts: break
                part = response.candidates[0].content.parts[0]
                if hasattr(part, "function_call") and part.function_call:
                    name, args = part.function_call.name, {k: v for k, v in part.function_call.args.items()}
                    res = self._dispatch(name, args)
                    response = self.chat.send_message(Part.from_function_response(name=name, response={"result": res}))
                else: break
            return response.text
        except Exception as e:
            return f"Error ({self.active_model_name if hasattr(self,'active_model_name') else 'Gemini'}): {str(e)}"

    def _dispatch(self, name, args):
        if name == "list_products": return str(get_all_products())
        if name == "list_coupons": return str(get_all_coupons())
        if name == "check_coupon": return str(get_coupon_by_code(**args))
        if name == "place_order": return str(create_order(**args))
        if name == "check_order": return str(get_order_by_id(**args))
        if name == "cancel_order": return str(update_order_status_cancel(**args))
        if name == "update_address": return str(update_order_address(**args))
        if name == "change_quantity": return str(update_order_quantity(**args))
        if name == "get_profile": return str(get_user_by_email(**args))
        if name == "reset_password": return str(reset_user_password(**args))
        if name == "faq_info": return get_platform_info()
        return "Not available."
