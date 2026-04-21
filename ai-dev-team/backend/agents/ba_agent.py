from agents.base_agent import BaseAgent
import json
from typing import List, Dict

class BusinessAnalystAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Alex",
            role="Senior Business Analyst & Domain Expert",
            goal="Analyse raw requirements, identify gaps, create complete agile backlog with user stories, acceptance criteria, and priority",
            backstory="Alex has 12 years of experience as a BA across fintech, healthcare, and e-commerce domains. Expert in agile, JIRA, user story mapping, and stakeholder communication."
        )

    def analyse_requirements(self, raw_requirements: str) -> Dict:
        prompt = f"""Analyse the following raw requirements and produce a complete agile backlog.

RAW REQUIREMENTS:
{raw_requirements}

Produce a JSON response with this exact structure:
{{
  "project_summary": "Brief project description",
  "domain": "Domain/industry",
  "assumptions": ["assumption1", "assumption2"],
  "risks": ["risk1", "risk2"],
  "epics": [
    {{
      "id": "EPIC-1",
      "title": "Epic title",
      "description": "Description",
      "user_stories": [
        {{
          "id": "US-1",
          "title": "User story title",
          "as_a": "user type",
          "i_want": "action/feature",
          "so_that": "benefit",
          "acceptance_criteria": ["criterion1", "criterion2"],
          "priority": "High/Medium/Low",
          "story_points": 0,
          "technical_notes": "Any technical considerations",
          "dependencies": []
        }}
      ]
    }}
  ],
  "non_functional_requirements": {{
    "performance": "e.g., <200ms response time",
    "security": "e.g., OWASP Top 10 compliance",
    "scalability": "e.g., 10,000 concurrent users",
    "accessibility": "e.g., WCAG 2.1 AA"
  }},
  "tech_stack_suggestions": ["suggestion1", "suggestion2"],
  "definition_of_done": ["criterion1", "criterion2"]
}}

Return ONLY valid JSON, no markdown."""

        output = self._call_llm(self._system_prompt(), prompt, max_tokens=8096)

        # Parse and validate JSON
        try:
            # Strip markdown if present
            if "```json" in output:
                output = output.split("```json")[1].split("```")[0].strip()
            elif "```" in output:
                output = output.split("```")[1].split("```")[0].strip()
            backlog = json.loads(output)
        except json.JSONDecodeError:
            backlog = {"error": "Failed to parse backlog", "raw": output}

        return backlog

    def refine_user_story(self, story: Dict, architect_feedback: str) -> Dict:
        prompt = f"""Refine this user story based on architect feedback.

USER STORY: {json.dumps(story, indent=2)}
ARCHITECT FEEDBACK: {architect_feedback}

Return the refined user story as valid JSON with the same structure."""

        output = self._call_llm(self._system_prompt(), prompt)
        try:
            return json.loads(output)
        except:
            return story

    def create_sprint_backlog(self, backlog: Dict, sprint_capacity_points: int) -> List[Dict]:
        """Select stories for a sprint based on capacity and priority."""
        all_stories = []
        for epic in backlog.get("epics", []):
            for story in epic.get("user_stories", []):
                story["epic_id"] = epic["id"]
                story["epic_title"] = epic["title"]
                all_stories.append(story)

        # Sort by priority
        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        all_stories.sort(key=lambda x: priority_order.get(x.get("priority", "Low"), 2))

        # Fill sprint up to capacity
        sprint_stories = []
        current_points = 0
        for story in all_stories:
            pts = story.get("story_points", 3)
            if current_points + pts <= sprint_capacity_points:
                sprint_stories.append(story)
                current_points += pts

        return sprint_stories
