import os
import smtplib
from email.mime.text import MIMEText

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
ALERT_TO = os.getenv("ALERT_TO")

def send_failure_alert(subject: str, body: str) -> bool:
    if not (SMTP_HOST and SMTP_PORT and SMTP_USER and SMTP_PASS and ALERT_TO):
        print("[alerts] SMTP/Gmail not configured; skipping email.")
        return False

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = ALERT_TO

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, [ALERT_TO], msg.as_string())
        print(f"[alerts] Email sent to {ALERT_TO}")
        return True
    except Exception as e:
        print(f"[alerts] Error sending email: {e}")
        return False
