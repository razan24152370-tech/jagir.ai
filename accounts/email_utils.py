"""
Email utilities for team member management and notifications
"""
from django.core.mail import send_mail, EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)


def get_email_connection():
    """
    Get email connection based on database configuration
    Falls back to settings.py if no active config exists
    """
    try:
        from .email_config import EmailConfiguration
        config = EmailConfiguration.get_active_config()
        
        if config:
            if config.backend == 'console':
                return get_connection(backend='django.core.mail.backends.console.EmailBackend')
            elif config.backend == 'smtp':
                return get_connection(
                    backend='django.core.mail.backends.smtp.EmailBackend',
                    host=config.smtp_host,
                    port=config.smtp_port,
                    username=config.smtp_username,
                    password=config.smtp_password,
                    use_tls=config.smtp_use_tls,
                    use_ssl=config.smtp_use_ssl,
                )
    except Exception as e:
        logger.warning(f"Could not load email config from database: {e}. Using settings.py")
    
    # Fallback to default connection from settings.py
    return get_connection()


def get_from_email():
    """
    Get 'from' email address from database configuration
    Falls back to settings.py if no active config exists
    """
    try:
        from .email_config import EmailConfiguration
        config = EmailConfiguration.get_active_config()
        
        if config:
            return config.get_from_email_formatted()
    except Exception:
        pass
    
    # Fallback to settings
    return getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@prorecruiter.ai')


def send_team_member_invitation(team_member, invitation_url, recruiter_profile):
    """
    Send an invitation email to a new team member
    
    Args:
        team_member: TeamMember instance
        invitation_url: Full URL for accepting the invitation
        recruiter_profile: Profile of the recruiter who sent the invitation
    """
    try:
        company_name = recruiter_profile.company_name or "Our Company"
        
        subject = f'Invitation to join {company_name} on ProRecruiter AI'
        
        # Email context
        context = {
            'team_member': team_member,
            'company_name': company_name,
            'recruiter_name': team_member.company_owner.get_full_name() or team_member.company_owner.username,
            'invitation_url': invitation_url,
            'role': team_member.get_role_display(),
            'permissions': team_member.get_permissions_display(),
        }
        
        # Render HTML and plain text versions
        html_message = render_to_string('accounts/emails/team_invitation.html', context)
        plain_message = strip_tags(html_message)
        
        # Get email connection and from address
        connection = get_email_connection()
        from_email = get_from_email()
        
        # Create email
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=from_email,
            to=[team_member.email],
            connection=connection
        )
        email.attach_alternative(html_message, "text/html")
        
        # Send email
        email.send()
        
        logger.info(f"Invitation email sent to {team_member.email} for {company_name}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send invitation email to {team_member.email}: {str(e)}")
        return False


def send_access_update_notification(team_member, updated_by, changes):
    """
    Send notification when team member access/permissions are updated
    
    Args:
        team_member: TeamMember instance
        updated_by: User who made the changes
        changes: Dictionary of changes made
    """
    try:
        company_name = updated_by.profile.company_name if hasattr(updated_by, 'profile') else "the company"
        
        subject = f'Your access has been updated - {company_name}'
        
        context = {
            'team_member': team_member,
            'company_name': company_name,
            'updated_by': updated_by.get_full_name() or updated_by.username,
            'changes': changes,
            'role': team_member.get_role_display(),
            'permissions': team_member.get_permissions_display(),
            'is_active': team_member.is_active,
        }
        
        html_message = render_to_string('accounts/emails/access_update.html', context)
        plain_message = strip_tags(html_message)
        
        # Get email connection and from address
        connection = get_email_connection()
        from_email = get_from_email()
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=from_email,
            to=[team_member.email],
            connection=connection
        )
        email.attach_alternative(html_message, "text/html")
        email.send()
        
        logger.info(f"Access update notification sent to {team_member.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send access update email to {team_member.email}: {str(e)}")
        return False


def send_account_deactivation_notification(team_member, deactivated_by):
    """
    Send notification when team member account is deactivated
    
    Args:
        team_member: TeamMember instance
        deactivated_by: User who deactivated the account
    """
    try:
        company_name = deactivated_by.profile.company_name if hasattr(deactivated_by, 'profile') else "the company"
        
        subject = f'Your access has been deactivated - {company_name}'
        
        context = {
            'team_member': team_member,
            'company_name': company_name,
            'deactivated_by': deactivated_by.get_full_name() or deactivated_by.username,
        }
        
        html_message = render_to_string('accounts/emails/account_deactivated.html', context)
        plain_message = strip_tags(html_message)
        
        # Get email connection and from address
        connection = get_email_connection()
        from_email = get_from_email()
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=from_email,
            to=[team_member.email],
            connection=connection
        )
        email.attach_alternative(html_message, "text/html")
        email.send()
        
        logger.info(f"Deactivation notification sent to {team_member.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send deactivation email to {team_member.email}: {str(e)}")
        return False


def send_welcome_email(team_member, recruiter_profile):
    """
    Send a welcome email after team member accepts invitation
    
    Args:
        team_member: TeamMember instance
        recruiter_profile: Profile of the recruiter/company owner
    """
    try:
        company_name = recruiter_profile.company_name or "Our Company"
        
        subject = f'Welcome to {company_name} - ProRecruiter AI'
        
        context = {
            'team_member': team_member,
            'company_name': company_name,
            'role': team_member.get_role_display(),
            'permissions': team_member.get_permissions_display(),
        }
        
        html_message = render_to_string('accounts/emails/welcome_team_member.html', context)
        plain_message = strip_tags(html_message)
        
        # Get email connection and from address
        connection = get_email_connection()
        from_email = get_from_email()
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=from_email,
            to=[team_member.email],
            connection=connection
        )
        email.attach_alternative(html_message, "text/html")
        email.send()
        
        logger.info(f"Welcome email sent to {team_member.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send welcome email to {team_member.email}: {str(e)}")
        return False
