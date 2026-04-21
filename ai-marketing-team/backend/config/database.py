from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, Boolean, Float
from datetime import datetime
from config.settings import settings

engine = create_async_engine(settings.DB_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

class Lead(Base):
    __tablename__ = "leads"
    id = Column(String, primary_key=True)
    name = Column(String)
    email = Column(String)
    company = Column(String)
    designation = Column(String)
    domain = Column(String)          # healthcare, banking, govt, manufacturing, etc.
    linkedin_url = Column(String)
    phone = Column(String)
    source = Column(String)          # manual, discovered, referral
    status = Column(String, default="active")   # active, converted, cold
    notes = Column(Text)
    tags = Column(JSON, default=list)
    last_contacted = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class ContentPost(Base):
    __tablename__ = "content_posts"
    id = Column(String, primary_key=True)
    platform = Column(String)        # linkedin, instagram, facebook, email
    content_type = Column(String)    # thought_leadership, product, news, case_study
    title = Column(String)
    body = Column(Text)
    hashtags = Column(JSON, default=list)
    image_prompt = Column(Text)      # For AI image generation
    status = Column(String, default="draft")  # draft, approved, posted, failed
    scheduled_at = Column(DateTime)
    posted_at = Column(DateTime)
    platform_post_id = Column(String)
    engagement = Column(JSON, default=dict)  # likes, comments, shares
    created_by = Column(String)      # which agent created it
    created_at = Column(DateTime, default=datetime.utcnow)

class EmailCampaign(Base):
    __tablename__ = "email_campaigns"
    id = Column(String, primary_key=True)
    subject = Column(String)
    body_html = Column(Text)
    campaign_type = Column(String)   # nurture, news_digest, cold_outreach, product_update
    target_domain = Column(String)   # which industry this is for
    lead_ids = Column(JSON, default=list)
    status = Column(String, default="draft")
    sent_at = Column(DateTime)
    open_count = Column(Integer, default=0)
    click_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class LeadOpportunity(Base):
    __tablename__ = "lead_opportunities"
    id = Column(String, primary_key=True)
    title = Column(String)
    source_url = Column(String)
    source_name = Column(String)
    opportunity_type = Column(String)  # tender, news, job_posting, funding
    domain = Column(String)
    relevant_product = Column(String)  # LOVAIC, SatyaDocAI, VoiceBuddy, etc.
    summary = Column(Text)
    action_suggested = Column(Text)
    priority = Column(String)          # High, Medium, Low
    status = Column(String, default="new")  # new, reviewed, actioned, dismissed
    discovered_at = Column(DateTime, default=datetime.utcnow)

class AgentRun(Base):
    __tablename__ = "agent_runs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_name = Column(String)
    task = Column(String)
    output_summary = Column(Text)
    status = Column(String)
    items_created = Column(Integer, default=0)
    ran_at = Column(DateTime, default=datetime.utcnow)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
