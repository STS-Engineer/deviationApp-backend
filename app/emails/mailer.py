import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


def send_email(to_email: str, subject: str, html_body: str, cc_emails: list = None):
    """
    Send email using SMTP (Outlook or standard SMTP server)
    Supports both authenticated and unauthenticated SMTP
    """
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = settings.SMTP_FROM
        msg["To"] = to_email
        msg["Subject"] = subject
        
        if cc_emails:
            msg["Cc"] = ", ".join(cc_emails)
        
        msg.attach(MIMEText(html_body, "html"))

        recipients = [to_email]
        if cc_emails:
            recipients.extend(cc_emails)

        # Try to use SMTP with TLS (for Outlook/Office 365)
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
            # Try STARTTLS for encrypted connection if on port 587
            try:
                if settings.SMTP_PORT == 587:
                    server.starttls()
                    logger.debug("STARTTLS connection established")
            except Exception as e:
                logger.debug(f"STARTTLS not available: {str(e)}")
            
            # Try to authenticate if credentials are provided
            try:
                if settings.SMTP_USER and settings.SMTP_PASSWORD:
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                    logger.debug(f"Authenticated as {settings.SMTP_USER}")
            except smtplib.SMTPAuthenticationError:
                # Server might not support AUTH, continue anyway
                logger.debug("SMTP AUTH not supported or credentials invalid, continuing without authentication")
            except smtplib.SMTPNotSupportedError:
                # AUTH extension not supported
                logger.debug("SMTP AUTH extension not supported by server, continuing without authentication")
            
            # Send email
            server.sendmail(
                settings.SMTP_FROM,
                recipients,
                msg.as_string(),
            )
            logger.info(f"Email sent successfully to {to_email}")
        
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        # Log but don't re-raise - we want the request to succeed even if email fails
        return False
    
    return True


def send_pricing_request_email(
    to_email: str,
    project_name: str,
    customer: str,
    initial_price: float,
    target_price: float,
    request_id: int,
    costing_number: str = "",
    cc_emails: list = None,
):
    """Send pricing request notification to PL Responsible"""
    subject = f"Action required – Pricing deviation request ({costing_number})"

    request_link = (
        f"{settings.FRONTEND_BASE_URL}"
        f"/pl/{request_id}"
    )

    price_diff = initial_price - target_price
    price_diff_pct = ((price_diff / initial_price) * 100) if initial_price > 0 else 0

    html_body = f"""
    <html>
      <body style="margin:0;padding:0;background:#f4f6f8;
                   font-family:Arial,Helvetica,sans-serif;">
        <table width="100%" cellpadding="0" cellspacing="0">
          <tr>
            <td align="center" style="padding:24px;">
              <table width="600" cellpadding="0" cellspacing="0"
                     style="background:#ffffff;border-radius:8px;
                            box-shadow:0 2px 8px rgba(0,0,0,0.08);">

                <!-- HEADER -->
                <tr>
                  <td style="background:#0f2a44;
                             padding:16px 24px;color:#ffffff;">
                    <strong>🎯 AVO Carbon – Pricing Deviation Request</strong>
                  </td>
                </tr>

                <!-- BODY -->
                <tr>
                  <td style="padding:24px;color:#333;font-size:14px;
                             line-height:1.6;">
                    <p>Hello,</p>

                    <p>
                      A new pricing deviation request requires your review and decision.
                    </p>

                    <table width="100%" cellpadding="0" cellspacing="0"
                           style="background:#f7f9fb;
                                  border-left:4px solid #0b5ed7;
                                  padding:14px;margin:16px 0;">
                      <tr>
                        <td>
                          <p style="margin:6px 0;"><strong>Costing #:</strong> {costing_number}</p>
                          <p style="margin:6px 0;"><strong>Project:</strong> {project_name}</p>
                          <p style="margin:6px 0;"><strong>Customer:</strong> {customer}</p>
                          <p style="margin:6px 0;"><strong>Initial Price:</strong> €{initial_price:.2f}</p>
                          <p style="margin:6px 0;"><strong>Target Price:</strong> <span style="color:#dc3545;font-weight:bold;">€{target_price:.2f}</span></p>
                          <p style="margin:6px 0;"><strong>Difference:</strong> <span style="color:#dc3545;">-€{price_diff:.2f} ({price_diff_pct:.1f}%)</span></p>
                        </td>
                      </tr>
                    </table>

                    <p style="text-align:center;margin:24px 0;">
                      <a href="{request_link}"
                         style="background:#0b5ed7;color:#ffffff;
                                text-decoration:none;padding:12px 24px;
                                border-radius:6px;font-weight:bold;
                                display:inline-block;font-size:16px;">
                        👁️ Review Request
                      </a>
                    </p>

                    <p style="background:#e7f3ff;border:1px solid #b3d9ff;
                              padding:12px;border-radius:6px;margin:16px 0;">
                      <strong>Your options:</strong>
                      <ul style="margin:8px 0;">
                        <li>✅ Approve the target price</li>
                        <li>💬 Suggest an alternative price with comments</li>
                        <li>⛔ Reject with justification</li>
                        <li>🔺 Escalate to VP for final decision</li>
                      </ul>
                    </p>

                    <p style="margin-top:24px;color:#666;font-size:12px;">
                      Please respond within 24 hours to ensure timely decision-making.
                    </p>

                    <p style="margin-top:24px;border-top:1px solid #e3e7ec;
                              padding-top:16px;">
                      Kind regards,<br/>
                      <strong>Pricing Deviation System</strong><br/>
                      AVO Carbon Group
                    </p>
                  </td>
                </tr>

                <!-- FOOTER -->
                <tr>
                  <td style="background:#f1f3f6;padding:12px;
                             font-size:11px;color:#777;text-align:center;">
                    This is an automated message. Please do not reply to this email.
                  </td>
                </tr>

              </table>
            </td>
          </tr>
        </table>
      </body>
    </html>
    """

    send_email(to_email, subject, html_body, cc_emails)


def send_pl_decision_to_commercial(
    to_email: str,
    project_name: str,
    decision: str,
    comments: str = None,
    suggested_price: float = None,
    costing_number: str = "",
    cc_emails: list = None,
):
    """Send PL decision back to commercial"""
    
    decision_icon = {
        "APPROVED_BY_PL": "✅",
        "BACK_TO_COMMERCIAL": "⚠️",
        "ESCALATED_TO_VP": "🔺",
    }.get(decision, "📋")
    
    decision_color = {
        "APPROVED_BY_PL": "#198754",
        "BACK_TO_COMMERCIAL": "#ffc107",
        "ESCALATED_TO_VP": "#0d6efd",
    }.get(decision, "#666")
    
    subject = f"Pricing deviation – Product Line decision ({costing_number})"

    comment_block = (
        f"""
        <p style="background:#fff3cd;border-left:4px solid #ffc107;
                  padding:12px;border-radius:6px;margin:12px 0;">
          <strong>📝 PL Comments:</strong><br/>
          {comments}
        </p>
        """
        if comments
        else ""
    )
    
    suggested_price_block = (
        f"""
        <p style="background:#e7f3ff;border-left:4px solid #0b5ed7;
                  padding:12px;border-radius:6px;margin:12px 0;">
          <strong>💰 Suggested Price:</strong> €{suggested_price:.2f}
        </p>
        """
        if suggested_price
        else ""
    )

    html_body = f"""
    <html>
      <body style="margin:0;padding:0;background:#f4f6f8;
                   font-family:Arial,Helvetica,sans-serif;">
        <table width="100%" cellpadding="0" cellspacing="0">
          <tr>
            <td align="center" style="padding:24px;">
              <table width="600" cellpadding="0" cellspacing="0"
                     style="background:#ffffff;border-radius:8px;
                            box-shadow:0 2px 8px rgba(0,0,0,0.08);">

                <!-- HEADER -->
                <tr>
                  <td style="background:{decision_color};
                             padding:16px 24px;color:#ffffff;">
                    <strong>{decision_icon} Pricing Deviation – Product Line Decision</strong>
                  </td>
                </tr>

                <!-- BODY -->
                <tr>
                  <td style="padding:24px;color:#333;font-size:14px;
                             line-height:1.6;">
                    <p>Hello,</p>

                    <p>
                      Your pricing deviation request for
                      <strong>{project_name}</strong>
                      has been reviewed by the Product Line responsible.
                    </p>

                    <p style="background:#f7f9fb;border-left:4px solid {decision_color};
                              padding:12px;border-radius:6px;margin:16px 0;">
                      <strong>Decision:</strong><br/>
                      <span style="font-weight:bold;color:{decision_color};font-size:16px;">
                        {decision}
                      </span>
                    </p>

                    {comment_block}
                    {suggested_price_block}

                    <p style="margin-top:24px;">
                      Please log in to the application to review and proceed accordingly.
                    </p>

                    <p style="margin-top:24px;border-top:1px solid #e3e7ec;
                              padding-top:16px;">
                      Kind regards,<br/>
                      <strong>Pricing Deviation System</strong><br/>
                      AVO Carbon Group
                    </p>
                  </td>
                </tr>

                <!-- FOOTER -->
                <tr>
                  <td style="background:#f1f3f6;padding:12px;
                             font-size:11px;color:#777;text-align:center;">
                    This is an automated message. Please do not reply to this email.
                  </td>
                </tr>

              </table>
            </td>
          </tr>
        </table>
      </body>
    </html>
    """

    send_email(to_email, subject, html_body, cc_emails)


def send_escalation_to_vp(
    to_email: str,
    project_name: str,
    target_price: float,
    comments: str,
    initial_price: float = None,
    pl_name: str = "",
    costing_number: str = "",
    cc_emails: list = None,
):
    """Send escalation notice to VP"""
    subject = f"Action required – Pricing deviation escalation ({costing_number})"

    price_block = ""
    if initial_price:
        price_diff = initial_price - target_price
        price_diff_pct = ((price_diff / initial_price) * 100) if initial_price > 0 else 0
        price_block = f"""
        <p style="margin:6px 0;"><strong>Initial Price:</strong> €{initial_price:.2f}</p>
        <p style="margin:6px 0;"><strong>Target Price:</strong> <span style="color:#dc3545;">€{target_price:.2f}</span></p>
        <p style="margin:6px 0;"><strong>Difference:</strong> <span style="color:#dc3545;">-€{price_diff:.2f} ({price_diff_pct:.1f}%)</span></p>
        """

    html_body = f"""
    <html>
      <body style="margin:0;padding:0;background:#f4f6f8;
                   font-family:Arial,Helvetica,sans-serif;">
        <table width="100%" cellpadding="0" cellspacing="0">
          <tr>
            <td align="center" style="padding:24px;">
              <table width="600" cellpadding="0" cellspacing="0"
                     style="background:#ffffff;border-radius:8px;
                            box-shadow:0 2px 8px rgba(0,0,0,0.08);">

                <!-- HEADER -->
                <tr>
                  <td style="background:#0d6efd;
                             padding:16px 24px;color:#ffffff;">
                    <strong>🔺 AVO Carbon – Pricing Deviation Escalation</strong>
                  </td>
                </tr>

                <!-- BODY -->
                <tr>
                  <td style="padding:24px;color:#333;font-size:14px;
                             line-height:1.6;">
                    <p>Hello,</p>

                    <p>
                      A pricing deviation request for
                      <strong>{project_name}</strong>
                      has been escalated to you for final decision.
                    </p>

                    <table width="100%" cellpadding="0" cellspacing="0"
                           style="background:#f7f9fb;
                                  border-left:4px solid #0d6efd;
                                  padding:14px;margin:16px 0;">
                      <tr>
                        <td>
                          <p style="margin:6px 0;"><strong>Costing #:</strong> {costing_number}</p>
                          <p style="margin:6px 0;"><strong>Project:</strong> {project_name}</p>
                          {price_block}
                          <p style="margin:6px 0;"><strong>Escalated by:</strong> {pl_name}</p>
                        </td>
                      </tr>
                    </table>

                    <p style="background:#fff3cd;border-left:4px solid #ffc107;
                              padding:12px;border-radius:6px;margin:16px 0;">
                      <strong>📝 Product Line Justification:</strong><br/>
                      {comments}
                    </p>

                    <p style="text-align:center;margin:24px 0;">
                      <a href="{settings.FRONTEND_BASE_URL}/vp"
                         style="background:#0d6efd;color:#ffffff;
                                text-decoration:none;padding:12px 24px;
                                border-radius:6px;font-weight:bold;
                                display:inline-block;font-size:16px;">
                        👁️ Review & Decide
                      </a>
                    </p>

                    <p style="background:#e7f3ff;border:1px solid #b3d9ff;
                              padding:12px;border-radius:6px;margin:16px 0;">
                      <strong>Your options:</strong>
                      <ul style="margin:8px 0;">
                        <li>✅ Approve the target price</li>
                        <li>💬 Approve with an alternative price</li>
                        <li>⛔ Reject with justification</li>
                      </ul>
                    </p>

                    <p style="margin-top:24px;border-top:1px solid #e3e7ec;
                              padding-top:16px;">
                      Kind regards,<br/>
                      <strong>Pricing Deviation System</strong><br/>
                      AVO Carbon Group
                    </p>
                  </td>
                </tr>

                <!-- FOOTER -->
                <tr>
                  <td style="background:#f1f3f6;padding:12px;
                             font-size:11px;color:#777;text-align:center;">
                    This is an automated message. Please do not reply to this email.
                  </td>
                </tr>

              </table>
            </td>
          </tr>
        </table>
      </body>
    </html>
    """

    send_email(to_email, subject, html_body, cc_emails)


def send_vp_decision_to_commercial(
    to_email: str,
    project_name: str,
    decision: str,
    comments: str,
    final_price: float = None,
    costing_number: str = "",
    cc_emails: list = None,
):
    """Send VP final decision to commercial"""
    
    decision_icon = {
        "CLOSED": "✅",
        "BACK_TO_COMMERCIAL": "⚠️",
    }.get(decision, "📋")
    
    decision_color = {
        "CLOSED": "#198754",
        "BACK_TO_COMMERCIAL": "#ffc107",
    }.get(decision, "#666")
    
    subject = f"Pricing deviation – VP Final Decision ({costing_number})"

    final_price_block = (
        f"""
        <p style="background:#d4edda;border-left:4px solid #198754;
                  padding:12px;border-radius:6px;margin:12px 0;">
          <strong>💰 Approved Price:</strong> €{final_price:.2f}
        </p>
        """
        if final_price
        else ""
    )

    html_body = f"""
    <html>
      <body style="margin:0;padding:0;background:#f4f6f8;
                   font-family:Arial,Helvetica,sans-serif;">
        <table width="100%" cellpadding="0" cellspacing="0">
          <tr>
            <td align="center" style="padding:24px;">
              <table width="600" cellpadding="0" cellspacing="0"
                     style="background:#ffffff;border-radius:8px;
                            box-shadow:0 2px 8px rgba(0,0,0,0.08);">

                <!-- HEADER -->
                <tr>
                  <td style="background:{decision_color};
                             padding:16px 24px;color:#ffffff;">
                    <strong>{decision_icon} Pricing Deviation – VP Final Decision</strong>
                  </td>
                </tr>

                <!-- BODY -->
                <tr>
                  <td style="padding:24px;color:#333;font-size:14px;
                             line-height:1.6;">
                    <p>Hello,</p>

                    <p>
                      The Vice President has taken a final decision on the
                      pricing deviation request for
                      <strong>{project_name}</strong>.
                    </p>

                    <p style="background:#f7f9fb;border-left:4px solid {decision_color};
                              padding:12px;border-radius:6px;margin:16px 0;">
                      <strong>Decision:</strong><br/>
                      <span style="font-weight:bold;color:{decision_color};font-size:16px;">
                        {decision}
                      </span>
                    </p>

                    {final_price_block}

                    <p style="background:#fff3cd;border-left:4px solid #ffc107;
                              padding:12px;border-radius:6px;margin:12px 0;">
                      <strong>📝 VP Comments:</strong><br/>
                      {comments}
                    </p>

                    <p style="background:#e7f3ff;border:1px solid #b3d9ff;
                              padding:12px;border-radius:6px;margin:16px 0;">
                      <strong>Next Steps:</strong><br/>
                      You can now proceed to close this request or inform the customer accordingly.
                    </p>

                    <p style="margin-top:24px;border-top:1px solid #e3e7ec;
                              padding-top:16px;">
                      Kind regards,<br/>
                      <strong>Pricing Deviation System</strong><br/>
                      AVO Carbon Group
                    </p>
                  </td>
                </tr>

                <!-- FOOTER -->
                <tr>
                  <td style="background:#f1f3f6;padding:12px;
                             font-size:11px;color:#777;text-align:center;">
                    This is an automated message. Please do not reply to this email.
                  </td>
                </tr>

              </table>
            </td>
          </tr>
        </table>
      </body>
    </html>
    """

    send_email(to_email, subject, html_body, cc_emails)


async def send_verification_email(to_email: str, code: str):
    """
    Send verification code email for login
    """
    subject = "Your AVO Carbon Verification Code"
    
    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; margin: 0; padding: 0;">
        <table style="max-width: 600px; margin: 0 auto; background-color: white;">
          <tr>
            <td style="padding: 20px; text-align: center; background-color: #0f2a44;">
              <h1 style="margin: 0; color: white; font-size: 24px;">AVO Carbon</h1>
              <p style="margin: 5px 0 0 0; color: #ccc; font-size: 14px;">Pricing Deviation Management</p>
            </td>
          </tr>
          
          <tr>
            <td style="padding: 40px 20px;">
              <h2 style="color: #0f2a44; margin-top: 0;">Verify Your Email</h2>
              <p style="color: #666; font-size: 14px; line-height: 1.6;">
                Thank you for logging into AVO Carbon. Please use the verification code below to complete your login:
              </p>
              
              <div style="background-color: #f0f4f8; border-left: 4px solid #0b5ed7; padding: 20px; margin: 20px 0; text-align: center;">
                <p style="margin: 0; font-size: 12px; color: #666;">Your Verification Code</p>
                <p style="margin: 10px 0 0 0; font-size: 36px; font-weight: bold; color: #0b5ed7; letter-spacing: 5px;">
                  {code}
                </p>
              </div>
              
              <p style="color: #999; font-size: 12px;">
                This code will expire in 10 minutes. If you did not request this verification code, please ignore this email.
              </p>
            </td>
          </tr>
          
          <tr>
            <td style="background-color: #f1f3f6; padding: 12px; font-size: 11px; color: #777; text-align: center;">
              This is an automated message. Please do not reply to this email.
            </td>
          </tr>
        </table>
      </body>
    </html>
    """
    
    send_email(to_email, subject, html_body)
