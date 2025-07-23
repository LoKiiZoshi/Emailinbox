from django.db import models
from users.models import User, Department, Position, TimestampedModel, TenantMixin
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone

# Employment Related Choices
class EmploymentTypeChoices(models.TextChoices):
    FULL_TIME = 'full_time', 'Full-Time'
    PART_TIME = 'part_time', 'Part-Time'
    CONTRACT = 'contract', 'Contract'
    INTERN = 'intern', 'Intern'

class EmploymentStatusChoices(models.TextChoices):
    ACTIVE = 'active', 'Active'
    INACTIVE = 'inactive', 'Inactive'
    TERMINATED = 'terminated', 'Terminated'

# Attendance Related Choices
class AttendanceStatusChoices(models.TextChoices):
    PRESENT = 'present', 'Present'
    ABSENT = 'absent', 'Absent'
    LATE = 'late', 'Late'
    HALF_DAY = 'half_day', 'Half Day'

# Leave Related Choices
class LeaveStatusChoices(models.TextChoices):
    PENDING = 'pending', 'Pending'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'

# Payroll Related Choices
class PayrollStatusChoices(models.TextChoices):
    PENDING = 'pending', 'Pending'
    PROCESSED = 'processed', 'Processed'
    PAID = 'paid', 'Paid'

# Training Related Choices
class TrainingStatusChoices(models.TextChoices):
    REGISTERED = 'registered', 'Registered'
    IN_PROGRESS = 'in_progress', 'In Progress'
    COMPLETED = 'completed', 'Completed'
    FAILED = 'failed', 'Failed'

# Project Related Choices
class ProjectStatusChoices(models.TextChoices):
    ACTIVE = 'active', 'Active'
    COMPLETED = 'completed', 'Completed'
    ON_HOLD = 'on_hold', 'On Hold'

# Disciplinary Action Related Choices
class DisciplinaryActionChoices(models.TextChoices):
    WARNING = 'warning', 'Warning'
    SUSPENSION = 'suspension', 'Suspension'
    FINE = 'fine', 'Fine'
    TERMINATION = 'termination', 'Termination'

# Benefit Related Choices
class BenefitStatusChoices(models.TextChoices):
    ACTIVE = 'active', 'Active'
    EXPIRED = 'expired', 'Expired'
    TERMINATED = 'terminated', 'Terminated'

# Task Related Choices
class TaskPriorityChoices(models.TextChoices):
    LOW = 'low', 'Low'
    MEDIUM = 'medium', 'Medium'
    HIGH = 'high', 'High'
    URGENT = 'urgent', 'Urgent'

class TaskStatusChoices(models.TextChoices):
    PENDING = 'pending', 'Pending'
    IN_PROGRESS = 'in_progress', 'In Progress'
    COMPLETED = 'completed', 'Completed'
    CANCELLED = 'cancelled', 'Cancelled'

class TaskFrequencyChoices(models.TextChoices):
    ONCE = 'once', 'Once'
    DAILY = 'daily', 'Daily'
    WEEKLY = 'weekly', 'Weekly'
    MONTHLY = 'monthly', 'Monthly'

# Employment Details
class EmploymentDetail(TenantMixin, TimestampedModel):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='employment_detail'
    )
    employee_id = models.CharField(max_length=20)
    hire_date = models.DateField()
    employment_type = models.CharField(
        max_length=20,
        choices=EmploymentTypeChoices.choices,
        default=EmploymentTypeChoices.FULL_TIME
    )
    salary = models.DecimalField(
        max_digits=50,
        decimal_places=2,
        validators=[MinValueValidator(0.0)]
    )
    status = models.CharField(
        max_length=20,
        choices=EmploymentStatusChoices.choices,
        default=EmploymentStatusChoices.ACTIVE
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    position = models.ForeignKey(
        Position,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    class Meta:
        unique_together = ('company', 'employee_id')
    
    def clean(self):
        super().clean()
        if self.user and self.user.company:
            self.company = self.user.company
            
        if self.department and self.department.company != self.company:
            raise ValidationError("Department must belong to the same company")
            
        if self.position and self.position.company != self.company:
            raise ValidationError("Position must belong to the same company")
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.employee_id}"

# Attendance
class Attendance(TenantMixin, TimestampedModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='attendances'
    )
    date = models.DateField()
    check_in = models.DateTimeField(null=True, blank=True)
    check_out = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=AttendanceStatusChoices.choices,
        default=AttendanceStatusChoices.PRESENT
    )
    remarks = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ('company', 'user', 'date')
    
    def clean(self):
        super().clean()
        if self.user and self.user.company:
            self.company = self.user.company
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.date}"

# Leave Management
class LeaveType(TenantMixin, TimestampedModel):
    name = models.CharField(max_length=100)
    max_days = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    
    class Meta:
        unique_together = ('company', 'name')
    
    def __str__(self):
        return f"{self.name} - {self.company.name}"

class LeaveRequest(TenantMixin, TimestampedModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='leave_requests'
    )
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=LeaveStatusChoices.choices,
        default=LeaveStatusChoices.PENDING
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_leaves'
    )
    
    def clean(self):
        super().clean()
        if self.user and self.user.company:
            self.company = self.user.company
            
        if self.leave_type and self.leave_type.company != self.company:
            raise ValidationError("Leave type must belong to the same company")
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.leave_type.name} ({self.start_date} to {self.end_date})"

# Payroll
class Payroll(TenantMixin, TimestampedModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='payrolls'
    )
    month = models.DateField()
    basic_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.0)]
    )
    allowances = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0
    )
    deductions = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0
    )
    net_salary = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=PayrollStatusChoices.choices,
        default=PayrollStatusChoices.PENDING
    )
    
    class Meta:
        unique_together = ('company', 'user', 'month')
    
    def clean(self):
        super().clean()
        if self.user and self.user.company:
            self.company = self.user.company
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.month.strftime('%B %Y')}"

# Performance Review
class PerformanceReview(TenantMixin, TimestampedModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='performance_reviews'
    )
    review_date = models.DateField()
    reviewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conducted_reviews'
    )
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    comments = models.TextField(blank=True)
    goals = models.TextField(blank=True, null=True)
    
    def clean(self):
        super().clean()
        if self.user and self.user.company:
            self.company = self.user.company
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - Review on {self.review_date}"

# Training
class TrainingProgram(TenantMixin, TimestampedModel):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    trainer = models.CharField(max_length=200, blank=True)
    is_mandatory = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.title} ({self.start_date} to {self.end_date}) - {self.company.name}"

class EmployeeTraining(TenantMixin, TimestampedModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='trainings'
    )
    training_program = models.ForeignKey(
        TrainingProgram,
        on_delete=models.CASCADE,
        related_name='participants'
    )
    completion_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=TrainingStatusChoices.choices,
        default=TrainingStatusChoices.REGISTERED
    )
    certificate = models.FileField(
        upload_to='certificates/',
        null=True,
        blank=True
    )
    
    class Meta:
        unique_together = ('company', 'user', 'training_program')
    
    def clean(self):
        super().clean()
        if self.user and self.user.company:
            self.company = self.user.company
            
        if self.training_program and self.training_program.company != self.company:
            raise ValidationError("Training program must belong to the same company")
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.training_program.title}"

# Project Management
class Project(TenantMixin, TimestampedModel):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_projects'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    def clean(self):
        super().clean()
        if self.manager and self.manager.company:
            self.company = self.manager.company
            
        if self.department and self.department.company != self.company:
            raise ValidationError("Department must belong to the same company")
    
    def __str__(self):
        return f"{self.name} - {self.company.name}"

class ProjectAssignment(TenantMixin, TimestampedModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='project_assignments'
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    role = models.CharField(max_length=100, blank=True)
    assigned_date = models.DateField()
    completion_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=ProjectStatusChoices.choices,
        default=ProjectStatusChoices.ACTIVE
    )
    
    class Meta:
        unique_together = ('company', 'user', 'project')
    
    def clean(self):
        super().clean()
        if self.user and self.user.company:
            self.company = self.user.company
            
        if self.project and self.project.company != self.company:
            raise ValidationError("Project must belong to the same company")
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.project.name}"

# Disciplinary Action
class DisciplinaryAction(TenantMixin, TimestampedModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='disciplinary_actions'
    )
    incident_date = models.DateField()
    description = models.TextField()
    action_type = models.CharField(
        max_length=50,
        choices=DisciplinaryActionChoices.choices
    )
    issued_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='issued_actions'
    )
    duration = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Duration in days (for suspension)"
    )
    resolved = models.BooleanField(default=False)
    resolution_date = models.DateField(null=True, blank=True)
    
    def clean(self):
        super().clean()
        if self.user and self.user.company:
            self.company = self.user.company
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.action_type} on {self.incident_date}"

# Employee Benefits
class BenefitType(TenantMixin, TimestampedModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.0)],
        null=True,
        blank=True
    )
    
    class Meta:
        unique_together = ('company', 'name')
    
    def __str__(self):
        return f"{self.name} - {self.company.name}"

class EmployeeBenefit(TenantMixin, TimestampedModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='benefits'
    )
    benefit_type = models.ForeignKey(BenefitType, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    details = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=BenefitStatusChoices.choices,
        default=BenefitStatusChoices.ACTIVE
    )
    
    def clean(self):
        super().clean()
        if self.user and self.user.company:
            self.company = self.user.company
            
        if self.benefit_type and self.benefit_type.company != self.company:
            raise ValidationError("Benefit type must belong to the same company")
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.benefit_type.name}"

# Task Management Models
class TaskCategory(TenantMixin, TimestampedModel):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7, default='#007bff')
    
    class Meta:
        unique_together = ('company', 'name')
        verbose_name_plural = 'Task Categories'
    
    def __str__(self):
        return f"{self.name} - {self.company.name}"

class Task(TenantMixin, TimestampedModel):
    title = models.CharField(max_length=200)
    description = models.TextField()
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assigned_tasks'
    )
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_tasks'
    )
    category = models.ForeignKey(
        TaskCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    priority = models.CharField(
        max_length=10,
        choices=TaskPriorityChoices.choices,
        default=TaskPriorityChoices.MEDIUM
    )
    status = models.CharField(
        max_length=15,
        choices=TaskStatusChoices.choices,
        default=TaskStatusChoices.PENDING
    )
    due_date = models.DateTimeField()
    start_date = models.DateTimeField(default=timezone.now)
    completion_date = models.DateTimeField(null=True, blank=True)
    estimated_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    actual_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    def clean(self):
        super().clean()
        if self.assigned_to and self.assigned_to.company:
            self.company = self.assigned_to.company
            
        if self.assigned_by and self.assigned_by.company != self.company:
            raise ValidationError("Assigned by user must belong to the same company")
            
        if self.category and self.category.company != self.company:
            raise ValidationError("Category must belong to the same company")
    
    def __str__(self):
        return f"{self.title} - {self.assigned_to.username}"

class TaskComment(TenantMixin, TimestampedModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    
    def clean(self):
        super().clean()
        if self.task and self.task.company:
            self.company = self.task.company
            
        if self.author and self.author.company != self.company:
            raise ValidationError("Author must belong to the same company")
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.task.title}"

class TaskSchedule(TenantMixin, TimestampedModel):
    task_template = models.CharField(max_length=200)
    description_template = models.TextField()
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='scheduled_tasks_assigned'
    )
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='scheduled_tasks_created'
    )
    category = models.ForeignKey(
        TaskCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    priority = models.CharField(
        max_length=10,
        choices=TaskPriorityChoices.choices,
        default=TaskPriorityChoices.MEDIUM
    )
    frequency = models.CharField(
        max_length=10,
        choices=TaskFrequencyChoices.choices
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    estimated_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    def clean(self):
        super().clean()
        if self.assigned_to and self.assigned_to.company:
            self.company = self.assigned_to.company
            
        if self.assigned_by and self.assigned_by.company != self.company:
            raise ValidationError("Assigned by user must belong to the same company")
            
        if self.category and self.category.company != self.company:
            raise ValidationError("Category must belong to the same company")
    
    def __str__(self):
        return f"{self.task_template} - {self.frequency}"

class EmailLog(TenantMixin, TimestampedModel):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True)
    sent_successfully = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    
    def clean(self):
        super().clean()
        if self.recipient and self.recipient.company:
            self.company = self.recipient.company
            
        if self.task and self.task.company != self.company:
            raise ValidationError("Task must belong to the same company")
    
    def __str__(self):
        return f"Email to {self.recipient.email} - {self.subject}"