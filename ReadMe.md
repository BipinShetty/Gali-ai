# 🛒 AI-Powered E-commerce Journey Analyzer

## Overview

This project is a cost-efficient prototype for deriving deep business insights from customer journey logs using OpenAI's GPT API. It provides a backend (FastAPI) and a minimal Streamlit-based frontend to upload JSON-formatted session data and generate actionable insights for product managers, analysts, and business leaders.

---

## 🎯 Objectives

* Automatically understand user behavior from complex e-commerce session data.
* Help PMs and analysts discover conversion blockers, engagement trends, and missed product opportunities.
* Do this affordably using OpenAI APIs by applying smart token-optimization and data summarization techniques.

---

## ✅ Key Features

### 🔎 Insight Dimensions Covered

Our prompt is specifically engineered to extract useful observations, such as:

* **Behavioral patterns**: what successful users do differently
* **Drop-off points**: where users lose interest
* **Search quality & gaps**: which searches succeed vs. frustrate
* **Cart behavior**: which products are added but not purchased
* **Conversion insights**: device, category, pricing influences
* **Product trends**: top viewed vs. top purchased discrepancies
* **Customer hesitation signals**: re-visits, search loops, time spent

These are **directly rooted in the schema of the JSON**: `activity_type`, `conversion`, `cart_value`, `search_query`, etc.
![Screen Shot 2025-05-06 at 8 31 50 PM](https://github.com/user-attachments/assets/c3ec5ff9-573f-4e5d-996a-f82835853b22)
![Screen Shot 2025-05-06 at 8 32 20 PM](https://github.com/user-attachments/assets/ef625286-5a7d-4217-9c5e-c768b36736a2)

---

## 💰 Cost Optimization Strategy

### 🔧 Techniques Used

* **Balanced sampling**: Equal number of converted and abandoned sessions selected (`select_balanced_sample`). This improves signal and reduces hallucination.
* **Pre-summarization**: We transform long activity logs into compact summaries with session metadata before sending to GPT (`json_summary`).
* **Token limit control**: Sessions are sliced to stay under 4K tokens.
* **Environment-based config**: API keys are securely loaded via config file or environment.

➡️ This reduces token usage by **70–85%** vs. naive approaches.

---

## 📂 Project Structure

```
Gali-ai/
├── app/
│   ├── main.py         # FastAPI backend
│   ├── analyzer.py     # GPT-based insight engine
│   ├── config.py       # Secure API key loader
├── streamlit_app.py    # Upload & UI
├── requirements.txt    # Dependencies
├── config.json         # (local only) OpenAI key
├── customer_journeys.json  # Input example
```

---

## ⚙️ How to Run

### Step 1: Install requirements

```bash
pip install -r requirements.txt
```

### Step 2: Add OpenAI Key

Save this file as `config.json` in the root:

```json
{
  "OPENAI_API_KEY": "sk-..."
}
```

### Step 3: Start FastAPI

```bash
uvicorn app.main:app --reload
```

### Step 4: Launch Streamlit

```bash
streamlit run streamlit_app.py
```

---

## 🎯 Success Criteria

A successful run should:

* Accept a JSON of user sessions
* Return GPT-generated insights clearly tied to what’s in the data
* Respect cost and prompt constraints
* Avoid generic fluff — insights should be actionable and reflect real journey patterns (e.g., "high cart values on mobile drop at checkout").

---

## 🙌 Why It Works

The combination of LLM + domain-aligned prompt + session sampling + activity summarization = high-quality analysis at low cost. This is not just an LLM wrapper — it’s a lightweight but intelligent insight engine.

