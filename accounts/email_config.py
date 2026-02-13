from django.db import models
from django.core.exceptions import ValidationError


class EmailConfiguration(models.Model):
    """
    Email/SMTP configuration stored in database and manageable via admin panel
    """
    
    BACKEND_CHOICES = [
        ('smtp', 'SMTP (Email Server)'),
        ('console', 'Console (Development - prints to terminal)'),
    ]
    
    name = models.CharField(max_length=100, default="Default Configuration", help_text="Configuration name")
    is_active = models.BooleanField(default=True, help_text="Use this configuration for sending emails")
    
    # Email Backend
    backend = models.CharField(
        max_length=20, 
        choices=BACKEND_CHOICES, 
        default='console',
        help_text="Email backend to use"
    )
    
    # SMTP Settings
    smtp_host = models.CharField(
        max_length=255, 
        default='smtp.gmail.com',
        help_text="SMTP server (e.g., smtp.gmail.com, smtp.sendgrid.net)"
    )
    smtp_port = models.IntegerField(
        default=587,
        help_text="SMTP port (587 for TLS, 465 for SSL, 25 for non-encrypted)"
    )
    smtp_use_tls = models.BooleanField(
        default=True,
        help_text="Use TLS encryption (recommended)"
    )
    smtp_use_ssl = models.BooleanField(
        default=False,
        help_text="Use SSL encryption"
    )
    smtp_username = models.CharField(
        max_length=255,
        blank=True,
        help_text="SMTP username (usually your email address)"
    )
    smtp_password = models.CharField(
        max_length=255,
        blank=True,
        help_text="SMTP password or app password"
    )
    
    # Email Settings
    from_email = models.EmailField(
        default='noreply@prorecruiter.ai',
        help_text="Default 'From' email address"
    )
    from_name = models.CharField(
        max_length=100,
        default='ProRecruiter AI',
        help_text="Default 'From' name"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Email Configuration"
        verbose_name_plural = "Email Configurations"
        ordering = ['-is_active', '-created_at']
    
    def __str__(self):
        status = "Active" if self.is_active else "Inactive"
        return f"{self.name} ({status}) - {self.get_backend_display()}"
    
    def clean(self):
        """Validate the configuration"""
        if self.backend == 'smtp':
            if not self.smtp_username:
                raise ValidationError({'smtp_username': 'Username is required for SMTP backend'})
            if not self.smtp_password:
                raise ValidationError({'smtp_password': 'Password is required for SMTP backend'})
    
    def save(self, *args, **kwargs):
        self.full_clean()
        
        # If this is active, deactivate all others
        if self.is_active:
            EmailConfiguration.objects.exclude(pk=self.pk).update(is_active=False)
        
        super().save(*args, **kwargs)
    
    @classmethod
    def get_active_config(cls):
        """Get the active email configuration"""
        try:
            return cls.objects.filter(is_active=True).first()
        except Exception:
            return None
    
    def get_from_email_formatted(self):
        """Get formatted 'From' email with name"""
        return f"{self.from_name} <{self.from_email}>"
    
    def test_connection(self):
        """Test the SMTP connection"""
        if self.backend != 'smtp':
            return True, "Console backend doesn't require connection test"
        
        try:
            from django.core.mail import get_connection
            
            connection = get_connection(
                backend='django.core.mail.backends.smtp.EmailBackend',
                host=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_username,
                password=self.smtp_password,
                use_tls=self.smtp_use_tls,
                use_ssl=self.smtp_use_ssl,
            )
            connection.open()
            connection.close()
            return True, "Connection successful"
        except Exception as e:
            return False, str(e)
