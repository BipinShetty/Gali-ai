# 🛒 AI-Powered E-commerce Journey Analyzer

## Overview

This project is a cost-efficient prototype for deriving deep business insights from customer journey logs using OpenAI's GPT API. It provides a backend (FastAPI) and a minimal Streamlit-based frontend to upload JSON-formatted session data and generate actionable insights for product managers, analysts, and business leaders.

---

## 🎯 Objectives

* Automatically understand user behavior from complex e-commerce session data.
* Help PMs and analysts discover conversion blockers, engagement trends, and missed product opportunities.
* Do this affordably using OpenAI APIs by applying smart token-optimization and data summarization techniques.

---

## Key Features

### 1. Ingests customer journey data

* Accepts `customer_journeys.json` file via Streamlit file uploader
* Backend reads and validates it using FastAPI

### 2. Uses an AI model to generate insights

* Uses `openai.OpenAI(api_key=...)` to call GPT-4-Turbo
* Extracts:

  * Common user behaviors
  * Drop-off and decision points
  * Conversion vs. abandonment contrasts
  * Search quality and cart behavior
  * Product interest vs. purchase delta
  * High-impact recommendations

### 3. Presents insights in a usable UI

* Simple Streamlit-based frontend
* Displays GPT output in Markdown block
* Slider for sample size control

### 4. Clean and intuitive, not overly polished

* The UI is minimal and task-focused
* Not styled or branded — aligns with "prototype" intent

### 5. Well-chosen tools and stack

* **FastAPI**: Efficient, async-ready backend
* **OpenAI**: LLM insights engine
* **Streamlit**: Lightweight, no-boilerplate UI
* **Python**: Simple for data processing

---

## 💡 Prompt Philosophy

> *"You're reviewing {sample\_size} customer journeys..."*

The prompt intentionally avoids generic phrasing and instead mirrors how a human business analyst would review a spreadsheet or analytics dashboard. It explicitly:

* Aligns to JSON structure (`activity_type`, `search_query`, `conversion`, etc.)
* Requests observations in bullet format
* Frames GPT as a **collaborator** instead of a content generator
* Encourages **practical, non-obvious business insights**

It covers all six insight areas from the assignment plus bonus ones:

* Price sensitivity
* Product performance
* Category drop-off
---

## 💰 Cost Optimization Strategy

### 🔧 Techniques Used

* **Balanced sampling**: Equal number of converted and abandoned sessions selected (`select_balanced_sample`). This improves signal and reduces hallucination.
* **Pre-summarization**: We transform long activity logs into compact summaries with session metadata before sending to GPT (`json_summary`).
* **Token limit control**: Sessions are sliced to stay under 4K tokens.
* **Environment-based config**: API keys are securely loaded via config file or environment.
### 🔍 Token Budget Control
* Pre-processes JSON into summaries (e.g., flow, session duration, avg duration)
*  Filters out noise (no raw HTML or huge payloads sent to GPT)
*  Uses `sample_size` slider with default = 10 sessions
* Uses **balanced sampling** to select a mix of converted and abandoned sessions for richer signal


## Tools & Choices

* **OpenAI GPT-4-turbo**: Fast, cost-effective LLM
* **FastAPI**: Scalable, clean Python web framework
* **Streamlit**: Ideal for quick UI without HTML/JS
* **Python + JSON**: Native match to assignment's format

---

## Tradeoffs

* No authentication or rate limiting (prototype scope)
* Prompt + analysis assumes English input and US market patterns
* UI is functional, not styled (per brief)

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

---

## Success Criteria

* [x] Can run and analyze real `customer_journeys.json`
* [x] GPT insights reflect **actual patterns** in the sessions, not generic advice
* [x] Cost remains low (<1000 tokens typical)
* [x] Frontend works locally via Streamlit
* [x] API works via `POST /analyze`
* [x] Reviewer sees clearly how AI, backend, and UI connect

---

## How to Run It

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Provide OpenAI Key
echo '{ "OPENAI_API_KEY": "sk-..." }' > config.json

# 3. Start API
uvicorn app.main:app --reload

# 4. Launch UI
streamlit run streamlit_app.py
```
