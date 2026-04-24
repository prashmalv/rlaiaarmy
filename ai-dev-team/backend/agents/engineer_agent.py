from agents.base_agent import BaseAgent, _parse_json_robust
import json
import os
from typing import Dict, List

class AIEngineerAgent(BaseAgent):
    def __init__(self, agent_id: int = 1):
        self.agent_id = agent_id
        super().__init__(
            name=f"Dev-E{agent_id}",
            role=f"AI Engineer #{agent_id} - Backend Specialist",
            goal="Write clean, tested, production-ready backend code following architecture specs and coding standards",
            backstory=f"Dev-E{agent_id} specialises in backend APIs, database design, authentication, and business logic. Expert in Python, FastAPI, SQLAlchemy, and REST/GraphQL APIs."
        )

    def implement_story(self, story: Dict, architecture: Dict, assignment: Dict) -> Dict:
        tech_stack = architecture.get("tech_stack", {})
        standards = architecture.get("coding_standards", {})
        module_id = assignment.get("module_id", "")
        module = next((m for m in architecture.get("modules", []) if m["id"] == module_id), {})

        prompt = f"""Implement the following user story as production-ready backend code.

USER STORY:
- Title: {story.get('title')}
- As a {story.get('as_a')}, I want {story.get('i_want')}, so that {story.get('so_that')}
- Acceptance Criteria: {json.dumps(story.get('acceptance_criteria', []))}
- Technical Notes: {story.get('technical_notes', '')}

MODULE: {module.get('name', '')} - {module.get('description', '')}
API ENDPOINTS TO IMPLEMENT: {json.dumps(module.get('api_endpoints', []), indent=2)}
TECH STACK: {json.dumps(tech_stack, indent=2)}
CODING STANDARDS: {json.dumps(standards, indent=2)}
TASK BREAKDOWN: {json.dumps(assignment.get('task_breakdown', []))}

Generate complete, working code files. Return JSON:
{{
  "files": [
    {{
      "path": "backend/src/module_name/router.py",
      "content": "# Complete file content here",
      "description": "What this file does"
    }}
  ],
  "tests": [
    {{
      "path": "backend/tests/test_module_name.py",
      "content": "# Complete test file content",
      "description": "Tests for the module"
    }}
  ],
  "environment_variables": ["VAR_NAME=description"],
  "dependencies": ["package==version"],
  "notes": "Any important implementation notes"
}}

IMPORTANT: Write REAL, complete, runnable code - not pseudocode or placeholders.
Return ONLY valid JSON."""

        output = self._call_llm(self._system_prompt(), prompt, max_tokens=8096)
        try:
            return _parse_json_robust(output)
        except:
            return {"files": [], "tests": [], "notes": output[:300], "error": "Parse failed"}

    def write_unit_tests(self, code_files: List[Dict], story: Dict) -> Dict:
        files_summary = "\n".join([f"File: {f['path']}\n{f['content'][:500]}..." for f in code_files])
        prompt = f"""Write comprehensive unit tests for this code.

STORY: {story.get('title')}
ACCEPTANCE CRITERIA: {json.dumps(story.get('acceptance_criteria', []))}

CODE FILES:
{files_summary}

Return JSON:
{{
  "test_files": [
    {{
      "path": "tests/test_name.py",
      "content": "# Complete pytest test file"
    }}
  ],
  "coverage_estimate": 85
}}"""

        output = self._call_llm(self._system_prompt(), prompt, max_tokens=4096)
        try:
            return _parse_json_robust(output)
        except:
            return {"test_files": [], "coverage_estimate": 0}
