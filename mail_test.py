from django.core.mail import send_mail

print(
    send_mail(
        subject="Test mail",
        message="To jest test z Railway",
        from_email=None,
        recipient_list=["flesner96@gmail.com"],
        fail_silently=False,
    )
)