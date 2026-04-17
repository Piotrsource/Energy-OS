"""
Email notification service using SendGrid.

Sends transactional alert emails when users have email notifications enabled.
Falls back gracefully (logs warning) if SendGrid is not configured.
"""

import logging
from app.config import settings

logger = logging.getLogger("energy_platform")

# Lazy-load the SendGrid client to avoid import errors when not installed
_sg_client = None


def _get_sendgrid_client():
    global _sg_client
    if _sg_client is not None:
        return _sg_client
    if not settings.sendgrid_api_key:
        return None
    try:
        from sendgrid import SendGridAPIClient
        _sg_client = SendGridAPIClient(settings.sendgrid_api_key)
        return _sg_client
    except ImportError:
        logger.warning("sendgrid package not installed — email notifications disabled")
        return None


async def send_alert_email(
    to_email: str,
    subject: str,
    body_text: str,
    severity: str = "medium",
) -> bool:
    """
    Send an alert notification email via SendGrid.

    Returns True on success, False on failure (never raises).
    """
    client = _get_sendgrid_client()
    if client is None:
        logger.debug("SendGrid not configured — skipping email to %s", to_email)
        return False

    try:
        from sendgrid.helpers.mail import Mail, Email, To, Content

        severity_emoji = {
            "low": "",
            "medium": "",
            "high": "",
            "critical": "",
        }
        emoji = severity_emoji.get(severity, "")

        message = Mail(
            from_email=Email(settings.from_email, "Energy Platform Alerts"),
            to_emails=To(to_email),
            subject=f"{emoji} [{severity.upper()}] {subject}",
            plain_text_content=Content("text/plain", body_text),
        )

        # Build HTML version
        html_body = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #1a1a2e; color: white; padding: 20px 24px; border-radius: 8px 8px 0 0;">
                <h2 style="margin: 0; font-size: 18px;">Energy Platform Alert</h2>
            </div>
            <div style="background: #ffffff; border: 1px solid #e5e7eb; padding: 24px; border-radius: 0 0 8px 8px;">
                <div style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 12px 16px; margin-bottom: 16px; border-radius: 4px;">
                    <strong>Severity:</strong> {severity.upper()}
                </div>
                <h3 style="margin: 0 0 8px 0; color: #111827;">{subject}</h3>
                <p style="color: #6b7280; line-height: 1.6;">{body_text}</p>
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;">
                <p style="color: #9ca3af; font-size: 12px;">
                    You received this because you have email alerts enabled.
                    Update your preferences in the Energy Platform dashboard.
                </p>
            </div>
        </div>
        """
        message.add_content(Content("text/html", html_body))

        response = client.send(message)
        if response.status_code in (200, 201, 202):
            logger.info("Alert email sent to %s (status=%d)", to_email, response.status_code)
            return True
        else:
            logger.warning("SendGrid returned status %d for email to %s", response.status_code, to_email)
            return False

    except Exception:
        logger.exception("Failed to send alert email to %s", to_email)
        return False
