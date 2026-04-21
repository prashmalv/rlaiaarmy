from agents.base_agent import BaseMarketingAgent
from data.rlai_brand import PRODUCT_MAPPING, PAIN_POINTS
import json
from typing import Dict, List

class EmailCampaignAgent(BaseMarketingAgent):
    def __init__(self):
        super().__init__(
            name="Neha (Email)",
            role="Email Marketing Specialist",
            goal="Write emails that leads actually open, read, and reply to. Build relationships, not just awareness.",
            backstory="Neha has 8 years in B2B email marketing. Average open rate 42% vs industry 21%. Expert at personalization, nurture sequences, and making CXOs respond."
        )

    def create_nurture_email(self, lead: Dict, ai_news_topic: str = None) -> Dict:
        domain = lead.get("domain", "technology")
        products = PRODUCT_MAPPING.get(domain, ["LOVAIC", "SatyaDocAI"])
        pain = PAIN_POINTS.get(products[0], []) if products else []

        prompt = f"""Write a lead nurture email for RightLeftAI.

LEAD DETAILS:
- Name: {lead.get('name', 'there')}
- Company: {lead.get('company', 'your company')}
- Domain: {domain}
- Designation: {lead.get('designation', 'Decision Maker')}

RELEVANT AI NEWS/TOPIC: {ai_news_topic or f"Latest AI developments in {domain} sector"}
RELEVANT PRODUCTS: {', '.join(products[:2])}
PAIN POINTS TO REFERENCE: {json.dumps(pain[:2])}

Email requirements:
- Subject line: Personalized, curiosity-driven, NOT salesy (avoid "Check out our product!")
- Body: 150-200 words, conversational
- Tie AI news/trend to THEIR business impact
- Mention 1 RLAI solution naturally — not as a hard sell
- CTA: Low-friction (reply to this email, read article, 15-min chat)
- P.S. line (always increases replies)

Return JSON:
{{
  "subject": "Email subject line",
  "subject_alternatives": ["Alt 1", "Alt 2"],
  "preview_text": "Email preview text (40 chars)",
  "greeting": "Hi [Name],",
  "body_html": "<p>Full HTML email body</p>",
  "body_text": "Plain text version",
  "cta": "Primary call to action",
  "ps_line": "P.S. line",
  "personalization_tokens": ["{{name}}", "{{company}}"],
  "send_day": "Tuesday | Wednesday | Thursday",
  "send_time": "9:30 AM IST"
}}

Return ONLY valid JSON."""

        output = self._call_llm(prompt, max_tokens=2000)
        try:
            return self._parse_json(output)
        except:
            return {"subject": f"AI in {domain}", "body_text": output, "error": "partial"}

    def create_industry_news_digest(self, domain: str, news_items: List[Dict]) -> Dict:
        products = PRODUCT_MAPPING.get(domain, [])
        news_text = "\n".join([f"- {n.get('title', '')}: {n.get('summary', '')}" for n in news_items[:5]])

        prompt = f"""Create a personalized AI news digest email for {domain} industry leads.

INDUSTRY: {domain}
NEWS THIS WEEK:
{news_text}

RLAI RELEVANT PRODUCTS: {', '.join(products)}

Create an email that:
- Curates the most relevant AI news for THIS industry (not generic AI news)
- Adds RLAI's expert commentary on 1-2 items
- Subtly shows how RLAI products relate WITHOUT hard selling
- Makes the reader feel: "These people really understand my industry"

Return JSON:
{{
  "subject": "Engaging subject (e.g., '5 AI moves your banking competitors made this week')",
  "header_line": "One-line intro",
  "news_items": [
    {{
      "headline": "News headline",
      "summary": "2-3 sentence summary",
      "rlai_angle": "What this means for them + subtle RLAI connection",
      "source_url": ""
    }}
  ],
  "closing_thought": "Expert perspective from RLAI (1 paragraph)",
  "cta": "CTA for this email",
  "ps_line": "P.S.",
  "body_html": "<complete HTML email>"
}}

Return ONLY valid JSON."""

        output = self._call_llm(prompt, max_tokens=3000)
        try:
            return self._parse_json(output)
        except:
            return {"subject": f"AI in {domain} this week", "error": "partial", "raw": output[:300]}

    def create_cold_outreach(self, lead: Dict, opportunity: str = None) -> Dict:
        domain = lead.get("domain", "technology")
        products = PRODUCT_MAPPING.get(domain, [])

        prompt = f"""Write a cold outreach email for RightLeftAI.

PROSPECT:
- Name: {lead.get('name', 'Decision Maker')}
- Company: {lead.get('company', 'Company')}
- Domain: {domain}
- Designation: {lead.get('designation', 'CXO')}

OPPORTUNITY/TRIGGER: {opportunity or f"General outreach for {domain} AI solutions"}
RELEVANT PRODUCTS: {', '.join(products[:2])}

Cold email requirements (IMPORTANT):
- DO NOT pitch immediately — build curiosity first
- Reference something specific about their industry/company
- ONE clear value proposition (specific, not generic)
- Ultra-short CTA: "Worth a 15-min call?" or "Curious to share a quick finding?"
- Max 100 words in body
- Personalized subject (not "Partnership Opportunity" or "Quick question")

Return JSON:
{{
  "subject": "Specific, personalized subject",
  "body_text": "Short cold email (under 100 words)",
  "body_html": "<p>HTML version</p>",
  "follow_up_day3": "Day 3 follow-up email text",
  "follow_up_day7": "Day 7 last-touch email",
  "personalization_notes": "What to research about this prospect before sending"
}}

Return ONLY valid JSON."""

        output = self._call_llm(prompt, max_tokens=2000)
        try:
            return self._parse_json(output)
        except:
            return {"subject": "Quick question", "body_text": output, "error": "partial"}

    def create_product_launch_email(self, product_name: str, update_details: str) -> Dict:
        prompt = f"""Write a product update/launch email for RightLeftAI.

PRODUCT: {product_name}
UPDATE/LAUNCH DETAILS: {update_details}

Write to existing leads and customers. Tone: exciting but professional.

Return JSON:
{{
  "subject": "...",
  "body_html": "<full HTML email>",
  "key_benefit_bullets": ["Benefit 1", "Benefit 2"],
  "cta_text": "Book a Demo / See It Live",
  "cta_url": "https://rightleft.ai"
}}

Return ONLY valid JSON."""

        output = self._call_llm(prompt, max_tokens=2000)
        try:
            return self._parse_json(output)
        except:
            return {"subject": f"{product_name} Update", "error": "partial"}
