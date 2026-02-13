from django.contrib import admin
from django.contrib import messages
from .models import Profile, TeamMember
from .email_config import EmailConfiguration


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type', 'get_email', 'company_name', 'location', 'experience_years')
    list_filter = ('user_type',)
    search_fields = ('user__username', 'user__email', 'company_name', 'skills')
    
    fieldsets = (
        ('User Info', {
            'fields': ('user', 'user_type')
        }),
        ('Job Seeker Info', {
            'fields': ('headline', 'bio', 'skills', 'experience_years', 'education', 'resume', 'linkedin_url'),
            'classes': ('collapse',)
        }),
        ('Recruiter Info', {
            'fields': ('company_name', 'company_website', 'company_description'),
            'classes': ('collapse',)
        }),
        ('Contact', {
            'fields': ('phone', 'location')
        }),
    )

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'email', 'role', 'permissions', 'company_owner', 'is_active', 'invited_at')
    list_filter = ('role', 'permissions', 'is_active')
    search_fields = ('first_name', 'last_name', 'email', 'company_owner__username', 'company_owner__profile__company_name')
    ordering = ('-invited_at',)
    
    fieldsets = (
        ('Team Member Info', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Role & Permissions', {
            'fields': ('role', 'permissions', 'is_active')
        }),
        ('Company', {
            'fields': ('company_owner', 'user')
        }),
    )


@admin.register(EmailConfiguration)
class EmailConfigurationAdmin(admin.ModelAdmin):
    list_display = ('name', 'backend', 'smtp_host', 'smtp_username', 'is_active', 'updated_at')
    list_filter = ('backend', 'is_active')
    search_fields = ('name', 'smtp_host', 'smtp_username', 'from_email')
    
    fieldsets = (
        ('Configuration Info', {
            'fields': ('name', 'is_active', 'backend'),
            'description': 'Set "Is active" to use this configuration. Activating this will automatically deactivate other configurations.'
        }),
        ('SMTP Settings', {
            'fields': ('smtp_host', 'smtp_port', 'smtp_use_tls', 'smtp_use_ssl', 'smtp_username', 'smtp_password'),
            'description': 'Configure SMTP server settings. Required when backend is set to SMTP.'
        }),
        ('Email Settings', {
            'fields': ('from_email', 'from_name'),
            'description': 'Default sender information for outgoing emails.'
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    actions = ['test_email_connection', 'activate_configuration']
    
    def test_email_connection(self, request, queryset):
        """Test SMTP connection for selected configurations"""
        for config in queryset:
            success, message = config.test_connection()
            if success:
                self.message_user(request, f"✅ {config.name}: {message}", messages.SUCCESS)
            else:
                self.message_user(request, f"❌ {config.name}: {message}", messages.ERROR)
    test_email_connection.short_description = "Test email connection"
    
    def activate_configuration(self, request, queryset):
        """Activate selected configuration"""
        if queryset.count() > 1:
            self.message_user(request, "Please select only one configuration to activate.", messages.ERROR)
            return
        
        config = queryset.first()
        config.is_active = True
        config.save()
        self.message_user(request, f"✅ {config.name} is now active.", messages.SUCCESS)
    activate_configuration.short_description = "Activate configuration"
    
    def save_model(self, request, obj, form, change):
        """Save model and show helpful messages"""
        try:
            # Check if there are other active configs before saving
            other_active = EmailConfiguration.objects.filter(is_active=True).exclude(pk=obj.pk)
            had_other_active = other_active.exists()
            
            super().save_model(request, obj, form, change)
            
            if obj.is_active:
                if had_other_active:
                    self.message_user(request, f"✅ {obj.name} is now the active email configuration. Previous active configuration has been deactivated.", messages.SUCCESS)
                else:
                    self.message_user(request, f"✅ {obj.name} is now the active email configuration.", messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f"❌ Error saving configuration: {str(e)}", messages.ERROR)
