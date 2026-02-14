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
    """Create or reset admin user using env vars or defaults"""
    username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin')
    email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@prorecruiter.ai')
    
    from accounts.models import Profile
    
    try:
        # Try to get existing admin user
        user = User.objects.get(username=username)
        print(f"User '{username}' already exists. Updating...")
        
        # Update user
        user.set_password(password)
        user.email = email
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()
        
        # Ensure Profile exists
        Profile.objects.get_or_create(user=user, defaults={'user_type': 'recruiter'})
        
        print(f"✅ Admin user '{username}' and profile updated successfully!")
        
    except User.DoesNotExist:
        # Create new admin user
        print(f"Creating new admin user '{username}'...")
        
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        
        # Create Profile
        Profile.objects.create(user=user, user_type='recruiter')
        
        print(f"✅ Admin user '{username}' and profile created successfully!")
    
    print("\n" + "="*60)
    print("Admin Credentials:")
    print("="*60)
    print(f"Username: {username}")
    print(f"Password: {password}")
    print(f"Email: {email}")
    print("="*60)

if __name__ == '__main__':
    create_admin()
