# import os
# import smtplib
# import smtplib
# from dotenv import load_dotenv

# load_dotenv()

# ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
# SMTP_SERVER = os.getenv("SMTP_SERVER")
# SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
# SMTP_EMAIL = os.getenv("SMTP_EMAIL")
# SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

# with smtplib.SMTP(
#     SMTP_SERVER,
#     SMTP_PORT
# ) as server:

#     server.starttls()

#     server.login(
#         SMTP_EMAIL,
#         SMTP_PASSWORD
#     )

#     server.sendmail(
#         SMTP_EMAIL,
#         ADMIN_EMAIL,
#         message.as_string()
#     )


# import os
# import smtplib

# from dotenv import load_dotenv
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart


# # Load .env
# load_dotenv()


# # Get email configuration
# ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
# SMTP_SERVER = os.getenv("SMTP_SERVER")
# SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
# SMTP_EMAIL = os.getenv("SMTP_EMAIL")
# SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")


# # Create email message
# message = MIMEMultipart()

# message["From"] = SMTP_EMAIL
# message["To"] = ADMIN_EMAIL
# message["Subject"] = "FMG AI Customer Support - Escalation"


# # Email body
# body = """
# Hello FMG Admin,

# A customer support issue has been escalated by the FMG AI Customer Support Agent.

# The AI agent was unable to confidently answer the customer's question
# using the available FMG documentation and previous Jira support tickets.

# Please review the customer's issue and provide further assistance.

# Best regards,
# FMG AI Customer Support Agent
# """


# message.attach(
#     MIMEText(body, "plain")
# )


# # Connect to Gmail SMTP server
# with smtplib.SMTP(
#     SMTP_SERVER,
#     SMTP_PORT
# ) as server:

#     # Secure the connection
#     server.starttls()

#     # Login to the sender email
#     server.login(
#         SMTP_EMAIL,
#         SMTP_PASSWORD
#     )

#     # Send email
#     server.sendmail(
#         SMTP_EMAIL,
#         ADMIN_EMAIL,
#         message.as_string()
#     )


# print("Escalation email sent successfully!")


import os
import resend
from dotenv import load_dotenv

load_dotenv()

# Load configuration
SEND_API_KEY = os.getenv("SEND_API_KEY")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")

# Configure Resend
resend.api_key = SEND_API_KEY


def send_escalation_email(customer_question, reason):

    params = {
        "from": "FMG AI Support <onboarding@resend.dev>",
        "to": [ADMIN_EMAIL],
        "subject": "FMG AI Customer Support - Escalation",
        "html": f"""
        <h2>FMG AI Customer Support Escalation</h2>

        <p><strong>A customer issue requires human assistance.</strong></p>

        <h3>Customer Question</h3>
        <p>{customer_question}</p>

        <h3>Reason for Escalation</h3>
        <p>{reason}</p>

        <hr>

        <p>
        This issue was automatically escalated by the
        FMG AI Customer Support Engineer.
        </p>
        """
    }

    try:

        email = resend.Emails.send(params)

        print("✅ Escalation email sent successfully!")
        print("Email response:", email)

        return True

    except Exception as e:

        print("❌ Failed to send escalation email")
        print("Error:", e)

        return False


# if __name__ == "__main__":

#     customer_question = input(
#         "Enter customer question: "
#     )

#     reason = (
#         "The AI could not find sufficient information "
#         "in FMG documentation or previous Jira tickets."
#     )

#     send_escalation_email(
#         customer_question,
#         reason
#     )