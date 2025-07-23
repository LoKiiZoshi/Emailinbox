from rest_framework import serializers
from .models import (
    EmploymentDetail, Attendance, LeaveType, LeaveRequest, Payroll,
    PerformanceReview, TrainingProgram, EmployeeTraining, Project, 
    ProjectAssignment, DisciplinaryAction, BenefitType, EmployeeBenefit,
    Task, TaskCategory, TaskComment, TaskSchedule, EmailLog,
    # Import the TextChoices classes
    EmploymentTypeChoices, EmploymentStatusChoices, AttendanceStatusChoices,
    LeaveStatusChoices, PayrollStatusChoices, TrainingStatusChoices,
    ProjectStatusChoices, DisciplinaryActionChoices, BenefitStatusChoices,
    TaskPriorityChoices, TaskStatusChoices, TaskFrequencyChoices
)
from users.models import Department, Position, User

# Base Company-Based Serializer
class CompanyBasedSerializer(serializers.ModelSerializer):
    def get_queryset_for_field(self, field_name, model_class):
        """Filter related field querysets by user's company"""
        request = self.context.get('request')
        if request and hasattr(request.user, 'company') and request.user.company:
            return model_class.objects.filter(company=request.user.company)
        return model_class.objects.none()

# Employment Detail Serializer
class EmploymentDetailSerializer(CompanyBasedSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        source='user', 
        write_only=True
    )
    department_name = serializers.CharField(source='department.name', read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        source='department',
        write_only=True,
        required=False
    )
    position_name = serializers.CharField(source='position.name', read_only=True)
    position_id = serializers.PrimaryKeyRelatedField(
        queryset=Position.objects.all(),
        source='position',
        write_only=True,
        required=False
    )
    
    # Add choice fields for frontend
    employment_type_choices = serializers.SerializerMethodField()
    status_choices = serializers.SerializerMethodField()
    
    class Meta:
        model = EmploymentDetail
        fields = [
            'id', 'user_id', 'user_name', 'employee_id', 'hire_date', 
            'employment_type', 'employment_type_choices', 'salary', 'status', 
            'status_choices', 'department_id', 'department_name', 
            'position_name', 'position_id', 'created_at', 'updated_at'
        ]
    
    def get_employment_type_choices(self, obj):
        return EmploymentTypeChoices.choices
    
    def get_status_choices(self, obj):
        return EmploymentStatusChoices.choices
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self, 'context') and self.context.get('request'):
            user = self.context['request'].user
            if hasattr(user, 'company') and user.company:
                self.fields['user_id'].queryset = User.objects.filter(company=user.company)
                self.fields['department_id'].queryset = Department.objects.filter(company=user.company)
                self.fields['position_id'].queryset = Position.objects.filter(company=user.company)

# Task Category Serializer
class TaskCategorySerializer(CompanyBasedSerializer):
    class Meta:
        model = TaskCategory
        fields = ['id', 'name', 'color', 'created_at', 'updated_at']

# Task Serializer
class TaskSerializer(CompanyBasedSerializer):
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='assigned_to',
        write_only=True
    )
    assigned_by_name = serializers.CharField(source='assigned_by.get_full_name', read_only=True)
    assigned_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='assigned_by',
        write_only=True
    )
    category_name = serializers.CharField(source='category.name', read_only=True, allow_null=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=TaskCategory.objects.all(),
        source='category',
        write_only=True,
        required=False,
        allow_null=True
    )
    
    # Choice fields
    priority_choices = serializers.SerializerMethodField()
    status_choices = serializers.SerializerMethodField()
    
    # Comments count
    comments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'assigned_to_id', 'assigned_to_name',
            'assigned_by_id', 'assigned_by_name', 'category_id', 'category_name',
            'priority', 'priority_choices', 'status', 'status_choices',
            'due_date', 'start_date', 'completion_date', 'estimated_hours',
            'actual_hours', 'comments_count', 'created_at', 'updated_at'
        ]
    
    def get_priority_choices(self, obj):
        return TaskPriorityChoices.choices
    
    def get_status_choices(self, obj):
        return TaskStatusChoices.choices
    
    def get_comments_count(self, obj):
        return obj.comments.count()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self, 'context') and self.context.get('request'):
            user = self.context['request'].user
            if hasattr(user, 'company') and user.company:
                self.fields['assigned_to_id'].queryset = User.objects.filter(company=user.company)
                self.fields['assigned_by_id'].queryset = User.objects.filter(company=user.company)
                self.fields['category_id'].queryset = TaskCategory.objects.filter(company=user.company)

# Task Comment Serializer
class TaskCommentSerializer(CompanyBasedSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='author',
        write_only=True
    )
    task_title = serializers.CharField(source='task.title', read_only=True)
    task_id = serializers.PrimaryKeyRelatedField(
        queryset=Task.objects.all(),
        source='task',
        write_only=True
    )
    
    class Meta:
        model = TaskComment
        fields = [
            'id', 'task_id', 'task_title', 'author_id', 'author_name',
            'comment', 'created_at', 'updated_at'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self, 'context') and self.context.get('request'):
            user = self.context['request'].user
            if hasattr(user, 'company') and user.company:
                self.fields['author_id'].queryset = User.objects.filter(company=user.company)
                self.fields['task_id'].queryset = Task.objects.filter(company=user.company)

# Task Schedule Serializer
class TaskScheduleSerializer(CompanyBasedSerializer):
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='assigned_to',
        write_only=True
    )
    assigned_by_name = serializers.CharField(source='assigned_by.get_full_name', read_only=True)
    assigned_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='assigned_by',
        write_only=True
    )
    category_name = serializers.CharField(source='category.name', read_only=True, allow_null=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=TaskCategory.objects.all(),
        source='category',
        write_only=True,
        required=False,
        allow_null=True
    )
    
    # Choice fields
    priority_choices = serializers.SerializerMethodField()
    frequency_choices = serializers.SerializerMethodField()
    
    class Meta:
        model = TaskSchedule
        fields = [
            'id', 'task_template', 'description_template', 'assigned_to_id',
            'assigned_to_name', 'assigned_by_id', 'assigned_by_name',
            'category_id', 'category_name', 'priority', 'priority_choices',
            'frequency', 'frequency_choices', 'start_date', 'end_date',
            'is_active', 'estimated_hours', 'created_at', 'updated_at'
        ]
    
    def get_priority_choices(self, obj):
        return TaskPriorityChoices.choices
    
    def get_frequency_choices(self, obj):
        return TaskFrequencyChoices.choices
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self, 'context') and self.context.get('request'):
            user = self.context['request'].user
            if hasattr(user, 'company') and user.company:
                self.fields['assigned_to_id'].queryset = User.objects.filter(company=user.company)
                self.fields['assigned_by_id'].queryset = User.objects.filter(company=user.company)
                self.fields['category_id'].queryset = TaskCategory.objects.filter(company=user.company)

# Email Log Serializer
class EmailLogSerializer(CompanyBasedSerializer):
    recipient_name = serializers.CharField(source='recipient.get_full_name', read_only=True)
    recipient_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='recipient',
        write_only=True
    )
    task_title = serializers.CharField(source='task.title', read_only=True, allow_null=True)
    task_id = serializers.PrimaryKeyRelatedField(
        queryset=Task.objects.all(),
        source='task',
        write_only=True,
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = EmailLog
        fields = [
            'id', 'recipient_id', 'recipient_name', 'subject', 'message',
            'task_id', 'task_title', 'sent_successfully', 'error_message',
            'created_at', 'updated_at'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self, 'context') and self.context.get('request'):
            user = self.context['request'].user
            if hasattr(user, 'company') and user.company:
                self.fields['recipient_id'].queryset = User.objects.filter(company=user.company)
                self.fields['task_id'].queryset = Task.objects.filter(company=user.company)

# Include all other existing serializers (Attendance, Leave, Payroll, etc.)
# ... (keeping all the previous serializers as they were)