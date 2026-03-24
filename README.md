# 🛍️ ShopMate: Agentic AI E-Commerce Assistant

A futuristic, high-performance E-Commerce platform powered by **Gemini 2.5 Flash** and **Google Cloud Firestore**.

## 🚀 Key Features
- **Agentic Intelligence**: Powered by `gemini-2.5-flash` via Vertex AI for smart order management and support.
- **Serverless Backend**: Built with **FastAPI** for high performance and low latency.
- **Cloud Native Storage**: Fully migrated to **Google Cloud Firestore** (NoSQL) for real-time, scalable data management.
- **Smart Support Tools**:
  - **Orders**: Precise check, cancel (pre-ship), address update, and quantity modification.
  - **Coupons**: Interactive browsing with cloud-synced descriptions.
  - **Profiles**: Secure fetching with automatic password redaction.
- **Session-Aware Chat**: Isolated chat histories for Guests vs. Logged-in users.
- **Minimalist Premium UI**: Sleek Black-Themed interface with glassmorphism elements.

## 🛠 Tech Stack
- **AI Core**: Google Vertex AI (Gemini 2.5 Flash)
- **Database**: Cloud Firestore
- **Backend**: Python 3.10+, FastAPI, Uvicorn
- **Frontend**: Vanilla JS, CSS3 (Minimalist High-Contrast)
- **Deployment**: Google Cloud Run (Containerized)

## 📦 Local Setup

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd Emmerce_proj
   ```

2. **Setup Environment**:
   Create a `.env` file with:
   ```env
   GOOGLE_CLOUD_PROJECT=ecommerce-ass
   GOOGLE_CLOUD_LOCATION=us-central1
   GOOGLE_API_KEY=YOUR_GEMINI_API_KEY
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize Database**:
   ```bash
   python database.py
   ```

5. **Run Locally**:
   ```bash
   python main.py
   ```
   Visit [http://localhost:8000](http://localhost:8000)

## ☁️ Deployment (GCP Cloud Run)

To deploy this service to Google Cloud Run:
```bash
gcloud run deploy ecommerce-assistant \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_CLOUD_PROJECT=ecommerce-ass,GOOGLE_CLOUD_LOCATION=us-central1,GOOGLE_API_KEY=YOUR_KEY
```

## 📜 Business Rules
- **Cancellations**: Forbidden for "Shipped" or "Delivered" orders.
- **Address Changes**: Only allowed before shipping.
- **Privacy**: Passwords are never returned in API responses or visible to the AI.
