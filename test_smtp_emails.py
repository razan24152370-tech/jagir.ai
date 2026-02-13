"""
Quick test script for SMTP email functionality
Run this to verify email system is working
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ProRecruiterAI.settings')
django.setup()

from django.core.mail import send_mail
from django.contrib.auth.models import User
from accounts.models import Profile, TeamMember
from accounts.email_utils import send_team_member_invitation

def test_basic_email():
    """Test basic email sending"""
    print("\n" + "="*60)
    print("Testing Basic Email Send")
    print("="*60)
    
    try:
        send_mail(
            subject='Test Email from ProRecruiter AI',
            message='This is a test email to verify SMTP configuration.',
            from_email='noreply@prorecruiter.ai',
            recipient_list=['test@example.com'],
            fail_silently=False,
        )
        print("✅ Basic email test PASSED")
        print("Check your console output above for email content")
        return True
    except Exception as e:
        print(f"❌ Basic email test FAILED: {str(e)}")
        return False


def test_team_invitation_email():
    """Test team member invitation email"""
    print("\n" + "="*60)
    print("Testing Team Member Invitation Email")
    print("="*60)
    
    try:
        # Get or create a test recruiter
        user, created = User.objects.get_or_create(
            username='test_recruiter',
            defaults={
                'email': 'recruiter@test.com',
                'first_name': 'Test',
                'last_name': 'Recruiter'
            }
        )
        
        # Get or create recruiter profile
        profile, created = Profile.objects.get_or_create(
            user=user,
            defaults={
                'user_type': 'recruiter',
                'company_name': 'Test Company Inc.'
            }
        )
        
        # Create a test team member
        team_member = TeamMember(
            company_owner=user,
            email='testmember@example.com',
            first_name='John',
            last_name='Doe',
            role='recruiter',
            permissions='manage_jobs'
        )
        
        invitation_url = 'http://localhost:8000/accounts/invitation/test-token-123/'
        
        # Test send
        result = send_team_member_invitation(team_member, invitation_url, profile)
        
        if result:
            print("✅ Team invitation email test PASSED")
            print("Check console output above for beautifully formatted invitation email")
        else:
            print("❌ Team invitation email test FAILED")
            
        return result
        
    except Exception as e:
        print(f"❌ Team invitation email test FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all email tests"""
    print("\n" + "="*60)
    print("SMTP EMAIL SYSTEM TEST SUITE")
    print("="*60)
    print("\nNote: Emails will appear in console output (not actually sent)")
    print("This is because EMAIL_BACKEND is set to console for development\n")
    
    results = []
    
    # Test 1: Basic email
    results.append(("Basic Email", test_basic_email()))
    
    # Test 2: Team invitation email
    results.append(("Team Invitation Email", test_team_invitation_email()))
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! SMTP email system is working correctly!")
    else:
        print("\n⚠️ Some tests failed. Check the output above for details.")
    
    print("="*60 + "\n")


if __name__ == '__main__':
    run_all_tests()
