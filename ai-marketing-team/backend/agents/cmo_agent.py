from agents.base_agent import BaseMarketingAgent
from data.rlai_brand import PRODUCT_MAPPING
import json
from typing import Dict, List

class CMOAgent(BaseMarketingAgent):
    def __init__(self):
        super().__init__(
            name="Priya (CMO)",
            role="Chief Marketing Officer",
            goal="Build RightLeftAI into the #1 recalled AI brand in India for enterprises and government. Drive pipeline through thought leadership, content, and precision outreach.",
            backstory="Priya has 15 years building B2B tech brands in India. Built marketing for 3 unicorns. Expert in content-led growth, enterprise sales cycles, and LinkedIn-first brand building."
        )

    def create_weekly_content_calendar(self, week_focus: str = None) -> Dict:
        prompt = f"""Create a 7-day content calendar for RightLeftAI.

WEEK FOCUS: {week_focus or "General brand awareness + product education"}

For each day, create content for LinkedIn, Instagram, and an email idea.

Return JSON:
{{
  "week_theme": "Theme for this week",
  "days": [
    {{
      "day": "Monday",
      "date": "2026-04-21",
      "linkedin": {{
        "content_type": "thought_leadership | product_spotlight | case_study | news_commentary | tip",
        "title": "Post headline",
        "angle": "What unique perspective or insight",
        "product_featured": "LOVAIC | SatyaDocAI | SalesBuddy | etc | none",
        "cta": "Call to action"
      }},
      "instagram": {{
        "content_type": "carousel | reel_script | infographic | quote",
        "caption_angle": "Brief description",
        "hashtags": ["AI", "RightLeftAI", "MachineLearning"]
      }},
      "email_idea": {{
        "target_domain": "banking | healthcare | manufacturing | all",
        "subject_line": "Email subject",
        "angle": "Core message"
      }}
    }}
  ],
  "weekly_thought_leadership_topic": "Long-form LinkedIn article topic for the week",
  "cmo_notes": "Strategic notes for this week"
}}

Make content specific, India-relevant, and tied to real business outcomes.
Return ONLY valid JSON."""

        output = self._call_llm(prompt, max_tokens=4096)
        try:
            return self._parse_json(output)
        except:
            return {"error": "Parse failed", "raw": output[:500]}

    def create_monthly_strategy(self, month: str) -> Dict:
        prompt = f"""Create a monthly marketing strategy for RightLeftAI for {month}.

Include:
- Focus products to push each week
- Key industry verticals to target
- Thought leadership pillars (3-4 topics we own)
- Lead generation targets
- Content mix recommendation

Return JSON:
{{
  "month": "{month}",
  "monthly_theme": "...",
  "focus_products": ["..."],
  "target_verticals": ["banking", "healthcare"],
  "thought_leadership_pillars": [
    {{"pillar": "Document Intelligence in India's KYC crisis", "products": ["SatyaDocAI"]}}
  ],
  "content_mix": {{
    "linkedin_posts_per_week": 5,
    "instagram_posts_per_week": 4,
    "emails_per_week": 2,
    "long_form_articles_per_month": 2
  }},
  "kpis": {{
    "linkedin_impressions_target": 50000,
    "email_open_rate_target": 35,
    "leads_to_discover": 20
  }},
  "cmo_strategy_note": "..."
}}

Return ONLY valid JSON."""

        output = self._call_llm(prompt, max_tokens=3000)
        try:
            return self._parse_json(output)
        except:
            return {"error": "Parse failed", "raw": output[:300]}

    def generate_weekly_report(self, metrics: Dict) -> Dict:
        prompt = f"""Generate a weekly marketing performance report for RightLeftAI.

METRICS THIS WEEK:
{json.dumps(metrics, indent=2)}

Return JSON:
{{
  "week_summary": "2-3 sentence executive summary",
  "performance_vs_target": {{
    "linkedin_impressions": {{"actual": 0, "target": 0, "status": "on_track | behind | ahead"}},
    "email_opens": {{"actual": 0, "target": 0, "status": "on_track"}},
    "leads_discovered": {{"actual": 0, "target": 0, "status": "on_track"}}
  }},
  "top_performing_content": "What worked best",
  "what_didnt_work": "What to stop or change",
  "next_week_recommendations": ["Recommendation 1", "Recommendation 2"],
  "opportunities_to_act_on": ["Specific lead or trend to chase"]
}}

Return ONLY valid JSON."""

        output = self._call_llm(prompt)
        try:
            return self._parse_json(output)
        except:
            return {"error": "Parse failed", "raw": output[:300]}
