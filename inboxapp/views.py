import imaplib
import email
from email.header import decode_header
from django.shortcuts import render
from .models import Email  # optional, only if saving to DB

# Email credentials
EMAIL_USER = "lokendarjoshi384@gmail.com"
EMAIL_PASS = "csph rizi xyhz loly"
IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993

def fetch_emails():
    """Fetch emails from Gmail using IMAP and return a list of dicts."""
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_USER, EMAIL_PASS)
    mail.select("inbox")

    status, messages = mail.search(None, "ALL")
    email_ids = messages[0].split()

    fetched_emails = []

    for num in email_ids[-20:][::-1]:  # fetch last 20 emails
        status, data = mail.fetch(num, "(RFC822)")
        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)

        subject, encoding = decode_header(msg["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding or "utf-8", errors="ignore")

        from_ = msg.get("From")
        date = msg.get("Date")

        fetched_emails.append({
            "subject": subject,
            "from": from_,
            "date": date,
        })

    mail.logout()
    return fetched_emails

def inbox_view(request):
    """View to render inbox.html with fetched email data"""
    emails = fetch_emails()
    return render(request, "inboxapp/inbox.html", {"emails": emails})
