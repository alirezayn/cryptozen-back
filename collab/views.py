from django.shortcuts import redirect
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import CollabLink
from users.models import User
from django.conf import settings


@api_view(["POST"])
@permission_classes([AllowAny])
def create_or_get_referral(request):
    """this view can get or create a new collab links"""
    email = request.data["email"]
    user = User.objects.get(email=email)
    link, created = CollabLink.objects.get_or_create(
        owner=user
    )

    # get number of invite
    referrals = len(link.join_users.all())

    return Response({
        "referral_link": link.url,
        "created": created,
        "referrals": referrals,
        'referrals_cost': link.cost_from_join_users,
        "referred_users": [{'email': user.email, 'username': user.username, 'data': user.date_joined} for user in
                           link.join_users.all()]
    })


@api_view(["GET"])
@permission_classes([AllowAny])
def register_link(request, referral_id):
    if CollabLink.objects.filter(collab_id=referral_id).exists():
        return redirect(f"http://localhost:5173/?ref={referral_id}")
    return redirect("http://localhost:5173/")


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
