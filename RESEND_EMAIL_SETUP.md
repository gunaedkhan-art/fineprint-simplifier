# 📧 Resend Email Integration Setup

## Overview

Small Print Checker uses [Resend](https://resend.com) for all transactional emails:
- ✅ Welcome emails on registration
- ✅ Password reset emails
- ✅ Password changed notifications
- ✅ Monthly limit reminders (optional)

## Quick Setup (5 minutes)

### 1. Create Resend Account

1. Go to https://resend.com
2. Sign up for a free account
3. Get 10,000 free emails/month (more than enough!)

### 2. Get Your API Key

1. Go to **API Keys** in Resend dashboard
2. Click **Create API Key**
3. Name it: `Small Print Checker Production`
4. Copy the API key (starts with `re_...`)

### 3. Configure Railway Environment Variables

**In Railway Dashboard:**

```bash
# Required
RESEND_API_KEY=re_your_api_key_here

# Optional (defaults shown)
FROM_EMAIL=noreply@smallprintchecker.com
SITE_URL=https://smallprintchecker.com
```

**Or via Railway CLI:**

```bash
railway variables set RESEND_API_KEY=re_your_api_key_here
railway variables set FROM_EMAIL=noreply@smallprintchecker.com
railway variables set SITE_URL=https://smallprintchecker.com
```

### 4. Verify Your Domain (Optional but Recommended)

**Without Domain Verification:**
- ✅ Emails work immediately
- ⚠️ From: `noreply@smallprintchecker.com` (may go to spam)
- ⚠️ Limited to 100 emails/day

**With Domain Verification:**
- ✅ Better deliverability
- ✅ Professional from address
- ✅ Full 10,000 emails/month
- ✅ Less likely to go to spam

**How to verify:**

1. In Resend dashboard, go to **Domains**
2. Click **Add Domain**
3. Enter: `smallprintchecker.com`
4. Add the DNS records to your domain provider:
   - **TXT record** for verification
   - **MX records** for email sending
5. Wait for verification (usually 5-15 minutes)

### 5. Test the Integration

After deployment, test each email type:

**Welcome Email:**
```bash
# Register a new account
# Check email inbox
```

**Password Reset:**
```bash
# Go to /forgot-password
# Enter your email
# Check email inbox for reset link
```

**Password Changed:**
```bash
# Reset your password
# Check email inbox for confirmation
```

## Development Mode (No Resend Configured)

When `RESEND_API_KEY` is not set:
- ✅ App still works normally
- ⚠️ No emails are sent
- 🔧 Password reset links displayed on screen instead
- 📝 Console logs show "Email service not configured"

This allows local development without Resend.

## Email Templates

All email templates are in `email_service.py` with:
- 📱 Responsive HTML design
- 🎨 Brand colors (blue gradient)
- 🔗 Clickable buttons
- 📊 Clear call-to-actions
- 🔒 Security warnings where appropriate

## Monitoring

Check email delivery in Resend dashboard:
- **Logs** tab shows all sent emails
- **Analytics** shows open rates
- **Bounces** shows delivery failures

## Troubleshooting

### Emails Not Sending

**Check:**
1. ✅ `RESEND_API_KEY` is set in Railway
2. ✅ API key is valid (check Resend dashboard)
3. ✅ Railway logs show "✓ email service imported successfully"
4. ✅ Railway logs show "✓ Email sent: ..." after actions

### Emails Going to Spam

**Fix:**
1. Verify your domain in Resend
2. Add SPF and DKIM records
3. Use a professional from address
4. Test with different email providers

### Rate Limits

**Free Tier:**
- 10,000 emails/month (unverified domain: 100/day)
- More than enough for most use cases

**If you exceed:**
- Resend has paid plans starting at $20/month for 50k emails
- Very cost-effective

## Cost Analysis

**Your Expected Usage:**
- New registrations: ~50-100/month = 100 emails
- Password resets: ~20-30/month = 30 emails
- Password changes: ~10/month = 10 emails
- **Total: ~140 emails/month**

**Resend Free Tier: 10,000 emails/month**

**You're using: 1.4% of the free tier** ✅

You won't need to pay for a long time!

## Security Notes

- ✅ Resend uses TLS encryption
- ✅ API keys are stored securely in Railway
- ✅ No email content is logged
- ✅ Tokens expire (30 min for password reset)
- ✅ Secure password reset flow

## Alternative Email Services

If you prefer a different service:

### SendGrid
```python
# pip install sendgrid
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
```

### AWS SES
```python
# pip install boto3
import boto3
ses = boto3.client('ses')
```

### Mailgun
```python
# pip install requests
# Use Mailgun API
```

**But Resend is recommended for its simplicity and modern API.**

## Support

- 📚 Resend Docs: https://resend.com/docs
- 💬 Resend Support: support@resend.com
- 🐛 Issues: Check Railway logs for error messages

