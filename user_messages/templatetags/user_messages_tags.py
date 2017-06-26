from django import template


register = template.Library()


@register.filter
def unread(thread, user):
    return bool(thread.userthread_set.filter(user=user, unread=True))


@register.filter
def unread_threads(user):
    return user.userthread_set.filter(unread=True, deleted=False).count()
