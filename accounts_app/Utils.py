from django.core.mail import EmailMessage
from rest_framework.response import Response

class Utils:
    @staticmethod
    def send_email(data):
        try:
            email = EmailMessage(subject=data["email_subject"], body=data["email_body"], from_email="support@livingcareservices.org", to=(data["email_to"],))
            email.send() 
        except Exception as e:
            return Response({"error": str(e)})
