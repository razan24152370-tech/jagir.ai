"""
Create default email configuration
This sets up a console backend for development
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ProRecruiterAI.settings')
django.setup()

from accounts.email_config import EmailConfiguration

def create_default_config():
    """Create default email configuration for development"""
    
    # Check if any config exists
    existing = EmailConfiguration.objects.first()
    
    if existing:
        print(f"✅ Email configuration already exists: {existing}")
        print(f"   Backend: {existing.get_backend_display()}")
        print(f"   Active: {existing.is_active}")
        return
    
    # Create default console config for development
    config = EmailConfiguration.objects.create(
        name="Development (Console)",
        is_active=True,
        backend='console',
        from_email='noreply@prorecruiter.ai',
        from_name='ProRecruiter AI',
    )
    
    print("="*60)
    print("✅ Default Email Configuration Created!")
    print("="*60)
    print(f"Name: {config.name}")
    print(f"Backend: {config.get_backend_display()}")
    print(f"Status: {'Active' if config.is_active else 'Inactive'}")
    print(f"From: {config.get_from_email_formatted()}")
    print("="*60)
    print("\nEmails will be printed to console during development.")
    print("To configure SMTP:")
    print("1. Go to Admin Panel: http://localhost:8000/admin/")
    print("2. Navigate to: Accounts → Email configurations")
    print("3. Add new or edit existing configuration")
    print("4. Set backend to 'SMTP' and add credentials")
    print("="*60)

if __name__ == '__main__':
    create_default_config()
