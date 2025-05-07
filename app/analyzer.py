import os
import json
from app.config import get_openai_key

# Builds the prompt as per req doc to get quick insights into customer behaviour
# Take 10 sample size at a time by default to optimize LLM call cost.
def analyze_journeys(journeys, sample_size=10):
    summary_input = json_summary(select_balanced_sample(journeys, sample_size))
    prompt = f"""
You are a senior business analyst for an e-commerce platform. You are provided with a summarized sample of {sample_size} customer sessions:

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
    half = sample_size // 2

    selected_converted = converted[:half]
    selected_abandoned = abandoned[:sample_size - len(selected_converted)]
    # Make sure the segmentation is balanced and not skewed towards one
    if len(selected_converted) < half:
        extra = converted[half:half + (sample_size - len(selected_converted) - len(selected_abandoned))]
        selected_converted += extra
    if len(selected_abandoned) < (sample_size - half):
        extra = abandoned[half:half + (sample_size - len(selected_converted) - len(selected_abandoned))]
        selected_abandoned += extra

    return (selected_converted + selected_abandoned)[:sample_size]


#This section builds the summary input to analyze
def json_summary(journeys):
    from datetime import datetime
    from collections import Counter

    summary = []
    product_views = Counter()
    product_purchases = Counter()

    for j in journeys:
        activities = j.get("activities", [])
        start = datetime.fromisoformat(j.get("session_start").replace("Z", "+00:00"))
        end = datetime.fromisoformat(j.get("session_end").replace("Z", "+00:00"))
        session_duration = (end - start).total_seconds()
        total_dur = sum(a.get("duration_ms", 0) for a in activities)
        activity_count = len(activities)

        # go thru all activities in the session...
        for a in activities:
            # if user viewed a product, track that
            if a.get("activity_type") == "product_view":
                product_id = a["details"].get("product_id")  # grab product id from activity details
                if product_id:  # double-check just in case it's missing
                    product_views[product_id] += 1  # count how many times this product was seen

            # if user actually bought something
            elif a.get("activity_type") == "purchase":
                # some sessions have multiple items purchased, loop accordingly
                for _ in range(a["details"].get("items", 1)):
                    product_purchases[a["details"].get("product_id", "unknown")] += 1

        summary.append({
            "session_id": j.get("session_id"),
            "device": j.get("device_type"),
            "converted": j.get("conversion"),
            "searches": [a["details"].get("search_query") for a in activities if a.get("activity_type") == "search"],
            "flow": [a.get("activity_type") for a in activities],
            "session_duration_sec": session_duration,
            "avg_activity_duration_ms": round(total_dur / max(1, activity_count)),
            "number_of_activities": activity_count
        })

    # if there's at least one session summary built above
    if summary:
        # get top 5 most viewed products across all sessions
        top_views = dict(product_views.most_common(5))

        # get top 5 most purchased products (again, across all)
        top_purchases = dict(product_purchases.most_common(5))

        # attach these to the first session summary — bit of a hack but works for now
        # ideally should go in a separate section maybe
        summary[0]["top_viewed_products"] = top_views
        summary[0]["top_purchased_products"] = top_purchases

    return json.dumps(summary, indent=2)
