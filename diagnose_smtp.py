"""
SMTP Diagnostic Script - Find and fix email issues
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ProRecruiterAI.settings')
django.setup()

from accounts.email_config import EmailConfiguration
from accounts.email_utils import get_email_connection, get_from_email
from django.core.mail import EmailMultiAlternatives

def diagnose_smtp():
    """Run comprehensive SMTP diagnostics"""
    
    print("\n" + "="*70)
    print("🔍 SMTP DIAGNOSTIC REPORT")
    print("="*70)
    
    # Check 1: Database configurations
    print("\n1️⃣ Checking Email Configurations in Database...")
    print("-"*70)
    
    configs = EmailConfiguration.objects.all()
    if not configs.exists():
        print("❌ No email configurations found in database!")
        print("   Run: python setup_email_config.py")
        return
    
    print(f"✅ Found {configs.count()} configuration(s)")
    for config in configs:
        status = "🟢 ACTIVE" if config.is_active else "⚪ Inactive"
        print(f"\n   {status} {config.name}")
        print(f"   Backend: {config.get_backend_display()}")
        if config.backend == 'smtp':
            print(f"   Host: {config.smtp_host}:{config.smtp_port}")
            print(f"   Username: {config.smtp_username}")
            print(f"   Password: {'*' * len(config.smtp_password) if config.smtp_password else 'NOT SET'}")
            print(f"   TLS: {config.smtp_use_tls}, SSL: {config.smtp_use_ssl}")
    
    # Check 2: Active configuration
    print("\n\n2️⃣ Checking Active Configuration...")
    print("-"*70)
    
    active_config = EmailConfiguration.get_active_config()
    if not active_config:
        print("❌ No active email configuration!")
        print("   Go to admin panel and activate a configuration")
        return
    
    print(f"✅ Active: {active_config.name}")
    print(f"   Backend: {active_config.get_backend_display()}")
    print(f"   From: {active_config.get_from_email_formatted()}")
    
    # Check 3: Test email connection
    print("\n\n3️⃣ Testing Email Connection...")
    print("-"*70)
    
    try:
        connection = get_email_connection()
        from_email = get_from_email()
        
        print(f"✅ Connection created successfully")
        print(f"   From email: {from_email}")
        print(f"   Backend: {type(connection).__name__}")
        
        if active_config.backend == 'smtp':
            print("\n   Testing SMTP connection...")
            success, message = active_config.test_connection()
            if success:
                print(f"   ✅ {message}")
            else:
                print(f"   ❌ {message}")
                print("\n   POSSIBLE ISSUES:")
                print("   - Wrong username/password")
                print("   - SMTP host or port incorrect")
                print("   - Firewall blocking port 587/465")
                print("   - Need to use App Password (Gmail)")
                return
        else:
            print("   ℹ️  Console backend - emails will print to terminal")
    
    except Exception as e:
        print(f"❌ Connection test failed: {str(e)}")
        return
    
    # Check 4: Send test email
    print("\n\n4️⃣ Sending Test Email...")
    print("-"*70)
    
    try:
        connection = get_email_connection()
        from_email = get_from_email()
        
        email = EmailMultiAlternatives(
            subject="Test Email - ProRecruiter AI SMTP Diagnostic",
            body="This is a test email to verify SMTP configuration is working.",
            from_email=from_email,
            to=['test@example.com'],
            connection=connection
        )
        
        email.send()
        
        if active_config.backend == 'console':
            print("✅ Test email sent to console (check terminal output above)")
        else:
            print("✅ Test email sent successfully!")
            print(f"   To: test@example.com")
            print(f"   From: {from_email}")
    
    except Exception as e:
        print(f"❌ Failed to send test email: {str(e)}")
        print(f"\n   ERROR DETAILS: {type(e).__name__}")
        import traceback
        print(traceback.format_exc())
        return
    
    # Summary
    print("\n\n" + "="*70)
    print("📊 DIAGNOSTIC SUMMARY")
    print("="*70)
    
    if active_config.backend == 'console':
        print("\n✅ SMTP Configuration: OK (Console Mode)")
        print("\nℹ️  You're in DEVELOPMENT mode - emails print to terminal")
        print("\nTo send real emails:")
        print("1. Go to: http://localhost:8000/admin/accounts/emailconfiguration/")
        print("2. Add SMTP configuration with your credentials")
        print("3. Check 'Is active' and save")
    elif active_config.backend == 'smtp':
        print("\n✅ SMTP Configuration: OK (SMTP Mode)")
        print(f"\n✉️  Emails will be sent via: {active_config.smtp_host}")
        print(f"📧 From address: {active_config.get_from_email_formatted()}")
        print("\n🎉 Ready to send emails!")
    
    print("\n" + "="*70)
    
    # Additional checks
    print("\n\n5️⃣ Checking Team Member Invitation Flow...")
    print("-"*70)
    
    from django.contrib.auth.models import User
    from accounts.models import Profile
    
    recruiters = User.objects.filter(profile__user_type='recruiter')
    if recruiters.exists():
        print(f"✅ Found {recruiters.count()} recruiter(s)")
        for recruiter in recruiters[:3]:
            team_count = recruiter.team_members.count()
            print(f"   - {recruiter.username}: {team_count} team member(s)")
    else:
        print("⚠️  No recruiters found")
        print("   Create a recruiter account to test team invitations")
    
    print("\n" + "="*70)
    print("✅ DIAGNOSTIC COMPLETE")
    print("="*70)
    print("\nIf you're still having issues:")
    print("1. Check the error messages above")
    print("2. Verify SMTP credentials in admin panel")
    print("3. Try switching to console backend for testing")
    print("4. Check terminal for error logs when adding team member")
    print("="*70 + "\n")


if __name__ == '__main__':
    diagnose_smtp()
