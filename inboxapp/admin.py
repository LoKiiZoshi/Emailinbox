from django.contrib import admin
from .models import EmailAccount, Email, EmailAttachment

@admin.register(EmailAccount)
class EmailAccountAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'imap_server', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'email']

class EmailAttachmentInline(admin.TabularInline):
    model = EmailAttachment
    extra = 0
    readonly_fields = ['filename', 'file_size', 'content_type', 'created_at']

@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ['subject', 'sender', 'sender_name', 'date_received', 'is_read']
    list_filter = ['is_read', 'date_received', 'account']
    search_fields = ['subject', 'sender', 'sender_name', 'body_text']
    readonly_fields = ['message_id', 'created_at']
    inlines = [EmailAttachmentInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('account')

@admin.register(EmailAttachment)
class EmailAttachmentAdmin(admin.ModelAdmin):
    list_display = ['filename', 'email', 'file_size', 'content_type', 'created_at']
    list_filter = ['content_type', 'created_at']
    search_fields = ['filename', 'email__subject']
    readonly_fields = ['created_at']
