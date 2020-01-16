from user_messages.models import Thread


def user_messages(request):
    c = {}
    if request.user.is_authenticated:
        c["inbox_count"] = Thread.objects.unread_threads(request.user).count()
    return c
