"""
Email utilities for Gravix backend.
Provides reusable email sending functions for bookings, assessments, authentication, etc.
"""
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from typing import Optional


def send_email(
    subject: str,
    message: str,
    recipient_list: list[str],
    html_message: Optional[str] = None,
    fail_silently: bool = False,
) -> int:
    """
    Send an email using Django's email system.

    Args:
        subject: Email subject line
        message: Plain text message
        recipient_list: List of recipient email addresses
        html_message: Optional HTML message
        fail_silently: If True, suppress errors

    Returns:
        Number of emails sent (0 or 1 typically)
    """
    return send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_FROM,
        recipient_list=recipient_list,
        html_message=html_message,
        fail_silently=fail_silently,
    )


def send_booking_confirmation(
    student_email: str,
    student_name: str,
    counselor_name: str,
    session_type: str,
    date_time: str,
    meeting_link: Optional[str] = None,
    location: Optional[str] = None,
) -> bool:
    """Send booking confirmation email to student."""
    session_info = {
        'video': f'Meeting Link: {meeting_link}' if meeting_link else 'Video session',
        'in-person': f'Location: {location}' if location else 'In-person session',
        'phone': 'Phone session - counselor will call you',
    }

    html_content = f"""
    <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <h2 style="color: #667eea;">Hello {student_name},</h2>
        <p>Your session has been confirmed! Here are the details:</p>
        <div style="background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <p><strong>Date & Time:</strong> {date_time}</p>
            <p><strong>Counselor:</strong> {counselor_name}</p>
            <p><strong>Session Type:</strong> {session_type}</p>
            <p><strong>Details:</strong> {session_info.get(session_type, '')}</p>
        </div>
        <p>Please log in to your Gravix dashboard to view or manage your bookings.</p>
        <p>Best regards,<br>The Gravix Team</p>
    </div>
    """

    try:
        send_mail(
            subject='Session Booking Confirmed - Gravix',
            message=f'''Hello {student_name},

Your session has been confirmed!

Date & Time: {date_time}
Counselor: {counselor_name}
Session Type: {session_type}
Details: {session_info.get(session_type, '')}

Please log in to your Gravix dashboard to view or manage your bookings.

Best regards,
The Gravix Team''',
            from_email=settings.EMAIL_FROM,
            recipient_list=[student_email],
            html_message=html_content,
        )
        return True
    except Exception:
        return False


def send_assessment_reminder(
    user_email: str,
    user_name: str,
    assessment_type: str,
    due_date: Optional[str] = None,
) -> bool:
    """Send assessment reminder email."""
    descriptions = {
        'PHQ-9': 'Depression screening questionnaire',
        'GAD-7': 'Anxiety screening questionnaire',
        'PSQI': 'Sleep quality assessment',
    }

    due_date_text = f'<p><strong>Due Date:</strong> {due_date}</p>' if due_date else ''

    html_content = f"""
    <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <h2 style="color: #667eea;">Hello {user_name},</h2>
        <p>This is a friendly reminder to complete your {assessment_type} assessment.</p>
        <p><strong>Assessment:</strong> {assessment_type} - {descriptions.get(assessment_type, '')}</p>
        {due_date_text}
        <p>Regular assessments help you track your mental wellness over time.</p>
        <p>Best regards,<br>The Gravix Team</p>
    </div>
    """

    try:
        send_mail(
            subject=f'Reminder: Complete Your {assessment_type} Assessment - Gravix',
            message=f'''Hello {user_name},

This is a friendly reminder to complete your {assessment_type} assessment.
Assessment: {assessment_type} - {descriptions.get(assessment_type, '')}
{"Due Date: " + due_date if due_date else ""}

Regular assessments help you track your mental wellness over time.

Best regards,
The Gravix Team''',
            from_email=settings.EMAIL_FROM,
            recipient_list=[user_email],
            html_message=html_content,
        )
        return True
    except Exception:
        return False


def send_account_verification(
    user_email: str,
    user_name: str,
    verification_url: str,
) -> bool:
    """Send account verification email with URL."""
    html_content = f"""
    <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <h2 style="color: #667eea;">Hello {user_name},</h2>
        <p>Thank you for creating an account on Gravix. Please verify your email address by clicking the button below:</p>
        <div style="text-align: center; margin: 30px 0;">
            <a href="{verification_url}" style="background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">Verify Email Address</a>
        </div>
        <p>Or copy and paste this link into your browser:</p>
        <p style="word-break: break-all; color: #667eea;">{verification_url}</p>
        <p>This verification link will expire in 24 hours.</p>
        <p>Best regards,<br>The Gravix Team</p>
    </div>
    """

    try:
        send_mail(
            subject='Verify Your Email Address - Gravix',
            message=f'''Hello {user_name},

Thank you for creating an account on Gravix. Please verify your email address by visiting this link:
{verification_url}

This verification link will expire in 24 hours.

Best regards,
The Gravix Team''',
            from_email=settings.EMAIL_FROM,
            recipient_list=[user_email],
            html_message=html_content,
        )
        return True
    except Exception:
        return False


def send_account_verification_code(
    user_email: str,
    user_name: str,
    code: str,
    expires_in_minutes: int = 10,
) -> bool:
    """Send account verification email with 6-digit OTP code."""
    html_content = f"""
    <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <h2 style="color: #667eea;">Hello {user_name},</h2>
        <p>Thank you for creating an account on Gravix. Your verification code is:</p>
        <div style="background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: center;">
            <p style="font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #667eea; margin: 0;">{code}</p>
        </div>
        <p>This code will expire in {expires_in_minutes} minutes.</p>
        <p>If you didn't create an account on Gravix, please ignore this email.</p>
        <p>Best regards,<br>The Gravix Team</p>
    </div>
    """

    try:
        send_mail(
            subject='Your Verification Code - Gravix',
            message=f'''Hello {user_name},

Thank you for creating an account on Gravix. Your verification code is:

{code}

This code will expire in {expires_in_minutes} minutes.

If you didn't create an account on Gravix, please ignore this email.

Best regards,
The Gravix Team''',
            from_email=settings.EMAIL_FROM,
            recipient_list=[user_email],
            html_message=html_content,
        )
        return True
    except Exception:
        return False


def send_password_reset(
    user_email: str,
    user_name: str,
    reset_url: str,
) -> bool:
    """Send password reset email."""
    html_content = f"""
    <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <h2 style="color: #667eea;">Hello {user_name},</h2>
        <p>We received a request to reset your password. Click the button below to create a new password:</p>
        <div style="text-align: center; margin: 30px 0;">
            <a href="{reset_url}" style="background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">Reset Password</a>
        </div>
        <p>Or copy and paste this link into your browser:</p>
        <p style="word-break: break-all; color: #667eea;">{reset_url}</p>
        <p>This reset link will expire in 1 hour.</p>
        <p>If you didn't request this, please ignore this email and your password will remain unchanged.</p>
        <p>Best regards,<br>The Gravix Team</p>
    </div>
    """

    try:
        send_mail(
            subject='Reset Your Password - Gravix',
            message=f'''Hello {user_name},

We received a request to reset your password. Visit this link to create a new password:
{reset_url}

This reset link will expire in 1 hour.

If you didn't request this, please ignore this email and your password will remain unchanged.

Best regards,
The Gravix Team''',
            from_email=settings.EMAIL_FROM,
            recipient_list=[user_email],
            html_message=html_content,
        )
        return True
    except Exception:
        return False


def send_counselor_booking_notification(
    counselor_email: str,
    counselor_name: str,
    student_name: str,
    session_type: str,
    date_time: str,
    student_notes: Optional[str] = None,
    meeting_link: Optional[str] = None,
    location: Optional[str] = None,
) -> bool:
    """Send booking notification email to counselor."""
    session_info = {
        'video': f'Meeting Link: {meeting_link}' if meeting_link else 'Video session',
        'in-person': f'Location: {location}' if location else 'In-person session',
        'phone': 'Phone session',
    }

    notes_text = f'<p><strong>Student Notes:</strong> {student_notes}</p>' if student_notes else ''

    html_content = f"""
    <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <h2 style="color: #667eea;">Hello {counselor_name},</h2>
        <p>You have a new session booking!</p>
        <div style="background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <p><strong>Date & Time:</strong> {date_time}</p>
            <p><strong>Student:</strong> {student_name}</p>
            <p><strong>Session Type:</strong> {session_type}</p>
            <p><strong>Details:</strong> {session_info.get(session_type, '')}</p>
            {notes_text}
        </div>
        <p>Please log in to your Gravix counselor dashboard to manage your schedule.</p>
        <p>Best regards,<br>The Gravix Team</p>
    </div>
    """

    try:
        send_mail(
            subject='New Session Booking - Gravix',
            message=f'''Hello {counselor_name},

You have a new session booking!

Date & Time: {date_time}
Student: {student_name}
Session Type: {session_type}
Details: {session_info.get(session_type, '')}
{"Student Notes: " + student_notes if student_notes else ""}

Please log in to your Gravix counselor dashboard to manage your schedule.

Best regards,
The Gravix Team''',
            from_email=settings.EMAIL_FROM,
            recipient_list=[counselor_email],
            html_message=html_content,
        )
        return True
    except Exception:
        return False
