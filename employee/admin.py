from django.contrib import admin
from .models import (
    EmploymentDetail, Attendance, LeaveType, LeaveRequest, Payroll,
    PerformanceReview, TrainingProgram, EmployeeTraining, Project,
    ProjectAssignment, DisciplinaryAction, BenefitType, EmployeeBenefit,
    Task, TaskCategory, TaskComment, TaskSchedule, EmailLog
)

# Base admin class for company filtering
class CompanyFilteredAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if hasattr(request.user, 'company') and request.user.company:
            return qs.filter(company=request.user.company)
        return qs.none()

# Employee Management Admin
@admin.register(EmploymentDetail)
class EmploymentDetailAdmin(CompanyFilteredAdmin):
    list_display = ['user', 'employee_id', 'employment_type', 'status', 'hire_date', 'department']
    list_filter = ['employment_type', 'status', 'department']
    search_fields = ['user__first_name', 'user__last_name', 'employee_id']

@admin.register(Attendance)
class AttendanceAdmin(CompanyFilteredAdmin):
    list_display = ['user', 'date', 'check_in', 'check_out', 'status']
    list_filter = ['status', 'date']
    search_fields = ['user__first_name', 'user__last_name']

@admin.register(LeaveType)
class LeaveTypeAdmin(CompanyFilteredAdmin):
    list_display = ['name', 'max_days', 'company']
    search_fields = ['name']

@admin.register(LeaveRequest)
class LeaveRequestAdmin(CompanyFilteredAdmin):
    list_display = ['user', 'leave_type', 'start_date', 'end_date', 'status', 'approved_by']
    list_filter = ['status', 'leave_type']
    search_fields = ['user__first_name', 'user__last_name']

@admin.register(Payroll)
class PayrollAdmin(CompanyFilteredAdmin):
    list_display = ['user', 'month', 'basic_salary', 'net_salary', 'status', 'payment_date']
    list_filter = ['status', 'month']
    search_fields = ['user__first_name', 'user__last_name']

# Task Management Admin
@admin.register(TaskCategory)
class TaskCategoryAdmin(CompanyFilteredAdmin):
    list_display = ['name', 'color', 'company']
    search_fields = ['name']

@admin.register(Task)
class TaskAdmin(CompanyFilteredAdmin):
    list_display = ['title', 'assigned_to', 'assigned_by', 'priority', 'status', 'due_date']
    list_filter = ['priority', 'status', 'category']
    search_fields = ['title', 'assigned_to__first_name', 'assigned_to__last_name']
    date_hierarchy = 'due_date'

@admin.register(TaskComment)
class TaskCommentAdmin(CompanyFilteredAdmin):
    list_display = ['task', 'author', 'created_at']
    search_fields = ['task__title', 'author__first_name', 'author__last_name']

@admin.register(TaskSchedule)
class TaskScheduleAdmin(CompanyFilteredAdmin):
    list_display = ['task_template', 'assigned_to', 'frequency', 'is_active', 'start_date']
    list_filter = ['frequency', 'is_active', 'priority']
    search_fields = ['task_template', 'assigned_to__first_name', 'assigned_to__last_name']

@admin.register(EmailLog)
class EmailLogAdmin(CompanyFilteredAdmin):
    list_display = ['recipient', 'subject', 'sent_successfully', 'created_at']
    list_filter = ['sent_successfully', 'created_at']
    search_fields = ['recipient__first_name', 'recipient__last_name', 'subject']
    readonly_fields = ['created_at', 'updated_at']

# Register other models
admin.site.register(PerformanceReview, CompanyFilteredAdmin)
admin.site.register(TrainingProgram, CompanyFilteredAdmin)
admin.site.register(EmployeeTraining, CompanyFilteredAdmin)
admin.site.register(Project, CompanyFilteredAdmin)
admin.site.register(ProjectAssignment, CompanyFilteredAdmin)
admin.site.register(DisciplinaryAction, CompanyFilteredAdmin)
admin.site.register(BenefitType, CompanyFilteredAdmin)
admin.site.register(EmployeeBenefit, CompanyFilteredAdmin)