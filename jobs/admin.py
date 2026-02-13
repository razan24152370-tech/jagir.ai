from django.contrib import admin
from .models import Job, JobApplication


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'posted_by', 'job_type', 'location', 'is_active', 'application_count', 'created_at')
    list_filter = ('job_type', 'is_active', 'created_at')
    search_fields = ('title', 'description', 'skills_required', 'posted_by__username')
    date_hierarchy = 'created_at'
    list_editable = ('is_active',)
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'description', 'requirements')
        }),
        ('Job Details', {
            'fields': ('job_type', 'skills_required', 'experience_required', 'location')
        }),
        ('Salary', {
            'fields': ('salary_min', 'salary_max'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('posted_by', 'is_active', 'deadline')
        }),
    )
    
    actions = ['activate_jobs', 'deactivate_jobs']
    
    def application_count(self, obj):
        return obj.applications.count()
    application_count.short_description = 'Applications'
    
    def activate_jobs(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f'{queryset.count()} jobs activated.')
    activate_jobs.short_description = "Activate selected jobs"
    
    def deactivate_jobs(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f'{queryset.count()} jobs deactivated.')
    deactivate_jobs.short_description = "Deactivate selected jobs"


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'job', 'status', 'match_score', 'applied_at')
    list_filter = ('status', 'applied_at', 'job')
    search_fields = ('applicant__username', 'applicant__email', 'job__title')
    ordering = ['-match_score', '-applied_at']
    list_editable = ('status',)
    
    readonly_fields = ('match_score', 'ranking_notes', 'applied_at')
    
    fieldsets = (
        ('Application Info', {
            'fields': ('job', 'applicant', 'status', 'applied_at')
        }),
        ('Documents', {
            'fields': ('resume', 'cover_letter')
        }),
        ('AI Analysis', {
            'fields': ('match_score', 'ranking_notes'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_reviewed', 'mark_shortlisted', 'mark_rejected']
    
    def mark_reviewed(self, request, queryset):
        queryset.update(status='reviewed')
        self.message_user(request, f'{queryset.count()} applications marked as reviewed.')
    mark_reviewed.short_description = "Mark as Reviewed"
    
    def mark_shortlisted(self, request, queryset):
        queryset.update(status='shortlisted')
        self.message_user(request, f'{queryset.count()} applications shortlisted.')
    mark_shortlisted.short_description = "Shortlist selected"
    
    def mark_rejected(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, f'{queryset.count()} applications rejected.')
    mark_rejected.short_description = "Reject selected"
