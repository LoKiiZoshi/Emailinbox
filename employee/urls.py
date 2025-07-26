from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EmploymentDetailViewSet, AttendanceViewSet, LeaveTypeViewSet,
    LeaveRequestViewSet, PayrollViewSet, PerformanceReviewViewSet,
    TrainingProgramViewSet, EmployeeTrainingViewSet, ProjectViewSet,
    ProjectAssignmentViewSet, DisciplinaryActionViewSet, BenefitTypeViewSet,
    EmployeeBenefitViewSet, TaskViewSet, TaskCategoryViewSet,
    TaskCommentViewSet, TaskScheduleViewSet, EmailLogViewSet
)

router = DefaultRouter()

# Employee Management Routes
router.register(r'employment-details', EmploymentDetailViewSet)
router.register(r'attendance', AttendanceViewSet)
router.register(r'leave-types', LeaveTypeViewSet)
router.register(r'leave-requests', LeaveRequestViewSet)
router.register(r'payroll', PayrollViewSet)
router.register(r'performance-reviews', PerformanceReviewViewSet)
router.register(r'training-programs', TrainingProgramViewSet)
router.register(r'employee-training', EmployeeTrainingViewSet)
router.register(r'projects', ProjectViewSet)
router.register(r'project-assignments', ProjectAssignmentViewSet)
router.register(r'disciplinary-actions', DisciplinaryActionViewSet)
router.register(r'benefit-types', BenefitTypeViewSet)
router.register(r'employee-benefits', EmployeeBenefitViewSet)

# Task Management Routes
router.register(r'tasks', TaskViewSet)
router.register(r'task-categories', TaskCategoryViewSet)
router.register(r'task-comments', TaskCommentViewSet)
router.register(r'task-schedules', TaskScheduleViewSet)
router.register(r'email-logs', EmailLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
]