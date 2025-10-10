from django.shortcuts import redirect
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.request import Request
from payments.models import Payment,Subscription
from .models import CollabLink
from users.models import User
from django.conf import settings
from django.db.models import Sum
from decimal import Decimal


PURCHASE_METHODS = ["crypto", "card", "paypal", "bank","withdraw"]

@api_view(["POST"])
@permission_classes([AllowAny])
def create_or_get_referral(request:Request): 
    """this view can get or create a new collab links"""
    email = request.data.get("email")
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    link, created = CollabLink.objects.get_or_create(owner=user)
    referrals = link.join_users.count()

    totals_qs = (
        Payment.objects
        .filter(
            user__in=link.join_users.all(),
            status__in=["paid", "partial"],
            method__in=PURCHASE_METHODS
        )
        .values("user_id")
        .annotate(total=Sum("amount"))
    )
    totals_by_user = {row["user_id"]: (row["total"] or Decimal("0")) for row in totals_qs}


    total_revenue_user = 0
    for item in link.join_users.all():
        total_revenue_user += totals_by_user.get(item.id, Decimal("0"))


    referred_users = []
    active_users_count = 0
    for u in link.join_users.all():
        total_revenue = totals_by_user.get(u.id, Decimal("0"))
        has_plan = Subscription.objects.filter(user=u, active=True).exists()
        if(has_plan):
            active_users_count += 1
        referred_users.append({
            "email": u.email,
            "username": u.username,
            "date": u.date_joined,
            "status":has_plan,
            "total_revenue": str(total_revenue),
        })

    return Response({
        "referral_link": link.url,
        "created": created,
        "referrals": referrals,
        "active_users":active_users_count,
        "total_revenue_users": total_revenue_user,
        "referrals_cost": link.cost_from_join_users,
        "rewards": link.reward,
        "referred_users": referred_users,
    })
@api_view(["GET"])
@permission_classes([AllowAny])
def register_link(request, referral_id):
    if CollabLink.objects.filter(collab_id=referral_id).exists():
        return redirect(f"{settings.FRONTEND_URL}/?ref={referral_id}")
    return redirect(settings.FRONTEND_URL)


from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from email.mime.image import MIMEImage
import os

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def receive_collab(request):
    user = request.user

    try:
        link = CollabLink.objects.get(owner=user)
    except CollabLink.DoesNotExist:
        return Response({"message": "No collab link found for this user."}, status=status.HTTP_404_NOT_FOUND)

    if link.cost_from_join_users < 50:
        return Response({"message": "Your earnings must be at least $50 to request payout."},
                        status=status.HTTP_400_BAD_REQUEST)

    admin_emails = list(User.objects.filter(is_superuser=True).values_list('email', flat=True))

    if not admin_emails:
        return Response({"message": "No admin emails configured."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    html_content = render_to_string(
        "email/receive_collab.html",
        {
            "username": user.username,
            "email": user.email,
            "total_revenue": link.cost_from_join_users,
            "share": link.cost_from_join_users * 0.5,
        }
    )

    email_msg = EmailMultiAlternatives(
        subject=f"💰 Collab Payout Request from {user.username}",
        body=f"User {user.username} ({user.email}) requested a payout.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=admin_emails,
    )
    email_msg.attach_alternative(html_content, "text/html")

    logo_path = os.path.join(settings.BASE_DIR, "users/templates/email/logo.png")
    with open(logo_path, "rb") as f:
        logo = MIMEImage(f.read())
        logo.add_header("Content-ID", "<logo_image>")
        logo.add_header("Content-Disposition", "inline", filename="logo.png")
        email_msg.attach(logo)

    email_msg.send()
    return Response({"message": "Payout request sent successfully!"}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def increase_collab_cost(request:Request):
    code = request.data.get("code")
    try:
        collab = CollabLink.objects.get(owner=request.user)
        if(collab.pro_cost_available):
            return Response({
                "success":False,
                "message":"You have already used your code"
            })
        if(code == "Wholesale2025EP50"):
            collab.cost_from_join_users += 30
            collab.pro_cost_available = True
            collab.save()
            return Response({"success":True,"message": "Collab cost increased successfully."}, status=status.HTTP_200_OK)
        return Response({"success":False,"message":"Wrong code please check the code again"})
    except CollabLink.DoesNotExist:
        return Response({"success":True,"message": "Collab link not found."}, status=status.HTTP_404_NOT_FOUND)