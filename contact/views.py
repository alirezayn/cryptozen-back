from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.request import Request
from .models import ContactMessage, UserComment
from .serializers import ContactMessageSerializer, UserCommentSerializer
from rest_framework.permissions import AllowAny
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from wallet.models import WithdrawRequests,UserWallet
class ContactMessageViewSet(viewsets.ModelViewSet):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [AllowAny]

    def create(self, request: Request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            contact_message = serializer.save()
            
            if contact_message.message_type == "withdraw" and request.user.is_authenticated:
                user_wallet,created = UserWallet.objects.get_or_create(user=request.user)
                if user_wallet.balance > 0:
                    WithdrawRequests.objects.get_or_create(
                        user = request.user,
                        amount = user_wallet.balance,
                        description = contact_message.message
                    )
                else:
                    return Response(
                {"success":False,"message": "Your balance is $0"},
                status=status.HTTP_400_BAD_REQUEST,
                    )      
            recipients = [
                # "Cryptozen.inquiries@gmail.com",
                # "Parhamrbt@gmail.com",
                # "Parhamfardian@gmail.com",
                "alirezayousefnezhadian@gmail.com"
            ]
            try:
                context = {
                    "name": contact_message.name,
                    "email": contact_message.email,
                    "message": contact_message.message,
                }
                
                subject = f"📩 New {contact_message} request from {contact_message.name}"

                html_content = render_to_string("email/contact_message.html", context)
                text_content = strip_tags(html_content)
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,
                    from_email="support@cryptozen360.com",
                    to=recipients,
                )
                email.attach_alternative(html_content, "text/html")
                email.send(fail_silently=False)

            except Exception as e:
                print("Email send error:", e)

            return Response(
                {"message": "Your message has been sent!"},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class UserCommentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UserComment.objects.all().order_by("-created_at")
    serializer_class = UserCommentSerializer
    permission_classes = [AllowAny]

    def get_serializer_context(self):
        return {"request": self.request}
