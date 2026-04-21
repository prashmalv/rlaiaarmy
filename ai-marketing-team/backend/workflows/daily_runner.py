"""
Daily automation workflow — runs on schedule or on-demand.
Each run: generate content → scan leads → create emails → post or queue.
"""
import uuid
from datetime import datetime
from typing import Dict, List, Callable, Optional

from agents.cmo_agent import CMOAgent
from agents.content_creator_agent import ContentCreatorAgent
from agents.email_agent import EmailCampaignAgent
from agents.lead_intelligence_agent import LeadIntelligenceAgent
from tools.social_poster import LinkedInPoster, FacebookPoster, InstagramPoster
from tools.email_sender import send_email
from config.settings import settings

class DailyMarketingRunner:
    def __init__(self):
        self.cmo = CMOAgent()
        self.content = ContentCreatorAgent()
        self.emailer = EmailCampaignAgent()
        self.intel = LeadIntelligenceAgent()
        self.linkedin = LinkedInPoster()
        self.facebook = FacebookPoster()
        self.instagram = InstagramPoster()

        self.logs: List[Dict] = []
        self.progress_callback: Optional[Callable] = None

    def set_progress_callback(self, cb: Callable):
        self.progress_callback = cb

    def _log(self, agent: str, action: str, result: str, status: str = "success"):
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent": agent,
            "action": action,
            "result": result[:300],
            "status": status,
        }
        self.logs.append(entry)
        if self.progress_callback:
            self.progress_callback(entry)

    def _emit(self, event: str, data: dict):
        if self.progress_callback:
            self.progress_callback({"event": event, **data})

    def run_daily(self, leads: List[Dict], day_focus: str = None,
                  posting_mode: str = None) -> Dict:
        """Main daily run — call this every morning."""
        mode = posting_mode or settings.POSTING_MODE
        results = {
            "run_id": str(uuid.uuid4())[:8],
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "mode": mode,
            "content_created": [],
            "emails_queued": [],
            "opportunities_found": [],
            "posts_status": {},
            "agent_logs": [],
        }

        # ── 1. Lead Intelligence Scan ──────────────────────────────────────
        self._emit("step", {"name": "Lead Intelligence Scan", "status": "started"})
        self._emit("agent_working", {"agent": "Vikram (Intel)", "task": "Scanning news for opportunities..."})

        opportunities = self.intel.scan_for_opportunities()
        gov_tenders = self.intel.scan_government_tenders()
        lead_suggestions = self.intel.generate_lead_suggestions(5)

        self._log("Vikram (Intel)", "scan_opportunities",
                  f"Found {len(opportunities)} opportunities, {len(gov_tenders)} tenders, {len(lead_suggestions)} lead suggestions")
        results["opportunities_found"] = opportunities[:5]
        results["gov_tenders"] = gov_tenders[:3]
        results["lead_suggestions"] = lead_suggestions[:5]
        self._emit("step", {"name": "Lead Intelligence Scan", "status": "complete",
                            "summary": f"{len(opportunities)} opportunities, {len(gov_tenders)} tenders"})

        # ── 2. LinkedIn Content ────────────────────────────────────────────
        self._emit("step", {"name": "LinkedIn Content Creation", "status": "started"})
        self._emit("agent_working", {"agent": "Arjun (Content)", "task": "Creating LinkedIn post..."})

        # Alternate content types across the week
        weekday = datetime.utcnow().weekday()
        linkedin_types = ["thought_leadership", "product_spotlight", "case_study",
                          "news_commentary", "tip_or_insight"]
        products = ["SatyaDocAI", "LOVAIC", "SalesBuddy", "AI Avatar L&D", None]
        content_type = linkedin_types[weekday % len(linkedin_types)]
        product = products[weekday % len(products)]

        linkedin_post = self.content.create_linkedin_post(
            content_type=content_type,
            product=product,
            topic=day_focus,
        )
        self._log("Arjun (Content)", "create_linkedin_post",
                  f"Type: {content_type}, Product: {product}, Hook: {linkedin_post.get('hook','')[:80]}")

        # Post or queue
        if mode == "auto":
            post_result = self.linkedin.post(linkedin_post.get("post_text", ""))
            linkedin_post["post_result"] = post_result
            self._log("Arjun (Content)", "post_to_linkedin",
                      f"Status: {post_result.get('status')}")
        else:
            linkedin_post["post_result"] = {"status": "queued_for_approval"}

        results["content_created"].append({"platform": "linkedin", "content": linkedin_post})
        self._emit("step", {"name": "LinkedIn Content Creation", "status": "complete"})

        # ── 3. Instagram Content ───────────────────────────────────────────
        self._emit("step", {"name": "Instagram Content Creation", "status": "started"})
        self._emit("agent_working", {"agent": "Arjun (Content)", "task": "Creating Instagram content..."})

        ig_types = ["carousel", "quote_card", "infographic", "reel_script"]
        ig_content = self.content.create_instagram_content(
            content_type=ig_types[weekday % len(ig_types)],
            product=product,
            topic=day_focus,
        )
        if mode == "auto":
            ig_result = self.instagram.post(ig_content.get("caption", ""))
            ig_content["post_result"] = ig_result
        else:
            ig_content["post_result"] = {"status": "queued_for_approval"}

        results["content_created"].append({"platform": "instagram", "content": ig_content})
        self._emit("step", {"name": "Instagram Content Creation", "status": "complete"})

        # ── 4. Facebook Content ────────────────────────────────────────────
        self._emit("step", {"name": "Facebook Content Creation", "status": "started"})
        self._emit("agent_working", {"agent": "Arjun (Content)", "task": "Creating Facebook post..."})

        fb_content = self.content.create_facebook_post(
            content_type=content_type, product=product, topic=day_focus
        )
        if mode == "auto":
            fb_result = self.facebook.post(fb_content.get("post_text", ""))
            fb_content["post_result"] = fb_result
        else:
            fb_content["post_result"] = {"status": "queued_for_approval"}

        results["content_created"].append({"platform": "facebook", "content": fb_content})
        self._emit("step", {"name": "Facebook Content Creation", "status": "complete"})

        # ── 5. Lead Nurturing Emails ───────────────────────────────────────
        if leads:
            self._emit("step", {"name": "Lead Nurturing Emails", "status": "started"})
            self._emit("agent_working", {"agent": "Neha (Email)", "task": f"Writing nurture emails for {len(leads)} leads..."})

            # Group leads by domain for personalized news digests
            domain_groups: Dict[str, List] = {}
            for lead in leads:
                d = lead.get("domain", "technology")
                domain_groups.setdefault(d, []).append(lead)

            for domain, domain_leads in list(domain_groups.items())[:3]:
                # Get relevant news for this domain
                domain_news = [{"title": o.get("title",""), "summary": o.get("summary","")}
                               for o in opportunities if o.get("domain") == domain]

                if domain_news:
                    # Industry news digest for this domain
                    digest = self.emailer.create_industry_news_digest(domain, domain_news)
                    self._log("Neha (Email)", f"create_digest:{domain}",
                              f"Subject: {digest.get('subject','')[:60]}")
                    for lead in domain_leads[:5]:
                        email_item = {
                            "lead": lead,
                            "type": "news_digest",
                            "domain": domain,
                            "subject": digest.get("subject"),
                            "body_html": digest.get("body_html", ""),
                            "status": "queued" if mode == "manual" else "sent",
                        }
                        if mode == "auto" and lead.get("email"):
                            send_result = send_email(
                                lead["email"], lead.get("name",""), digest.get("subject",""),
                                digest.get("body_html","")
                            )
                            email_item["send_result"] = send_result
                        results["emails_queued"].append(email_item)
                else:
                    # Individual nurture email
                    for lead in domain_leads[:3]:
                        nurture = self.emailer.create_nurture_email(lead)
                        self._log("Neha (Email)", f"create_nurture:{lead.get('name','')}",
                                  f"Subject: {nurture.get('subject','')[:60]}")
                        email_item = {
                            "lead": lead,
                            "type": "nurture",
                            "subject": nurture.get("subject"),
                            "body_html": nurture.get("body_html", ""),
                            "status": "queued" if mode == "manual" else "sent",
                        }
                        if mode == "auto" and lead.get("email"):
                            send_result = send_email(
                                lead["email"], lead.get("name",""), nurture.get("subject",""),
                                nurture.get("body_html","")
                            )
                            email_item["send_result"] = send_result
                        results["emails_queued"].append(email_item)

            self._emit("step", {"name": "Lead Nurturing Emails", "status": "complete",
                                "summary": f"{len(results['emails_queued'])} emails {'sent' if mode=='auto' else 'queued'}"})

        # ── 6. Thursday: Thought Leadership Article ────────────────────────
        if weekday == 3:  # Thursday
            self._emit("step", {"name": "Thought Leadership Article", "status": "started"})
            self._emit("agent_working", {"agent": "Arjun (Content)", "task": "Writing weekly thought leadership article..."})

            strategy = self.cmo.create_weekly_content_calendar(day_focus)
            tl_topic = strategy.get("weekly_thought_leadership_topic", "AI's role in India's next growth decade")

            article = self.content.create_thought_leadership_article(tl_topic)
            self._log("Arjun (Content)", "create_thought_leadership",
                      f"Title: {article.get('title','')[:80]}")
            results["thought_leadership_article"] = article
            self._emit("step", {"name": "Thought Leadership Article", "status": "complete"})

        # ── 7. Monday: Competitor Analysis ────────────────────────────────
        if weekday == 0:  # Monday
            self._emit("step", {"name": "Competitor Intelligence", "status": "started"})
            self._emit("agent_working", {"agent": "Vikram (Intel)", "task": "Analysing competitor activity..."})
            competitor_intel = self.intel.analyse_competitor_activity()
            self._log("Vikram (Intel)", "competitor_analysis",
                      f"Found {len(competitor_intel.get('competitive_gaps',[]))} gaps")
            results["competitor_intel"] = competitor_intel
            self._emit("step", {"name": "Competitor Intelligence", "status": "complete"})

        results["agent_logs"] = self.logs
        results["total_actions"] = len(self.logs)

        self._emit("completed", {
            "content_count": len(results["content_created"]),
            "emails_count": len(results["emails_queued"]),
            "opportunities_count": len(results["opportunities_found"]),
        })

        return results
