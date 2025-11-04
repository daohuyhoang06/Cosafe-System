import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from app.core import settings

class EmailService:
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_pass = settings.SMTP_PASS
    
    def send_guide_email(self, to_email: str):
        """Send guide PDF via email"""
        if not (self.smtp_user and self.smtp_pass):
            print("Missing SMTP_USER or SMTP_PASS in environment!")
            return
        
        subject = "Your Free Copy of EWG's Quick Tips for Safer Personal Care Products"
        
        text = (
            "Thank you for requesting EWG's Quick Tips for Choosing Safer Personal Care Products!\n\n"
            "Please find your free guide attached to this email.\n\n"
            "This guide will help you make smarter, healthier choices for you and your family. "
            "Explore ingredient safety, learn how to spot EWG VERIFIED® products, and see how easy it is to shop with confidence.\n\n"
            "Stay informed and empowered—visit EWG's Skin Deep® database any time to search for safety scores and ingredient information on thousands of personal care products.\n\n"
            "Thank you for supporting EWG's mission to make safer products available for everyone!\n\n"
            "With care,\n"
            "The EWG Team"
        )
        
        # Create multipart message
        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["From"] = self.smtp_user
        msg["To"] = to_email
        msg.attach(MIMEText(text, "plain", "utf-8"))
        
        # Attach PDF
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        pdf_path = os.path.join(BASE_DIR, "..", "frontend", "public", "assets", "ewg-guide.pdf")
        
        try:
            with open(pdf_path, "rb") as f:
                part = MIMEBase("application", "pdf")
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    'attachment; filename="EWG-Quick-Tips-Guide.pdf"'
                )
                msg.attach(part)
        except Exception as e:
            print(f"Error attaching PDF: {e}")
        
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.sendmail(self.smtp_user, [to_email], msg.as_string())
        except Exception as e:
            print(f"Error sending guide email to {to_email}: {e}")
