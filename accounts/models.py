from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import uuid
from datetime import timedelta
from django.utils import timezone

# Import EmailConfiguration model
from .email_config import EmailConfiguration


class Profile(models.Model):
    USER_TYPE_CHOICES = [
        ('recruiter', 'Recruiter'),
        ('jobseeker', 'Job Seeker'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    
    # Job Seeker Profile Fields
    headline = models.CharField(max_length=200, blank=True)
    bio = models.TextField(blank=True)
    skills = models.TextField(blank=True, help_text="Comma-separated skills")
    experience_years = models.PositiveIntegerField(default=0)
    education = models.TextField(blank=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=100, blank=True)
    linkedin_url = models.URLField(blank=True)
    
    # Recruiter Profile Fields
    company_name = models.CharField(max_length=200, blank=True)
    company_website = models.URLField(blank=True)
    company_description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.user_type})"
    
    def get_skills_list(self):
        if self.skills:
            return [s.strip() for s in self.skills.split(',')]
        return []
    
    def is_company_owner(self):
        """Check if this recruiter is the company owner"""
        return self.user_type == 'recruiter'
    
    def get_team_members(self):
        """Get all team members for this recruiter's company"""
        if self.user_type == 'recruiter':
            return TeamMember.objects.filter(company_owner=self.user)
        return TeamMember.objects.none()


class TeamMember(models.Model):
    """Team members who can access company's recruitment portal"""
    
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('hr_manager', 'HR Manager'),
        ('recruiter', 'Recruiter'),
        ('hiring_manager', 'Hiring Manager'),
        ('interviewer', 'Interviewer'),
        ('viewer', 'Viewer'),
    ]
    
    PERMISSION_CHOICES = [
        ('full_access', 'Full Access - Can manage everything'),
        ('manage_jobs', 'Manage Jobs - Can post, edit, and delete jobs'),
        ('view_applications', 'View Applications - Can view and review applications'),
        ('interview_candidates', 'Interview Candidates - Can review and update application status'),
        ('view_only', 'View Only - Can only view jobs and applications'),
    ]
    
    company_owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_members')
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer')
    permissions = models.CharField(max_length=30, choices=PERMISSION_CHOICES, default='view_only')
    is_active = models.BooleanField(default=True)
    invited_at = models.DateTimeField(auto_now_add=True)
    
    # Invitation system
    invitation_token = models.UUIDField(default=uuid.uuid4, editable=False, db_index=True)
    invitation_accepted = models.BooleanField(default=False)
    invitation_accepted_at = models.DateTimeField(null=True, blank=True)
    
    # User account (if they've accepted the invitation)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='team_membership')
    
    class Meta:
        ordering = ['-invited_at']
        unique_together = ['company_owner', 'email']
    
    def __str__(self):
        company_name = "Unknown Company"
        if self.company_owner_id:
            try:
                company_name = self.company_owner.profile.company_name or "Unknown Company"
            except:
                company_name = "Unknown Company"
        return f"{self.first_name} {self.last_name} ({self.get_role_display()}) - {company_name}"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def can_manage_jobs(self):
        return self.permissions in ['full_access', 'manage_jobs']
    
    def can_view_applications(self):
        return self.permissions in ['full_access', 'manage_jobs', 'view_applications', 'interview_candidates']
    
    def can_update_applications(self):
        return self.permissions in ['full_access', 'manage_jobs', 'view_applications', 'interview_candidates']
    
    def has_full_access(self):
        return self.permissions == 'full_access'
    
    def clean(self):
        # Ensure the company owner is a recruiter
        if self.company_owner_id:
            try:
                if hasattr(self.company_owner, 'profile'):
                    if self.company_owner.profile.user_type != 'recruiter':
                        raise ValidationError('Team members can only be added by recruiters.')
            except Exception:
                pass  # Skip validation if profile doesn't exist yet
    
    def is_invitation_valid(self):
        """Check if invitation is still valid (within 7 days)"""
        if self.invitation_accepted:
            return False
        days_since_invite = (timezone.now() - self.invited_at).days
        return days_since_invite <= 7
    
    def regenerate_invitation_token(self):
        """Generate a new invitation token"""
        self.invitation_token = uuid.uuid4()
        self.invited_at = timezone.now()
        self.save()
        return self.invitation_token
