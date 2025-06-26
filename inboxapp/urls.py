from django.urls import path
from . import views

urlpatterns = [
    path('', views.inbox_view, name='inbox'),
    path('email/<int:email_id>/', views.email_detail_view, name='email_detail'),
    path('fetch/', views.fetch_new_emails, name='fetch_emails'),
    path('download/<int:attachment_id>/', views.download_attachment, name='download_attachment'),
    path('search/', views.search_emails, name='search_emails'),
]
