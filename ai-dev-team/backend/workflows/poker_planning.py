from agents.base_agent import BaseAgent
from anthropic import Anthropic
from config.settings import settings
import json
from typing import List, Dict

FIBONACCI = [1, 2, 3, 5, 8, 13, 21]

client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

POKER_AGENTS = [
    {"name": "Alex (BA)", "perspective": "business complexity and requirements clarity"},
    {"name": "Morgan (Architect)", "perspective": "technical complexity and architecture effort"},
    {"name": "Dev-E1 (AI Engineer)", "perspective": "backend implementation effort"},
    {"name": "Dev-F1 (Full Stack Dev)", "perspective": "frontend + integration effort"},
    {"name": "Sam (Security)", "perspective": "security testing effort"},
    {"name": "Perry (Performance)", "perspective": "performance testing effort"},
]

def estimate_story(story: Dict) -> Dict:
    """Run poker planning for a single user story - all agents vote."""
    votes = []

    for agent in POKER_AGENTS:
        prompt = f"""You are {agent['name']} participating in agile poker planning.
Estimate this user story from your perspective as {agent['perspective']}.

USER STORY:
Title: {story.get('title')}
As a {story.get('as_a')}, I want {story.get('i_want')}, so that {story.get('so_that')}
Acceptance Criteria: {json.dumps(story.get('acceptance_criteria', []))}
Technical Notes: {story.get('technical_notes', '')}

Choose ONE number from Fibonacci sequence: {FIBONACCI}
Consider only the effort from YOUR perspective.

Respond with ONLY this JSON:
{{"vote": 5, "reasoning": "One sentence why"}}"""

        response = client.messages.create(
            model=settings.MODEL_NAME,
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = response.content[0].text.strip()
        try:
            if "```" in raw:
                raw = raw.split("```")[1].split("```")[0].strip()
                if raw.startswith("json"):
                    raw = raw[4:].strip()
            vote_data = json.loads(raw)
            vote_data["agent"] = agent["name"]
            votes.append(vote_data)
        except:
            votes.append({"agent": agent["name"], "vote": 5, "reasoning": "Default estimate"})

    # Calculate consensus
    vote_values = [v["vote"] for v in votes]
    avg = sum(vote_values) / len(vote_values)
    consensus = min(FIBONACCI, key=lambda x: abs(x - avg))

    # Check if there's high disagreement (spread > 8 points)
    needs_discussion = (max(vote_values) - min(vote_values)) > 8

    return {
        "story_id": story.get("id"),
        "story_title": story.get("title"),
        "votes": votes,
        "average": round(avg, 1),
        "consensus_points": consensus,
        "needs_discussion": needs_discussion,
        "min_vote": min(vote_values),
        "max_vote": max(vote_values),
    }

def run_poker_planning(stories: List[Dict]) -> List[Dict]:
    """Run poker planning for all stories in the sprint."""
    results = []
    for story in stories:
        estimate = estimate_story(story)
        story["story_points"] = estimate["consensus_points"]
        estimate["final_points"] = estimate["consensus_points"]
        results.append(estimate)
    return results
