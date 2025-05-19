import os
from app.config import get_openai_key
import json
from datetime import datetime
from collections import Counter, defaultdict

# Builds the prompt as per req doc to get quick insights into customer behaviour
# Take 10 sample size at a time by default to optimize LLM call cost.


# activity type
    # page_view ->  The produc/page navigate and stuff of interest
    # search -> The outcome of seach, what didnt bring result vs exits
    # product_view -> The product of interest
    # add_to_cart -> the product of interest,check price sensitivity, carted but not brought
    # checkout -> Check for flow and maybe shipping cost
    # purchase -> product purchased and conversion rate.

    # Additional prompts
    # Segment Abandonment by Journey Stage
    #     - Search abandonment (searched but no view)
    #     - Product abandonment (viewed but no cart)
    #     - Cart abandonment (added but no checkout)
    #     - Checkout abandonment (initiated but didn't complete)

    # Top Carted But Not Purchased Products
    #     Products that are added to cart often but never purchased:
    #     - "Deluxe Smartwatches H" (p-1036)
    #     - "Classic Smartwatches E" (p-1033)
    #     - "Vintage Laptops C" (p-1009)

    # Purchase Paths and behaviour
    # Monetization Insight Layer
    #     - Average conversion revenue per session
    #     - Highest value cart that got abandonedc

    # User Paths and behaviour
        # New vs returning user



def analyze_journeys(journeys, sample_size=10):
    summary_input = json_summary(select_balanced_sample(journeys, sample_size))
    prompt = f"""
You are a senior business analyst for an e-commerce platform. You are provided with a summarized sample of {sample_size} customer sessions.
Note: The lists of "viewed_products_by_popularity" and "purchased_products_by_popularity" are pre-sorted in descending order of frequency — i.e., the most viewed/purchased products appear at the top.

{summary_input}

Please analyze and generate insights across these dimensions:
1. Behavioral patterns: What are the common behaviors in converted vs abandoned sessions?
2. Drop-off points: Are there recurring steps where users disengage?
3. Search quality: Which searches led to product views or drop-offs?
4. Cart behavior: Are there products that frequently get abandoned?
5. Recommendations: Suggest 3–5 high-impact changes to improve conversion or product discovery.
6. Product Insights: Which products are viewed often but rarely purchased?
7. Search Gaps: Which searches returned few or no results and correlated with exits?
8. Repeated Actions: Any user sessions that suggest indecision or hesitation?
9. Price Barriers: At what price points do users typically abandon?
10. Device/Category Impact: Do certain devices or categories show stronger engagement?

Respond in clear bullet points.
"""

    try:
        from openai import OpenAI
        client = OpenAI(api_key=get_openai_key())
        response = client.chat.completions.create(
            model=os.getenv("GPT_MODEL", "gpt-4-turbo"),
            messages=[
                {"role": "system", "content": "You generate business insights from customer journey logs."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error during analysis: {str(e)}"


# This section divides the customer into segmentation of abandoned vs conversion
def select_balanced_sample(journeys, sample_size):
    converted = [j for j in journeys if j.get("conversion")]
    abandoned = [j for j in journeys if not j.get("conversion")]

    # Calculate max number of balanced samples we can get
    max_balanced = min(len(converted), len(abandoned), sample_size // 2)

    # Select balanced subset
    selected_converted = converted[:max_balanced]
    selected_abandoned = abandoned[:max_balanced]

    return selected_converted + selected_abandoned

def json_summary(journeys):
    """
    Summarizes a list of customer journey sessions into a compact JSON structure
    that captures behavioral insights, search activity, product interaction, and purchase behavior.
    """

    summary = []
    product_views = Counter()         # Tracks how many times each product is viewed
    product_purchases = Counter()     # Tracks how many times each product is purchased
    product_info = defaultdict(dict)  # Stores metadata (name, category, price) for each product_id

    for j in journeys:
        activities = j.get("activities", [])

        # Compute session duration
        start = datetime.fromisoformat(j.get("session_start").replace("Z", "+00:00"))
        end = datetime.fromisoformat(j.get("session_end").replace("Z", "+00:00"))
        session_duration = (end - start).total_seconds()

        # Total duration across all activities for avg calculation
        total_dur = sum(a.get("duration_ms", 0) for a in activities)
        activity_count = len(activities)

        # Initialize containers to collect specific activity-level insights
        searches = []
        search_results = []
        pages_viewed = []
        cart_additions = []
        checkout_steps = []
        total_revenue = 0
        total_purchases = 0

        for a in activities:
            act_type = a.get("activity_type")
            details = a.get("details", {})

            # Capture product views and associated metadata
            if act_type == "product_view":
                pid = details.get("product_id")
                if pid:
                    product_views[pid] += 1
                    product_details = details.get("product_details", {})
                    if product_details:
                        product_info[pid] = {
                            "name": product_details.get("name"),
                            "category": product_details.get("category"),
                            "price": product_details.get("price"),
                        }

            # Track purchases, quantities, and total spend
            elif act_type == "purchase":
                pid = details.get("product_id", "unknown")
                qty = details.get("items", 1)
                total_purchases += 1
                total_revenue += details.get("total_amount", 0)
                for _ in range(qty):
                    product_purchases[pid] += 1

            # Record search terms and how many results were returned
            elif act_type == "search":
                searches.append(details.get("search_query"))
                search_results.append({
                    "query": details.get("search_query"),
                    "results": details.get("results_count")
                })

            # Track which category or product pages were viewed
            elif act_type == "page_view":
                pages_viewed.append(details.get("page_path"))

            # Track what was added to the cart (but not necessarily purchased)
            elif act_type == "add_to_cart":
                cart_additions.append({
                    "product_id": details.get("product_id"),
                    "quantity": details.get("quantity"),
                    "cart_value": details.get("cart_value")
                })

            # Capture checkout steps (e.g., address, payment) and whether they were completed
            elif act_type == "checkout":
                checkout_steps.append({
                    "step": details.get("step"),
                    "completed": details.get("completed")
                })

        # Summarize one session's worth of information
        session_summary = {
            "session_id": j.get("session_id"),
            "device": j.get("device_type"),
            "converted": j.get("conversion"),
            "session_duration_sec": session_duration,
            "avg_activity_duration_ms": round(total_dur / max(1, activity_count)),
            "number_of_activities": activity_count,
            "flow": [a.get("activity_type") for a in activities],  # ordered sequence of actions
            "searches": searches,
            "search_results": search_results,
            "pages_viewed": pages_viewed,
            "cart_additions": cart_additions,
            "checkout_steps": checkout_steps,
            "purchase_summary": {
                "total_purchases": total_purchases,
                "total_revenue": round(total_revenue, 2)
            }
        }

        summary.append(session_summary)

    # Attach top-level insights across all sessions — only once
    if summary:
        def enrich(counter):
            """
            Takes a product counter and returns a list of top N=25 products with their metadata
            (or 'Unknown' if details were not captured during the session).
            """
            enriched = []
            for pid, count in counter.most_common(25):
                info = product_info.get(pid, {})
                enriched.append({
                    "product_id": pid,
                    "name": info.get("name", "Unknown"),
                    "category": info.get("category", "Unknown"),
                    "price": info.get("price", "Unknown"),
                    "count": count
                })
            return enriched

        summary[0]["viewed_products_by_popularity"] = enrich(product_views)
        summary[0]["purchased_products_by_popularity"] = enrich(product_purchases)

    return json.dumps(summary, indent=2)



