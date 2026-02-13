from django.db import models
from django.contrib.auth.models import User


class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('remote', 'Remote'),
    ]
    
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    requirements = models.TextField(blank=True)
    skills_required = models.TextField(blank=True, help_text="Comma-separated skills")
    location = models.CharField(max_length=100, blank=True)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='full_time')
    experience_required = models.PositiveIntegerField(default=0, help_text="Years of experience")
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='jobs')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    deadline = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.title
    
    def get_skills_list(self):
        if self.skills_required:
            return [s.strip().lower() for s in self.skills_required.split(',')]
        return []

    class Meta:
        ordering = ['-created_at']


class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('shortlisted', 'Shortlisted'),
        ('rejected', 'Rejected'),
        ('hired', 'Hired'),
    ]
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    resume = models.FileField(upload_to='applications/', blank=True, null=True)
    cover_letter = models.TextField(blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # AI Ranking Fields
    match_score = models.FloatField(default=0.0, help_text="AI-calculated match score 0-100")
    ranking_notes = models.TextField(blank=True, help_text="AI analysis notes")
    
    # Rejection Feedback
    rejection_reason = models.TextField(blank=True, help_text="Reason for rejection (visible to applicant)")

    class Meta:
        unique_together = ['job', 'applicant']
        ordering = ['-match_score', '-applied_at']

    def __str__(self):
        return f"{self.applicant.username} - {self.job.title}"


class JobView(models.Model):
    """Track user behavior - which jobs they view and for how long"""
    SOURCE_CHOICES = [
        ('search', 'Search'),
        ('recommendations', 'Recommendations'),
        ('browse', 'Browse'),
        ('direct', 'Direct'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_views')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='views')
    viewed_at = models.DateTimeField(auto_now_add=True, db_index=True)
    time_spent_seconds = models.PositiveIntegerField(default=0, help_text="Time spent viewing this job in seconds")
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='browse')
    
    class Meta:
        ordering = ['-viewed_at']
        indexes = [
            models.Index(fields=['user', '-viewed_at']),
            models.Index(fields=['job', '-viewed_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} viewed {self.job.title} ({self.time_spent_seconds}s)"


class JobPreference(models.Model):
    """Track explicit and implicit user preferences"""
    PREFERENCE_CHOICES = [
        ('applied', 'Applied'),
        ('rejected', 'Rejected'),
        ('saved', 'Saved'),
        ('ignored', 'Ignored'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_preferences')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='preferences')
    preference_type = models.CharField(max_length=20, choices=PREFERENCE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'job', 'preference_type']
    
    def __str__(self):
        return f"{self.user.username} - {self.preference_type} - {self.job.title}"
