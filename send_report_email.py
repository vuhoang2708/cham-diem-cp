"""
Send execution report email via Gmail SMTP.
Usage: python send_report_email.py

Prerequisites:
  1. Enable 2-Step Verification on your Google Account
  2. Generate an App Password:
     - Go to: https://myaccount.google.com/apppasswords
     - Select app: "Mail", device: "Windows Computer"
     - Copy the 16-character password
  3. Fill in GMAIL_APP_PASSWORD below
"""

import smtplib
import os
import glob
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

# ---- CONFIGURATION ----
SENDER_EMAIL    = "vuhoang2708@gmail.com"
RECIPIENT_EMAIL = "vuhoang2708@gmail.com"
GMAIL_APP_PASSWORD = ""   # <-- FILL IN YOUR APP PASSWORD HERE (16 chars, no spaces)

PROJECT_DIR = r"c:\Users\Nguyen To Dung\.gemini\antigravity\scratch\Cham diem co phieu"


def collect_logs():
    """Collect all phase log files."""
    log_files = []
    patterns = [
        "AGENT_PHASE_*_LOG.txt",
        "AGENT_PHASE_*_CHECKLIST.txt",
        "AGENT_FINAL_SUMMARY.txt",
    ]
    for pattern in patterns:
        found = glob.glob(os.path.join(PROJECT_DIR, pattern))
        log_files.extend(sorted(found))
    return log_files


def read_file_safe(path):
    """Read file content safely."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"[Error reading file: {e}]"


def build_email_body(log_files):
    """Build email body from log files."""
    lines = []
    lines.append("=" * 70)
    lines.append("ANTIGRAVITY — AmiBroker Connector Implementation Report")
    lines.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Project: VN100 Stock Scoring Dashboard")
    lines.append("=" * 70)
    lines.append("")

    # Try to read final summary first
    summary_path = os.path.join(PROJECT_DIR, "AGENT_FINAL_SUMMARY.txt")
    if os.path.exists(summary_path):
        lines.append(">>> FINAL SUMMARY <<<")
        lines.append(read_file_safe(summary_path))
        lines.append("")

    # Append each phase log
    for log_path in log_files:
        if "FINAL_SUMMARY" in log_path:
            continue  # Already included above
        filename = os.path.basename(log_path)
        lines.append(f">>> {filename} <<<")
        lines.append(read_file_safe(log_path))
        lines.append("")

    if not log_files and not os.path.exists(summary_path):
        lines.append("[WARNING] No log files found. Agent may not have completed yet.")

    return "\n".join(lines)


def send_email():
    if not GMAIL_APP_PASSWORD:
        print("[ERROR] GMAIL_APP_PASSWORD is empty.")
        print("Please fill in the App Password in this script and run again.")
        print("")
        print("How to get App Password:")
        print("  1. Go to: https://myaccount.google.com/apppasswords")
        print("  2. Sign in with vuhoang2708@gmail.com")
        print("  3. Select app: Mail, device: Windows Computer")
        print("  4. Click Generate")
        print("  5. Copy the 16-character password (e.g. abcd efgh ijkl mnop)")
        print("  6. Paste it into GMAIL_APP_PASSWORD in this file (remove spaces)")
        return False

    log_files = collect_logs()
    body = build_email_body(log_files)

    # Build email
    msg = MIMEMultipart()
    msg["From"]    = SENDER_EMAIL
    msg["To"]      = RECIPIENT_EMAIL
    msg["Subject"] = f"[Antigravity] AmiBroker Implementation Report — {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    msg.attach(MIMEText(body, "plain", "utf-8"))

    # Attach log files
    for log_path in log_files:
        try:
            with open(log_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename={os.path.basename(log_path)}"
            )
            msg.attach(part)
        except Exception as e:
            print(f"[WARN] Could not attach {log_path}: {e}")

    # Send
    try:
        print(f"[INFO] Connecting to Gmail SMTP...")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, GMAIL_APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
        print(f"[OK] Email sent to {RECIPIENT_EMAIL}")
        print(f"     Subject: {msg['Subject']}")
        print(f"     Attachments: {len(log_files)} log files")
        return True
    except smtplib.SMTPAuthenticationError:
        print("[ERROR] Authentication failed.")
        print("  -> Check that GMAIL_APP_PASSWORD is correct (16 chars, no spaces)")
        print("  -> Make sure 2-Step Verification is enabled on your Google Account")
        return False
    except Exception as e:
        print(f"[ERROR] Failed to send email: {e}")
        return False


if __name__ == "__main__":
    send_email()
