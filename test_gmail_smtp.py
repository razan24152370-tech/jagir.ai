"""
Gmail SMTP Connection Test - Debug real email sending
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ProRecruiterAI.settings')
django.setup()

from accounts.email_config import EmailConfiguration
from django.core.mail import EmailMultiAlternatives
from accounts.email_utils import get_email_connection, get_from_email
import sys

def test_gmail_smtp():
    print("\n" + "="*70)
    print("📧 GMAIL SMTP CONNECTION TEST")
    print("="*70)
    
    # Get all configurations
    configs = EmailConfiguration.objects.all()
    print(f"\n📋 Total configurations: {configs.count()}")
    
    for config in configs:
        active = "🟢 ACTIVE" if config.is_active else "⚪ Inactive"
        print(f"\n{active} {config.name}")
        print(f"   Backend: {config.backend}")
        if config.backend == 'smtp':
            print(f"   Host: {config.smtp_host}:{config.smtp_port}")
            print(f"   Username: {config.smtp_username}")
            print(f"   Password: {'*' * 16 if config.smtp_password else '❌ NOT SET'}")
            print(f"   From: {config.from_email}")
            print(f"   TLS: {config.smtp_use_tls}, SSL: {config.smtp_use_ssl}")
    
    # Get active config
    print("\n" + "-"*70)
    active_config = EmailConfiguration.get_active_config()
    
    if not active_config:
        print("❌ ERROR: No active configuration found!")
        print("\n💡 Fix: Go to admin panel and check 'Is active' on your Gmail config")
        return
    
    print(f"✅ Active config: {active_config.name}")
    
    if active_config.backend != 'smtp':
        print(f"\n⚠️  WARNING: Active backend is '{active_config.backend}', not 'smtp'")
        print("   Emails will print to console, not send via Gmail")
        print("\n💡 Fix: Activate your Gmail SMTP configuration in admin panel")
        return
    
    # Validate SMTP settings
    print("\n" + "-"*70)
    print("🔍 Validating SMTP Configuration...")
    
    issues = []
    
    if not active_config.smtp_host:
        issues.append("❌ SMTP Host is empty")
    elif active_config.smtp_host != 'smtp.gmail.com':
        issues.append(f"⚠️  SMTP Host is '{active_config.smtp_host}' (should be 'smtp.gmail.com')")
    
    if active_config.smtp_port not in [587, 465]:
        issues.append(f"⚠️  SMTP Port is {active_config.smtp_port} (should be 587 for TLS or 465 for SSL)")
    
    if not active_config.smtp_username:
        issues.append("❌ SMTP Username is empty")
    elif '@gmail.com' not in active_config.smtp_username:
        issues.append(f"⚠️  Username '{active_config.smtp_username}' doesn't look like Gmail")
    
    if not active_config.smtp_password:
        issues.append("❌ SMTP Password is empty")
    elif len(active_config.smtp_password) < 16:
        issues.append("⚠️  Password seems short (Gmail app passwords are 16 chars)")
    elif ' ' in active_config.smtp_password:
        issues.append("⚠️  Password contains spaces (remove spaces from app password)")
    
    if active_config.smtp_port == 587 and not active_config.smtp_use_tls:
        issues.append("❌ Port 587 requires TLS enabled")
    
    if active_config.smtp_port == 465 and not active_config.smtp_use_ssl:
        issues.append("❌ Port 465 requires SSL enabled")
    
    if not active_config.from_email:
        issues.append("❌ From Email is empty")
    
    if issues:
        print("\n🚨 CONFIGURATION ISSUES FOUND:")
        for issue in issues:
            print(f"   {issue}")
        print("\n💡 Fix these issues in the admin panel first!")
        return
    else:
        print("✅ Configuration looks good")
    
    # Test connection
    print("\n" + "-"*70)
    print("🔌 Testing SMTP Connection...")
    
    try:
        success, message = active_config.test_connection()
        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
            print("\n🚨 COMMON GMAIL ISSUES:")
            print("   1. Wrong app password (must be 16 chars, no spaces)")
            print("   2. App password not created (need 2FA enabled first)")
            print("   3. Wrong Gmail account")
            print("   4. Less secure app access disabled")
            print("   5. Account security alert from Google")
            print("\n💡 TROUBLESHOOTING STEPS:")
            print("   1. Check inbox of Gmail account for security alerts")
            print("   2. Verify 2-Step Verification is ON in Google Account")
            print("   3. Generate NEW app password:")
            print("      → https://myaccount.google.com/apppasswords")
            print("   4. Copy password WITHOUT spaces")
            print("   5. Update password in admin panel")
            return
    except Exception as e:
        print(f"❌ Connection test crashed: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    # Send actual test email
    print("\n" + "-"*70)
    print("📨 Sending Test Email...")
    
    test_email = input("\nEnter email address to send test to (or press Enter for yourself): ").strip()
    if not test_email:
        test_email = active_config.smtp_username
    
    print(f"\n📧 Sending to: {test_email}")
    print(f"📤 From: {active_config.get_from_email_formatted()}")
    
    try:
        connection = get_email_connection()
        from_email = get_from_email()
        
        email = EmailMultiAlternatives(
            subject="✅ ProRecruiter AI - SMTP Test Successful",
            body="This is a test email from ProRecruiter AI.\n\nIf you received this, your SMTP configuration is working correctly!",
            from_email=from_email,
            to=[test_email],
            connection=connection
        )
        
        email.attach_alternative(
            f"""
            <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #7c3aed;">✅ SMTP Test Successful!</h2>
                <p>This is a test email from <strong>ProRecruiter AI</strong>.</p>
                <p>If you received this, your SMTP configuration is working correctly!</p>
                <hr style="border: 1px solid #e5e7eb; margin: 20px 0;">
                <p style="color: #6b7280; font-size: 14px;">
                    Configuration: {active_config.name}<br>
                    Host: {active_config.smtp_host}:{active_config.smtp_port}<br>
                    Username: {active_config.smtp_username}
                </p>
            </body>
            </html>
            """,
            "text/html"
        )
        
        result = email.send(fail_silently=False)
        
        if result == 1:
            print("\n🎉 SUCCESS! Email sent successfully!")
            print(f"\n📬 Check inbox: {test_email}")
            print("   (Also check spam/junk folder)")
            print("\n✅ Your SMTP is now working!")
            print("   Team member invitations will be sent successfully!")
        else:
            print("\n⚠️  Email send returned 0 (may indicate failure)")
            print("   Check Django logs for errors")
    
    except Exception as e:
        print(f"\n❌ FAILED TO SEND EMAIL")
        print(f"\nError Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        
        print("\n🔍 DETAILED ERROR:")
        import traceback
        traceback.print_exc()
        
        error_str = str(e).lower()
        
        if 'authentication failed' in error_str or 'username and password not accepted' in error_str:
            print("\n🚨 AUTHENTICATION FAILED")
            print("   → Wrong username or password")
            print("   → App password might be incorrect")
            print("\n💡 FIX:")
            print("   1. Go to: https://myaccount.google.com/apppasswords")
            print("   2. Delete old app password")
            print("   3. Create NEW app password")
            print("   4. Copy it WITHOUT spaces (remove all spaces)")
            print("   5. Update in admin panel")
        
        elif 'timed out' in error_str or 'connection' in error_str:
            print("\n🚨 CONNECTION ISSUE")
            print("   → Cannot reach Gmail servers")
            print("   → Firewall or network blocking")
            print("\n💡 FIX:")
            print("   1. Check your internet connection")
            print("   2. Check if port 587 is blocked by firewall")
            print("   3. Try different network")
        
        elif 'ssl' in error_str or 'tls' in error_str:
            print("\n🚨 SSL/TLS ISSUE")
            print("   → Wrong security settings")
            print("\n💡 FIX:")
            print("   1. For port 587: Enable TLS only")
            print("   2. For port 465: Enable SSL only")
    
    print("\n" + "="*70)


if __name__ == '__main__':
    test_gmail_smtp()
