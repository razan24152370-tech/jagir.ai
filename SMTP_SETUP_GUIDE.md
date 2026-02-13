# SMTP Email Configuration Guide

## Overview
This guide explains how to configure SMTP email functionality for ProRecruiter AI's team member management system.

## Features Implemented

### 1. **Team Member Invitation System**
- Send email invitations when adding new team members
- Unique invitation tokens with 7-day expiration
- Resend invitation functionality
- Invitation acceptance flow with account creation

### 2. **Email Notifications**
- **Invitation Emails**: Sent when a team member is added
- **Access Update Notifications**: Sent when permissions or roles are changed
- **Account Deactivation Notifications**: Sent when a team member is deactivated
- **Welcome Emails**: Sent after accepting an invitation

### 3. **Access Control**
- Track invitation status (pending/accepted)
- Link team members to user accounts
- Control who can manage team members (recruiters only)

## SMTP Configuration

### Step 1: Update Django Settings

The SMTP configuration is in `ProRecruiterAI/settings.py`:

```python
# Email Configuration (SMTP)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Use your SMTP server
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = ''  # Set this in environment variable or here
EMAIL_HOST_PASSWORD = ''  # Set this in environment variable or here
DEFAULT_FROM_EMAIL = 'ProRecruiter AI <noreply@prorecruiter.ai>'
SERVER_EMAIL = DEFAULT_FROM_EMAIL
```

### Step 2: Configure for Development (Console Backend)

For development/testing, uncomment this line to print emails to console:

```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

This will display all emails in the terminal instead of sending them.

### Step 3: Configure for Production (Gmail Example)

#### Using Gmail SMTP:

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate an App Password**:
   - Go to Google Account → Security → 2-Step Verification → App passwords
   - Generate a new app password for "Mail"
   - Copy the 16-character password

3. **Update settings.py**:
```python
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'  # 16-character app password
DEFAULT_FROM_EMAIL = 'ProRecruiter AI <your-email@gmail.com>'
```

#### Using Environment Variables (Recommended for Production):

Create a `.env` file:
```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

Update `settings.py`:
```python
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
```

### Step 4: Other SMTP Providers

#### SendGrid:
```python
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = 'your-sendgrid-api-key'
```

#### AWS SES:
```python
EMAIL_BACKEND = 'django_ses.SESBackend'
AWS_SES_REGION_NAME = 'us-east-1'
AWS_SES_REGION_ENDPOINT = 'email.us-east-1.amazonaws.com'
```

#### Mailgun:
```python
EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'postmaster@your-domain.com'
EMAIL_HOST_PASSWORD = 'your-mailgun-password'
```

## Database Migration

After updating the TeamMember model, run migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

This will add the new fields:
- `invitation_token` (UUID)
- `invitation_accepted` (Boolean)
- `invitation_accepted_at` (DateTime)

## Usage Guide

### Adding a Team Member

1. Log in as a recruiter
2. Navigate to "Team Management"
3. Click "Add Team Member"
4. Fill in team member details:
   - First Name
   - Last Name
   - Email (will receive invitation)
   - Role
   - Permissions
   - Active status
5. Submit the form
6. **Email automatically sent** with invitation link

### Resending an Invitation

1. Go to Team Management
2. Find team member with "Pending Invitation" status
3. Click the envelope icon (📧) to resend
4. New invitation email sent with fresh token

### Accepting an Invitation

Team members receive an email with a link like:
```
https://yoursite.com/accounts/invitation/abc-123-def-456/
```

When they click:
1. If logged in with matching email → Account linked automatically
2. If not logged in → Show signup form
3. After signup → Account created and linked
4. Welcome email sent automatically

### Managing Team Member Access

**Edit Permissions:**
1. Click edit button (✏️)
2. Update role, permissions, or status
3. Save changes
4. **Email notification sent automatically** with changes

**Deactivate/Activate:**
1. Click toggle button (⏸️/▶️)
2. Status changes immediately
3. **Email notification sent** for deactivation

**Remove Team Member:**
1. Click delete button (🗑️)
2. Confirm deletion
3. Team member removed from system

## Email Templates

All email templates are in `accounts/templates/accounts/emails/`:

- `team_invitation.html` - Invitation email
- `access_update.html` - Permission/role change notification
- `account_deactivated.html` - Deactivation notification
- `welcome_team_member.html` - Welcome after accepting invitation

### Customizing Email Templates

Edit the HTML templates to match your branding:
- Update colors (current: purple gradient)
- Add company logo
- Modify copy/text
- Change button styles

## Testing

### Test Email Configuration:

```python
# In Django shell
python manage.py shell

from django.core.mail import send_mail

send_mail(
    'Test Email',
    'This is a test email from ProRecruiter AI.',
    'from@example.com',
    ['to@example.com'],
    fail_silently=False,
)
```

### Test Team Member Invitation:

1. Use console backend for development
2. Add a team member with your test email
3. Check terminal for email output
4. Copy invitation URL and test acceptance flow

## Troubleshooting

### Email Not Sending

1. **Check SMTP credentials**: Verify EMAIL_HOST_USER and EMAIL_HOST_PASSWORD
2. **Check firewall**: Ensure port 587 (TLS) or 465 (SSL) is open
3. **Check spam folder**: Emails might be filtered as spam
4. **Enable less secure apps**: Some providers require this setting
5. **Check logs**: Look for errors in `debug.log` or console

### Gmail-Specific Issues

- **"Username and Password not accepted"**: Use app password, not account password
- **"Please log in via your web browser"**: Enable "Less secure app access" or use app password
- **Rate limits**: Gmail has sending limits (500/day for free accounts)

### Invitation Link Issues

- **Link expired**: Invitations expire after 7 days - resend invitation
- **Invalid token**: Check that URL is complete and hasn't been modified
- **Already accepted**: User may have already accepted - check team member status

## Security Best Practices

1. **Never commit credentials**: Use environment variables
2. **Use app passwords**: Don't use main account password
3. **Enable TLS/SSL**: Always encrypt email connections
4. **Validate email addresses**: Check format before sending
5. **Rate limiting**: Implement rate limits for invitation sending
6. **Token expiration**: Keep invitation expiration reasonable (current: 7 days)

## Email Delivery Best Practices

1. **SPF/DKIM/DMARC**: Configure for production domain
2. **Warmup sending**: Gradually increase email volume for new accounts
3. **Monitor bounce rates**: Remove invalid addresses
4. **Provide unsubscribe**: For notification emails (if required)
5. **Use reputable SMTP service**: SendGrid, Mailgun, or AWS SES for production

## Future Enhancements

Consider adding:
- Email templates in plain text format
- Internationalization (i18n) for multiple languages
- Email preferences for team members
- Batch invitation system
- Email activity logging
- Retry mechanism for failed sends
- Email queue system for high volume

## API Reference

### Email Utility Functions

Located in `accounts/email_utils.py`:

**`send_team_member_invitation(team_member, invitation_url, recruiter_profile)`**
- Sends invitation email to new team member
- Returns: Boolean (success/failure)

**`send_access_update_notification(team_member, updated_by, changes)`**
- Notifies team member of permission changes
- changes: Dictionary of changed fields

**`send_account_deactivation_notification(team_member, deactivated_by)`**
- Notifies team member of account deactivation

**`send_welcome_email(team_member, recruiter_profile)`**
- Sends welcome email after invitation acceptance

## Support

For issues or questions:
1. Check Django documentation: https://docs.djangoproject.com/en/stable/topics/email/
2. Check SMTP provider documentation
3. Review application logs: `debug.log`
4. Test with console backend first

---

**Last Updated**: February 2026
**ProRecruiter AI** - Team Member Management System
