import asyncio
import json
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, List, Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import select, desc

from config.database import (init_db, AsyncSessionLocal, Lead, ContentPost,
                               EmailCampaign, LeadOpportunity, AgentRun)
from config.settings import settings
from workflows.daily_runner import DailyMarketingRunner
from agents.cmo_agent import CMOAgent
from agents.content_creator_agent import ContentCreatorAgent
from agents.email_agent import EmailCampaignAgent
from agents.lead_intelligence_agent import LeadIntelligenceAgent

# In-memory run state
active_runs: Dict[str, dict] = {}
ws_connections: List[WebSocket] = []
scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    _setup_scheduler()
    scheduler.start()
    yield
    scheduler.shutdown()

app = FastAPI(title="RightLeftAI Marketing Team API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def _setup_scheduler():
    h, m = settings.DAILY_LEADS_SCAN_TIME.split(":")
    scheduler.add_job(_scheduled_daily_run, "cron", hour=int(h), minute=int(m),
                      id="daily_marketing_run", replace_existing=True)

async def _scheduled_daily_run():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Lead).where(Lead.status == "active"))
        leads = [{"id": l.id, "name": l.name, "email": l.email, "company": l.company,
                  "domain": l.domain, "designation": l.designation}
                 for l in result.scalars().all()]
    await _run_daily(leads=leads)

# ── WebSocket ────────────────────────────────────────────────────────────────
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    ws_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_connections.remove(websocket)

async def broadcast(msg: dict):
    dead = []
    for ws in ws_connections:
        try:
            await ws.send_json(msg)
        except:
            dead.append(ws)
    for ws in dead:
        ws_connections.remove(ws)

# ── Daily Run ────────────────────────────────────────────────────────────────
class RunRequest(BaseModel):
    day_focus: Optional[str] = None
    posting_mode: Optional[str] = "manual"
    lead_ids: Optional[List[str]] = None

@app.post("/api/run/daily")
async def trigger_daily_run(req: RunRequest):
    run_id = str(uuid.uuid4())[:8]
    active_runs[run_id] = {"status": "running", "started_at": datetime.utcnow().isoformat(), "logs": []}

    async with AsyncSessionLocal() as db:
        query = select(Lead).where(Lead.status == "active")
        if req.lead_ids:
            query = query.where(Lead.id.in_(req.lead_ids))
        result = await db.execute(query)
        leads = [{"id": l.id, "name": l.name, "email": l.email, "company": l.company,
                  "domain": l.domain, "designation": l.designation}
                 for l in result.scalars().all()]

    asyncio.create_task(_run_daily(run_id=run_id, leads=leads,
                                   day_focus=req.day_focus, posting_mode=req.posting_mode))
    return {"run_id": run_id, "status": "started", "leads_count": len(leads)}

async def _run_daily(run_id: str = None, leads: list = None, day_focus: str = None, posting_mode: str = None):
    rid = run_id or "scheduled"
    if rid not in active_runs:
        active_runs[rid] = {"status": "running", "started_at": datetime.utcnow().isoformat(), "logs": []}

    def progress_cb(data: dict):
        active_runs[rid]["logs"].append(data)
        asyncio.create_task(broadcast({"run_id": rid, **data}))

    runner = DailyMarketingRunner()
    runner.set_progress_callback(progress_cb)

    try:
        result = await asyncio.to_thread(runner.run_daily, leads or [], day_focus, posting_mode)
        active_runs[rid].update({"status": "completed", "result": result, "completed_at": datetime.utcnow().isoformat()})

        # Persist to DB
        async with AsyncSessionLocal() as db:
            # Save content posts
            for item in result.get("content_created", []):
                post = ContentPost(
                    id=str(uuid.uuid4())[:8],
                    platform=item["platform"],
                    content_type=item["content"].get("content_type", ""),
                    title=item["content"].get("hook", item["content"].get("title", ""))[:200],
                    body=item["content"].get("post_text") or item["content"].get("caption") or item["content"].get("article_body", ""),
                    hashtags=item["content"].get("hashtags", []),
                    status=item["content"].get("post_result", {}).get("status", "draft"),
                    created_by="Arjun (Content)",
                )
                db.add(post)

            # Save opportunities
            for opp in result.get("opportunities_found", []):
                o = LeadOpportunity(
                    id=str(uuid.uuid4())[:8],
                    title=opp.get("title", ""),
                    source_url=opp.get("source_url", ""),
                    opportunity_type=opp.get("opportunity_type", ""),
                    domain=opp.get("domain", ""),
                    relevant_product=opp.get("relevant_product", ""),
                    summary=opp.get("summary", ""),
                    action_suggested=opp.get("action_suggested", ""),
                    priority=opp.get("priority", "Medium"),
                )
                db.add(o)

            # Log the run
            run_log = AgentRun(
                agent_name="DailyRunner",
                task=f"Daily run {rid}",
                output_summary=f"Content: {len(result.get('content_created',[]))}, Emails: {len(result.get('emails_queued',[]))}, Opps: {len(result.get('opportunities_found',[]))}",
                status="completed",
                items_created=len(result.get("content_created",[])) + len(result.get("emails_queued",[])),
            )
            db.add(run_log)
            await db.commit()

        await broadcast({"run_id": rid, "event": "completed", "result": {
            "content_count": len(result.get("content_created", [])),
            "emails_count": len(result.get("emails_queued", [])),
            "opportunities_count": len(result.get("opportunities_found", [])),
        }})
    except Exception as e:
        active_runs[rid]["status"] = "error"
        active_runs[rid]["error"] = str(e)
        await broadcast({"run_id": rid, "event": "error", "message": str(e)})

@app.get("/api/run/{run_id}")
async def get_run(run_id: str):
    if run_id not in active_runs:
        raise HTTPException(404, "Run not found")
    return active_runs[run_id]

# ── Leads CRUD ───────────────────────────────────────────────────────────────
class LeadCreate(BaseModel):
    name: str
    email: str
    company: str
    designation: str = ""
    domain: str = "technology"
    linkedin_url: str = ""
    phone: str = ""
    notes: str = ""
    tags: List[str] = []

@app.get("/api/leads")
async def get_leads():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Lead).order_by(desc(Lead.created_at)))
        leads = result.scalars().all()
        return {"leads": [{"id": l.id, "name": l.name, "email": l.email, "company": l.company,
                           "domain": l.domain, "designation": l.designation, "status": l.status,
                           "tags": l.tags, "notes": l.notes, "created_at": str(l.created_at)}
                          for l in leads]}

@app.post("/api/leads")
async def create_lead(lead: LeadCreate):
    async with AsyncSessionLocal() as db:
        new_lead = Lead(id=str(uuid.uuid4())[:8], **lead.model_dump())
        db.add(new_lead)
        await db.commit()
    return {"id": new_lead.id, "status": "created"}

@app.delete("/api/leads/{lead_id}")
async def delete_lead(lead_id: str):
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Lead).where(Lead.id == lead_id))
        lead = result.scalar_one_or_none()
        if not lead:
            raise HTTPException(404)
        await db.delete(lead)
        await db.commit()
    return {"status": "deleted"}

# ── Content Posts ────────────────────────────────────────────────────────────
@app.get("/api/posts")
async def get_posts():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(ContentPost).order_by(desc(ContentPost.created_at)))
        posts = result.scalars().all()
        return {"posts": [{"id": p.id, "platform": p.platform, "content_type": p.content_type,
                           "title": p.title, "body": p.body[:300], "hashtags": p.hashtags,
                           "status": p.status, "created_at": str(p.created_at)}
                          for p in posts]}

@app.post("/api/posts/{post_id}/approve")
async def approve_post(post_id: str):
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(ContentPost).where(ContentPost.id == post_id))
        post = result.scalar_one_or_none()
        if not post:
            raise HTTPException(404)
        post.status = "approved"
        await db.commit()
    return {"status": "approved"}

@app.post("/api/posts/{post_id}/publish")
async def publish_post(post_id: str):
    from tools.social_poster import LinkedInPoster, FacebookPoster, InstagramPoster
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(ContentPost).where(ContentPost.id == post_id))
        post = result.scalar_one_or_none()
        if not post:
            raise HTTPException(404)

        if post.platform == "linkedin":
            poster_result = LinkedInPoster().post(post.body)
        elif post.platform == "facebook":
            poster_result = FacebookPoster().post(post.body)
        else:
            poster_result = InstagramPoster().post(post.body)

        post.status = poster_result.get("status", "posted")
        post.platform_post_id = poster_result.get("post_id", "")
        post.posted_at = datetime.utcnow()
        await db.commit()
    return poster_result

# ── Opportunities ────────────────────────────────────────────────────────────
@app.get("/api/opportunities")
async def get_opportunities():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(LeadOpportunity).order_by(desc(LeadOpportunity.discovered_at)))
        opps = result.scalars().all()
        return {"opportunities": [{"id": o.id, "title": o.title, "domain": o.domain,
                                   "relevant_product": o.relevant_product, "priority": o.priority,
                                   "summary": o.summary, "action_suggested": o.action_suggested,
                                   "status": o.status, "source_url": o.source_url,
                                   "discovered_at": str(o.discovered_at)}
                                  for o in opps]}

@app.patch("/api/opportunities/{opp_id}/status")
async def update_opportunity_status(opp_id: str, body: dict = Body(...)):
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(LeadOpportunity).where(LeadOpportunity.id == opp_id))
        opp = result.scalar_one_or_none()
        if not opp:
            raise HTTPException(404)
        opp.status = body.get("status", opp.status)
        await db.commit()
    return {"status": "updated"}

# ── On-demand content generation ─────────────────────────────────────────────
class ContentRequest(BaseModel):
    platform: str   # linkedin | instagram | facebook
    content_type: str
    product: Optional[str] = None
    topic: Optional[str] = None
    industry: Optional[str] = None

@app.post("/api/generate/content")
async def generate_content(req: ContentRequest):
    creator = ContentCreatorAgent()
    if req.platform == "linkedin":
        result = creator.create_linkedin_post(req.content_type, req.product, req.topic, req.industry)
    elif req.platform == "instagram":
        result = creator.create_instagram_content(req.content_type, req.product, req.topic)
    else:
        result = creator.create_facebook_post(req.content_type, req.product, req.topic)
    return result

@app.post("/api/generate/email")
async def generate_email(lead_id: str, email_type: str = "nurture"):
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Lead).where(Lead.id == lead_id))
        lead = result.scalar_one_or_none()
        if not lead:
            raise HTTPException(404)

    lead_dict = {"id": lead.id, "name": lead.name, "email": lead.email,
                 "company": lead.company, "domain": lead.domain, "designation": lead.designation}
    agent = EmailCampaignAgent()
    if email_type == "cold":
        return agent.create_cold_outreach(lead_dict)
    return agent.create_nurture_email(lead_dict)

@app.get("/api/generate/weekly-calendar")
async def generate_weekly_calendar(focus: str = None):
    cmo = CMOAgent()
    return cmo.create_weekly_content_calendar(focus)

@app.get("/api/generate/lead-suggestions")
async def generate_lead_suggestions():
    intel = LeadIntelligenceAgent()
    return {"suggestions": intel.generate_lead_suggestions(10)}

@app.get("/api/stats")
async def get_stats():
    async with AsyncSessionLocal() as db:
        leads_r = await db.execute(select(Lead))
        posts_r = await db.execute(select(ContentPost))
        opps_r = await db.execute(select(LeadOpportunity))
        runs_r = await db.execute(select(AgentRun))
        leads = leads_r.scalars().all()
        posts = posts_r.scalars().all()
        opps = opps_r.scalars().all()
        runs = runs_r.scalars().all()

    return {
        "total_leads": len(leads),
        "active_leads": sum(1 for l in leads if l.status == "active"),
        "total_posts": len(posts),
        "posts_by_status": {s: sum(1 for p in posts if p.status == s) for s in ["draft", "approved", "posted"]},
        "total_opportunities": len(opps),
        "new_opportunities": sum(1 for o in opps if o.status == "new"),
        "total_runs": len(runs),
        "next_scheduled_run": settings.DAILY_LEADS_SCAN_TIME + " UTC",
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
