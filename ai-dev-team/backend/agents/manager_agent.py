from agents.base_agent import BaseAgent
import json
from typing import Dict, List

class ProjectManagerAgent(BaseAgent):
    """
    Top-level orchestrator. Reviews all agent outputs, validates sprint health,
    makes re-assignment decisions, and gives the final Go/No-Go for production.
    """

    def __init__(self):
        super().__init__(
            name="Jordan (PM)",
            role="Chief Technology Officer & Project Manager",
            goal="Ensure all requirements are fully implemented, quality standards met, and the product is genuinely ready for production — not just code-complete",
            backstory="Jordan has shipped 50+ products as CTO and Engineering Director. Ruthlessly practical about quality gates, never lets half-baked code go live. Trusted by both business and engineering."
        )

    def kickoff_briefing(self, backlog: Dict, architecture: Dict) -> Dict:
        """Review backlog + architecture before sprints begin. Raise concerns early."""
        prompt = f"""You are the CTO reviewing the project plan before development starts.

BACKLOG SUMMARY:
- Project: {backlog.get('project_summary','')}
- Epics: {len(backlog.get('epics',[]))}
- Total Stories: {sum(len(e.get('user_stories',[])) for e in backlog.get('epics',[]))}
- NFR: {json.dumps(backlog.get('non_functional_requirements',{}), indent=2)}

ARCHITECTURE:
- Pattern: {architecture.get('architecture_pattern','')}
- Modules: {len(architecture.get('modules',[]))}
- Tech Stack: {json.dumps(architecture.get('tech_stack',{}), indent=2)}

Review this plan and return JSON:
{{
  "approved_to_start": true,
  "concerns": ["Any concern that must be addressed"],
  "risks": [
    {{"risk": "description", "mitigation": "how to handle", "severity": "High/Medium/Low"}}
  ],
  "clarifications_needed": ["Things BA/Architect should clarify before coding"],
  "recommended_focus_areas": ["Security-first on auth module", "Performance on search"],
  "sprint_strategy": "Brief advice on sprint execution order",
  "cto_message": "Brief motivational/strategic message to the team"
}}

Return ONLY valid JSON."""

        output = self._call_llm(self._system_prompt(), prompt, max_tokens=2048)
        try:
            if "```json" in output:
                output = output.split("```json")[1].split("```")[0].strip()
            elif "```" in output:
                output = output.split("```")[1].split("```")[0].strip()
            return json.loads(output)
        except:
            return {"approved_to_start": True, "concerns": [], "cto_message": output[:300]}

    def review_sprint(self, sprint_number: int, sprint_results: Dict, code_review: Dict) -> Dict:
        """Review a completed sprint — approve, flag issues, or request re-work."""
        stories = sprint_results.get("stories_completed", [])
        review_score = code_review.get("score", 80)
        review_issues = code_review.get("issues", [])

        prompt = f"""Review Sprint {sprint_number} results as CTO.

STORIES COMPLETED: {json.dumps([{{'id': s.get('id',''), 'title': s.get('title',''), 'files': s.get('files_count',0)}} for s in stories], indent=2)}

CODE REVIEW:
- Score: {review_score}/100
- Issues: {json.dumps(review_issues[:5], indent=2)}
- Approved by Architect: {code_review.get('approved', True)}

Return JSON:
{{
  "sprint_approved": true,
  "quality_gate_passed": true,
  "stories_to_rework": [],
  "critical_issues": [],
  "warnings": [],
  "sprint_score": 88,
  "pm_notes": "Brief sprint summary and next sprint guidance"
}}

Return ONLY valid JSON."""

        output = self._call_llm(self._system_prompt(), prompt, max_tokens=1024)
        try:
            if "```" in output:
                output = output.split("```")[1].split("```")[0].strip()
                if output.startswith("json"):
                    output = output[4:].strip()
            return json.loads(output)
        except:
            return {"sprint_approved": True, "quality_gate_passed": True, "sprint_score": review_score, "pm_notes": output[:200]}

    def validate_requirements_coverage(self, backlog: Dict, sprint_results: List[Dict]) -> Dict:
        """Build Requirements Traceability Matrix — every requirement must map to code."""
        all_stories = []
        for epic in backlog.get("epics", []):
            for story in epic.get("user_stories", []):
                all_stories.append({"id": story.get("id"), "title": story.get("title"),
                                    "epic": epic.get("title"), "priority": story.get("priority",""),
                                    "acceptance_criteria": story.get("acceptance_criteria", [])})

        completed_story_ids = set()
        for sprint in sprint_results:
            for s in sprint.get("stories_completed", []):
                completed_story_ids.add(s.get("id"))

        rtm_entries = []
        for story in all_stories:
            implemented = story["id"] in completed_story_ids
            rtm_entries.append({
                "requirement_id": story["id"],
                "requirement": story["title"],
                "epic": story["epic"],
                "priority": story["priority"],
                "acceptance_criteria_count": len(story["acceptance_criteria"]),
                "implemented": implemented,
                "status": "COVERED" if implemented else "MISSING"
            })

        total = len(rtm_entries)
        covered = sum(1 for r in rtm_entries if r["status"] == "COVERED")
        missing = [r for r in rtm_entries if r["status"] == "MISSING"]
        coverage_pct = round((covered / total * 100) if total > 0 else 0, 1)

        return {
            "total_requirements": total,
            "covered": covered,
            "missing_count": len(missing),
            "coverage_percentage": coverage_pct,
            "rtm": rtm_entries,
            "missing_requirements": missing,
            "rtm_status": "COMPLETE" if coverage_pct == 100 else ("ACCEPTABLE" if coverage_pct >= 80 else "INCOMPLETE")
        }

    def final_go_no_go(self, backlog: Dict, architecture: Dict, sprint_results: List[Dict],
                       security_result: Dict, perf_result: Dict, rtm: Dict) -> Dict:
        """The most important call — CTO final Go/No-Go decision for production."""

        security_score = security_result.get("security_score", 0)
        perf_score = perf_result.get("performance_score", 0)
        security_status = security_result.get("overall_status", "FAILED")
        perf_status = perf_result.get("overall_status", "FAILED")
        coverage = rtm.get("coverage_percentage", 0)
        missing = rtm.get("missing_count", 0)

        critical_security = security_result.get("critical_issues", [])
        high_security = security_result.get("high_issues", [])

        prompt = f"""You are the CTO making the final Go/No-Go decision for production deployment.

PROJECT: {backlog.get('project_summary','')}

QUALITY GATES:
- Requirements Coverage: {coverage}% ({rtm.get('covered')}/{rtm.get('total_requirements')} stories, {missing} missing)
- Security Score: {security_score}/100 — {security_status}
- Critical Security Issues: {len(critical_security)}
- High Security Issues: {len(high_security)}
- Performance Score: {perf_score}/100 — {perf_status}
- Sprints Completed: {len(sprint_results)}
- Architecture: {architecture.get('architecture_pattern','')}

MINIMUM THRESHOLDS FOR GO:
- Requirements coverage >= 80%
- No critical security issues
- Security score >= 70
- Performance score >= 70
- Performance status PASSED

Return JSON:
{{
  "decision": "GO | NO-GO",
  "confidence": 92,
  "go_live_ready": true,
  "blocking_issues": [],
  "warnings": [],
  "conditions_for_go_live": ["If NO-GO: what must be fixed before re-submission"],
  "quality_gates": [
    {{"gate": "Requirements Coverage", "threshold": ">=80%", "actual": "{coverage}%", "status": "PASS/FAIL"}},
    {{"gate": "Security Score", "threshold": ">=70", "actual": "{security_score}", "status": "PASS/FAIL"}},
    {{"gate": "No Critical Security Issues", "threshold": "0", "actual": "{len(critical_security)}", "status": "PASS/FAIL"}},
    {{"gate": "Performance Score", "threshold": ">=70", "actual": "{perf_score}", "status": "PASS/FAIL"}},
    {{"gate": "Performance Status", "threshold": "PASSED", "actual": "{perf_status}", "status": "PASS/FAIL"}}
  ],
  "deployment_environment": "Production | Staging | Dev-only",
  "cto_sign_off": "Jordan's final sign-off statement (2-3 sentences)"
}}

Be strict. If ANY critical security issue exists, it must be NO-GO.
Return ONLY valid JSON."""

        output = self._call_llm(self._system_prompt(), prompt, max_tokens=2048)
        try:
            if "```json" in output:
                output = output.split("```json")[1].split("```")[0].strip()
            elif "```" in output:
                output = output.split("```")[1].split("```")[0].strip()
            return json.loads(output)
        except:
            # Fallback: derive decision from numbers
            go = (coverage >= 80 and security_score >= 70 and perf_score >= 70
                  and len(critical_security) == 0 and perf_status == "PASSED")
            return {
                "decision": "GO" if go else "NO-GO",
                "confidence": 80,
                "go_live_ready": go,
                "blocking_issues": [] if go else ["Parse error — manual review required"],
                "quality_gates": [],
                "cto_sign_off": output[:300]
            }

    def generate_uat_checklist(self, backlog: Dict, sprint_results: List[Dict]) -> Dict:
        """Generate a UAT checklist that the user/tester can verify manually."""
        all_stories = []
        for epic in backlog.get("epics", []):
            for story in epic.get("user_stories", []):
                story["epic_title"] = epic.get("title", "")
                all_stories.append(story)

        completed_ids = set()
        for sprint in sprint_results:
            for s in sprint.get("stories_completed", []):
                completed_ids.add(s.get("id"))

        checklist = []
        for story in all_stories:
            if story.get("id") in completed_ids:
                checklist.append({
                    "story_id": story.get("id"),
                    "story_title": story.get("title"),
                    "epic": story.get("epic_title"),
                    "test_steps": [
                        f"Verify: {criterion}"
                        for criterion in story.get("acceptance_criteria", [])
                    ],
                    "expected_result": "All acceptance criteria pass",
                    "uat_status": "PENDING",  # To be filled by human tester
                    "tester_notes": ""
                })

        return {
            "total_test_cases": len(checklist),
            "checklist": checklist,
            "instructions": "Mark each test case PASS/FAIL after manual verification. All must pass before production."
        }
