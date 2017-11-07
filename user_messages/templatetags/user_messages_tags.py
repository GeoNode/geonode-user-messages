from django import template

from user_messages.models import Thread


register = template.Library()


@register.filter
def unread(thread, user):
    return bool(thread.userthread_set.filter(user=user, unread=True))


@register.filter
def unread_threads(user):
    return Thread.objects.unread_threads(user).count()
