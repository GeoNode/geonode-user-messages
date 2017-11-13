"""Unit tests for user_messages.models."""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from django.test import TestCase

from geonode.groups.models import GroupProfile

from user_messages import models


class MessageTestCase(TestCase):

    def setUp(self):
        self.thread_author = get_user_model().objects.create_user(
            "sender", "sender@fakemail.com", "pass")
        self.single_user = get_user_model().objects.create_user(
            "tester_single", "testersingle@fakemail.com", "pass")
        self.first_message_to_single_user = models.Message.objects.new_message(
            from_user=self.thread_author,
            subject="message a single user",
            content="test",
            to_users=[self.single_user],
        )
        self.thread_message_to_single_user = (
            self.first_message_to_single_user.thread)

    def test_get_absolute_url(self):
        abs_url = self.first_message_to_single_user.get_absolute_url()
        expected = reverse(
            "messages_thread_detail",
            kwargs={
                "thread_id": self.first_message_to_single_user.thread.id
            }
        )
        self.assertEqual(abs_url, expected)


class ThreadBase(TestCase):

    def setUp(self):
        self.first_user = get_user_model().objects.create_user(
            "first", "first@fakemail.com", "pass")
        self.second_user = get_user_model().objects.create_user(
            "second", "second@fakemail.com", "pass")
        self.third_user = get_user_model().objects.create_user(
            "third", "third@fakemail.com", "pass")
        self.fourth_user = get_user_model().objects.create_user(
            "fourth", "fourth@fakemail.com", "pass")
        self.fifth_user = get_user_model().objects.create_user(
            "fifth", "fifth@fakemail.com", "pass")

        self.first_group_profile = GroupProfile.objects.create(
            title="testfirst",
            slug="testfirst",
            description="test",
            access="public",
        )
        self.second_group_profile = GroupProfile.objects.create(
            title="testsecond",
            slug="testsecond",
            description="test",
            access="public",
        )

        self.first_group = self.first_group_profile.group
        self.second_group = self.second_group_profile.group

        self.first_group_profile.join(self.first_user)
        self.first_group_profile.join(self.second_user)
        self.second_group_profile.join(self.first_user)
        self.second_group_profile.join(self.third_user)
        self.second_group_profile.join(self.fourth_user)


class ThreadSingleUserTestCase(ThreadBase):

    def setUp(self):
        super(ThreadSingleUserTestCase, self).setUp()
        self.first_message = models.Message.objects.new_message(
            from_user=self.first_user,
            subject="first message of the first thread",
            content="test",
            to_users=[self.second_user],
        )
        self.first_thread = self.first_message.thread
        self.first_reply = models.Message.objects.new_reply(
            self.first_thread, self.second_user,
            "second message of the first thread"
        )

    def test_first_message(self):
        self.assertEqual(self.first_thread.first_message, self.first_message)

    def test_latest_message(self):
        self.assertEqual(self.first_thread.latest_message, self.first_reply)

    def test_num_messages(self):
        self.assertEqual(self.first_thread.num_messages, 2)

    def test_registered_users(self):
        self.assertIn(self.first_user, self.first_thread.registered_users)
        self.assertIn(self.second_user, self.first_thread.registered_users)
        self.assertNotIn(self.third_user, self.first_thread.registered_users)
        self.assertNotIn(self.fourth_user, self.first_thread.registered_users)
        self.assertNotIn(self.fifth_user, self.first_thread.registered_users)

    def test_registered_groups(self):
        self.assertEqual(len(self.first_thread.registered_groups), 0)

    def test_num_users(self):
        self.assertEqual(self.first_thread.num_users, 2)


class ThreadMultiUserTestCase(ThreadBase):

    def setUp(self):
        super(ThreadMultiUserTestCase, self).setUp()
        self.first_message = models.Message.objects.new_message(
            from_user=self.first_user,
            subject="first message of the first thread",
            content="test",
            to_users=[self.second_user, self.third_user],
        )
        self.first_thread = self.first_message.thread
        self.first_reply = models.Message.objects.new_reply(
            self.first_thread, self.second_user,
            "second message of the first thread"
        )

    def test_registered_users(self):
        self.assertIn(self.first_user, self.first_thread.registered_users)
        self.assertIn(self.second_user, self.first_thread.registered_users)
        self.assertIn(self.third_user, self.first_thread.registered_users)
        self.assertNotIn(self.fourth_user, self.first_thread.registered_users)
        self.assertNotIn(self.fifth_user, self.first_thread.registered_users)

    def test_num_users(self):
        self.assertEqual(self.first_thread.num_users, 3)


class ThreadSingleGroupTestCase(ThreadBase):
    """Tests threaded messages sent to a single group"""

    def setUp(self):
        super(ThreadSingleGroupTestCase, self).setUp()
        self.first_message = models.Message.objects.new_message(
            from_user=self.first_user,
            subject="first message of the first thread",
            content="test",
            to_groups=[self.first_group_profile],
        )
        self.first_thread = self.first_message.thread
        self.first_reply = models.Message.objects.new_reply(
            self.first_thread, self.second_user,
            "second message of the first thread"
        )

    def test_registered_users(self):
        self.assertIn(self.first_user, self.first_thread.registered_users)
        self.assertIn(self.second_user, self.first_thread.registered_users)
        self.assertNotIn(self.third_user, self.first_thread.registered_users)
        self.assertNotIn(self.fourth_user, self.first_thread.registered_users)
        self.assertNotIn(self.fifth_user, self.first_thread.registered_users)

    def test_registered_groups(self):
        self.assertIn(self.first_group_profile.group,
                      self.first_thread.registered_groups)
        self.assertEqual(len(self.first_thread.registered_groups), 1)

    def test_num_users(self):
        self.assertEqual(self.first_thread.num_users, 2)


class ThreadMultipleGroupTestCase(ThreadBase):
    """Tests threaded messages when groups are independent"""

    def setUp(self):
        super(ThreadMultipleGroupTestCase, self).setUp()
        self.first_message = models.Message.objects.new_message(
            from_user=self.first_user,
            subject="first message of the first thread",
            content="test",
            to_groups=[self.first_group_profile, self.second_group_profile],
        )
        self.first_thread = self.first_message.thread
        self.first_reply = models.Message.objects.new_reply(
            self.first_thread, self.second_user,
            "second message of the first thread"
        )

    def test_registered_users(self):
        self.assertIn(self.first_user, self.first_thread.registered_users)
        self.assertIn(self.second_user, self.first_thread.registered_users)
        self.assertIn(self.third_user, self.first_thread.registered_users)
        self.assertIn(self.fourth_user, self.first_thread.registered_users)
        self.assertNotIn(self.fifth_user, self.first_thread.registered_users)

    def test_registered_groups(self):
        self.assertIn(self.first_group_profile.group,
                      self.first_thread.registered_groups)
        self.assertIn(self.second_group_profile.group,
                      self.first_thread.registered_groups)
        self.assertEqual(len(self.first_thread.registered_groups), 2)

    def test_num_users(self):
        self.assertEqual(self.first_thread.num_users, 4)


class ThreadMixGroupAndSingleUserTestCase(ThreadBase):
    """Tests threaded messages to groups and individual users"""

    def setUp(self):
        super(ThreadMixGroupAndSingleUserTestCase, self).setUp()
        self.first_message = models.Message.objects.new_message(
            from_user=self.first_user,
            subject="first message of the first thread",
            content="test",
            to_users=[self.second_user],
            to_groups=[self.first_group_profile],
        )
        self.first_thread = self.first_message.thread
        self.first_reply = models.Message.objects.new_reply(
            self.first_thread, self.second_user,
            "second message of the first thread"
        )

    def test_num_users(self):
        self.assertEqual(self.first_thread.num_users, 2)
