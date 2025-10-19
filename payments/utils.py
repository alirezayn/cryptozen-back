import datetime
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from django.db.models import Sum, Count
from .models import Payment


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



def generate_payment_report(period="week"):
    today = datetime.date.today()

    if period == "week":
        start_date = today - datetime.timedelta(days=today.weekday())  # Monday
        end_date = start_date + datetime.timedelta(days=7)
        label = "Current Week"
    else:
        start_date = today.replace(day=1)
        next_month = (start_date + datetime.timedelta(days=32)).replace(day=1)
        end_date = next_month
        label = "Current Month"

    payments = Payment.objects.filter(
        created_at__date__gte=start_date, created_at__date__lt=end_date, status="paid"
    )

    total_sales = payments.aggregate(total=Sum("amount"))["total"] or 0
    total_count = payments.aggregate(count=Count("id"))["count"]

    html_content = render_to_string(
        "emails/payment_report.html",
        {
            "label": label,
            "start_date": start_date,
            "end_date": end_date - datetime.timedelta(days=1),
            "total_sales": total_sales,
            "total_count": total_count,
            "payments": payments,
        },
    )

    return html_content, total_sales, total_count


def send_payment_report_email():
    html_content_week, total_sales_week, total_count_week = generate_payment_report("week")
    html_content_month, total_sales_month, total_count_month = generate_payment_report("month")

    subject = f"📊 Weekly & Monthly Payment Report ({datetime.date.today()})"
    from_email = settings.DEFAULT_FROM_EMAIL
    to_emails = [admin[1] for admin in settings.ADMINS]  # change if needed

    full_html = f"""
    <h2>Weekly Report</h2>
    {html_content_week}
    <hr>
    <h2>Monthly Report</h2>
    {html_content_month}
    """

    text_content = strip_tags(full_html)
    msg = EmailMultiAlternatives(subject, text_content, from_email, to_emails)
    msg.attach_alternative(full_html, "text/html")
    msg.send()
    print("✅ Payment report email sent successfully.")