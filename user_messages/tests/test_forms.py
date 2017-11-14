"""Unit tests for user_messages.forms"""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase

from geonode.groups.models import GroupProfile

from user_messages import forms


class NewMessageFormTestCase(TestCase):

    def setUp(self):
        self.user_password = "fakepass"
        self.first_user = get_user_model().objects.create_user(
            "first", "first@fakemail.com", self.user_password)
        self.second_user = get_user_model().objects.create_user(
            "second", "second@fakemail.com", self.user_password)
        self.third_user = get_user_model().objects.create_user(
            "third", "third@fakemail.com", self.user_password)
        self.fourth_user = get_user_model().objects.create_user(
            "fourth", "fourth@fakemail.com", self.user_password)
        self.inactive_user = get_user_model().objects.create_user(
            "inactive_user", "inactive@fakemail.com", self.user_password)
        self.inactive_user.is_active = False
        self.inactive_user.save()
        self.admin_user = get_user_model().objects.create_superuser(
            "admin", "admin@fakemail.com", self.user_password)

        self.first_group_profile = GroupProfile.objects.create(
            title="testfirst",
            slug="testfirst",
            description="testfirst",
            access="public",
        )
        self.second_group_profile = GroupProfile.objects.create(
            title="testsecond",
            slug="testsecond",
            description="testsecond",
            access="public",
        )
        self.third_group_profile = GroupProfile.objects.create(
            title="testthird",
            slug="testthird",
            description="testthird",
            access="private",
        )
        self.fourth_group_profile = GroupProfile.objects.create(
            title="testfourth",
            slug="testfourth",
            description="testfourth",
            access="private",
        )

        self.first_group = self.first_group_profile.group
        self.second_group = self.second_group_profile.group
        self.third_group = self.third_group_profile.group
        self.fourth_group = self.third_group_profile.group

        self.first_group_profile.join(self.first_user)
        self.first_group_profile.join(self.second_user)
        self.second_group_profile.join(self.first_user)
        self.second_group_profile.join(self.third_user)
        self.second_group_profile.join(self.fourth_user)
        self.third_group_profile.join(self.second_user)
        self.third_group_profile.join(self.third_user)
        self.fourth_group_profile.join(self.second_user)
        self.fourth_group_profile.join(self.third_user)

    def test_new_message_form_no_subject(self):
        new_form = forms.NewMessageForm(
            {
                "subject": "",
                "content": "dummy content",
                "to_users": [2,],
                "to_groups": [1,],
            },
            current_user=self.first_user
        )
        self.assertFalse(new_form.is_valid())

    def test_new_message_form_no_content(self):
        new_form = forms.NewMessageForm(
            {
                "subject": "dummy subject",
                "content": "",
                "to_users": [2,],
                "to_groups": [1,],
            },
            current_user=self.first_user
        )
        self.assertFalse(new_form.is_valid())

    def test_new_message_form_no_recipients(self):
        new_form = forms.NewMessageForm(
            {
                "subject": "dummy subject",
                "content": "dummy content",
                "to_users": [],
                "to_groups": [],
            },
            current_user=self.first_user
        )
        self.assertFalse(new_form.is_valid())

    def test_new_message_form_only_single_users(self):
        new_form = forms.NewMessageForm(
            {
                "subject": "dummy subject",
                "content": "dummy content",
                "to_users": [2,],
                "to_groups": [],
            },
            current_user=self.first_user
        )
        self.assertTrue(new_form.is_valid())

    def test_new_message_form_only_groups(self):
        new_form = forms.NewMessageForm(
            {
                "subject": "dummy subject",
                "content": "dummy content",
                "to_users": [],
                "to_groups": [1, 2],
            },
            current_user=self.first_user
        )
        self.assertTrue(new_form.is_valid())

    def test_new_message_form_same_user(self):
        new_form = forms.NewMessageForm(
            {
                "subject": "dummy subject",
                "content": "dummy content",
                "to_users": [self.first_user.id,],
                "to_groups": [],
            },
            current_user=self.first_user
        )
        with self.assertRaises(TypeError):
            new_form.is_valid()

    def test_new_message_form_non_existent_user(self):
        new_form = forms.NewMessageForm(
            {
                "subject": "dummy subject",
                "content": "dummy content",
                "to_users": [10000,],
                "to_groups": [],
            },
            current_user=self.first_user
        )
        with self.assertRaises(TypeError):
            new_form.is_valid()

    def test_new_message_form_to_private_group_is_not_allowed(self):
        new_form = forms.NewMessageForm(
            {
                "subject": "dummy subject",
                "content": "dummy content",
                "to_users": [],
                "to_groups": [self.third_group_profile.id],
            },
            current_user=self.first_user
        )
        with self.assertRaises(TypeError):
            new_form.is_valid()

    def test_new_message_form_to_public_invite_group_is_not_allowed(self):
        new_form = forms.NewMessageForm(
            {
                "subject": "dummy subject",
                "content": "dummy content",
                "to_users": [],
                "to_groups": [self.fourth_group_profile.id],
            },
            current_user=self.first_user
        )
        with self.assertRaises(TypeError):
            new_form.is_valid()

    def test_new_message_form_cannot_message_inactive_users(self):
        new_form = forms.NewMessageForm(
            {
                "subject": "dummy subject",
                "content": "dummy content",
                "to_users": [self.inactive_user.id],
                "to_groups": [],
            },
            current_user=self.first_user
        )
        with self.assertRaises(TypeError):
            new_form.is_valid()

    def test_new_message_form_inactive_users_do_not_show(self):
        new_form = forms.NewMessageForm(
            {
                "subject": "dummy subject",
                "content": "dummy content",
                "to_users": [],
                "to_groups": [],
            },
            current_user=self.first_user
        )
        eligible_users = list(new_form.fields["to_users"].queryset)
        self.assertNotIn(self.inactive_user, eligible_users)

    def test_new_message_form_admin_can_message_all_groups(self):
        new_form = forms.NewMessageForm(
            {
                "subject": "dummy subject",
                "content": "dummy content",
                "to_users": [],
                "to_groups": [],
            },
            current_user=self.admin_user
        )
        all_group_profiles = [
            self.first_group_profile,
            self.second_group_profile,
            self.third_group_profile,
            self.fourth_group_profile,
        ]
        for group in all_group_profiles:
            self.assertIn(group, new_form.fields["to_groups"].queryset)
