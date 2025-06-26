from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from .models import Email, EmailAccount, EmailAttachment
from .email_utils import fetch_emails, save_emails_to_db
import mimetypes

def inbox_view(request):
    """Display inbox with all emails"""
    # Get or create default email account
    account, created = EmailAccount.objects.get_or_create(
        email="your_email@gmail.com",
        defaults={
            'name': 'Default Account',
            'password': 'your_app_password',  # Use App Password for Gmail
            'imap_server': 'imap.gmail.com',
            'imap_port': 993
        }
    )
    
    # Get all emails
    emails = Email.objects.filter(account=account).order_by('-date_received')
    
    # Pagination
    paginator = Paginator(emails, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'emails': page_obj,
        'account': account,
        'total_emails': emails.count()
    }
    
    return render(request, 'inboxapp/inbox.html', context)

def email_detail_view(request, email_id):
    """Display detailed view of a single email"""
    email_obj = get_object_or_404(Email, id=email_id)
    
    # Mark as read
    if not email_obj.is_read:
        email_obj.is_read = True
        email_obj.save()
    
    context = {
        'email': email_obj,
        'attachments': email_obj.attachments.all()
    }
    
    return render(request, 'inboxapp/email_detail.html', context)

def fetch_new_emails(request):
    """Fetch new emails from server"""
    if request.method == 'POST':
        try:
            account = EmailAccount.objects.first()
            if not account:
                messages.error(request, 'No email account configured')
                return redirect('inbox')
            
            # Fetch emails
            emails_data = fetch_emails(
                account.email, 
                account.password, 
                account.imap_server, 
                account.imap_port
            )
            
            # Save to database
            saved_count = save_emails_to_db(emails_data, account)
            
            messages.success(request, f'Fetched {saved_count} new emails')
            
        except Exception as e:
            messages.error(request, f'Error fetching emails: {str(e)}')
    
    return redirect('inbox')

def download_attachment(request, attachment_id):
    """Download email attachment"""
    attachment = get_object_or_404(EmailAttachment, id=attachment_id)
    
    try:
        response = HttpResponse(
            attachment.file_path.read(),
            content_type=attachment.content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{attachment.filename}"'
        return response
    except Exception as e:
        messages.error(request, f'Error downloading attachment: {str(e)}')
        return redirect('email_detail', email_id=attachment.email.id)

def search_emails(request):
    """Search emails"""
    query = request.GET.get('q', '')
    account = EmailAccount.objects.first()
    
    if query and account:
        emails = Email.objects.filter(
            account=account
        ).filter(
            subject__icontains=query
        ) | Email.objects.filter(
            account=account
        ).filter(
            sender__icontains=query
        ) | Email.objects.filter(
            account=account
        ).filter(
            body_text__icontains=query
        )
        emails = emails.order_by('-date_received')
    else:
        emails = Email.objects.none()
    
    # Pagination
    paginator = Paginator(emails, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'emails': page_obj,
        'query': query,
        'total_emails': emails.count()
    }
    
    return render(request, 'inboxapp/search_results.html', context)
