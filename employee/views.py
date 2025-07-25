from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import (
    EmploymentDetail, Attendance, LeaveType, LeaveRequest, Payroll,
    PerformanceReview, TrainingProgram, EmployeeTraining, Project, 
    ProjectAssignment, DisciplinaryAction, BenefitType, EmployeeBenefit,
    Task, TaskCategory, TaskComment, TaskSchedule, EmailLog
)
from .serializers import (
    EmploymentDetailSerializer, AttendanceSerializer, LeaveTypeSerializer,
    LeaveRequestSerializer, PayrollSerializer, PerformanceReviewSerializer,
    TrainingProgramSerializer, EmployeeTrainingSerializer, ProjectSerializer,
    ProjectAssignmentSerializer, DisciplinaryActionSerializer, BenefitTypeSerializer,
    EmployeeBenefitSerializer, TaskSerializer, TaskCategorySerializer,
    TaskCommentSerializer, TaskScheduleSerializer, EmailLogSerializer
)
from .tasks import send_task_assignment_email, create_scheduled_task

# Base ViewSet with Company Filtering
class CompanyFilteredViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if hasattr(self.request.user, 'company') and self.request.user.company:
            return self.queryset.filter(company=self.request.user.company)
        return self.queryset.none()
    
    def perform_create(self, serializer):
        if hasattr(self.request.user, 'company') and self.request.user.company:
            serializer.save(company=self.request.user.company)

# Employment Management ViewSets
class EmploymentDetailViewSet(CompanyFilteredViewSet):
    queryset = EmploymentDetail.objects.select_related('user', 'department', 'position').all()
    serializer_class = EmploymentDetailSerializer

class AttendanceViewSet(CompanyFilteredViewSet):
    queryset = Attendance.objects.select_related('user').all()
    serializer_class = AttendanceSerializer

class LeaveTypeViewSet(CompanyFilteredViewSet):
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer

class LeaveRequestViewSet(CompanyFilteredViewSet):
    queryset = LeaveRequest.objects.select_related('user', 'leave_type', 'approved_by').all()
    serializer_class = LeaveRequestSerializer

class PayrollViewSet(CompanyFilteredViewSet):
    queryset = Payroll.objects.select_related('user').all()
    serializer_class = PayrollSerializer

class PerformanceReviewViewSet(CompanyFilteredViewSet):
    queryset = PerformanceReview.objects.select_related('user', 'reviewer').all()
    serializer_class = PerformanceReviewSerializer

class TrainingProgramViewSet(CompanyFilteredViewSet):
    queryset = TrainingProgram.objects.all()
    serializer_class = TrainingProgramSerializer

class EmployeeTrainingViewSet(CompanyFilteredViewSet):
    queryset = EmployeeTraining.objects.select_related('user', 'training_program').all()
    serializer_class = EmployeeTrainingSerializer

class ProjectViewSet(CompanyFilteredViewSet):
    queryset = Project.objects.select_related('manager', 'department').all()
    serializer_class = ProjectSerializer

class ProjectAssignmentViewSet(CompanyFilteredViewSet):
    queryset = ProjectAssignment.objects.select_related('user', 'project').all()
    serializer_class = ProjectAssignmentSerializer

class DisciplinaryActionViewSet(CompanyFilteredViewSet):
    queryset = DisciplinaryAction.objects.select_related('user', 'issued_by').all()
    serializer_class = DisciplinaryActionSerializer

class BenefitTypeViewSet(CompanyFilteredViewSet):
    queryset = BenefitType.objects.all()
    serializer_class = BenefitTypeSerializer

class EmployeeBenefitViewSet(CompanyFilteredViewSet):
    queryset = EmployeeBenefit.objects.select_related('user', 'benefit_type').all()
    serializer_class = EmployeeBenefitSerializer

# Task Management ViewSets
class TaskCategoryViewSet(CompanyFilteredViewSet):
    queryset = TaskCategory.objects.all()
    serializer_class = TaskCategorySerializer

class TaskViewSet(CompanyFilteredViewSet):
    queryset = Task.objects.select_related('assigned_to', 'assigned_by', 'category').all()
    serializer_class = TaskSerializer
    
    def perform_create(self, serializer):
        task = serializer.save(company=self.request.user.company)
        # Send email notification asynchronously
        send_task_assignment_email.delay(task.id)
    
    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        task = self.get_object()
        try:
            comment = TaskComment.objects.create(
                task=task,
                author=request.user,
                comment=request.data.get('comment', ''),
                company=request.user.company
            )
            serializer = TaskCommentSerializer(comment, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        task = self.get_object()
        new_status = request.data.get('status')
        if new_status in [choice[0] for choice in TaskStatusChoices.choices]:
            task.status = new_status
            if new_status == TaskStatusChoices.COMPLETED:
                task.completion_date = timezone.now()
            task.save()
            return Response({'status': 'Status updated successfully'})
        return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def my_tasks(self, request):
        """Get tasks assigned to the current user"""
        tasks = self.get_queryset().filter(assigned_to=request.user)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue_tasks(self, request):
        """Get overdue tasks"""
        tasks = self.get_queryset().filter(
            due_date__lt=timezone.now(),
            status__in=[TaskStatusChoices.PENDING, TaskStatusChoices.IN_PROGRESS]
        )
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

class TaskCommentViewSet(CompanyFilteredViewSet):
    queryset = TaskComment.objects.select_related('author', 'task').all()
    serializer_class = TaskCommentSerializer

class TaskScheduleViewSet(CompanyFilteredViewSet):
    queryset = TaskSchedule.objects.select_related('assigned_to', 'assigned_by', 'category').all()
    serializer_class = TaskScheduleSerializer
    
    def perform_create(self, serializer):
        schedule = serializer.save(company=self.request.user.company)
        # Create the first scheduled task
        create_scheduled_task.delay(schedule.id)

class EmailLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EmailLog.objects.select_related('recipient', 'task').all()
    serializer_class = EmailLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if hasattr(self.request.user, 'company') and self.request.user.company:
            return self.queryset.filter(company=self.request.user.company)
        return self.queryset.none()