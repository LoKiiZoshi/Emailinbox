from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone

class EmailAccount(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=255)
    imap_server = models.CharField(max_length=100, default='imap.gmail.com')
    imap_port = models.IntegerField(default=993)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.email})"

class Email(models.Model):
    account = models.ForeignKey(EmailAccount, on_delete=models.CASCADE)
    subject = models.CharField(max_length=500)
    sender = models.EmailField()
    sender_name = models.CharField(max_length=200, blank=True)
    recipient = models.EmailField()
    date_received = models.DateTimeField()
    body_text = models.TextField(blank=True)
    body_html = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    message_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_received']

    def __str__(self):
        return f"{self.subject} - {self.sender}"

class EmailAttachment(models.Model):
    email = models.ForeignKey(Email, related_name='attachments', on_delete=models.CASCADE)
    filename = models.CharField(max_length=255)
    file_path = models.FileField(upload_to='attachments/')
    file_size = models.IntegerField()
    content_type = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.filename} - {self.email.subject}"

    @property
    def is_image(self):
        return self.content_type.startswith('image/')

    @property
    def is_pdf(self):
        return self.content_type == 'application/pdf'
