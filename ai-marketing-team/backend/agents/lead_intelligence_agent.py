from agents.base_agent import BaseMarketingAgent
from data.rlai_brand import PRODUCT_MAPPING
import json
import httpx
from typing import Dict, List
from config.settings import settings

class LeadIntelligenceAgent(BaseMarketingAgent):
    def __init__(self):
        super().__init__(
            name="Vikram (Intel)",
            role="Lead Intelligence & Market Research Specialist",
            goal="Find RightLeftAI's next customers before they even know they need us. Monitor news, tenders, funding, and signals that indicate AI buying intent.",
            backstory="Vikram is a former management consultant and market research expert. Expert at reading between the lines of news to find sales opportunities. Knows India's enterprise and government procurement landscape deeply."
        )

    def _fetch_news(self, query: str, domains: str = None) -> List[Dict]:
        """Fetch news using NewsAPI."""
        if not settings.NEWS_API_KEY:
            return self._get_mock_news(query)

        try:
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": query,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 10,
                "apiKey": settings.NEWS_API_KEY,
            }
            if domains:
                params["domains"] = domains

            with httpx.Client(timeout=10) as client:
                response = client.get(url, params=params)
                data = response.json()
                return data.get("articles", [])
        except Exception as e:
            return self._get_mock_news(query)

    def _get_mock_news(self, query: str) -> List[Dict]:
        """Mock news for when API key is not set."""
        return [
            {"title": f"Government announces ₹500 crore AI initiative for {query}",
             "description": "Ministry pushes AI adoption across departments with major budget allocation",
             "url": "https://example.com/news1", "publishedAt": "2026-04-21"},
            {"title": f"Major bank deploys AI for fraud detection — {query}",
             "description": "India's top PSU bank implements computer vision for KYC document verification",
             "url": "https://example.com/news2", "publishedAt": "2026-04-21"},
            {"title": f"Insurance sector to invest ₹200 crore in AI this year",
             "description": "IRDAI pushes insurers to adopt AI for claims processing and fraud prevention",
             "url": "https://example.com/news3", "publishedAt": "2026-04-21"},
        ]

    def scan_for_opportunities(self, domains: List[str] = None) -> List[Dict]:
        """Scan news for companies/organisations likely needing RLAI solutions."""
        target_domains = domains or ["banking", "healthcare", "government", "insurance", "manufacturing"]
        all_opportunities = []

        search_queries = [
            "India AI tender government procurement 2026",
            "India bank fraud detection AI investment",
            "document verification KYC AI India",
            "computer vision manufacturing quality India",
            "India healthcare AI hospital deployment",
            "insurance fraud AI India",
            "enterprise AI solution India budget 2026",
        ]

        for query in search_queries[:3]:  # Limit API calls
            articles = self._fetch_news(query)
            for article in articles[:3]:
                opp = self._analyse_article_for_opportunity(article, target_domains)
                if opp and opp.get("is_opportunity"):
                    all_opportunities.append(opp)

        return all_opportunities[:10]

    def _analyse_article_for_opportunity(self, article: Dict, target_domains: List[str]) -> Dict:
        title = article.get("title", "")
        description = article.get("description", "")

        prompt = f"""Analyse this news article for RightLeftAI sales opportunities.

NEWS: {title}
DETAILS: {description}
SOURCE: {article.get("url", "")}

RLAI Products to match:
- LOVAIC: Computer vision, image/video analytics, fraud detection via visuals
- SatyaDocAI: Document forgery detection, KYC, certificates, contracts
- SalesBuddy/VoiceBuddy: Voice AI, customer service automation
- AI Avatar L&D: Training, HR, marketing video content

Return JSON:
{{
  "is_opportunity": true/false,
  "title": "Opportunity title",
  "summary": "What the news says in 2 sentences",
  "opportunity_type": "tender | investment | problem_signal | hiring_signal | regulatory_push",
  "relevant_product": "LOVAIC | SatyaDocAI | SalesBuddy | VoiceBuddy | AI Avatar | Multiple",
  "target_company_or_org": "Specific company/org name if mentioned",
  "domain": "banking | healthcare | government | insurance | manufacturing | retail | hr | education",
  "priority": "High | Medium | Low",
  "action_suggested": "Specific action RLAI should take (e.g., 'Reach out to SBI's CTO with SatyaDocAI demo offer')",
  "estimated_deal_size": "₹XX lakh | Unknown",
  "source_url": "{article.get('url', '')}"
}}

If not an opportunity, return {{"is_opportunity": false}}
Return ONLY valid JSON."""

        output = self._call_llm(prompt, max_tokens=800)
        try:
            result = self._parse_json(output)
            result["source_url"] = article.get("url", "")
            result["published_at"] = article.get("publishedAt", "")
            return result
        except:
            return {"is_opportunity": False}

    def scan_government_tenders(self) -> List[Dict]:
        """Scan for government AI tenders (simulated — integrate GeM API when available)."""
        prompt = """Generate realistic government AI tender opportunities that RightLeftAI could bid for.
These should be based on REAL types of tenders that Indian government departments issue.

Return JSON array of 5 realistic opportunities:
[
  {{
    "tender_title": "Tender title",
    "issuing_department": "Ministry of X / State Govt / PSU",
    "tender_type": "Expression of Interest | RFP | GeM | Direct Purchase",
    "estimated_value": "₹XX crore",
    "relevant_product": "LOVAIC | SatyaDocAI | VoiceBuddy | AI Avatar",
    "deadline": "2026-05-15",
    "summary": "What they need",
    "action": "What RLAI should do",
    "priority": "High | Medium | Low",
    "source": "gem.gov.in | cppp.nic.in | news"
  }}
]

Make these specific and realistic for 2026 India. Return ONLY valid JSON array."""

        output = self._call_llm(prompt, max_tokens=2000)
        try:
            return self._parse_json(output)
        except:
            return []

    def generate_lead_suggestions(self, count: int = 10) -> List[Dict]:
        """Suggest companies RLAI should reach out to based on market signals."""
        prompt = f"""Suggest {count} specific companies/organisations in India that RightLeftAI should target for outreach NOW (April 2026).

Base suggestions on:
- Recent AI investment announcements
- Companies known to have digitisation/fraud/training problems
- Government departments with AI budget
- Companies hiring AI/ML roles (buying signal)

For each, suggest the right RLAI product and the right person to contact.

Return JSON array:
[
  {{
    "company": "Company name",
    "industry": "banking | insurance | healthcare | manufacturing | govt",
    "why_now": "Why reach out now (specific trigger)",
    "relevant_product": "LOVAIC | SatyaDocAI | SalesBuddy | VoiceBuddy | AI Avatar",
    "suggested_contact": "CISO | CTO | Head of Operations | HR Head",
    "opening_angle": "First line of outreach email",
    "priority": "High | Medium",
    "estimated_size": "Enterprise | Mid-market | SME"
  }}
]

Be specific — name real Indian companies. Return ONLY valid JSON array."""

        output = self._call_llm(prompt, max_tokens=3000)
        try:
            return self._parse_json(output)
        except:
            return []

    def analyse_competitor_activity(self) -> Dict:
        """Monitor what competitors are doing and find gaps."""
        prompt = """Analyse the competitive landscape for RightLeftAI's products in India (April 2026).

Competitors to consider:
- Computer Vision: Staqu, Mad Street Den, Niki.ai
- Document Verification: IDfy, Signzy, AuthBridge
- Voice AI: Sarvam AI, Voicebot.ai, Kore.ai
- L&D/Avatars: Synthesia, HeyGen, Murf (global), Rephrase.ai (India)

Return JSON:
{{
  "competitive_gaps": [
    {{
      "gap": "What competitors are NOT doing that RLAI should own",
      "rlai_product": "Which RLAI product fills this gap",
      "content_angle": "How to communicate this differentiation"
    }}
  ],
  "competitor_messaging_weaknesses": ["What competitors say that RLAI can counter"],
  "market_opportunities": ["Underserved segments or use cases"],
  "recommended_differentiators": ["Key messages RLAI should own"],
  "content_ideas_from_gaps": ["Post/article ideas based on competitive gaps"]
}}

Return ONLY valid JSON."""

        output = self._call_llm(prompt, max_tokens=2000)
        try:
            return self._parse_json(output)
        except:
            return {"error": "parse failed", "raw": output[:300]}
