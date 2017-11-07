from datetime import datetime

from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from user_messages.managers import ThreadManager, MessageManager
from user_messages.utils import cached_attribute


class Thread(models.Model):
    
    subject = models.CharField(
        _('Subject'), max_length=150
    )
    single_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="UserThread",
        verbose_name=_('Users'),
        blank=True,
        related_name="single_threads"
    )
    group_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="GroupMemberThread",
        verbose_name=_('Group Members'),
        blank=True,
        related_name="group_threads"
    )

    objects = ThreadManager()
    
    def get_absolute_url(self):
        return reverse("messages_thread_detail", kwargs={"thread_id": self.pk})

    @property
    @cached_attribute
    def first_message(self):
        return self.messages.all()[0]
    
    @property
    @cached_attribute
    def latest_message(self):
        return self.messages.order_by("-sent_at")[0]

    @property
    def num_messages(self):
        return self.messages.count()

    @property
    def registered_users(self):
        return get_user_model().objects.filter(
            Q(userthread__thread=self) |
            Q(groupmemberthread__thread=self)
        ).distinct()

    @property
    def registered_groups(self):
        return Group.objects.filter(groupmemberthread__thread=self).distinct()

    @property
    def num_users(self):
        """Total number of users that are registered to this thread."""
        return self.registered_users.count()

    def __str__(self):
        return self.subject


class GroupMemberThread(models.Model):
    thread = models.ForeignKey(Thread)
    # we could replace ``group`` and ``user`` below with
    # ``member=models.ForeignKey(geonode.groups.models.GroupMember)``
    # but that would mean importing from geonode core apps inside an external
    # app. This is an argument for moving this app into genode.contrib
    group = models.ForeignKey(Group)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    unread = models.BooleanField(
        default=True
    )
    deleted = models.BooleanField(
        default=False
    )


class UserThread(models.Model):
    
    thread = models.ForeignKey(Thread)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    
    unread = models.BooleanField(
        default=True
    )
    deleted = models.BooleanField(
        default=False
    )


class Message(models.Model):
    
    thread = models.ForeignKey(Thread, related_name="messages")
    
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="sent_messages", verbose_name=_('Sender'))
    sent_at = models.DateTimeField(_('Sent at'), default=timezone.now)
    
    content = models.TextField(_('Content'))
    
    objects = MessageManager()
    
    class Meta:
        ordering = ("sent_at",)
    
    def get_absolute_url(self):
        return self.thread.get_absolute_url()
