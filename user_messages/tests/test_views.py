"""Unit tests for user_messages.views"""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from django.http.request import QueryDict
from django.test import TestCase
import mock

from geonode.groups.models import GroupProfile

from user_messages import models


class Base(TestCase):

    def setUp(self):
        self.user_password = "pass"
        self.first_user = get_user_model().objects.create_user(
            "first", "first@fakemail.com", self.user_password)
        self.second_user = get_user_model().objects.create_user(
            "second", "second@fakemail.com", self.user_password)
        self.third_user = get_user_model().objects.create_user(
            "third", "third@fakemail.com", self.user_password)
        self.fourth_user = get_user_model().objects.create_user(
            "fourth", "fourth@fakemail.com", self.user_password)

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

        self.first_group = self.first_group_profile.group
        self.second_group = self.second_group_profile.group

        self.first_group_profile.join(self.first_user)
        self.first_group_profile.join(self.second_user)
        self.second_group_profile.join(self.first_user)
        self.second_group_profile.join(self.third_user)
        self.second_group_profile.join(self.fourth_user)

        self.first_message = models.Message.objects.new_message(
            from_user=self.first_user,
            subject="first message of the first thread",
            content="test",
            to_users=[self.second_user],
        )
        self.second_message = models.Message.objects.new_message(
            from_user=self.first_user,
            subject="first message of the second thread",
            content="test",
            to_groups=[self.second_group_profile],
        )
        self.first_thread = self.first_message.thread
        self.second_thread = self.second_message.thread
        self.first_reply = models.Message.objects.new_reply(
            self.first_thread, self.second_user,
            "second message of the first thread"
        )
        print("number of groups: {}".format(Group.objects.count()))
        print("number of groupprofiles: {}".format(GroupProfile.objects.count()))


class ViewsTestCase(Base):

    def setUp(self):
        super(ViewsTestCase, self).setUp()
        self.user = self.first_user
        self.thread = self.first_thread
        self.client.login(
            username=self.user.username, password=self.user_password)

    def test_inbox(self):
        self.client.login(
            username=self.first_user.username, password=self.user_password)
        with mock.patch("user_messages.views.Thread",
                        autospec=True) as mock_thread:
            mock_thread.objects.sorted_active_threads.return_value = []
            mock_thread.objects.sorted_unread_threads.return_value = []
            response = self.client.get(reverse("messages_inbox"))
            self.assertEqual(response.status_code, 200)
            mock_thread.objects.sorted_active_threads.assert_called_with(
                self.first_user)

    def test_thread_detail_get_renders(self):
        with mock.patch("user_messages.views.MessageReplyForm",
                        autospec=True) as MockForm:
            response = self.client.get(
                reverse("messages_thread_detail", args=(self.thread.id,)))
            MockForm.assert_called_with(user=self.user, thread=self.thread)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context["form"], MockForm.return_value)

    def test_thread_detail_get_existing_thread_sets_unread_to_false(self):
        self.client.get(
            reverse("messages_thread_detail", args=(self.thread.id,)))
        user_thread = self.thread.userthread_set.get(user=self.user)
        self.assertFalse(user_thread.unread)

    def test_thread_detail_post(self):
        post_data = {"dummy_param": "dummy_value"}
        query_string = "&".join(
            "{}={}".format(k, v) for k, v in post_data.items())
        mock_post_querydict = QueryDict(query_string)
        post_data = QueryDict("dummy_param=dummy_value")
        with mock.patch("user_messages.views.MessageReplyForm",
                        autospec=True) as MockForm:
            MockForm.return_value.is_valid.return_value = True
            response = self.client.post(
                reverse("messages_thread_detail", args=(self.thread.id,)),
                data=post_data,
            )
            MockForm.assert_called_with(
                mock_post_querydict, user=self.user, thread=self.thread)
            self.assertTrue(MockForm.return_value.is_valid.called)
            self.assertTrue(MockForm.return_value.save.called)
            self.assertRedirects(response, reverse("messages_inbox"))

    def test_message_create_no_args_get_renders(self):
        mock_initial = {
            "to_users": [None],
            "to_groups": [None],
        }
        response = self.client.get(reverse("message_create_multiple"))
        self.assertEqual(response.status_code, 200)

    def test_message_create_post(self):
        test_subject = "hi"
        test_content = "hello"
        post_data = {
            "to_users": [self.second_user.id],
            "to_groups": [],
            "subject": test_subject,
            "content": test_content,
        }
        response = self.client.post(
            reverse("message_create_multiple"),
            data=post_data
        )
        new_thread = models.Thread.objects.get(subject=test_subject)
        new_message = models.Message.objects.get(
            thread=new_thread, sender=self.user, content=test_content)
        self.assertRedirects(response, new_message.get_absolute_url())

    def test_thread_delete_single_user(self):
        response = self.client.post(
            reverse(
                "messages_thread_delete",
                kwargs={"thread_id": self.thread.id}
            )
        )
        user_thread = models.UserThread.objects.get(
            thread=self.thread, user=self.user)
        self.assertEqual(user_thread.deleted, True)
        self.assertRedirects(response, reverse("messages_inbox"))

    def test_thread_delete_group_member(self):
        self.client.logout()
        self.client.login(username=self.third_user.username,
                          password=self.user_password)
        response = self.client.post(
            reverse(
                "messages_thread_delete",
                kwargs={"thread_id": self.second_thread.id}
            )
        )
        groupmember_thread = models.GroupMemberThread.objects.get(
            thread=self.second_thread,
            user=self.third_user,
            group=self.second_group
        )
        self.assertEqual(groupmember_thread.deleted, True)
        self.assertRedirects(response, reverse("messages_inbox"))
