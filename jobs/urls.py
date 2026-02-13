from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    # Public
    path('', views.job_list, name='job_list'),
    path('browse/', views.browse_jobs, name='browse_jobs'),
    path('job/<int:job_id>/', views.job_detail, name='job_detail'),
    
    # User/Job Seeker Panel
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('apply/<int:job_id>/', views.apply_job, name='apply_job'),
    path('my-applications/', views.my_applications, name='my_applications'),
    
    # Recruiter Panel
    path('recruiter/', views.recruiter_dashboard, name='recruiter_dashboard'),
    path('recruiter/jobs/', views.recruiter_jobs, name='recruiter_jobs'),
    path('recruiter/post/', views.post_job, name='post_job'),
    path('recruiter/edit/<int:job_id>/', views.edit_job, name='edit_job'),
    path('recruiter/delete/<int:job_id>/', views.delete_job, name='delete_job'),
    path('recruiter/applications/', views.view_all_applications, name='view_all_applications'),
    path('recruiter/applications/<int:job_id>/', views.view_applications, name='view_applications'),
    path('recruiter/application/<int:application_id>/status/', views.update_application_status, name='update_application_status'),
    path('recruiter/candidate/<int:application_id>/', views.view_candidate, name='view_candidate'),
    
    # API Endpoints
    path('api/rank/', views.rank_applications_api, name='rank_applications_api'),
    path('api/track-view/', views.track_job_view, name='track_job_view'),
    path('api/track-preference/', views.track_job_preference, name='track_job_preference'),
]
