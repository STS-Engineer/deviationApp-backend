"""
Cron/scheduled tasks for sending reminder emails
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.pricing_request import PricingRequest
from app.models.enums import RequestStatus
from app.emails.mailer import send_email
import logging

logger = logging.getLogger(__name__)


def send_pl_reminder_emails(db: Session):
    """
    Send reminder emails to PL responsible for requests pending >2 days
    """
    two_days_ago = datetime.utcnow() - timedelta(days=2)
    
    # Get all requests that are still under review and older than 2 days
    old_requests = db.query(PricingRequest).filter(
        PricingRequest.status == RequestStatus.UNDER_REVIEW_PL.value,
        PricingRequest.created_at < two_days_ago
    ).all()
    
    for request in old_requests:
        try:
            subject = f"⏰ Reminder – Pending approval ({request.costing_number})"
            
            html_body = f"""
            <html>
              <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; margin: 0; padding: 0;">
                <table style="max-width: 600px; margin: 0 auto; background-color: white;">
                  <tr>
                    <td style="padding: 20px; text-align: center; background-color: #f59e0b;">
                      <h1 style="margin: 0; color: white; font-size: 24px;">⏰ Reminder</h1>
                    </td>
                  </tr>
                  
                  <tr>
                    <td style="padding: 40px 20px;">
                      <h2 style="color: #0f2a44; margin-top: 0;">Action Required</h2>
                      <p style="color: #666; font-size: 14px; line-height: 1.6;">
                        This is a friendly reminder that the following pricing deviation request
                        has been pending your approval for more than 2 days.
                      </p>
                      
                      <div style="background-color: #fff3cd; border-left: 4px solid #f59e0b; padding: 20px; margin: 20px 0; border-radius: 6px;">
                        <p style="margin: 6px 0;"><strong>Project:</strong> {request.project_name}</p>
                        <p style="margin: 6px 0;"><strong>Customer:</strong> {request.customer}</p>
                        <p style="margin: 6px 0;"><strong>Costing #:</strong> {request.costing_number}</p>
                        <p style="margin: 6px 0;"><strong>Submitted:</strong> {request.created_at.strftime('%Y-%m-%d %H:%M')}</p>
                        <p style="margin: 6px 0;"><strong>Days Pending:</strong> {(datetime.utcnow() - request.created_at).days} days</p>
                      </div>
                      
                      <p style="text-align: center; margin: 24px 0;">
                        <a href="http://localhost:5173/pl"
                           style="background: #f59e0b; color: white; text-decoration: none; padding: 12px 24px; border-radius: 6px; font-weight: bold; display: inline-block; font-size: 16px;">
                          Review Now
                        </a>
                      </p>
                      
                      <p style="color: #999; font-size: 12px;">
                        Please review and make a decision on this request as soon as possible.
                      </p>
                    </td>
                  </tr>
                  
                  <tr>
                    <td style="background-color: #f1f3f6; padding: 12px; font-size: 11px; color: #777; text-align: center;">
                      This is an automated reminder message. Please do not reply to this email.
                    </td>
                  </tr>
                </table>
              </body>
            </html>
            """
            
            send_email(request.product_line_responsible_email, subject, html_body)
            logger.info(f"Sent PL reminder for request {request.id}")
        except Exception as e:
            logger.error(f"Failed to send PL reminder for request {request.id}: {str(e)}")


def send_vp_reminder_emails(db: Session):
    """
    Send reminder emails to VP for requests escalated >2 days
    """
    two_days_ago = datetime.utcnow() - timedelta(days=2)
    
    # Get all requests that are escalated and older than 2 days
    old_requests = db.query(PricingRequest).filter(
        PricingRequest.status == RequestStatus.ESCALATED_TO_VP.value,
        PricingRequest.created_at < two_days_ago
    ).all()
    
    for request in old_requests:
        try:
            subject = f"🚨 Urgent – Escalated request pending ({request.costing_number})"
            
            html_body = f"""
            <html>
              <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; margin: 0; padding: 0;">
                <table style="max-width: 600px; margin: 0 auto; background-color: white;">
                  <tr>
                    <td style="padding: 20px; text-align: center; background-color: #dc3545;">
                      <h1 style="margin: 0; color: white; font-size: 24px;">🚨 Urgent Reminder</h1>
                    </td>
                  </tr>
                  
                  <tr>
                    <td style="padding: 40px 20px;">
                      <h2 style="color: #0f2a44; margin-top: 0;">Escalated Request Awaiting Decision</h2>
                      <p style="color: #666; font-size: 14px; line-height: 1.6;">
                        An escalated pricing deviation request has been pending your final decision
                        for more than 2 days. Please review and decide urgently.
                      </p>
                      
                      <div style="background-color: #f8d7da; border-left: 4px solid #dc3545; padding: 20px; margin: 20px 0; border-radius: 6px;">
                        <p style="margin: 6px 0;"><strong>Project:</strong> {request.project_name}</p>
                        <p style="margin: 6px 0;"><strong>Customer:</strong> {request.customer}</p>
                        <p style="margin: 6px 0;"><strong>Costing #:</strong> {request.costing_number}</p>
                        <p style="margin: 6px 0;"><strong>Escalated:</strong> {request.created_at.strftime('%Y-%m-%d %H:%M')}</p>
                        <p style="margin: 6px 0;"><strong>Days Pending:</strong> {(datetime.utcnow() - request.created_at).days} days</p>
                      </div>
                      
                      <p style="text-align: center; margin: 24px 0;">
                        <a href="http://localhost:5173/vp"
                           style="background: #dc3545; color: white; text-decoration: none; padding: 12px 24px; border-radius: 6px; font-weight: bold; display: inline-block; font-size: 16px;">
                          Make Decision Now
                        </a>
                      </p>
                      
                      <p style="color: #999; font-size: 12px;">
                        Your timely decision is critical for the customer and internal processes.
                      </p>
                    </td>
                  </tr>
                  
                  <tr>
                    <td style="background-color: #f1f3f6; padding: 12px; font-size: 11px; color: #777; text-align: center;">
                      This is an automated urgent reminder. Please do not reply to this email.
                    </td>
                  </tr>
                </table>
              </body>
            </html>
            """
            
            send_email(request.vp_email, subject, html_body)
            logger.info(f"Sent VP reminder for request {request.id}")
        except Exception as e:
            logger.error(f"Failed to send VP reminder for request {request.id}: {str(e)}")
