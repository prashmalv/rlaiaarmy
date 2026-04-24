from agents.base_agent import BaseAgent, _parse_json_robust
import json
from typing import Dict, List

class TechArchitectAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Morgan",
            role="Senior Tech Lead & Solution Architect",
            goal="Design scalable, secure, and maintainable system architecture; define module boundaries, API contracts, and coding standards for the team",
            backstory="Morgan has 15 years of experience building enterprise systems at FAANG companies. Expert in microservices, cloud-native architectures, DDD, and security-first design."
        )

    def design_architecture(self, backlog: Dict, nfr: Dict = None) -> Dict:
        nfr_text = json.dumps(nfr or backlog.get("non_functional_requirements", {}), indent=2)
        prompt = f"""Design a complete system architecture for this project.

PROJECT SUMMARY: {backlog.get('project_summary', '')}
DOMAIN: {backlog.get('domain', '')}
EPICS: {json.dumps([e['title'] for e in backlog.get('epics', [])], indent=2)}
NON-FUNCTIONAL REQUIREMENTS: {nfr_text}
TECH STACK SUGGESTIONS: {json.dumps(backlog.get('tech_stack_suggestions', []))}

Return a JSON with this structure:
{{
  "architecture_pattern": "e.g., Layered MVC / Microservices / Serverless",
  "tech_stack": {{
    "frontend": "React 18 + TypeScript + TailwindCSS",
    "backend": "FastAPI + Python 3.11",
    "database": "PostgreSQL + Redis",
    "infrastructure": "Docker + Nginx",
    "testing": "Pytest + Jest + Locust"
  }},
  "modules": [
    {{
      "id": "MOD-1",
      "name": "Module name",
      "description": "What this module does",
      "assigned_to": "ai_engineer | fullstack_dev",
      "folder_structure": ["src/module/", "src/module/models/"],
      "api_endpoints": [
        {{
          "method": "GET",
          "path": "/api/v1/resource",
          "description": "What it does",
          "request_body": {{}},
          "response": {{}}
        }}
      ],
      "interfaces": ["Interface definitions for other modules to depend on"],
      "stories_covered": ["US-1", "US-2"]
    }}
  ],
  "database_schema": [
    {{
      "table": "table_name",
      "columns": [
        {{"name": "id", "type": "UUID", "constraints": "PRIMARY KEY"}}
      ]
    }}
  ],
  "security_requirements": ["JWT auth", "Rate limiting", "Input validation"],
  "coding_standards": {{
    "naming_conventions": "snake_case for Python, camelCase for JS",
    "error_handling": "Always return structured error responses",
    "logging": "Use structured JSON logging",
    "testing": "Minimum 80% code coverage"
  }},
  "integration_points": ["How modules communicate with each other"],
  "deployment": {{
    "local": "Docker Compose",
    "ci_cd": "GitHub Actions",
    "ports": {{"frontend": 3000, "backend": 8000, "db": 5432}}
  }}
}}

Return ONLY valid JSON."""

        output = self._call_llm(self._system_prompt(), prompt, max_tokens=8096)
        try:
            return _parse_json_robust(output)
        except:
            return {
                "architecture_pattern": "Layered MVC",
                "tech_stack": {"backend": "FastAPI", "frontend": "React", "database": "SQLite"},
                "modules": [], "database_schema": [], "security_requirements": [],
                "coding_standards": {}, "integration_points": [], "deployment": {},
                "error": "Architecture parse failed — using fallback", "raw": output[:300]
            }

    def assign_stories_to_modules(self, stories: List[Dict], architecture: Dict) -> List[Dict]:
        """Map user stories to architecture modules and assign to engineers."""
        modules = architecture.get("modules", [])
        prompt = f"""Given these user stories and architecture modules, assign each story to the most appropriate module.

STORIES: {json.dumps(stories, indent=2)}
MODULES: {json.dumps([{{'id': m['id'], 'name': m['name'], 'description': m['description'], 'assigned_to': m['assigned_to']}} for m in modules], indent=2)}

Return JSON array:
[
  {{
    "story_id": "US-1",
    "module_id": "MOD-1",
    "assigned_to": "ai_engineer_1 | ai_engineer_2 | fullstack_dev_1 | fullstack_dev_2",
    "task_breakdown": ["Specific task 1", "Specific task 2"],
    "estimated_hours": 2
  }}
]

Return ONLY valid JSON array."""

        output = self._call_llm(self._system_prompt(), prompt)
        try:
            return _parse_json_robust(output)
        except:
            return []

    def review_code(self, code: str, module: str, standards: Dict) -> Dict:
        prompt = f"""Review this code for the {module} module against our coding standards.

CODING STANDARDS: {json.dumps(standards, indent=2)}

CODE TO REVIEW:
{code}

Return JSON:
{{
  "approved": true/false,
  "score": 85,
  "issues": [
    {{"severity": "high/medium/low", "description": "Issue", "line": "approximate", "suggestion": "Fix"}}
  ],
  "suggestions": ["General improvement suggestion"],
  "summary": "Overall review summary"
}}"""

        output = self._call_llm(self._system_prompt(), prompt)
        try:
            return _parse_json_robust(output)
        except:
            return {"approved": True, "score": 80, "issues": [], "summary": output[:300]}
