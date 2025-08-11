"""
Email service for sending authentication-related emails
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging
from app.core.config import settings
from app.core.shop_manager import get_shop_config

logger = logging.getLogger(__name__)

class EmailService:
    """Email service for sending notifications"""
    
    def __init__(self):
        self.smtp_server = getattr(settings, 'SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = getattr(settings, 'SMTP_PORT', 587)
        self.smtp_username = getattr(settings, 'SMTP_USERNAME', None)
        self.smtp_password = getattr(settings, 'SMTP_PASSWORD', None)
        self.from_email = getattr(settings, 'FROM_EMAIL', 'noreply@nhan88ng.com')
        self.from_name = getattr(settings, 'FROM_NAME', 'Nhan88ng API')
    
    def send_email(
        self, 
        to_email: str, 
        subject: str, 
        html_content: str, 
        text_content: Optional[str] = None
    ) -> bool:
        """Send email using SMTP"""
        try:
            # Skip email sending if no SMTP credentials configured
            if not self.smtp_username or not self.smtp_password:
                logger.warning(f"Email sending skipped - no SMTP credentials configured. Would send to: {to_email}, Subject: {subject}")
                return True
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            
            # Add text and HTML parts
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)
            
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

# Initialize email service
email_service = EmailService()

def send_verification_email(email: str, full_name: str, verification_token: str, shop: str = None) -> bool:
    """Send email verification email"""
    # Get shop-specific frontend URL or fallback to default
    if shop:
        shop_config = get_shop_config(shop)
        frontend_url = shop_config.frontend_url if shop_config else settings.FRONTEND_URL
    else:
        frontend_url = settings.FRONTEND_URL
    
    verification_url = f"{frontend_url}/verify-email?token={verification_token}"
    
    subject = "Verify Your Email - Nhan88ng Platform"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Email Verification</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
            .content {{ padding: 30px; background: #f9f9f9; }}
            .button {{ display: inline-block; padding: 12px 24px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            .footer {{ padding: 20px; text-align: center; color: #666; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Welcome to Nhan88ng Platform!</h1>
            </div>
            <div class="content">
                <h2>Hello {full_name},</h2>
                <p>Thank you for registering with Nhan88ng Platform. To complete your registration, please verify your email address by clicking the button below:</p>
                
                <div style="text-align: center;">
                    <a href="{verification_url}" class="button">Verify Email Address</a>
                </div>
                
                <p>Or copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #667eea;">{verification_url}</p>
                
                <p>This verification link will expire in 24 hours for security reasons.</p>
                
                <p>If you didn't create an account with us, please ignore this email.</p>
                
                <p>Best regards,<br>The Nhan88ng Team</p>
            </div>
            <div class="footer">
                <p>&copy; 2024 Nhan88ng Platform. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Welcome to Nhan88ng Platform!
    
    Hello {full_name},
    
    Thank you for registering with Nhan88ng Platform. To complete your registration, please verify your email address by visiting:
    
    {verification_url}
    
    This verification link will expire in 24 hours for security reasons.
    
    If you didn't create an account with us, please ignore this email.
    
    Best regards,
    The Nhan88ng Team
    """
    
    return email_service.send_email(email, subject, html_content, text_content)

def send_password_reset_email(email: str, full_name: str, reset_token: str, shop: str = None) -> bool:
    """Send password reset email"""
    # Get shop-specific frontend URL or fallback to default
    if shop:
        shop_config = get_shop_config(shop)
        frontend_url = shop_config.frontend_url if shop_config else settings.FRONTEND_URL
    else:
        frontend_url = settings.FRONTEND_URL
    
    reset_url = f"{frontend_url}/reset-password?token={reset_token}"
    
    subject = "Password Reset Request - Nhan88ng Platform"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Password Reset</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
            .content {{ padding: 30px; background: #f9f9f9; }}
            .button {{ display: inline-block; padding: 12px 24px; background: #dc3545; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            .footer {{ padding: 20px; text-align: center; color: #666; font-size: 14px; }}
            .warning {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Password Reset Request</h1>
            </div>
            <div class="content">
                <h2>Hello {full_name},</h2>
                <p>We received a request to reset your password for your Nhan88ng Platform account.</p>
                
                <div class="warning">
                    <strong>⚠️ Security Notice:</strong> If you didn't request this password reset, please ignore this email and your password will remain unchanged.
                </div>
                
                <p>To reset your password, click the button below:</p>
                
                <div style="text-align: center;">
                    <a href="{reset_url}" class="button">Reset Password</a>
                </div>
                
                <p>Or copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #667eea;">{reset_url}</p>
                
                <p>This password reset link will expire in 1 hour for security reasons.</p>
                
                <p>Best regards,<br>The Nhan88ng Team</p>
            </div>
            <div class="footer">
                <p>&copy; 2024 Nhan88ng Platform. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Password Reset Request - Nhan88ng Platform
    
    Hello {full_name},
    
    We received a request to reset your password for your Nhan88ng Platform account.
    
    SECURITY NOTICE: If you didn't request this password reset, please ignore this email and your password will remain unchanged.
    
    To reset your password, visit:
    {reset_url}
    
    This password reset link will expire in 1 hour for security reasons.
    
    Best regards,
    The Nhan88ng Team
    """
    
    return email_service.send_email(email, subject, html_content, text_content)

def send_welcome_email(email: str, full_name: str, shop: str) -> bool:
    """Send welcome email after successful verification"""
    subject = f"Welcome to {shop.title()} - Nhan88ng Platform"
    
    # Get shop-specific frontend URL or fallback to default
    shop_config = get_shop_config(shop)
    if shop_config:
        shop_url = shop_config.frontend_url
        shop_name = shop_config.name
    else:
        shop_url = settings.FRONTEND_URL
        shop_name = shop.title()
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Welcome</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
            .content {{ padding: 30px; background: #f9f9f9; }}
            .button {{ display: inline-block; padding: 12px 24px; background: #28a745; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            .footer {{ padding: 20px; text-align: center; color: #666; font-size: 14px; }}
            .features {{ background: white; padding: 20px; border-radius: 5px; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎉 Welcome to {shop.title()}!</h1>
            </div>
            <div class="content">
                <h2>Hello {full_name},</h2>
                <p>Congratulations! Your email has been verified and your account is now active.</p>
                
                <div class="features">
                    <h3>What you can do now:</h3>
                    <ul>
                        <li>Browse our exclusive product collection</li>
                        <li>Add items to your cart and wishlist</li>
                        <li>Track your orders in real-time</li>
                        <li>Manage your profile and preferences</li>
                        <li>Enjoy personalized recommendations</li>
                    </ul>
                </div>
                
                <div style="text-align: center;">
                    <a href="{shop_url}" class="button">Start Shopping</a>
                </div>
                
                <p>If you have any questions or need assistance, feel free to contact our support team.</p>
                
                <p>Happy shopping!<br>The {shop.title()} Team</p>
            </div>
            <div class="footer">
                <p>&copy; 2024 Nhan88ng Platform. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Welcome to {shop.title()}!
    
    Hello {full_name},
    
    Congratulations! Your email has been verified and your account is now active.
    
    What you can do now:
    - Browse our exclusive product collection
    - Add items to your cart and wishlist  
    - Track your orders in real-time
    - Manage your profile and preferences
    - Enjoy personalized recommendations
    
    Start shopping: {shop_url}
    
    If you have any questions or need assistance, feel free to contact our support team.
    
    Happy shopping!
    The {shop.title()} Team
    """
    
    return email_service.send_email(email, subject, html_content, text_content)
