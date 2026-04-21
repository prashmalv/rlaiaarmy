import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Dict
from config.settings import settings

def send_email(to_email: str, to_name: str, subject: str, html_body: str,
               text_body: str = None) -> Dict:
    """Send a single email via SMTP."""
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        return {"status": "dry_run", "message": f"SMTP not configured — email queued for {to_email}", "subject": subject}

    # Replace personalization tokens
    html = html_body.replace("{{name}}", to_name).replace("{{company}}", "")
    text = (text_body or "").replace("{{name}}", to_name)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{settings.FROM_NAME} <{settings.SMTP_USER}>"
    msg["To"] = to_email

    if text:
        msg.attach(MIMEText(text, "plain"))
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_USER, to_email, msg.as_string())
        return {"status": "sent", "to": to_email, "subject": subject}
    except Exception as e:
        return {"status": "error", "message": str(e), "to": to_email}


def send_bulk_emails(leads: List[Dict], subject: str, html_body: str) -> List[Dict]:
    """Send personalized emails to a list of leads."""
    results = []
    for lead in leads:
        result = send_email(
            to_email=lead.get("email", ""),
            to_name=lead.get("name", "there"),
            subject=subject,
            html_body=html_body,
        )
        results.append({**result, "lead_id": lead.get("id"), "lead_name": lead.get("name")})
    return results
