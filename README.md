# RLAI Army — AI Agents Platform

Autonomous AI agent teams built for RightLeftAI (RLAI).

## Projects

### 1. `ai-dev-team/` — AI Software Development Team
An autonomous team of AI agents that takes requirements and delivers production-ready code.

**Agents:** BA (Alex) · Architect (Morgan) · AI Engineers × 3 · Full Stack Devs × 3 · Security (Sam) · Performance (Perry) · PM/CTO (Jordan)

**Flow:** Requirements → Backlog → Architecture → Poker Planning → Sprint Execution → Security Test → Performance Test → RTM → Go/No-Go → Email Approval

**Stack:** FastAPI · React · Anthropic Claude · SQLite · Locust · OWASP

### 2. `ai-marketing-team/` — AI Marketing Team for RightLeftAI
Autonomous daily marketing execution for brand building, lead nurturing, and opportunity discovery.

**Agents:** CMO (Priya) · Content (Arjun) · Email (Neha) · Intelligence (Vikram)

**Capabilities:** LinkedIn/Instagram/Facebook posts · Personalized lead nurturing emails · Government tender scanning · Competitor intelligence · Daily lead suggestions · Weekly content calendar

**Stack:** FastAPI · React · Anthropic Claude · APScheduler · NewsAPI · Social Media APIs

## Setup

```bash
# AI Dev Team
cd ai-dev-team/backend
cp .env.example .env   # Add ANTHROPIC_API_KEY
cd ../..
./ai-dev-team/start.sh

# AI Marketing Team
cd ai-marketing-team/backend
cp .env.example .env   # Add ANTHROPIC_API_KEY
cd ../..
./ai-marketing-team/start.sh
```

## Products Being Marketed
- **LOVAIC** — Computer vision at pixel level
- **SatyaDocAI** — Document forgery detection
- **SalesBuddy / VoiceBuddy / EvalBuddy** — AI Voice Agent Suite
- **AI Avatar L&D** — Training & marketing video generation

## Website
[rightleft.ai](https://rightleft.ai)
