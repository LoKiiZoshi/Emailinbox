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
