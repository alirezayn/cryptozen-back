from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.request import Request
from .models import ContactMessage, UserComment
from .serializers import ContactMessageSerializer, UserCommentSerializer
from rest_framework.permissions import AllowAny
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
class ContactMessageViewSet(viewsets.ModelViewSet):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [AllowAny]

    def create(self, request:Request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            contact_message = serializer.save()

            subject = f"📩 New Contact Message from {contact_message.name}"
            html_content = f"""
                <div style="font-family: sans-serif; line-height: 1.6;">
                    <h2 style="color: #2a9d8f;">New Contact Message</h2>
                    <p><strong>Name:</strong> {contact_message.name}</p>
                    <p><strong>Email:</strong> {contact_message.email}</p>
                    <p><strong>Message:</strong></p>
                    <div style="background-color: #f9f9f9; padding: 10px; border-radius: 6px;">
                        {contact_message.message}
                    </div>
                    <hr>
                    <p style="font-size: 12px; color: #555;">
                        Sent automatically from your website contact form.
                    </p>
                </div>
            """

            text_content = strip_tags(html_content)  # نسخه‌ی متنی ساده برای fallback

            # ساخت و ارسال ایمیل
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=None,  # از DEFAULT_FROM_EMAIL استفاده می‌کند
                to=["alirezayousefnezhadiab@gmail.com"],  # آدرس ایمیل مقصد (شما)
            )
            email.attach_alternative(html_content, "text/html")
            email.send(fail_silently=False)

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
