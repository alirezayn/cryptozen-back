from django.core.management.base import BaseCommand
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.timezone import now
from datetime import timedelta
from django.db.models import Sum

from payments.models import Payment


class Command(BaseCommand):
    help = "Send payment reports to admin via email (weekly or monthly)"

    def add_arguments(self, parser):
        parser.add_argument(
            '--period',
            type=str,
            choices=['week', 'month'],
            default='week',
            help='Specify period: week or month'
        )

    def handle(self, *args, **options):
        period = options['period']
        self.send_report(period)
        self.stdout.write(self.style.SUCCESS(f"✅ {period.capitalize()} report sent."))

    def send_report(self, period):
        now_time = now()
        if period == "week":
            start_date = now_time - timedelta(days=7)
            subject = "Weekly Payment Report"
        else:
            start_date = now_time - timedelta(days=30)
            subject = "Monthly Payment Report"

        payments = Payment.objects.filter(
            created_at__gte=start_date, status="paid"
        ).order_by("-created_at")

        total_sales = payments.aggregate(Sum("amount"))["amount__sum"] or 0

        html_content = render_to_string(
            "emails/sales_report.html",
            {"payments": payments, "total_sales": total_sales, "period": period.capitalize()},
        )

        text_content = f"{period.capitalize()} Payment Report\nTotal Sales: {total_sales}"

        email = EmailMultiAlternatives(
            subject,
            text_content,
            to=[
                "Cryptozen.inquiries@gmail.com",
                "Parhamrbt@gmail.com",
                "Parhamfardian@gmail.com"
            ],
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
