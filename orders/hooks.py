from django.conf import settings
from django.core.mail import EmailMessage
from django.contrib.sites.models import Site
from django.template.loader import render_to_string

def send_receipt(self, charge, email=None):
        
        if not charge.receipt_sent:
            # Import here to not add a hard dependency on the Sites framework
            site = Site.objects.get_current()
            protocol = getattr(settings, "DEFAULT_HTTP_PROTOCOL", "http")
            ctx = {
                "charge": charge,
                "site": site,
                "protocol": protocol,
            }
            subject = render_to_string("foodhub/stripe/email/subject.txt", ctx)
            subject = subject.strip()
            message = render_to_string("foodhub/stripe/email/body.txt", ctx)

            if not email and charge.customer:
                email = charge.customer.user.email

            num_sent = EmailMessage(
                subject,
                message,
                to=[email],
                from_email=settings.INVOICE_FROM_EMAIL
            ).send()
            charge.receipt_sent = num_sent > 0
            charge.save()