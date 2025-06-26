import imaplib
import email
import os
from email.header import decode_header
from django.core.files.base import ContentFile
from django.conf import settings
from .models import Email, EmailAttachment, EmailAccount
from datetime import datetime
import re

def clean_filename(filename):
    """Clean filename for safe storage"""
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def decode_mime_words(s):
    """Decode MIME encoded words"""
    if s is None:
        return ""
    decoded_parts = decode_header(s)
    decoded_string = ""
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            decoded_string += part.decode(encoding or 'utf-8', errors='ignore')
        else:
            decoded_string += part
    return decoded_string

def fetch_emails(username, password, imap_server='imap.gmail.com', imap_port=993):
    """Fetch emails from IMAP server"""
    try:
        # Connect to IMAP server
        mail = imaplib.IMAP4_SSL(imap_server, imap_port)
        mail.login(username, password)
        mail.select('inbox')

        # Search for all emails
        status, messages = mail.search(None, 'ALL')
        email_ids = messages[0].split()

        # Get the last 20 emails
        recent_emails = email_ids[-20:] if len(email_ids) > 20 else email_ids
        
        emails_data = []
        
        for email_id in reversed(recent_emails):  # Most recent first
            status, msg_data = mail.fetch(email_id, '(RFC822)')
            
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    # Extract email details
                    subject = decode_mime_words(msg.get("Subject", "No Subject"))
                    sender = decode_mime_words(msg.get("From", "Unknown"))
                    recipient = decode_mime_words(msg.get("To", "Unknown"))
                    date_str = msg.get("Date", "")
                    message_id = msg.get("Message-ID", f"unknown_{email_id.decode()}")
                    
                    # Parse date
                    try:
                        date_received = email.utils.parsedate_to_datetime(date_str)
                    except:
                        date_received = datetime.now()
                    
                    # Extract sender name and email
                    sender_name = ""
                    sender_email = sender
                    if '<' in sender and '>' in sender:
                        sender_name = sender.split('<')[0].strip().strip('"')
                        sender_email = sender.split('<')[1].split('>')[0]
                    
                    # Get email body
                    body_text = ""
                    body_html = ""
                    attachments = []
                    
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))
                            
                            if "attachment" in content_disposition:
                                # Handle attachments
                                filename = part.get_filename()
                                if filename:
                                    filename = decode_mime_words(filename)
                                    filename = clean_filename(filename)
                                    
                                    attachment_data = {
                                        'filename': filename,
                                        'content': part.get_payload(decode=True),
                                        'content_type': content_type,
                                        'size': len(part.get_payload(decode=True))
                                    }
                                    attachments.append(attachment_data)
                            
                            elif content_type == "text/plain" and "attachment" not in content_disposition:
                                body_text = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                            elif content_type == "text/html" and "attachment" not in content_disposition:
                                body_html = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    else:
                        # Single part message
                        content_type = msg.get_content_type()
                        if content_type == "text/plain":
                            body_text = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                        elif content_type == "text/html":
                            body_html = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                    
                    email_data = {
                        'subject': subject,
                        'sender': sender_email,
                        'sender_name': sender_name,
                        'recipient': recipient,
                        'date_received': date_received,
                        'body_text': body_text,
                        'body_html': body_html,
                        'message_id': message_id,
                        'attachments': attachments
                    }
                    
                    emails_data.append(email_data)
        
        mail.close()
        mail.logout()
        
        return emails_data
        
    except Exception as e:
        print(f"Error fetching emails: {str(e)}")
        return []

def save_emails_to_db(emails_data, account):
    """Save fetched emails to database"""
    saved_count = 0
    
    for email_data in emails_data:
        # Check if email already exists
        if not Email.objects.filter(message_id=email_data['message_id']).exists():
            # Create email record
            email_obj = Email.objects.create(
                account=account,
                subject=email_data['subject'],
                sender=email_data['sender'],
                sender_name=email_data['sender_name'],
                recipient=email_data['recipient'],
                date_received=email_data['date_received'],
                body_text=email_data['body_text'],
                body_html=email_data['body_html'],
                message_id=email_data['message_id']
            )
            
            # Save attachments
            for attachment_data in email_data['attachments']:
                file_content = ContentFile(attachment_data['content'])
                
                attachment = EmailAttachment(
                    email=email_obj,
                    filename=attachment_data['filename'],
                    file_size=attachment_data['size'],
                    content_type=attachment_data['content_type']
                )
                
                attachment.file_path.save(
                    attachment_data['filename'],
                    file_content,
                    save=True
                )
            
            saved_count += 1
    
    return saved_count
