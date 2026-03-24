import os
from google.cloud import firestore
from dotenv import load_dotenv

load_dotenv()

# Client
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "ecommerce-ass")
db = firestore.Client(project=PROJECT_ID)

# --- Service Functions ---

def get_all_products():
    docs = db.collection("products").stream()
    return [{"id": d.id, **d.to_dict()} for d in docs]

def get_product(p_id):
    doc = db.collection("products").document(p_id).get()
    return {"id": doc.id, **d.to_dict()} if doc.exists else None

def get_all_coupons():
    docs = db.collection("coupons").stream()
    return [d.to_dict() for d in docs]

def get_coupon_by_code(code):
    doc = db.collection("coupons").document(code.upper()).get()
    return doc.to_dict() if doc.exists else None

def user_login(email, password):
    doc = db.collection("users").document(email).get()
    if doc.exists:
        u = doc.to_dict()
        if u["password"] == password:
            u.pop("password") # SECURE: Redact password after successful match
            return {"id": doc.id, **u}
    return None

def user_register(name, email, password, address=""):
    doc_ref = db.collection("users").document(email)
    if doc_ref.get().exists:
        return "Email already exists."
    doc_ref.set({"name": name, "email": email, "password": password, "address": address})
    return f"Successfully registered user {name}."

def get_user_by_email(email):
    doc = db.collection("users").document(email).get()
    if doc.exists:
        u = doc.to_dict()
        u.pop("password", None) # SECURITY: Never return the password
        return u
    return None

def reset_user_password(email, new_password):
    """Securely update a user's password in Firestore."""
    doc_ref = db.collection("users").document(email)
    if not doc_ref.get().exists:
        return "Error: User with that email not found."
    doc_ref.update({"password": new_password})
    return f"Password for {email} has been successfully updated. You can now log in."

def create_order(user_id, product_id, delivery_address, quantity=1):
    # Quick product lookup
    p_doc = db.collection("products").document(product_id).get()
    if not p_doc.exists: return "Product not found."
    p = p_doc.to_dict()
    
    order_ref = db.collection("orders").add({
        "user_id": user_id, "product_id": product_id, "product_name": p["name"],
        "status": "Pending", "delivery_address": delivery_address, "quantity": quantity,
        "ordered_at": firestore.SERVER_TIMESTAMP
    })
    return f"Order #{order_ref[1].id} placed successfully."

def get_user_orders(user_id):
    docs = db.collection("orders").where("user_id", "==", user_id).stream()
    return [{"id": d.id, **d.to_dict()} for d in docs]

def get_order_by_id(order_id):
    doc = db.collection("orders").document(order_id).get()
    return {"id": doc.id, **doc.to_dict()} if doc.exists else None

# --- Logic Condition Updates ---

def update_order_status_cancel(order_id):
    doc_ref = db.collection("orders").document(order_id)
    doc = doc_ref.get()
    if not doc.exists: return "Order not found."
    data = doc.to_dict()
    if data["status"] in ["Shipped", "Delivered"]:
        return f"Cannot cancel order {order_id}. It is already {data['status']}."
    doc_ref.update({"status": "Cancelled"})
    return f"Order {order_id} has been successfully cancelled."

def update_order_address(order_id, new_address):
    doc_ref = db.collection("orders").document(order_id)
    doc = doc_ref.get()
    if not doc.exists: return "Order not found."
    data = doc.to_dict()
    if data["status"] in ["Shipped", "Delivered"]:
        return f"Cannot update address. Order {order_id} is already {data['status']}."
    doc_ref.update({"delivery_address": new_address})
    return f"Delivery address for order {order_id} updated."

def update_order_quantity(order_id, new_quantity):
    doc_ref = db.collection("orders").document(order_id)
    doc = doc_ref.get()
    if not doc.exists: return "Order not found."
    data = doc.to_dict()
    if data["status"] != "Pending":
        return f"Cannot change quantity. Order {order_id} is already in '{data['status']}' state."
    doc_ref.update({"quantity": new_quantity})
    return f"Quantity for order {order_id} updated."

def get_platform_info():
    return "Cloud Firestore Agent Platform active. Secure Password Resets and Profile redaction now enabled."
