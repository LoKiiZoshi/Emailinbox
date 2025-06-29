import imaplib
import email
from email.header import decode_header
import datetime
import re
import math
import random
import logging
from collections import Counter
from .models import Email, EmailAccount, EmailAttachment
from django.utils import timezone
from bs4 import BeautifulSoup
import base64

logger = logging.getLogger(__name__)

def connect_to_email_server(email_account):
    try:
        mail = imaplib.IMAP4_SSL(email_account.imap_server)
        mail.login(email_account.email, email_account.password)
        mail.select("inbox")
        return mail
    except Exception as e:
        logger.error(f"IMAP Connection failed: {e}")
        return None

def decode_mime_words(s):
    decoded_fragments = decode_header(s)
    return ''.join([
        fragment.decode(charset or 'utf-8') if isinstance(fragment, bytes) else fragment
        for fragment, charset in decoded_fragments
    ])

def clean_text(text):
    clean = re.sub(r'<[^>]+>', '', text)
    return re.sub(r'\s+', ' ', clean).strip()

def get_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            if ctype == "text/plain":
                return part.get_payload(decode=True).decode(errors="ignore")
            elif ctype == "text/html":
                html = part.get_payload(decode=True).decode(errors="ignore")
                soup = BeautifulSoup(html, "html.parser")
                return soup.get_text()
    else:
        return msg.get_payload(decode=True).decode(errors="ignore")

def fetch_emails(email_account, limit=20):
    mail = connect_to_email_server(email_account)
    if not mail:
        return []

    result, data = mail.search(None, "ALL")
    mail_ids = data[0].split()
    latest_ids = mail_ids[-limit:]
    fetched_emails = []

    for mail_id in reversed(latest_ids):
        result, data = mail.fetch(mail_id, "(RFC822)")
        if result != "OK":
            continue

        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)

        subject = decode_mime_words(msg.get("Subject", "No Subject"))
        from_email = decode_mime_words(msg.get("From", ""))
        to_email = decode_mime_words(msg.get("To", ""))
        date_str = msg.get("Date")
        date = parse_email_date(date_str)

        body = get_body(msg)
        text = clean_text(body)

        # Save to DB
        email_obj = Email(
            subject=subject,
            sender=from_email,
            receiver=to_email,
            body=text,
            received_at=date,
            account=email_account
        )
        email_obj.save()

        save_attachments(msg, email_obj)

        fetched_emails.append(email_obj)

    return fetched_emails

def parse_email_date(date_str):
    try:
        return datetime.datetime.strptime(date_str[:25], "%a, %d %b %Y %H:%M:%S")
    except Exception:
        return timezone.now()

def save_attachments(msg, email_obj):
    for part in msg.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        if part.get('Content-Disposition') is None:
            continue
        filename = part.get_filename()
        if filename:
            payload = part.get_payload(decode=True)
            attachment = EmailAttachment(
                email=email_obj,
                filename=filename,
                filedata=base64.b64encode(payload).decode()
            )
            attachment.save()

### ------------------------------
### 🔍 Math/Algo Based Utilities
### ------------------------------

def word_count(text):
    return len(re.findall(r'\w+', text))

def keyword_frequency(text, keywords):
    words = re.findall(r'\w+', text.lower())
    freq = Counter(words)
    score = sum(freq.get(k.lower(), 0) for k in keywords)
    return score

def cosine_similarity(vec1, vec2):
    dot = sum([vec1[i]*vec2[i] for i in range(len(vec1))])
    mag1 = math.sqrt(sum([i**2 for i in vec1]))
    mag2 = math.sqrt(sum([i**2 for i in vec2]))
    return dot / (mag1 * mag2 + 1e-5)

def compute_priority_score(email_obj):
    score = 0

    # 1. Word count score
    wc = word_count(email_obj.body)
    score += min(wc / 50, 5)

    # 2. Important sender weight
    important_senders = ['boss@company.com', 'hr@company.com']
    if any(s.lower() in email_obj.sender.lower() for s in important_senders):
        score += 5

    # 3. Subject keyword boost
    score += keyword_frequency(email_obj.subject, ['urgent', 'action', 'important']) * 2

    return min(score, 10)

def classify_email(email_obj):
    """Simple classifier for demonstration"""
    spam_keywords = ['win', 'free', 'offer', 'click']
    ham_keywords = ['meeting', 'schedule', 'project']

    spam_score = keyword_frequency(email_obj.body, spam_keywords)
    ham_score = keyword_frequency(email_obj.body, ham_keywords)

    if spam_score > ham_score:
        return 'spam'
    return 'important'

def rank_emails(email_list):
    scored = [(email, compute_priority_score(email)) for email in email_list]
    return sorted(scored, key=lambda x: x[1], reverse=True)

def generate_summary(email_obj):
    words = email_obj.body.split()
    summary = ' '.join(words[:30])
    return summary + ('...' if len(words) > 30 else '')

def extract_emails_from_text(text):
    return re.findall(r'[\w\.-]+@[\w\.-]+', text)

def extract_urls(text):
    return re.findall(r'(https?://\S+)', text)

def extract_phone_numbers(text):
    return re.findall(r'\+?\d[\d -]{8,}\d', text)

def is_weekend(date_obj):
    return date_obj.weekday() >= 5

def random_label():
    return random.choice(["info", "warning", "danger", "success"])

def is_internal_email(email_obj):
    domain = email_obj.sender.split('@')[-1]
    return domain.endswith("company.com")

def time_since_received(email_obj):
    delta = timezone.now() - email_obj.received_at
    return delta.total_seconds() / 3600  # in hours

def email_age_category(email_obj):
    hours = time_since_received(email_obj)
    if hours < 24:
        return 'new'
    elif hours < 72:
        return 'recent'
    else:
        return 'old'

def detect_language(text):
    if re.search(r'[\u0900-\u097F]', text):
        return 'nepali'
    return 'english'

def is_reply(subject):
    return subject.lower().startswith("re:")

def is_forward(subject):
    return subject.lower().startswith("fwd:")

def get_thread_subject(subject):
    return re.sub(r'^(Re:|Fwd:)\s*', '', subject, flags=re.IGNORECASE).strip()

