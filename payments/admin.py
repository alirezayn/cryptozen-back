from django.contrib import admin, messages
from django.core.mail import EmailMultiAlternatives
from django.utils.timezone import now
from django.db.models import Sum
from datetime import timedelta
from django.template.loader import render_to_string
from django.contrib import admin
from .models import (
    Subscription,
    PaymentHistory,
    SubscriptionPlan,
    DiscountedPlan,
    Payment,
)
from django.urls import path
from django.shortcuts import redirect
from openpyxl import Workbook
from django.http import HttpResponse
@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ["user", "plan", "start_date", "end_date", "active"]
    search_fields = ["user__username", "plan"]
    list_filter = ["plan", "active"]
    readonly_fields = ["start_date"]


@admin.register(PaymentHistory)
class PaymentHistoryAdmin(admin.ModelAdmin):
    list_display = ["user", "amount", "method", "status", "date"]
    list_filter = ["status", "method"]
    search_fields = ["user__username"]



@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["user", "amount", "currency", "method", "status", "created_at"]
    list_filter = ["status", "method", "currency"]
    search_fields = ["user__username", "cryptomus_payment_uuid"]
    readonly_fields = ["created_at"]

    change_list_template = "admin/payments_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("weekly-report/", self.admin_site.admin_view(self.generate_weekly_report), name="weekly_report"),
            path("monthly-report/", self.admin_site.admin_view(self.generate_monthly_report), name="monthly_report"),
            path("download-weekly-report/", self.admin_site.admin_view(self.download_weekly_report), name="weekly_report"),
            path("download-monthly-report/", self.admin_site.admin_view(self.download_monthly_report), name="monthly_report"),
        ]
        return custom_urls + urls

    def generate_weekly_report(self, request):
        return self._generate_report(request, "week")

    def generate_monthly_report(self, request):
        return self._generate_report(request, "month")

    def _generate_report(self, request, period):
        now_time = now()
        if period == "week":
            start_date = now_time - timedelta(days=7)
            subject = "Weekly Sales Report"
        else:
            start_date = now_time - timedelta(days=30)
            subject = "Monthly Sales Report"

        payments = Payment.objects.filter(
            created_at__gte=start_date, status="paid"
        ).order_by("-created_at")

        total_sales = payments.aggregate(Sum("amount"))["amount__sum"] or 0

        html_content = render_to_string(
            "emails/sales_report.html",
            {"payments": payments, "total_sales": total_sales, "period": period.capitalize()},
        )
        text_content = f"{period.capitalize()} Sales Report\nTotal Sales: {total_sales}"

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

        messages.success(request, f"{period.capitalize()} sales report has been sent successfully.")
        return redirect("..")

    def download_weekly_report(self, request):
        return self._generate_excel_report(request, "week")

    def download_monthly_report(self, request):
        return self._generate_excel_report(request, "month")

    def _generate_excel_report(self, request, period):
        now_time = now()
        if period == "week":
            start_date = now_time - timedelta(days=7)
            filename = "weekly_sales_report.xlsx"
        else:
            start_date = now_time - timedelta(days=30)
            filename = "monthly_sales_report.xlsx"

        payments = Payment.objects.filter(
            created_at__gte=start_date, status="paid"
        ).order_by("-created_at")

        wb = Workbook()
        ws = wb.active
        ws.title = f"{period.capitalize()} Report"

        # Header
        headers = ["User", "Amount", "Currency", "Method", "Status", "Created At"]
        ws.append(headers)

        # Data rows
        for p in payments:
            ws.append([
                p.user.username,
                float(p.amount),
                p.currency,
                p.method,
                p.status,
                p.created_at.strftime("%Y-%m-%d %H:%M"),
            ])

        total_sales = payments.aggregate(Sum("amount"))["amount__sum"] or 0
        ws.append([])
        ws.append(["", "Total Sales", float(total_sales)])

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        wb.save(response)
        return response



@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ("title", "plan_type", "price", "duration","months")
    list_filter = ("plan_type",)
    search_fields = ("title", "description", "features")
    ordering = ("plan_type",)


@admin.register(DiscountedPlan)
class DiscountedPlanAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "duration",
        "original_price",
        "discounted_price",
        "highlight_text",
    )
