import os
import random
from google.cloud import firestore
from dotenv import load_dotenv

load_dotenv()

# --- Firestore Client ---
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "ecommerce-ass")
db = firestore.Client(project=PROJECT_ID)

def init_db():
    """Seed abundant mock data into Firestore."""
    print("Populating Firestore with rich test data...")

    # Products List
    products_ref = db.collection("products")
    # Clean products for fresh IDs if needed (optional)
    products = [
        {"name": "MacBook Pro M3", "price": 1999.0, "description": "High-end laptop."},
        {"name": "iPhone 15 Pro", "price": 1199.0, "description": "Titanium smartphone."},
        {"name": "Sony XM5 Headphones", "price": 349.0, "description": "ANC King."},
        {"name": "Apple Watch Ultra", "price": 799.0, "description": "Rugged watch."},
        {"name": "Samsung S24 Ultra", "price": 1299.0, "description": "Ultimate Android."},
        {"name": "Dell XPS 15", "price": 1599.0, "description": "Windows powerhouse."},
        {"name": "AirPods Pro 2", "price": 249.0, "description": "Best earbuds."}
    ]
    product_ids = []
    for p in products:
        # Avoid duplicates by checking name (simple check)
        existing = products_ref.where("name", "==", p["name"]).limit(1).get()
        if not existing:
            ref = products_ref.add(p)
            product_ids.append(ref[1].id)
        else:
            product_ids.append(existing[0].id)

    # Users
    users_ref = db.collection("users")
    test_users = [
        {"email": "rabeeh@example.com", "name": "Rabeeh", "password": "pass123", "address": "Main St, Kerala"},
        {"email": "john@example.com", "name": "John Smith", "password": "pass123", "address": "Springfield, USA"},
        {"email": "emma@example.com", "name": "Emma Watson", "password": "pass123", "address": "London, UK"},
        {"email": "tester@example.com", "name": "Master Tester", "password": "pass123", "address": "Cloud City"}
    ]
    for u in test_users:
        users_ref.document(u["email"]).set(u)

    # Orders (Randomly Generated)
    orders_ref = db.collection("orders")
    statuses = ["Pending", "Packed", "Shipped", "Delivered", "Cancelled"]
    
    # Generate 5 random orders for each test user
    for u in test_users:
        # Check if they already have orders (keep it clean)
        existing_orders = orders_ref.where("user_id", "==", u["email"]).limit(1).get()
        if not existing_orders:
            for _ in range(5):
                p_id = random.choice(product_ids)
                p_doc = products_ref.document(p_id).get().to_dict()
                orders_ref.add({
                    "user_id": u["email"],
                    "product_id": p_id,
                    "product_name": p_doc["name"],
                    "status": random.choice(statuses),
                    "quantity": random.randint(1, 3),
                    "delivery_address": u["address"],
                    "ordered_at": firestore.SERVER_TIMESTAMP
                })
    
    # Coupons (Ensure active/expired are clearly marked)
    coupons_ref = db.collection("coupons")
    coupon_data = [
        {"code": "SAVE20", "discount": 20, "description": "20% off for newcomers", "status": "Active"},
        {"code": "FESTIVE10", "discount": 10, "description": "10% Holiday Joy", "status": "Expired"},
        {"code": "WELCOME50", "discount": 50, "description": "First time user mega deal", "status": "Active"},
        {"code": "FLASH5", "discount": 5, "description": "Flash sale for loyal users", "status": "Active"}
    ]
    for c in coupon_data:
        coupons_ref.document(c["code"]).set(c)

    print("Success! Firestore is now populated with rich, diverse data.")

if __name__ == "__main__":
    init_db()
