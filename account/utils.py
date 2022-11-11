from django.core.mail import EmailMessage, send_mail
import threading


class EmailThread(threading.Thread):
    
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)
    
    def run(self):
        self.email.send(fail_silently = False)

class Utils:
    def send_email(data):
        email = send_mail(
            subject=data['email_subject'], 
            message=data['email_body'], 
            from_email=data['sender_email'], 
            recipient_list=[data['receiver_email']]
            )
        EmailThread(email).start()