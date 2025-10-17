from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings


def send_payment_confirmation_email(user, plan_type, amount, purpose, subscription_end_date=None):
    """
    Sends a payment confirmation email to the user.
    """
    subject = "✅ Payment Confirmation"
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [
          "Cryptozen.inquiries@gmail.com",
          "Parhamrbt@gmail.com",
          "Parhamfardian@gmail.com",
           user.email
        ]

    context = {
        "full_name": f"{user.first_name} {user.last_name}".strip() or user.username,
        "plan_type": plan_type,
        "amount": amount,
        "purpose": purpose,
        "subscription_end_date": subscription_end_date,
        "dashboard_link":"https://cryptozen360.com/dashboard"
    }

    html_content = render_to_string("emails/payment_success.html", context)
    text_content = (
        f"Hi {context['full_name']},\n\n"
        f"Your payment of ${amount} for {purpose} has been successfully processed.\n"
        + (f"Your subscription plan: {plan_type}, valid until {subscription_end_date}.\n" if subscription_end_date else "")
        + "\nThank you for your trust and support!"
    )

    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send(fail_silently=False)
