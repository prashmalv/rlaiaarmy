from agents.base_agent import BaseAgent, _parse_json_robust
import json
from typing import Dict, List

class FullStackDeveloperAgent(BaseAgent):
    def __init__(self, agent_id: int = 1):
        self.agent_id = agent_id
        super().__init__(
            name=f"Dev-F{agent_id}",
            role=f"Full Stack Developer #{agent_id}",
            goal="Build complete features including React frontend components and backend integration, ensuring seamless UX",
            backstory=f"Dev-F{agent_id} excels at building end-to-end features. Expert in React, TypeScript, TailwindCSS, REST API integration, state management, and responsive design."
        )

    def implement_story(self, story: Dict, architecture: Dict, assignment: Dict) -> Dict:
        tech_stack = architecture.get("tech_stack", {})
        standards = architecture.get("coding_standards", {})
        module_id = assignment.get("module_id", "")
        module = next((m for m in architecture.get("modules", []) if m["id"] == module_id), {})
        endpoints = module.get("api_endpoints", [])

        prompt = f"""Implement this user story as a complete full-stack feature with React frontend and backend integration.

USER STORY:
- Title: {story.get('title')}
- As a {story.get('as_a')}, I want {story.get('i_want')}, so that {story.get('so_that')}
- Acceptance Criteria: {json.dumps(story.get('acceptance_criteria', []))}

MODULE: {module.get('name', '')}
API ENDPOINTS (backend already built by AI Engineers - just consume them):
{json.dumps(endpoints, indent=2)}

TECH STACK: {json.dumps(tech_stack, indent=2)}
TASK BREAKDOWN: {json.dumps(assignment.get('task_breakdown', []))}

Generate complete React TypeScript components + API service layer. Return JSON:
{{
  "files": [
    {{
      "path": "frontend/src/components/ComponentName.tsx",
      "content": "// Complete TypeScript React component",
      "description": "What this component does"
    }},
    {{
      "path": "frontend/src/services/apiService.ts",
      "content": "// API integration service",
      "description": "API calls to backend"
    }},
    {{
      "path": "frontend/src/hooks/useHookName.ts",
      "content": "// Custom React hook",
      "description": "State management hook"
    }}
  ],
  "tests": [
    {{
      "path": "frontend/src/__tests__/ComponentName.test.tsx",
      "content": "// Jest + React Testing Library tests"
    }}
  ],
  "notes": "Implementation notes and any UX decisions made"
}}

Write REAL, complete, runnable TypeScript/React code. Use TailwindCSS for styling.
Return ONLY valid JSON."""

        output = self._call_llm(self._system_prompt(), prompt, max_tokens=8096)
        try:
            return _parse_json_robust(output)
        except:
            return {"files": [], "tests": [], "notes": output[:300], "error": "Parse failed"}

    def integrate_modules(self, all_modules_code: List[Dict], architecture: Dict) -> Dict:
        """Handle integration between multiple modules - resolves conflicts and ensures cohesion."""
        modules_summary = "\n".join([
            f"Module: {m.get('module_name')}, Files: {[f['path'] for f in m.get('files', [])]}"
            for m in all_modules_code
        ])

        prompt = f"""Review and integrate these frontend modules from multiple developers into a cohesive application.

MODULES BUILT:
{modules_summary}

ARCHITECTURE: {json.dumps(architecture.get('modules', []), indent=2)}

Create integration files:
{{
  "files": [
    {{
      "path": "frontend/src/App.tsx",
      "content": "// Main app with routing",
      "description": "Root app component with all routes"
    }},
    {{
      "path": "frontend/src/router/index.tsx",
      "content": "// React Router setup",
      "description": "All app routes"
    }},
    {{
      "path": "frontend/src/store/index.ts",
      "content": "// Global state (Zustand or Context)",
      "description": "Shared state management"
    }},
    {{
      "path": "frontend/src/types/index.ts",
      "content": "// Shared TypeScript types",
      "description": "Common types used across modules"
    }}
  ],
  "conflicts_resolved": ["List of any conflicts found and resolved"],
  "notes": "Integration summary"
}}

Return ONLY valid JSON."""

        output = self._call_llm(self._system_prompt(), prompt, max_tokens=8096)
        try:
            return _parse_json_robust(output)
        except:
            return {"files": [], "conflicts_resolved": [], "notes": output[:300]}
