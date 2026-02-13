"""
Quick script to create/reset admin user
Username: admin
Password: admin
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ProRecruiterAI.settings')
django.setup()

from django.contrib.auth.models import User

def create_admin():
    """Create or reset admin user"""
    username = 'admin'
    password = 'admin'
    email = 'admin@prorecruiter.ai'
    
    try:
        # Try to get existing admin user
        user = User.objects.get(username=username)
        print(f"User '{username}' already exists. Resetting password...")
        
        # Reset password
        user.set_password(password)
        user.email = email
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()
        
        print(f"✅ Admin user '{username}' password reset successfully!")
        
    except User.DoesNotExist:
        # Create new admin user
        print(f"Creating new admin user '{username}'...")
        
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        
        print(f"✅ Admin user '{username}' created successfully!")
    
    print("\n" + "="*60)
    print("Admin Credentials:")
    print("="*60)
    print(f"Username: {username}")
    print(f"Password: {password}")
    print(f"Email: {email}")
    print("="*60)
    print(f"\nAdmin panel: http://localhost:8000/admin/")
    print("="*60)

if __name__ == '__main__':
    create_admin()
