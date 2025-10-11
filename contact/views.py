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
            try:
                subject = f"📩 New Contact Message from {contact_message.name}"
                html_content = f"""
                <div style="background-color:#f5f7fa;padding:30px;font-family:'Segoe UI',Roboto,Helvetica,Arial,sans-serif;color:#333;">
                <div style="max-width:600px;margin:0 auto;background:#fff;border-radius:10px;overflow:hidden;box-shadow:0 4px 10px rgba(0,0,0,0.08);">
                    <div style="background:linear-gradient(135deg,#2a9d8f,#27ae60);padding:16px 24px;">
                    <h2 style="margin:0;color:#fff;font-size:20px;font-weight:600;">📩 New Contact Message</h2>
                    </div>
                    <div style="padding:24px;">
                    <p style="font-size:15px;margin-bottom:12px;">You’ve received a new message from your website contact form:</p>

                    <table style="width:100%;border-collapse:collapse;margin-bottom:20px;">
                        <tr>
                        <td style="padding:8px 0;width:100px;font-weight:bold;">Name:</td>
                        <td style="padding:8px 0;">{contact_message.name}</td>
                        </tr>
                        <tr>
                        <td style="padding:8px 0;font-weight:bold;">Email:</td>
                        <td style="padding:8px 0;">
                            <a href="mailto:{contact_message.email}" style="color:#2a9d8f;text-decoration:none;">{contact_message.email}</a>
                        </td>
                        </tr>
                    </table>

                    <div style="background-color:#f9fafb;border-left:4px solid #2a9d8f;padding:15px 18px;border-radius:6px;font-size:14px;line-height:1.6;color:#444;">
                        {contact_message.message}
                    </div>

                    <p style="margin-top:24px;font-size:12px;color:#888;text-align:center;border-top:1px solid #eee;padding-top:10px;">
                        Sent automatically from your website contact form.<br>
                        <span style="color:#2a9d8f;">Please do not reply directly to this email.</span>
                    </p>
                    </div>
                </div>
                </div>
                """

                text_content = strip_tags(html_content)  # نسخه‌ی متنی ساده برای fallback

                # ساخت و ارسال ایمیل

                email = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,
                    from_email=None,  # از DEFAULT_FROM_EMAIL استفاده می‌کند
                    to=["alirezayousefnezhadian@gmail.com"],  # آدرس ایمیل مقصد (شما)
                )
                email.attach_alternative(html_content, "text/html")
                email.send(fail_silently=False)
            except Exception as e:
                print(e)
                

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
