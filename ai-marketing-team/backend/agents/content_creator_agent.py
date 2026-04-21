from agents.base_agent import BaseMarketingAgent
from data.rlai_brand import PAIN_POINTS, PRODUCT_MAPPING
import json
from typing import Dict, List, Optional

class ContentCreatorAgent(BaseMarketingAgent):
    def __init__(self):
        super().__init__(
            name="Arjun (Content)",
            role="Senior Content Strategist & Copywriter",
            goal="Create scroll-stopping, insight-rich content that builds RightLeftAI's authority and drives meaningful engagement",
            backstory="Arjun has written for India's top tech brands. Expert at translating complex AI concepts into business-friendly stories. Knows what Indian CXOs and decision-makers read and share."
        )

    def create_linkedin_post(self, content_type: str, product: str = None,
                              topic: str = None, industry: str = None) -> Dict:
        pain_points = PAIN_POINTS.get(product, []) if product else []
        prompt = f"""Write a high-performing LinkedIn post for RightLeftAI.

CONTENT TYPE: {content_type}
PRODUCT FOCUS: {product or "General RightLeftAI brand"}
TOPIC/ANGLE: {topic or "Choose the most relevant current angle"}
TARGET INDUSTRY: {industry or "General B2B decision makers in India"}
RELEVANT PAIN POINTS: {json.dumps(pain_points)}

LinkedIn post requirements:
- Hook first line (must make someone stop scrolling)
- 150-300 words
- Use line breaks and bullet points for readability
- End with a thought-provoking question OR clear CTA
- Include 5-8 relevant hashtags
- NO generic phrases like "In today's fast-paced world"

Return JSON:
{{
  "post_text": "Full LinkedIn post text",
  "hook": "First line extracted",
  "hashtags": ["#AI", "#RightLeftAI", "#SatyaDocAI"],
  "image_description": "What image/graphic would work best with this post",
  "image_prompt": "DALL-E/Midjourney prompt to generate this image",
  "estimated_reach_type": "high_engagement | educational | viral_potential",
  "best_posting_time": "Tuesday 8-9am IST",
  "content_type": "{content_type}"
}}

Return ONLY valid JSON."""

        output = self._call_llm(prompt, max_tokens=2000)
        try:
            return self._parse_json(output)
        except:
            return {"post_text": output, "hashtags": ["#RightLeftAI", "#AI"], "error": "partial"}

    def create_instagram_content(self, content_type: str, product: str = None, topic: str = None) -> Dict:
        prompt = f"""Create Instagram content for RightLeftAI.

CONTENT TYPE: {content_type} (carousel | reel_script | quote_card | infographic)
PRODUCT FOCUS: {product or "RightLeftAI brand"}
TOPIC: {topic or "AI innovation in Indian business"}

Return JSON:
{{
  "content_type": "{content_type}",
  "caption": "Instagram caption (shorter, punchy, 100-150 words)",
  "carousel_slides": [
    {{"slide_number": 1, "headline": "...", "body": "2-3 lines", "visual_description": "..."}}
  ],
  "reel_script": "If reel, 30-60 second script with scene descriptions",
  "hashtags": ["#AI", "#RightLeftAI", "#ArtificialIntelligence", "#IndiaAI", "#TechIndia"],
  "story_ideas": ["Related story idea 1", "Related story idea 2"],
  "image_prompt": "Visual generation prompt"
}}

Return ONLY valid JSON."""

        output = self._call_llm(prompt, max_tokens=2000)
        try:
            return self._parse_json(output)
        except:
            return {"caption": output, "hashtags": ["#RightLeftAI"], "error": "partial"}

    def create_thought_leadership_article(self, topic: str, target_audience: str = "CXO") -> Dict:
        prompt = f"""Write a thought leadership LinkedIn article for RightLeftAI.

TOPIC: {topic}
TARGET AUDIENCE: {target_audience}
LENGTH: 600-800 words

Requirements:
- Author voice: Knowledgeable, not salesy. Share insights, not pitches.
- Include: 1 specific India data point, 1 global trend, 1 RLAI product mention (natural, not forced)
- Structure: Hook → Problem → Insight → Solution direction → Call to reflect

Return JSON:
{{
  "title": "Article title",
  "subtitle": "One line subtitle",
  "article_body": "Full article text (use markdown for formatting)",
  "key_takeaways": ["Takeaway 1", "Takeaway 2", "Takeaway 3"],
  "products_mentioned": ["LOVAIC", "SatyaDocAI"],
  "suggested_tags": ["Artificial Intelligence", "Digital Transformation"],
  "estimated_read_time": "4 min",
  "image_prompt": "Header image prompt"
}}

Return ONLY valid JSON."""

        output = self._call_llm(prompt, max_tokens=4096)
        try:
            return self._parse_json(output)
        except:
            return {"title": topic, "article_body": output, "error": "partial"}

    def create_facebook_post(self, content_type: str, product: str = None, topic: str = None) -> Dict:
        prompt = f"""Write a Facebook post for RightLeftAI's company page.

CONTENT TYPE: {content_type}
PRODUCT: {product or "General brand"}
TOPIC: {topic or "AI trends and solutions"}

Facebook audience: Mix of tech enthusiasts, business owners, job seekers, and partners.

Return JSON:
{{
  "post_text": "Facebook post (200-400 words, more conversational than LinkedIn)",
  "hashtags": ["#RightLeftAI", "#AI", "#ArtificialIntelligence"],
  "image_description": "Visual to accompany post",
  "image_prompt": "Image generation prompt",
  "link_to_share": "https://rightleft.ai or specific product page",
  "call_to_action": "Comment below | Share | Visit our website"
}}

Return ONLY valid JSON."""

        output = self._call_llm(prompt, max_tokens=1500)
        try:
            return self._parse_json(output)
        except:
            return {"post_text": output, "hashtags": ["#RightLeftAI"], "error": "partial"}

    def create_product_comparison_post(self, our_product: str, generic_approach: str) -> Dict:
        prompt = f"""Create a comparison content piece for RightLeftAI.

OUR PRODUCT: {our_product}
VS GENERIC APPROACH: {generic_approach}

Create a LinkedIn post/infographic idea that shows:
"Why {our_product} beats {generic_approach}" without being arrogant.
Use data, real business outcomes, and specifics.

Return JSON:
{{
  "linkedin_post": "Post text",
  "comparison_table": [
    {{"aspect": "Accuracy", "generic": "70-75%", "rlai": "95%+ at pixel level"}}
  ],
  "key_differentiator": "The one thing we do that nobody else does",
  "hashtags": [],
  "image_prompt": "Comparison infographic visual"
}}

Return ONLY valid JSON."""

        output = self._call_llm(prompt, max_tokens=2000)
        try:
            return self._parse_json(output)
        except:
            return {"error": "partial", "raw": output[:300]}
