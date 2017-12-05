from django import forms
from django.db.models import Q
from django.core.exceptions import ValidationError

from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from user_messages.models import Message

from geonode.groups.models import GroupProfile


class NewMessageForm(forms.Form):

    to_users = forms.ModelMultipleChoiceField(
        label=_("To users"),
        queryset=get_user_model().objects.all(),  # refined below in __init__
        required=False,
    )
    to_groups = forms.ModelMultipleChoiceField(
        label=_("To groups"),
        queryset=GroupProfile.objects.all().order_by('title'),  # refined below in __init__
        required=False,
    )
    subject = forms.CharField(label=_("Subject"))
    content = forms.CharField(label=_("Content"), widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        self.sender = kwargs.pop("current_user")
        super(NewMessageForm, self).__init__(*args, **kwargs)
        if not self.sender.is_superuser:
            # show only public groups or ones that the current user is a
            # member of
            groups = self.sender.groups.all()
            group_list_all = []
            try:
                group_list_all = self.sender.group_list_all().values('group')
            except:
                pass
            public_groups = GroupProfile.objects.exclude(access="public-invite").exclude(access="private").values('group')

            self.fields["to_groups"].queryset = GroupProfile.objects.filter(
                Q(group__isnull=True) | Q(group__in=groups) |
                Q(group__in=public_groups) | Q(group__in=group_list_all) |
                Q(group__user=self.sender)
            ).distinct().order_by('title')

        self.fields["to_users"].queryset = get_user_model().objects.exclude(
            username="AnonymousUser").exclude(
            id=self.sender.id).exclude(
            is_active=False
        ).order_by('username')

    def clean(self):
        """Validate fields that depend on each other

        In this case we need to verify if at least one user or group has
        been selected.

        """

        super(NewMessageForm, self).clean()
        users = self.cleaned_data.get("to_users")
        groups = self.cleaned_data.get("to_groups")
        if not any(users) and not any(groups):
            raise ValidationError(_("Must select at least one user or group."))


class MessageReplyForm(forms.Form):

    content = forms.CharField(label=_("Content"), widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        self.thread = kwargs.pop("thread")
        self.user = kwargs.pop("user")
        super(MessageReplyForm, self).__init__(*args, **kwargs)

    def save(self):
        return Message.objects.new_reply(self.thread, self.user,
            self.cleaned_data["content"])
