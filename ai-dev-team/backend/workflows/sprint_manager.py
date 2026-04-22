import asyncio
import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Callable, Optional

from agents.ba_agent import BusinessAnalystAgent
from agents.architect_agent import TechArchitectAgent
from agents.engineer_agent import AIEngineerAgent
from agents.fullstack_agent import FullStackDeveloperAgent
from agents.security_agent import SecurityTestingAgent
from agents.performance_agent import PerformanceTestingAgent
from agents.manager_agent import ProjectManagerAgent
from workflows.poker_planning import run_poker_planning
from reports.report_generator import ReportGenerator
from config.settings import settings

class SprintManager:
    def __init__(self, project_id: str, project_name: str, output_dir: str = None):
        self.project_id = project_id
        self.project_name = project_name
        self.output_dir = output_dir or os.path.join(settings.OUTPUT_DIR, project_id)
        self.logs: List[Dict] = []
        self.all_generated_files: List[Dict] = []

        # Initialise all agents
        self.manager = ProjectManagerAgent()
        self.ba = BusinessAnalystAgent()
        self.architect = TechArchitectAgent()
        self.engineers = [AIEngineerAgent(i) for i in range(1, settings.MAX_ENGINEERS + 1)]
        self.fullstack_devs = [FullStackDeveloperAgent(i) for i in range(1, settings.MAX_FULLSTACK_DEVS + 1)]
        self.security = SecurityTestingAgent()
        self.performance = PerformanceTestingAgent()
        self.reporter = ReportGenerator()

        self.progress_callback: Optional[Callable] = None

    def set_progress_callback(self, cb: Callable):
        self.progress_callback = cb

    def _log(self, agent: str, action: str, input_data: str, output_summary: str, status: str = "success"):
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent": agent,
            "action": action,
            "input": input_data[:300],
            "output_summary": output_summary[:500],
            "status": status
        }
        self.logs.append(entry)
        if self.progress_callback:
            self.progress_callback(entry)
        return entry

    def _emit(self, event: str, data: dict):
        if self.progress_callback:
            self.progress_callback({"event": event, **data})

    def _save_file(self, path: str, content):
        if not path:
            return
        if not isinstance(content, str):
            content = str(content) if content is not None else ""
        full_path = os.path.join(self.output_dir, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        self.all_generated_files.append({"path": path, "full_path": full_path})

    def run(self, raw_requirements: str) -> Dict:
        os.makedirs(self.output_dir, exist_ok=True)
        self._emit("phase", {"name": "REQUIREMENTS ANALYSIS", "status": "started"})

        # ── PHASE 1: BA analyses requirements ──────────────────────────────
        self._emit("agent_working", {"agent": "Alex (BA)", "task": "Analysing requirements..."})
        backlog = self.ba.analyse_requirements(raw_requirements)
        self._log("Alex (BA)", "analyse_requirements", raw_requirements[:200],
                  f"Created {sum(len(e.get('user_stories',[])) for e in backlog.get('epics',[]))} user stories across {len(backlog.get('epics',[]))} epics")

        self._save_file("backlog.json", json.dumps(backlog, indent=2))
        self._emit("phase", {"name": "REQUIREMENTS ANALYSIS", "status": "complete",
                             "summary": f"{len(backlog.get('epics',[]))} epics, {sum(len(e.get('user_stories',[]))for e in backlog.get('epics',[]))} user stories"})

        # ── PHASE 2: Tech Architect designs system ──────────────────────────
        self._emit("phase", {"name": "ARCHITECTURE DESIGN", "status": "started"})
        self._emit("agent_working", {"agent": "Morgan (Architect)", "task": "Designing system architecture..."})
        architecture = self.architect.design_architecture(backlog)
        self._log("Morgan (Architect)", "design_architecture", backlog.get("project_summary", ""),
                  f"Designed {len(architecture.get('modules',[]))} modules with {architecture.get('architecture_pattern','')}")

        self._save_file("architecture.json", json.dumps(architecture, indent=2))
        self._emit("phase", {"name": "ARCHITECTURE DESIGN", "status": "complete",
                             "summary": f"{len(architecture.get('modules',[]))} modules defined"})

        # ── PHASE 2b: Manager Kickoff Briefing ─────────────────────────────
        self._emit("agent_working", {"agent": "Jordan (PM)", "task": "CTO kickoff review — checking plan before dev starts..."})
        kickoff = self.manager.kickoff_briefing(backlog, architecture)
        self._log("Jordan (PM)", "kickoff_briefing", "backlog + architecture",
                  f"Approved: {kickoff.get('approved_to_start')}, Concerns: {len(kickoff.get('concerns',[]))}, Risks: {len(kickoff.get('risks',[]))}")
        self._save_file("manager/kickoff_briefing.json", json.dumps(kickoff, indent=2))
        self._emit("phase", {"name": "CTO KICKOFF REVIEW", "status": "complete",
                             "summary": kickoff.get("cto_message","")[:120]})

        # ── PHASE 3: Sprint Planning & Poker ───────────────────────────────
        all_stories = []
        for epic in backlog.get("epics", []):
            for story in epic.get("user_stories", []):
                story["epic_id"] = epic["id"]
                story["epic_title"] = epic["title"]
                all_stories.append(story)

        self._emit("phase", {"name": "POKER PLANNING", "status": "started"})
        self._emit("agent_working", {"agent": "All Agents", "task": f"Estimating {len(all_stories)} user stories..."})
        poker_results = run_poker_planning(all_stories)
        total_points = sum(r["final_points"] for r in poker_results)
        self._log("All Agents", "poker_planning", f"{len(all_stories)} stories",
                  f"Total {total_points} story points estimated")
        self._save_file("poker_results.json", json.dumps(poker_results, indent=2))
        self._emit("phase", {"name": "POKER PLANNING", "status": "complete",
                             "summary": f"Total {total_points} story points"})

        # ── PHASE 4: Architect assigns stories to modules ───────────────────
        story_assignments = self.architect.assign_stories_to_modules(all_stories, architecture)
        self._log("Morgan (Architect)", "assign_stories_to_modules", f"{len(all_stories)} stories",
                  f"Assigned stories to {len(story_assignments)} tasks across engineers")
        self._save_file("story_assignments.json", json.dumps(story_assignments, indent=2))

        # ── PHASE 5: Sprint Execution ───────────────────────────────────────
        SPRINT_CAPACITY = 21
        sprints = []
        current_sprint_stories = []
        current_points = 0
        sprint_number = 1

        for story in all_stories:
            pts = story.get("story_points", 3)
            if current_points + pts > SPRINT_CAPACITY and current_sprint_stories:
                sprints.append({"sprint": sprint_number, "stories": current_sprint_stories, "total_points": current_points})
                sprint_number += 1
                current_sprint_stories = [story]
                current_points = pts
            else:
                current_sprint_stories.append(story)
                current_points += pts

        if current_sprint_stories:
            sprints.append({"sprint": sprint_number, "stories": current_sprint_stories, "total_points": current_points})

        all_sprint_results = []
        engineer_idx = 0
        fullstack_idx = 0

        for sprint_data in sprints:
            sprint_num = sprint_data["sprint"]
            sprint_stories = sprint_data["stories"]

            self._emit("phase", {"name": f"SPRINT {sprint_num}", "status": "started",
                                 "stories": len(sprint_stories), "points": sprint_data["total_points"]})

            sprint_files = []
            sprint_results = {"sprint": sprint_num, "stories_completed": [], "files_generated": [], "tests": []}

            for story in sprint_stories:
                # Find assignment for this story
                assignment = next((a for a in story_assignments if a.get("story_id") == story.get("id")), {})
                assigned_to = assignment.get("assigned_to", "ai_engineer_1")

                if "fullstack" in assigned_to:
                    dev = self.fullstack_devs[fullstack_idx % len(self.fullstack_devs)]
                    fullstack_idx += 1
                    self._emit("agent_working", {"agent": dev.name, "task": f"Building: {story.get('title')}"})
                    result = dev.implement_story(story, architecture, assignment)
                else:
                    dev = self.engineers[engineer_idx % len(self.engineers)]
                    engineer_idx += 1
                    self._emit("agent_working", {"agent": dev.name, "task": f"Implementing: {story.get('title')}"})
                    result = dev.implement_story(story, architecture, assignment)

                self._log(dev.name, f"implement_story:{story.get('id')}", story.get("title"),
                          f"Generated {len(result.get('files',[]))} files, {len(result.get('tests',[]))} test files")

                # Save generated files
                for file_data in result.get("files", []):
                    if not isinstance(file_data, dict):
                        continue
                    path = file_data.get("path")
                    if not path:
                        continue
                    self._save_file(path, file_data.get("content") or "")
                    sprint_files.append(file_data)

                for test_data in result.get("tests", []):
                    if not isinstance(test_data, dict):
                        continue
                    path = test_data.get("path")
                    if not path:
                        continue
                    self._save_file(path, test_data.get("content") or "")
                    sprint_results["tests"].append(test_data)

                sprint_results["stories_completed"].append({
                    "id": story.get("id"),
                    "title": story.get("title"),
                    "assigned_to": dev.name,
                    "files_count": len(result.get("files", [])),
                    "notes": result.get("notes", "")
                })
                sprint_results["files_generated"].extend(sprint_files)

            # Architect code review
            self._emit("agent_working", {"agent": "Morgan (Architect)", "task": f"Code review for Sprint {sprint_num}..."})
            if sprint_files:
                review = self.architect.review_code(
                    "\n".join([f.get("content", "")[:500] for f in sprint_files[:3]]),
                    f"Sprint {sprint_num}",
                    architecture.get("coding_standards", {})
                )
                sprint_results["code_review"] = review
                self._log("Morgan (Architect)", f"code_review:sprint_{sprint_num}",
                          f"{len(sprint_files)} files", f"Score: {review.get('score')}, Approved: {review.get('approved')}")

                # Manager reviews the sprint
                self._emit("agent_working", {"agent": "Jordan (PM)", "task": f"PM sprint review for Sprint {sprint_num}..."})
                pm_review = self.manager.review_sprint(sprint_num, sprint_results, review)
                sprint_results["pm_review"] = pm_review
                self._log("Jordan (PM)", f"sprint_review:{sprint_num}", f"Sprint {sprint_num}",
                          f"Approved: {pm_review.get('sprint_approved')}, Score: {pm_review.get('sprint_score')}, Notes: {pm_review.get('pm_notes','')[:120]}")

            all_sprint_results.append(sprint_results)
            self._emit("phase", {"name": f"SPRINT {sprint_num}", "status": "complete",
                                 "stories_done": len(sprint_results["stories_completed"])})

        # ── PHASE 6: Integration (Full Stack leads) ─────────────────────────
        self._emit("phase", {"name": "INTEGRATION", "status": "started"})
        integration_dev = self.fullstack_devs[0]
        self._emit("agent_working", {"agent": integration_dev.name, "task": "Integrating all modules..."})

        modules_code = [{"module_name": s["title"], "files": s.get("files", [])}
                        for sprint in all_sprint_results for s in sprint.get("stories_completed", [])]
        integration_result = integration_dev.integrate_modules(modules_code, architecture)
        self._log(integration_dev.name, "integrate_modules", f"{len(modules_code)} modules",
                  f"Generated {len(integration_result.get('files',[]))} integration files")

        for file_data in integration_result.get("files", []):
            if isinstance(file_data, dict) and file_data.get("path"):
                self._save_file(file_data["path"], file_data.get("content") or "")

        self._emit("phase", {"name": "INTEGRATION", "status": "complete",
                             "conflicts_resolved": len(integration_result.get("conflicts_resolved", []))})

        # ── PHASE 7: Security Testing ───────────────────────────────────────
        self._emit("phase", {"name": "SECURITY TESTING", "status": "started"})
        self._emit("agent_working", {"agent": "Sam (Security)", "task": "Running OWASP security analysis..."})
        all_code_files = [f for sprint in all_sprint_results for f in sprint.get("files_generated", [])]
        security_result = self.security.run_security_analysis(all_code_files, architecture)
        security_scripts = self.security.generate_security_test_scripts(architecture)
        self._log("Sam (Security)", "security_analysis", f"{len(all_code_files)} files",
                  f"Status: {security_result.get('overall_status')}, Score: {security_result.get('security_score')}")

        for test_file in security_scripts.get("test_files", []):
            self._save_file(test_file["path"], test_file.get("content", ""))

        self._save_file("reports/security_report.json", json.dumps(security_result, indent=2))
        self._emit("phase", {"name": "SECURITY TESTING", "status": "complete",
                             "result": security_result.get("overall_status"), "score": security_result.get("security_score")})

        # ── PHASE 8: Performance Testing ────────────────────────────────────
        self._emit("phase", {"name": "PERFORMANCE TESTING", "status": "started"})
        self._emit("agent_working", {"agent": "Perry (Performance)", "task": "Running load and stress tests..."})
        perf_result = self.performance.run_performance_analysis(architecture, backlog.get("non_functional_requirements"))
        locust_script = self.performance.generate_locust_script(architecture)
        self._log("Perry (Performance)", "performance_analysis", "architecture",
                  f"Status: {perf_result.get('overall_status')}, Score: {perf_result.get('performance_score')}")

        for test_file in locust_script.get("test_files", []):
            self._save_file(test_file["path"], test_file.get("content", ""))

        self._save_file("reports/performance_report.json", json.dumps(perf_result, indent=2))
        self._emit("phase", {"name": "PERFORMANCE TESTING", "status": "complete",
                             "result": perf_result.get("overall_status"), "score": perf_result.get("performance_score")})

        # ── PHASE 9: RTM + UAT Checklist + Go/No-Go ────────────────────────
        self._emit("phase", {"name": "RTM & GO/NO-GO DECISION", "status": "started"})
        self._emit("agent_working", {"agent": "Jordan (PM)", "task": "Building RTM and making Go/No-Go decision..."})

        rtm = self.manager.validate_requirements_coverage(backlog, all_sprint_results)
        uat_checklist = self.manager.generate_uat_checklist(backlog, all_sprint_results)
        go_no_go = self.manager.final_go_no_go(backlog, architecture, all_sprint_results,
                                                security_result, perf_result, rtm)

        self._log("Jordan (PM)", "requirements_traceability", f"{rtm['total_requirements']} requirements",
                  f"Coverage: {rtm['coverage_percentage']}%, Missing: {rtm['missing_count']}, Status: {rtm['rtm_status']}")
        self._log("Jordan (PM)", "final_go_no_go", "all results",
                  f"DECISION: {go_no_go.get('decision')} | Confidence: {go_no_go.get('confidence')}% | {go_no_go.get('cto_sign_off','')[:150]}")

        self._save_file("manager/rtm.json", json.dumps(rtm, indent=2))
        self._save_file("manager/uat_checklist.json", json.dumps(uat_checklist, indent=2))
        self._save_file("manager/go_no_go.json", json.dumps(go_no_go, indent=2))

        self._emit("phase", {"name": "RTM & GO/NO-GO DECISION", "status": "complete",
                             "summary": f"{go_no_go.get('decision')} — Coverage: {rtm['coverage_percentage']}%",
                             "result": go_no_go.get("decision")})

        # ── PHASE 10: Generate Final Report ────────────────────────────────
        self._emit("phase", {"name": "REPORT GENERATION", "status": "started"})
        final_report = self.reporter.generate(
            project_id=self.project_id,
            project_name=self.project_name,
            backlog=backlog,
            architecture=architecture,
            poker_results=poker_results,
            sprint_results=all_sprint_results,
            security_result=security_result,
            perf_result=perf_result,
            agent_logs=self.logs,
            all_files=self.all_generated_files,
            rtm=rtm,
            go_no_go=go_no_go,
            uat_checklist=uat_checklist,
            kickoff=kickoff,
        )

        report_path = os.path.join(self.output_dir, "reports/final_report.html")
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(final_report)

        self._emit("phase", {"name": "REPORT GENERATION", "status": "complete"})

        # ── PHASE 11: Final Approval Status ────────────────────────────────
        cto_decision = go_no_go.get("decision", "NO-GO")
        security_passed = security_result.get("overall_status") == "PASSED"
        perf_passed = perf_result.get("overall_status") == "PASSED"
        all_passed = (security_passed and perf_passed and cto_decision == "GO")

        return {
            "project_id": self.project_id,
            "project_name": self.project_name,
            "status": "pending_approval" if all_passed else "failed_testing",
            "output_dir": self.output_dir,
            "sprints_completed": len(all_sprint_results),
            "total_stories": len(all_stories),
            "total_files": len(self.all_generated_files),
            "security": {"status": security_result.get("overall_status"), "score": security_result.get("security_score")},
            "performance": {"status": perf_result.get("overall_status"), "score": perf_result.get("performance_score")},
            "rtm": {"coverage": rtm.get("coverage_percentage"), "status": rtm.get("rtm_status"), "missing": rtm.get("missing_count")},
            "go_no_go": {"decision": cto_decision, "confidence": go_no_go.get("confidence")},
            "report_path": report_path,
            "approval_required": all_passed,
            "agent_log_count": len(self.logs),
            "backlog": backlog,
            "architecture": architecture,
            "sprint_results": all_sprint_results,
            "security_result": security_result,
            "perf_result": perf_result,
            "agent_logs": self.logs,
        }
