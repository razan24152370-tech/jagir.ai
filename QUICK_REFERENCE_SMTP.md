# Team Member Email System - Quick Reference

## 🚀 Quick Start

### For Testing (Development):
Emails print to console - no SMTP setup needed!

```bash
# Start server
python manage.py runserver

# Add team member through web UI
# Check terminal for email content!
```

### For Production:
Update `settings.py`:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

## 📧 Email Types

| Event | Email Sent | Recipient |
|-------|-----------|-----------|
| Add team member | **Invitation Email** 📨 | New member |
| Edit permissions | **Access Update** 🔄 | Team member |
| Deactivate account | **Deactivation Notice** ⚠️ | Team member |
| Activate account | **Activation Notice** ✅ | Team member |
| Accept invitation | **Welcome Email** 🎉 | New member |

## 🔧 Admin Actions

### Add Team Member
1. Go to Team Management
2. Click "Add Team Member"
3. Fill form → Submit
4. ✉️ Email sent automatically!

### Resend Invitation
- Click 📧 icon next to "Pending Invitation" status
- New link generated and sent

### Update Access
- Click ✏️ edit icon
- Change role/permissions
- ✉️ Notification sent automatically!

## 🔗 Invitation Process

```
Recruiter adds member
    ↓
Email sent with unique link (valid 7 days)
    ↓
Member clicks link
    ↓
Creates account OR logs in
    ↓
Welcome email sent
    ↓
Access granted! ✅
```

## 📝 Files Reference

```
ProRecruiterAI/
├── settings.py              # SMTP config here
├── accounts/
│   ├── email_utils.py       # Email functions
│   ├── views.py             # Updated with email sending
│   ├── models.py            # TeamMember with tokens
│   └── templates/accounts/emails/
│       ├── team_invitation.html
│       ├── access_update.html
│       ├── account_deactivated.html
│       └── welcome_team_member.html
├── SMTP_SETUP_GUIDE.md      # Full setup guide
├── TEAM_MEMBER_SMTP_SUMMARY.md  # Implementation details
└── test_smtp_emails.py      # Test script
```

## 🧪 Testing

```bash
# Run email tests
python test_smtp_emails.py

# Expected output:
# ✅ Basic Email: PASSED
# ✅ Team Invitation Email: PASSED
# 🎉 All tests passed!
```

## 🛠️ Configuration Options

### Development (Current):
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```
✅ Emails display in terminal  
✅ No SMTP setup needed  
✅ Perfect for testing  

### Production with Gmail:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your@gmail.com'
EMAIL_HOST_PASSWORD = 'app-password-16-chars'
```

### Production with SendGrid:
```python
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = 'your-sendgrid-key'
```

## 🎨 Customization

### Change email colors:
Edit `accounts/templates/accounts/emails/*.html`
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
/* Change to your brand colors */
```

### Add logo:
```html
<div class="header">
    <img src="your-logo.png" alt="Logo">
    <h1>Title</h1>
</div>
```

## 🔒 Security

- ✅ Unique UUID tokens per invitation
- ✅ 7-day expiration
- ✅ One-time use (marked as accepted)
- ✅ Email verification
- ✅ Recruiter-only access

## 📊 Status Indicators

| Badge | Meaning |
|-------|---------|
| 🟡 Pending Invitation | Not accepted yet |
| 🟢 Active | Working member |
| ⚫ Inactive | Deactivated |

## ⚡ Quick Commands

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Start server
python manage.py runserver

# Test emails
python test_smtp_emails.py

# Django shell (test sending)
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Message', 'from@test.com', ['to@test.com'])
```

## 🐛 Common Issues

**Problem:** Emails not in console  
**Fix:** Check `EMAIL_BACKEND` is set to console

**Problem:** Gmail not working  
**Fix:** Use App Password, not regular password

**Problem:** Invitation link expired  
**Fix:** Click 📧 to resend with new link

**Problem:** "Invalid invitation"  
**Fix:** Verify URL is complete, ask recruiter to resend

## 📚 Documentation

- **Setup:** `SMTP_SETUP_GUIDE.md`
- **Details:** `TEAM_MEMBER_SMTP_SUMMARY.md`
- **This file:** `QUICK_REFERENCE.md`

## ✅ Checklist

- [x] SMTP configuration added
- [x] Email templates created
- [x] Invitation system working
- [x] Database migrations applied
- [x] Tests passing
- [x] Documentation complete

## 🎯 Next Steps

1. ✅ Test with development console backend
2. ⭕ Configure production SMTP
3. ⭕ Customize email branding
4. ⭕ Deploy and monitor

---

**Version:** 1.0  
**Status:** ✅ Production Ready  
**Last Updated:** February 11, 2026
