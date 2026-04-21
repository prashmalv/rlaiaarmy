from typing import Dict, List
from datetime import datetime
import json

class ReportGenerator:
    def generate(self, project_id: str, project_name: str, backlog: Dict, architecture: Dict,
                 poker_results: List, sprint_results: List, security_result: Dict,
                 perf_result: Dict, agent_logs: List, all_files: List,
                 rtm: Dict = None, go_no_go: Dict = None,
                 uat_checklist: Dict = None, kickoff: Dict = None) -> str:

        total_stories = sum(len(s.get("stories_completed", [])) for s in sprint_results)
        total_files = len(all_files)
        security_score = security_result.get("security_score", 0)
        perf_score = perf_result.get("performance_score", 0)
        security_status = security_result.get("overall_status", "UNKNOWN")
        perf_status = perf_result.get("overall_status", "UNKNOWN")

        # RTM + Go/No-Go defaults
        rtm = rtm or {}
        go_no_go = go_no_go or {}
        uat_checklist = uat_checklist or {}
        kickoff = kickoff or {}

        rtm_coverage = rtm.get("coverage_percentage", 0)
        rtm_status = rtm.get("rtm_status", "UNKNOWN")
        go_decision = go_no_go.get("decision", "PENDING")
        go_color = "#16a34a" if go_decision == "GO" else "#dc2626"
        go_confidence = go_no_go.get("confidence", 0)

        # Build sprint cards HTML
        sprint_cards = ""
        for sprint in sprint_results:
            review = sprint.get("code_review", {})
            pm_review = sprint.get("pm_review", {})
            stories_html = "".join([
                f'<div class="story-item"><span class="badge">{s.get("id","")}</span> {s.get("title","")} <span class="agent-tag">{s.get("assigned_to","")}</span></div>'
                for s in sprint.get("stories_completed", [])
            ])
            pm_html = f'<div class="review-info" style="margin-top:6px;">PM Score: <strong>{pm_review.get("sprint_score","N/A")}</strong> — {pm_review.get("pm_notes","")[:120]}</div>' if pm_review else ""
            sprint_cards += f"""
            <div class="sprint-card">
              <div class="sprint-header">Sprint {sprint.get('sprint')} <span class="sprint-meta">{len(sprint.get('stories_completed', []))} stories · {sprint.get('total_files_count', len(sprint.get('files_generated', [])))} files</span></div>
              <div class="sprint-body">
                {stories_html}
                <div class="review-info">Code Review Score: <strong>{review.get('score', 'N/A')}</strong> — {review.get('summary', '')[:120]}</div>
                {pm_html}
              </div>
            </div>"""

        # RTM table
        rtm_rows = ""
        for entry in rtm.get("rtm", []):
            status = entry.get("status", "MISSING")
            color = "#4ade80" if status == "COVERED" else "#f87171"
            rtm_rows += f"""
            <tr>
              <td><span class="badge">{entry.get('requirement_id','')}</span></td>
              <td>{entry.get('requirement','')[:70]}</td>
              <td>{entry.get('epic','')[:40]}</td>
              <td><span style="color:#94a3b8;font-size:0.8rem;">{entry.get('priority','')}</span></td>
              <td>{entry.get('acceptance_criteria_count',0)}</td>
              <td style="color:{color};font-weight:600;">{status}</td>
            </tr>"""

        # Go/No-Go quality gates
        gate_rows = ""
        for gate in go_no_go.get("quality_gates", []):
            g_status = gate.get("status","")
            g_color = "#4ade80" if "PASS" in g_status else "#f87171"
            gate_rows += f"""
            <tr>
              <td>{gate.get('gate','')}</td>
              <td style="color:#94a3b8;">{gate.get('threshold','')}</td>
              <td style="font-weight:600;">{gate.get('actual','')}</td>
              <td style="color:{g_color};font-weight:600;">{g_status}</td>
            </tr>"""

        # UAT checklist
        uat_rows = ""
        for tc in (uat_checklist.get("checklist", []))[:30]:
            steps_html = "".join([f"<li>{step}</li>" for step in tc.get("test_steps", [])])
            uat_rows += f"""
            <tr>
              <td><span class="badge">{tc.get('story_id','')}</span></td>
              <td>{tc.get('story_title','')[:60]}</td>
              <td><ul style="margin:0;padding-left:16px;font-size:0.82rem;color:#94a3b8;">{steps_html}</ul></td>
              <td><span style="background:#1e3a5f;color:#60a5fa;padding:2px 8px;border-radius:4px;font-size:0.78rem;">PENDING</span></td>
            </tr>"""

        # Kickoff concerns
        concerns_html = ""
        if kickoff.get("concerns"):
            concerns_html = "<ul>" + "".join([f"<li style='color:#fbbf24;margin:4px 0;'>{c}</li>" for c in kickoff["concerns"]]) + "</ul>"
        risks_html = ""
        if kickoff.get("risks"):
            risks_html = "".join([f'<div style="margin:6px 0;padding:8px;background:#0f172a;border-radius:6px;border-left:3px solid {"#dc2626" if r.get("severity")=="High" else "#d97706"};"><strong>{r.get("risk","")}</strong><br/><span style="color:#94a3b8;font-size:0.85rem;">Mitigation: {r.get("mitigation","")}</span></div>' for r in kickoff["risks"]])

        # Agent logs table
        log_rows = ""
        for log in agent_logs:
            status_class = "success" if log.get("status") == "success" else "error"
            log_rows += f"""
            <tr>
              <td>{log.get('timestamp','')[:19]}</td>
              <td><span class="agent-badge">{log.get('agent','')}</span></td>
              <td>{log.get('action','')}</td>
              <td class="log-output">{log.get('output_summary','')[:150]}</td>
              <td><span class="status-{status_class}">{log.get('status','')}</span></td>
            </tr>"""

        # Poker planning table
        poker_rows = ""
        for p in poker_results:
            votes_str = " | ".join([f"{v['agent'].split('(')[0].strip()}: {v['vote']}" for v in p.get("votes", [])])
            poker_rows += f"""
            <tr>
              <td>{p.get('story_id','')}</td>
              <td>{p.get('story_title','')[:60]}</td>
              <td>{votes_str}</td>
              <td>{p.get('average', '')}</td>
              <td><strong>{p.get('final_points','')}</strong></td>
            </tr>"""

        # OWASP table
        owasp_rows = ""
        for check in security_result.get("owasp_checks", []):
            status = check.get("status", "PASSED")
            color = "#16a34a" if status == "PASSED" else "#dc2626" if status == "FAILED" else "#d97706"
            owasp_rows += f"""
            <tr>
              <td>{check.get('category','')}</td>
              <td style="color:{color};font-weight:600;">{status}</td>
              <td>{check.get('severity','')}</td>
              <td>{', '.join(check.get('findings', [])) or '—'}</td>
            </tr>"""

        # Performance scenarios
        perf_rows = ""
        for scenario in perf_result.get("test_scenarios", []):
            res = scenario.get("results", {})
            status = res.get("status", "PASSED")
            color = "#16a34a" if status == "PASSED" else "#dc2626" if status == "FAILED" else "#d97706"
            perf_rows += f"""
            <tr>
              <td>{scenario.get('name','')}</td>
              <td>{scenario.get('concurrent_users','')}</td>
              <td>{res.get('requests_per_second','')}</td>
              <td>{res.get('avg_response_ms','')} ms</td>
              <td>{res.get('p95_response_ms','')} ms</td>
              <td>{res.get('error_rate_percent','')}%</td>
              <td style="color:{color};font-weight:600;">{status}</td>
            </tr>"""

        overall_status = "✅ GO — PENDING SENIOR APPROVAL" if go_decision == "GO" else "❌ NO-GO — REMEDIATION REQUIRED"
        overall_color = "#16a34a" if go_decision == "GO" else "#dc2626"

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Dev Team Report — {project_name}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: 'Inter', -apple-system, sans-serif; background: #0f172a; color: #e2e8f0; line-height: 1.6; }}
  .header {{ background: linear-gradient(135deg, #1e40af, #7c3aed); padding: 40px; }}
  .header h1 {{ font-size: 2rem; font-weight: 700; }}
  .header .meta {{ opacity: 0.8; margin-top: 8px; }}
  .container {{ max-width: 1400px; margin: 0 auto; padding: 32px; }}
  .section {{ background: #1e293b; border-radius: 12px; padding: 24px; margin-bottom: 24px; border: 1px solid #334155; }}
  .section h2 {{ font-size: 1.3rem; font-weight: 600; margin-bottom: 16px; color: #93c5fd; border-bottom: 1px solid #334155; padding-bottom: 12px; }}
  .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin-bottom: 24px; }}
  .stat-card {{ background: #0f172a; border-radius: 10px; padding: 20px; text-align: center; border: 1px solid #334155; }}
  .stat-card .value {{ font-size: 2rem; font-weight: 700; color: #60a5fa; }}
  .stat-card .label {{ font-size: 0.85rem; color: #94a3b8; margin-top: 4px; }}
  .overall-status {{ background: #0f172a; border-radius: 10px; padding: 20px; text-align: center; border: 2px solid {overall_color}; margin-bottom: 24px; }}
  .overall-status .value {{ font-size: 1.4rem; font-weight: 700; color: {overall_color}; }}
  .sprint-card {{ background: #0f172a; border-radius: 8px; margin-bottom: 16px; border: 1px solid #334155; overflow: hidden; }}
  .sprint-header {{ background: #1e40af; padding: 12px 16px; font-weight: 600; display: flex; justify-content: space-between; }}
  .sprint-meta {{ opacity: 0.8; font-size: 0.85rem; }}
  .sprint-body {{ padding: 16px; }}
  .story-item {{ padding: 6px 0; border-bottom: 1px solid #1e293b; font-size: 0.9rem; }}
  .badge {{ background: #1d4ed8; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; margin-right: 8px; }}
  .agent-tag {{ background: #6d28d9; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; float: right; }}
  .review-info {{ margin-top: 12px; padding: 8px; background: #1e293b; border-radius: 6px; font-size: 0.85rem; color: #94a3b8; }}
  .agent-badge {{ background: #0f766e; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; white-space: nowrap; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 0.88rem; }}
  th {{ background: #0f172a; padding: 10px 12px; text-align: left; color: #94a3b8; font-weight: 500; border-bottom: 2px solid #334155; }}
  td {{ padding: 10px 12px; border-bottom: 1px solid #1e293b; vertical-align: top; }}
  tr:hover td {{ background: #0f172a55; }}
  .log-output {{ color: #94a3b8; font-size: 0.82rem; max-width: 300px; }}
  .status-success {{ color: #4ade80; }}
  .status-error {{ color: #f87171; }}
  .score-circle {{ display: inline-block; width: 60px; height: 60px; border-radius: 50%; line-height: 60px; text-align: center; font-weight: 700; font-size: 1.1rem; }}
  .pass {{ background: #14532d; color: #4ade80; border: 2px solid #16a34a; }}
  .fail {{ background: #450a0a; color: #f87171; border: 2px solid #dc2626; }}
</style>
</head>
<body>
<div class="header">
  <h1>🤖 AI Dev Team — Execution Report</h1>
  <div class="meta">Project: <strong>{project_name}</strong> &nbsp;·&nbsp; ID: {project_id} &nbsp;·&nbsp; Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}</div>
</div>
<div class="container">

  <div class="overall-status">
    <div class="label" style="color:#94a3b8;margin-bottom:8px;">OVERALL PROJECT STATUS</div>
    <div class="value">{overall_status}</div>
  </div>

  <div class="stats-grid">
    <div class="stat-card"><div class="value">{len(backlog.get('epics',[]))}</div><div class="label">Epics</div></div>
    <div class="stat-card"><div class="value">{total_stories}</div><div class="label">Stories Completed</div></div>
    <div class="stat-card"><div class="value">{len(sprint_results)}</div><div class="label">Sprints</div></div>
    <div class="stat-card"><div class="value">{total_files}</div><div class="label">Files Generated</div></div>
    <div class="stat-card"><div class="value" style="color:{'#4ade80' if rtm_coverage >= 80 else '#f87171'};">{rtm_coverage}%</div><div class="label">Req. Coverage</div></div>
    <div class="stat-card"><div class="value">{security_score}</div><div class="label">Security Score</div></div>
    <div class="stat-card"><div class="value">{perf_score}</div><div class="label">Performance Score</div></div>
    <div class="stat-card"><div class="value" style="color:{go_color};">{go_decision}</div><div class="label">CTO Decision</div></div>
    <div class="stat-card"><div class="value">{len(agent_logs)}</div><div class="label">Agent Actions</div></div>
    <div class="stat-card"><div class="value">{sum(r.get('final_points',0) for r in poker_results)}</div><div class="label">Story Points</div></div>
  </div>

  <div class="section">
    <h2>📋 Requirements & Backlog</h2>
    <p style="color:#94a3b8;margin-bottom:16px;">{backlog.get('project_summary','')}</p>
    {"".join([f'<div style="margin-bottom:12px;"><strong style="color:#60a5fa;">{e.get("id")}: {e.get("title")}</strong> — {len(e.get("user_stories",[]))} stories<br/><span style="color:#94a3b8;font-size:0.9rem;">{e.get("description","")[:200]}</span></div>' for e in backlog.get('epics',[])])}
  </div>

  <div class="section">
    <h2>🏗️ Architecture</h2>
    <div class="stats-grid" style="margin-bottom:16px;">
      <div class="stat-card"><div class="value" style="font-size:1rem;">{architecture.get('architecture_pattern','')}</div><div class="label">Pattern</div></div>
      <div class="stat-card"><div class="value">{len(architecture.get('modules',[]))}</div><div class="label">Modules</div></div>
    </div>
    {"".join([f'<div style="margin-bottom:8px;padding:10px;background:#0f172a;border-radius:6px;"><strong style="color:#60a5fa;">{m.get("id")}: {m.get("name")}</strong> <span style="color:#94a3b8;font-size:0.85rem;">→ {m.get("assigned_to","")}</span><br/><span style="font-size:0.88rem;">{m.get("description","")[:200]}</span></div>' for m in architecture.get('modules',[])])}
  </div>

  <div class="section">
    <h2>🃏 Poker Planning</h2>
    <table>
      <tr><th>Story ID</th><th>Title</th><th>Agent Votes</th><th>Average</th><th>Final Points</th></tr>
      {poker_rows}
    </table>
  </div>

  <div class="section">
    <h2>🏃 Sprint Execution</h2>
    {sprint_cards}
  </div>

  <div class="section">
    <h2>🔐 Security Testing (OWASP Top 10)</h2>
    <div style="margin-bottom:16px;">
      <span class="score-circle {'pass' if security_status=='PASSED' else 'fail'}">{security_score}</span>
      <span style="margin-left:16px;font-size:1.1rem;font-weight:600;color:{'#4ade80' if security_status=='PASSED' else '#f87171'};">{security_status}</span>
    </div>
    <table>
      <tr><th>OWASP Category</th><th>Status</th><th>Severity</th><th>Findings</th></tr>
      {owasp_rows}
    </table>
    {"<div style='margin-top:16px;'><strong>Recommendations:</strong><ul>" + "".join([f"<li style='color:#94a3b8;margin:4px 0;'>{r}</li>" for r in security_result.get('recommendations',[])]) + "</ul></div>" if security_result.get('recommendations') else ""}
  </div>

  <div class="section">
    <h2>⚡ Performance Testing</h2>
    <div style="margin-bottom:16px;">
      <span class="score-circle {'pass' if perf_status=='PASSED' else 'fail'}">{perf_score}</span>
      <span style="margin-left:16px;font-size:1.1rem;font-weight:600;color:{'#4ade80' if perf_status=='PASSED' else '#f87171'};">{perf_status}</span>
    </div>
    <table>
      <tr><th>Scenario</th><th>Users</th><th>RPS</th><th>Avg</th><th>P95</th><th>Error Rate</th><th>Status</th></tr>
      {perf_rows}
    </table>
    {"<div style='margin-top:16px;'><strong>Bottlenecks & Recommendations:</strong><ul>" + "".join([f"<li style='color:#94a3b8;margin:4px 0;'>{r}</li>" for r in perf_result.get('recommendations',[])]) + "</ul></div>" if perf_result.get('recommendations') else ""}
  </div>

  <div class="section">
    <h2>🎯 CTO Go/No-Go Decision</h2>
    <div style="display:flex;align-items:center;gap:24px;margin-bottom:20px;padding:20px;background:#0f172a;border-radius:10px;border:2px solid {go_color};">
      <div style="font-size:3rem;font-weight:900;color:{go_color};">{go_decision}</div>
      <div>
        <div style="font-size:1.1rem;font-weight:600;color:#e2e8f0;">Confidence: {go_confidence}%</div>
        <div style="color:#94a3b8;margin-top:4px;font-size:0.9rem;">{go_no_go.get('cto_sign_off','')}</div>
      </div>
    </div>
    {"<div style='margin-bottom:12px;'><strong style='color:#f87171;'>Blocking Issues:</strong><ul>" + "".join([f"<li style='color:#f87171;margin:4px 0;'>{i}</li>" for i in go_no_go.get('blocking_issues',[])]) + "</ul></div>" if go_no_go.get('blocking_issues') else ""}
    {"<div style='margin-bottom:12px;'><strong style='color:#fbbf24;'>Warnings:</strong><ul>" + "".join([f"<li style='color:#fbbf24;margin:4px 0;'>{w}</li>" for w in go_no_go.get('warnings',[])]) + "</ul></div>" if go_no_go.get('warnings') else ""}
    <table>
      <tr><th>Quality Gate</th><th>Threshold</th><th>Actual</th><th>Result</th></tr>
      {gate_rows}
    </table>
  </div>

  <div class="section">
    <h2>📋 Requirements Traceability Matrix (RTM)</h2>
    <div style="display:flex;gap:16px;margin-bottom:16px;">
      <div class="stat-card" style="flex:1;"><div class="value" style="color:{'#4ade80' if rtm_coverage>=80 else '#f87171'};">{rtm_coverage}%</div><div class="label">Coverage</div></div>
      <div class="stat-card" style="flex:1;"><div class="value">{rtm.get('covered',0)}/{rtm.get('total_requirements',0)}</div><div class="label">Stories Covered</div></div>
      <div class="stat-card" style="flex:1;"><div class="value" style="color:{'#4ade80' if rtm.get('missing_count',0)==0 else '#f87171'};">{rtm.get('missing_count',0)}</div><div class="label">Missing</div></div>
      <div class="stat-card" style="flex:1;"><div class="value" style="font-size:1rem;color:{'#4ade80' if rtm_status=='COMPLETE' else '#fbbf24' if rtm_status=='ACCEPTABLE' else '#f87171'};">{rtm_status}</div><div class="label">RTM Status</div></div>
    </div>
    <table>
      <tr><th>ID</th><th>Requirement</th><th>Epic</th><th>Priority</th><th>AC Count</th><th>Status</th></tr>
      {rtm_rows}
    </table>
  </div>

  <div class="section">
    <h2>✅ UAT Checklist — Manual Verification</h2>
    <p style="color:#94a3b8;margin-bottom:16px;font-size:0.9rem;">
      {uat_checklist.get('total_test_cases',0)} test cases to verify. Mark each PASS/FAIL after manual testing. All must pass before production go-live.
    </p>
    <table>
      <tr><th>Story</th><th>Title</th><th>Test Steps (Acceptance Criteria)</th><th>UAT Status</th></tr>
      {uat_rows}
    </table>
  </div>

  {"<div class='section'><h2>🔍 CTO Kickoff Review</h2><p style='color:#94a3b8;margin-bottom:12px;font-style:italic;'>" + kickoff.get('cto_message','') + "</p>" + (f"<div style='margin-bottom:12px;'><strong>Concerns:</strong>{concerns_html}</div>" if concerns_html else "") + (f"<div><strong>Risks:</strong>{risks_html}</div>" if risks_html else "") + "</div>" if kickoff else ""}

  <div class="section">
    <h2>📊 Agent Action Log</h2>
    <table>
      <tr><th>Timestamp</th><th>Agent</th><th>Action</th><th>Output Summary</th><th>Status</th></tr>
      {log_rows}
    </table>
  </div>

  <div class="section" style="text-align:center;">
    <h2>🚀 Deployment Status</h2>
    <p style="color:#94a3b8;margin:16px 0;">Application is currently running on <strong>localhost / Dev environment</strong>.</p>
    <p style="color:#94a3b8;">{"Senior management approval via email has been requested. Production deployment will proceed after CTO sign-off and management approval." if go_decision=='GO' else "CTO has issued NO-GO. Resolve blocking issues and re-run the pipeline."}</p>
  </div>

</div>
</body>
</html>"""
