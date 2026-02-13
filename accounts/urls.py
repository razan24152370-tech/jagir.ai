from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('home/', views.home, name='home'),
    # Job Seeker Authentication
    path('jobseeker/signup/', views.jobseeker_signup_view, name='jobseeker_signup'),
    path('jobseeker/login/', views.jobseeker_login_view, name='jobseeker_login'),
    
    # Recruiter Authentication
    path('recruiter/signup/', views.recruiter_signup_view, name='recruiter_signup'),
    path('recruiter/login/', views.recruiter_login_view, name='recruiter_login'),
    
    # Common
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    
    # Team Member Management (Recruiter only)
    path('team/', views.team_members_view, name='team_members'),
    path('team/add/', views.add_team_member, name='add_team_member'),
    path('team/<int:member_id>/edit/', views.edit_team_member, name='edit_team_member'),
    path('team/<int:member_id>/delete/', views.delete_team_member, name='delete_team_member'),
    path('team/<int:member_id>/toggle/', views.toggle_team_member_status, name='toggle_team_member_status'),
    path('team/<int:member_id>/resend/', views.resend_team_invitation, name='resend_team_invitation'),
    
    # Team Member Invitation Acceptance
    path('invitation/<uuid:token>/', views.accept_team_invitation, name='accept_team_invitation'),
]
