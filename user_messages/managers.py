from django.db.models import Manager
from django.db.models import Q

from user_messages.signals import message_sent


class ThreadManager(Manager):
    
    def active_threads(self, user):
        """Return all active threads where the user is involved.

        A user can be involved in a thread directly or indirectly, via one of
        its groups.

        """

        return self.filter(
            Q(
                userthread__user__id=user.id,
                userthread__deleted=False
            ) | Q(
                groupmemberthread__user__id=user.id,
                groupmemberthread__deleted=False
            )
        ).distinct()

    def sorted_active_threads(self, user):
        return _sort_distinct_thread_queryset(self.active_threads(user))

    def unread_threads(self, user):
        """Return all unread threads where the user is involved."""
        return self.filter(
            Q(
                userthread__user=user,
                userthread__deleted=False,
                userthread__unread=True
            ) | Q(
                groupmemberthread__user=user,
                groupmemberthread__deleted=False,
                groupmemberthread__unread=True,
            )
        ).distinct()

    def sorted_unread_threads(self, user):
        return _sort_distinct_thread_queryset(self.unread_threads(user))


class MessageManager(Manager):
    
    def new_reply(self, thread, user, content):
        """Generate a new message for the input thread.

        Whenever a new reply is created, all of the previously subscribed
        users will see this message in their inbox, even if they had
        previously deleted the message in the past.

        """

        msg = self.create(thread=thread, sender=user, content=content)
        thread.userthread_set.exclude(user=user).update(
            deleted=False, unread=True)
        thread.groupmemberthread_set.exclude(user=user).update(
            deleted=False, unread=True)
        thread.userthread_set.filter(user=user).update(unread=False)
        thread.groupmemberthread_set.filter(user=user).update(unread=False)
        message_sent.send(
            sender=self.model, message=msg, thread=thread, reply=True)
        return msg

    def new_message(self, from_user, subject, content, to_users=None,
                    to_groups=None):
        """Create a new conversation thread and its first message.

        The new thread will involve both the ``from_user`` and all users from
        the ``to_users`` and ``to_groups`` parameters. All users belonging to
        a group in the ``to_groups`` parameter are added to the thread.

        """

        to_users = list(to_users) if to_users is not None else []
        to_groups = list(to_groups) if to_groups is not None else []
        from user_messages.models import Thread
        thread = Thread.objects.create(subject=subject)
        thread.userthread_set.create(user=from_user, unread=False)
        for user in to_users:
            if user.id != from_user.id:
                thread.userthread_set.create(user=user)
        for group_profile in to_groups:
            active_members = group_profile.groupmember_set.filter(
                user__is_active=True)
            for group_member in active_members:
                thread.groupmemberthread_set.create(
                    user=group_member.user,
                    group=group_profile.group,
                    unread=False if group_member.user == from_user else True
                )
        msg = self.create(thread=thread, sender=from_user, content=content)
        message_sent.send(
            sender=self.model, message=msg, thread=thread, reply=False)
        return msg


def _sort_distinct_thread_queryset(thread_qs, sort_descending=True):
    """Sort a Thread queryset according to its latest message's date.

    This function is a workaround for the fact that django inserts duplicate
    records when trying to use ``.order_by`` and ``.distinct`` in the
    same queryset. More details at:

    https://docs.djangoproject.com/en/1.8/ref/models/querysets/#django.db.models.query.QuerySet.distinct

    """

    materialized_qs = list(thread_qs)
    materialized_qs.sort(
        key=lambda thread: thread.latest_message.sent_at,
        reverse=sort_descending
    )
    return materialized_qs
