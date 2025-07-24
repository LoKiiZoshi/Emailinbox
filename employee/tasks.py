from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import Task, TaskSchedule, EmailLog, TaskStatusChoices, TaskFrequencyChoices
from users.models import User

@shared_task
def send_task_assignment_email(task_id):
    try:
        task = Task.objects.get(id=task_id)
        subject = f"New Task Assigned: {task.title}"
        message = f"""
        Hello {task.assigned_to.get_full_name()},
        
        You have been assigned a new task:
        
        Title: {task.title}
        Description: {task.description}
        Priority: {task.get_priority_display()}
        Due Date: {task.due_date.strftime('%Y-%m-%d %H:%M')}
        Assigned by: {task.assigned_by.get_full_name()}
        
        Please log in to the system to view more details.
        
        Best regards,
        Task Management System
        """
        
        email_log = EmailLog.objects.create(
            recipient=task.assigned_to,
            subject=subject,
            message=message,
            task=task,
            company=task.company
        )
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [task.assigned_to.email],
            fail_silently=False,
        )
        
        email_log.sent_successfully = True
        email_log.save()
        
    except Task.DoesNotExist:
        pass
    except Exception as e:
        if 'email_log' in locals():
            email_log.error_message = str(e)
            email_log.save()

@shared_task
def send_task_reminder_email(task_id):
    try:
        task = Task.objects.get(id=task_id)
        if task.status not in [TaskStatusChoices.COMPLETED, TaskStatusChoices.CANCELLED]:
            subject = f"Task Reminder: {task.title}"
            message = f"""
            Hello {task.assigned_to.get_full_name()},
            
            This is a reminder for your pending task:
            
            Title: {task.title}
            Due Date: {task.due_date.strftime('%Y-%m-%d %H:%M')}
            Priority: {task.get_priority_display()}
            
            Please complete this task as soon as possible.
            
            Best regards,
            Task Management System
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [task.assigned_to.email],
                fail_silently=False,
            )
            
    except Task.DoesNotExist:
        pass
