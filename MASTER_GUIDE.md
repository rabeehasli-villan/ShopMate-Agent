# 🍱 ShopMate: The Master Overview & Usage Guide

Welcome to the definitive manual for the **ShopMate Agentic E-Commerce Platform**! 
This project combines the power of **Gemini 2.5 Flash** with **Google Cloud Firestore**. Below, you'll find an exhaustive explanation of every feature we built, how to use them, how the Agent thinks, and how the platform is deployed.

---

## 🛠️ 1. The Core Architecture & Important Tools

### **The "Brain" of the Platform: Gemini 2.5 Flash Agent**
The assistant isn't a simple chatbot. It uses *function-calling tools* to execute real business logic based on your conversational input:
*   **`list_products` / `list_coupons`**: Automatically retrieves active stock and discount codes directly from the cloud.
*   **`place_order`**: Securely converts a user's conversational intent into a confirmed Firestore database record. 
*   **`check_order` / `cancel_order`**: Executes intelligent deep-dives to fetch item status—and strictly enforces business rules (e.g., rejecting cancellation if already marked 'Shipped').
*   **`update_address` / `change_quantity`**: Performs precise modifications to existing documents.
*   **`get_profile` / `reset_password`**: Handles user identity securely with built-in password redaction logic.

### **The Memory: Cloud Firestore (NoSQL)**
Instead of a simple local SQL setup, this platform relies entirely on Google's globally scalable Firestore database. This allows real-time updates across multiple endpoints.

---

## 👤 2. User State & Guest Mode Capabilities

### **What is Guest Mode?**
Whenever a user lands on the website without logging in, they are assigned an anonymous, isolated **Guest Session ID**. This means multiple guests can use the bot simultaneously without chat history bleeding.

**As a Guest, you can:**
*   **Say "Hi" or "Hello"**: The AI will warmly introduce itself as **ShopMate** and guide you on what you *can* do.
*   **Browse Products**: You can freely chat about the available products in the store's inventory.
*   **View Valid Coupons**: You can ask what coupons are available (`SAVE20`, `WELCOME50`, etc.).
*   **Ask FAQs**: E.g., *"How do I buy?"*, *"How to cancel?"*

**What a Guest CANNOT do:**
*   If a guest asks to see *"My Orders"* or *"My Profile"*, the AI recognizes their Guest status and politely requests that they log in first to protect data privacy.

---

## 🔐 3. Authentication & Account Recovery 

### **How to Create a User & Login:**
1.  Click the **Login** overlay on startup. 
2.  If you're new, click **Create account**. You'll need to provide a Name, Email, Password, and your default Delivery Address.
3.  Upon signing in, the Chat Interface will completely clear itself, providing a fresh, secure session linked strictly to your registered identity.

### **How to Reset a Password (Conversational):**
If you or a user forgets their password, they don't need to dig through menus. Simply ask the AI assistant:
*   *"I forgot my password for john@example.com, please change it to NewPass123."*
*   The Agent will verify the email exists in Firestore, invoke the `reset_password` tool, and update it instantly.

### **Privacy Guardrails:**
We built a strict rule in the `services.py` layer. If you ask to see your profile details, the Agent will never display your password. The system auto-redacts the password field before sending the API response up to the AI!

---

## 🛒 4. Product Buying & Application Workflow

### **How to Buy a Product:**
*   If you're signed in, simply click **"Order Now"** on any product card in the `Products` tab.
*   A browser prompt will ask you to confirm your delivery address (pre-filled with the one from your profile).
*   Once confirmed, an order document is instantly created in the cloud. You can immediately ask the AI: *"What is the status of my new order?"*

### **Applying Coupons:**
*   Navigate to the `Coupons` tab to see visually styled Active (Green) and Expired (White) coupons.
*   When checking out via the AI or browsing, you can ask for details, and the AI will pull the specific discount rate directly from the coupon document.

---

## 📦 5. Order Management (The "Agentic" Actions)

Navigating to the **Orders** tab shows a list of your purchases. We deployed action buttons that trigger Agentic tasks directly:

1.  **Details Feature**:
    *   Clicking **"Details"** forces the AI to check that specific Order ID. It will generate a summarized report on status, item, and origin address.
2.  **Cancel Option**:
    *   You can click **"Cancel"** or ask the AI to cancel it. 
    *   *Intelligent Block:* If the order's status is "Shipped" or "Delivered", the AI's internal guardrails will stop the action and inform you it isn't possible anymore.
3.  **Address Option**:
    *   You can request to reroute a package. The AI will accept a new address string and update the Cloud DB (provided the item hasn't shipped yet!).
4.  **Quantity Option**:
    *   Want 3 laptops instead of 1? The agent can update your `Pending` order seamlessly.

---

## ☁️ 6. Cloud Native Deployment Architecture

We successfully transitioned this app from a local script to a production-grade GCP service.

### **How it's deployed:**
1.  **Dockerized Base**: The entire project was wrapped up in an isolated `python:3.10-slim` container using a `Dockerfile`.
2.  **Dependencies Cleaned**: We optimized the `requirements.txt` to only include the precise GCP components (`google-cloud-aiplatform`, `google-cloud-firestore`, etc.), preventing build-time bloat.
3.  **GCP Artifact Registry & Cloud Run**:
    *   We leveraged `gcloud run deploy`. 
    *   This built the Docker container on Google's remote servers and placed the application behind Google's load balancers.
4.  **Security IAM Config**: 
    *   For the Cloud Run app to securely talk to the Firestore database and Vertex AI, we updated the Identity Access Management (IAM) for the internal Compute Service Account (`roles/datastore.user` and `roles/aiplatform.user`), ensuring zero permission issues without needing to expose raw account JSON files.

The final deployed URL connects directly to these microservices, ready to handle large scale global traffic!
