"""
Email service using Resend API
Handles all transactional emails for the application
"""

import os
import resend
from typing import Optional

# Initialize Resend with API key from environment
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
FROM_EMAIL = os.environ.get("FROM_EMAIL", "noreply@smallprintchecker.com")
SITE_URL = os.environ.get("SITE_URL", "https://smallprintchecker.com")

# Only initialize if API key is present
if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY
    print("✓ Resend email service initialized")
else:
    print("⚠ RESEND_API_KEY not set - emails will not be sent")


class EmailService:
    """Service for sending transactional emails"""
    
    def __init__(self):
        self.enabled = bool(RESEND_API_KEY)
        self.from_email = FROM_EMAIL
        self.site_url = SITE_URL
    
    def send_email(self, to: str, subject: str, html: str) -> dict:
        """Send an email using Resend"""
        if not self.enabled:
            print(f"⚠ Email not sent (Resend not configured): {subject} to {to}")
            return {"success": False, "error": "Email service not configured"}
        
        try:
            response = resend.Emails.send({
                "from": self.from_email,
                "to": [to],
                "subject": subject,
                "html": html
            })
            print(f"✓ Email sent: {subject} to {to}")
            return {"success": True, "id": response.get("id")}
        except Exception as e:
            print(f"✗ Email failed: {subject} to {to} - Error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def send_welcome_email(self, email: str, username: str) -> dict:
        """Send welcome email to new user"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
                    color: white;
                    padding: 40px 20px;
                    text-align: center;
                    border-radius: 8px 8px 0 0;
                }}
                .content {{
                    background: #ffffff;
                    padding: 40px 30px;
                    border: 1px solid #e5e7eb;
                    border-top: none;
                }}
                .button {{
                    display: inline-block;
                    background: #2563eb;
                    color: white;
                    padding: 14px 28px;
                    text-decoration: none;
                    border-radius: 6px;
                    font-weight: 600;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    color: #6b7280;
                    font-size: 14px;
                    padding: 20px;
                    border-top: 1px solid #e5e7eb;
                }}
                .features {{
                    background: #f9fafb;
                    padding: 20px;
                    border-radius: 6px;
                    margin: 20px 0;
                }}
                .feature {{
                    margin: 10px 0;
                }}
                .feature-icon {{
                    color: #10b981;
                    font-weight: bold;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1 style="margin: 0; font-size: 28px;">Welcome to Small Print Checker! 🎉</h1>
            </div>
            
            <div class="content">
                <p style="font-size: 18px; margin-top: 0;">Hi {username},</p>
                
                <p>Thank you for joining Small Print Checker! We're excited to help you understand contracts and legal documents in plain English.</p>
                
                <div class="features">
                    <h3 style="margin-top: 0;">What you can do now:</h3>
                    <div class="feature"><span class="feature-icon">✓</span> Analyze up to 3 documents per month</div>
                    <div class="feature"><span class="feature-icon">✓</span> Detect potential risks and favorable terms</div>
                    <div class="feature"><span class="feature-icon">✓</span> Get detailed analysis with severity ratings</div>
                    <div class="feature"><span class="feature-icon">✓</span> Upload PDFs, Word docs, or paste text</div>
                </div>
                
                <p style="text-align: center;">
                    <a href="{self.site_url}/upload" class="button" style="display: inline-block; background: #2563eb; color: white; padding: 14px 28px; text-decoration: none; border-radius: 6px; font-weight: 600; margin: 20px 0;">Start Analyzing Documents</a>
                </p>
                
                <p>Need more? <a href="{self.site_url}/pricing">Upgrade to Pro</a> for unlimited analyses and advanced features.</p>
                
                <p style="margin-bottom: 0;">
                    Best regards,<br>
                    <strong>The Small Print Checker Team</strong>
                </p>
            </div>
            
            <div class="footer">
                <p>You received this email because you created an account at Small Print Checker.</p>
                <p><a href="{self.site_url}" style="color: #2563eb;">smallprintchecker.com</a></p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(
            to=email,
            subject=f"Welcome to Small Print Checker, {username}!",
            html=html
        )
    
    def send_password_reset_email(self, email: str, reset_token: str) -> dict:
        """Send password reset email with secure link"""
        reset_url = f"{self.site_url}/reset-password?token={reset_token}"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
                    color: white;
                    padding: 40px 20px;
                    text-align: center;
                    border-radius: 8px 8px 0 0;
                }}
                .content {{
                    background: #ffffff;
                    padding: 40px 30px;
                    border: 1px solid #e5e7eb;
                    border-top: none;
                }}
                .button {{
                    display: inline-block;
                    background: #2563eb;
                    color: white;
                    padding: 14px 28px;
                    text-decoration: none;
                    border-radius: 6px;
                    font-weight: 600;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    color: #6b7280;
                    font-size: 14px;
                    padding: 20px;
                    border-top: 1px solid #e5e7eb;
                }}
                .warning {{
                    background: #fef3c7;
                    border-left: 4px solid #f59e0b;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 4px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1 style="margin: 0; font-size: 28px;">Reset Your Password 🔐</h1>
            </div>
            
            <div class="content">
                <p style="font-size: 18px; margin-top: 0;">Password Reset Request</p>
                
                <p>We received a request to reset your password for Small Print Checker. If you didn't make this request, you can safely ignore this email.</p>
                
                <p style="text-align: center;">
                    <a href="{reset_url}" class="button" style="display: inline-block; background: #2563eb; color: white; padding: 14px 28px; text-decoration: none; border-radius: 6px; font-weight: 600; margin: 20px 0;">Reset My Password</a>
                </p>
                
                <div class="warning">
                    <strong>⏰ This link expires in 30 minutes</strong><br>
                    For security reasons, this password reset link will only work for 30 minutes.
                </div>
                
                <p>If the button doesn't work, copy and paste this URL into your browser:</p>
                <p style="word-break: break-all; background: #f9fafb; padding: 10px; border-radius: 4px; font-size: 14px;">
                    {reset_url}
                </p>
                
                <p style="margin-bottom: 0;">
                    Best regards,<br>
                    <strong>The Small Print Checker Team</strong>
                </p>
            </div>
            
            <div class="footer">
                <p>If you didn't request a password reset, please ignore this email.</p>
                <p><a href="{self.site_url}" style="color: #2563eb;">smallprintchecker.com</a></p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(
            to=email,
            subject="Reset Your Password - Small Print Checker",
            html=html
        )
    
    def send_password_changed_email(self, email: str, username: str = "there") -> dict:
        """Send notification that password was changed"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                    color: white;
                    padding: 40px 20px;
                    text-align: center;
                    border-radius: 8px 8px 0 0;
                }}
                .content {{
                    background: #ffffff;
                    padding: 40px 30px;
                    border: 1px solid #e5e7eb;
                    border-top: none;
                }}
                .button {{
                    display: inline-block;
                    background: #2563eb;
                    color: white;
                    padding: 14px 28px;
                    text-decoration: none;
                    border-radius: 6px;
                    font-weight: 600;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    color: #6b7280;
                    font-size: 14px;
                    padding: 20px;
                    border-top: 1px solid #e5e7eb;
                }}
                .alert {{
                    background: #fee2e2;
                    border-left: 4px solid #dc2626;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 4px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1 style="margin: 0; font-size: 28px;">Password Changed Successfully ✓</h1>
            </div>
            
            <div class="content">
                <p style="font-size: 18px; margin-top: 0;">Hi {username},</p>
                
                <p>This is a confirmation that your password for Small Print Checker has been successfully changed.</p>
                
                <div class="alert">
                    <strong>⚠️ Didn't make this change?</strong><br>
                    If you did not change your password, please contact us immediately and secure your account.
                </div>
                
                <p>You can now log in with your new password.</p>
                
                <p style="text-align: center;">
                    <a href="{self.site_url}/login" class="button" style="display: inline-block; background: #2563eb; color: white; padding: 14px 28px; text-decoration: none; border-radius: 6px; font-weight: 600; margin: 20px 0;">Go to Login</a>
                </p>
                
                <p style="margin-bottom: 0;">
                    Best regards,<br>
                    <strong>The Small Print Checker Team</strong>
                </p>
            </div>
            
            <div class="footer">
                <p>This is an automated security notification.</p>
                <p><a href="{self.site_url}" style="color: #2563eb;">smallprintchecker.com</a></p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(
            to=email,
            subject="Your Password Has Been Changed - Small Print Checker",
            html=html
        )
    
    def send_monthly_limit_reminder(self, email: str, username: str, documents_used: int, limit: int) -> dict:
        """Send reminder when approaching monthly limit"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
                    color: white;
                    padding: 40px 20px;
                    text-align: center;
                    border-radius: 8px 8px 0 0;
                }}
                .content {{
                    background: #ffffff;
                    padding: 40px 30px;
                    border: 1px solid #e5e7eb;
                    border-top: none;
                }}
                .button {{
                    display: inline-block;
                    background: #2563eb;
                    color: white;
                    padding: 14px 28px;
                    text-decoration: none;
                    border-radius: 6px;
                    font-weight: 600;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    color: #6b7280;
                    font-size: 14px;
                    padding: 20px;
                    border-top: 1px solid #e5e7eb;
                }}
                .usage-box {{
                    background: #fef3c7;
                    padding: 20px;
                    border-radius: 6px;
                    text-align: center;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1 style="margin: 0; font-size: 28px;">Monthly Limit Reminder 📊</h1>
            </div>
            
            <div class="content">
                <p style="font-size: 18px; margin-top: 0;">Hi {username},</p>
                
                <p>Just a friendly reminder about your document analysis usage:</p>
                
                <div class="usage-box">
                    <h2 style="margin: 0 0 10px 0; font-size: 36px; color: #d97706;">{documents_used}/{limit}</h2>
                    <p style="margin: 0; font-size: 18px; font-weight: 600;">Documents Analyzed This Month</p>
                </div>
                
                <p>Want unlimited analyses? Upgrade to Pro for just $9.99/month!</p>
                
                <p style="text-align: center;">
                    <a href="{self.site_url}/pricing" class="button" style="display: inline-block; background: #2563eb; color: white; padding: 14px 28px; text-decoration: none; border-radius: 6px; font-weight: 600; margin: 20px 0;">Upgrade to Pro</a>
                </p>
                
                <p style="margin-bottom: 0;">
                    Best regards,<br>
                    <strong>The Small Print Checker Team</strong>
                </p>
            </div>
            
            <div class="footer">
                <p><a href="{self.site_url}" style="color: #2563eb;">smallprintchecker.com</a></p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(
            to=email,
            subject=f"You've Used {documents_used}/{limit} Documents This Month",
            html=html
        )


# Global email service instance
email_service = EmailService()


# Helper functions for easy imports
def send_welcome_email(email: str, username: str) -> dict:
    """Send welcome email to new user"""
    return email_service.send_welcome_email(email, username)


def send_password_reset_email(email: str, reset_token: str) -> dict:
    """Send password reset email"""
    return email_service.send_password_reset_email(email, reset_token)


def send_password_changed_email(email: str, username: str = "there") -> dict:
    """Send password changed notification"""
    return email_service.send_password_changed_email(email, username)


def send_monthly_limit_reminder(email: str, username: str, documents_used: int, limit: int) -> dict:
    """Send monthly limit reminder"""
    return email_service.send_monthly_limit_reminder(email, username, documents_used, limit)

