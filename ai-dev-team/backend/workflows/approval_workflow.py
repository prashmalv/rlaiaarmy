import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from config.settings import settings
from datetime import datetime

def send_approval_email(project_name: str, project_id: str, report_path: str,
                        security_score: int, perf_score: int, total_stories: int) -> bool:
    """Send approval request email to senior management."""
    if not settings.SMTP_USER or not settings.APPROVAL_EMAIL:
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"[APPROVAL REQUIRED] {project_name} - Ready for Production"
    msg["From"] = settings.SMTP_USER
    msg["To"] = settings.APPROVAL_EMAIL

    approval_link = f"http://localhost:3000/projects/{project_id}/approve"
    reject_link = f"http://localhost:3000/projects/{project_id}/reject"

    html = f"""
    <html><body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <div style="background: #1e293b; color: white; padding: 20px; border-radius: 8px 8px 0 0;">
      <h2>🚀 Production Deployment Approval Required</h2>
      <p>Project: <strong>{project_name}</strong></p>
      <p>Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}</p>
    </div>
    <div style="background: #f8fafc; padding: 20px; border: 1px solid #e2e8f0;">
      <h3>Build Summary</h3>
      <table style="width:100%; border-collapse: collapse;">
        <tr><td style="padding:8px; border-bottom:1px solid #e2e8f0;"><strong>Total Stories Completed</strong></td><td style="padding:8px;">{total_stories}</td></tr>
        <tr><td style="padding:8px; border-bottom:1px solid #e2e8f0;"><strong>Security Score</strong></td><td style="padding:8px; color:{'green' if security_score >= 80 else 'red'};">{security_score}/100 ✅</td></tr>
        <tr><td style="padding:8px; border-bottom:1px solid #e2e8f0;"><strong>Performance Score</strong></td><td style="padding:8px; color:{'green' if perf_score >= 80 else 'red'};">{perf_score}/100 ✅</td></tr>
        <tr><td style="padding:8px;"><strong>Current Environment</strong></td><td style="padding:8px;">localhost / Dev</td></tr>
      </table>
      <br/>
      <p>The AI Dev Team has completed development and all automated tests have passed.
      Please review the attached report and approve or reject production deployment.</p>
      <br/>
      <div style="text-align:center;">
        <a href="{approval_link}" style="background:#16a34a;color:white;padding:12px 24px;border-radius:6px;text-decoration:none;margin-right:16px;">✅ APPROVE PRODUCTION</a>
        <a href="{reject_link}" style="background:#dc2626;color:white;padding:12px 24px;border-radius:6px;text-decoration:none;">❌ REJECT</a>
      </div>
      <br/>
      <p style="color:#64748b;font-size:12px;">Note: Until approved, the application is running on localhost/dev environment only.</p>
    </div>
    </body></html>
    """

    msg.attach(MIMEText(html, "html"))

    # Attach report if exists
    if os.path.exists(report_path):
        with open(report_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename=report_{project_id}.html")
            msg.attach(part)

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_USER, settings.APPROVAL_EMAIL, msg.as_string())
        return True
    except Exception as e:
        print(f"Email send failed: {e}")
        return False
