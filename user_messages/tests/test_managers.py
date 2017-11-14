"""Unit tests for user_messages.managers."""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
import mock

from geonode.groups.models import GroupProfile

from user_messages import models
from user_messages import managers
#from user_messages.signals import message_sent


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
        self.fifth_user = get_user_model().objects.create_user(
            "fifth", "fifth@fakemail.com", self.user_password)
        self.inactive_user = get_user_model().objects.create_user(
            "inactive_user", "inactive@fakemail.com", self.user_password)
        self.inactive_user.is_active = False
        self.inactive_user.save()

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
        self.second_group_profile.join(self.inactive_user)


class ThreadManagerSingleUsersTestCase(Base):

    def setUp(self):
        super(ThreadManagerSingleUsersTestCase, self).setUp()
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
            to_users=[self.second_user, self.third_user],
        )
        self.first_thread = self.first_message.thread
        self.second_thread = self.second_message.thread
        self.first_reply = models.Message.objects.new_reply(
            self.first_thread, self.second_user,
            "second message of the first thread"
        )

    def test_active_threads(self):
        first = models.Thread.objects.active_threads(self.first_user)
        second = models.Thread.objects.active_threads(self.second_user)
        third = models.Thread.objects.active_threads(self.third_user)
        fourth = models.Thread.objects.active_threads(self.fourth_user)
        fifth = models.Thread.objects.active_threads(self.fifth_user)

        self.assertEqual(len(first), 2)
        self.assertEqual(len(second), 2)
        self.assertEqual(len(third), 1)
        self.assertEqual(len(fourth), 0)
        self.assertEqual(len(fifth), 0)

        self.assertIn(self.first_thread, first)
        self.assertIn(self.second_thread, first)
        self.assertIn(self.first_thread, second)
        self.assertIn(self.second_thread, second)
        self.assertIn(self.second_thread, third)

    def test_unread_threads(self):
        first = models.Thread.objects.unread_threads(self.first_user)
        second = models.Thread.objects.unread_threads(self.second_user)
        third = models.Thread.objects.unread_threads(self.third_user)
        fourth = models.Thread.objects.unread_threads(self.fourth_user)
        fifth = models.Thread.objects.unread_threads(self.fifth_user)

        self.assertEqual(len(first), 1)
        self.assertEqual(len(second), 1)
        self.assertEqual(len(third), 1)
        self.assertEqual(len(fourth), 0)
        self.assertEqual(len(fifth), 0)

        self.assertIn(self.first_thread, first)
        self.assertIn(self.second_thread, second)
        self.assertIn(self.second_thread, third)


class ThreadManagerGroupsTestCase(Base):

    def setUp(self):
        super(ThreadManagerGroupsTestCase, self).setUp()
        self.first_message = models.Message.objects.new_message(
            from_user=self.first_user,
            subject="first message of the third thread",
            content="test",
            to_groups=[self.first_group_profile,]
        )
        self.second_message = models.Message.objects.new_message(
            from_user=self.first_user,
            subject="first message of the third thread",
            content="test",
            to_groups=[self.first_group_profile, self.second_group_profile]
        )
        self.first_thread = self.first_message.thread
        self.second_thread = self.second_message.thread
        self.first_reply = models.Message.objects.new_reply(
            self.first_thread, self.second_user,
            "second message of the first thread"
        )

    def test_active_threads(self):
        first = models.Thread.objects.active_threads(self.first_user)
        second = models.Thread.objects.active_threads(self.second_user)
        third = models.Thread.objects.active_threads(self.third_user)
        fourth = models.Thread.objects.active_threads(self.fourth_user)
        fifth = models.Thread.objects.active_threads(self.fifth_user)

        self.assertEqual(len(first), 2)
        self.assertEqual(len(second), 2)
        self.assertEqual(len(third), 1)
        self.assertEqual(len(fourth), 1)
        self.assertEqual(len(fifth), 0)

        self.assertIn(self.first_thread, first)
        self.assertIn(self.second_thread, first)
        self.assertIn(self.first_thread, second)
        self.assertIn(self.second_thread, second)
        self.assertIn(self.second_thread, third)

    def test_unread_threads(self):
        first = models.Thread.objects.unread_threads(self.first_user)
        second = models.Thread.objects.unread_threads(self.second_user)
        third = models.Thread.objects.unread_threads(self.third_user)
        fourth = models.Thread.objects.unread_threads(self.fourth_user)
        fifth = models.Thread.objects.unread_threads(self.fifth_user)

        self.assertEqual(len(first), 1)
        self.assertEqual(len(second), 1)
        self.assertEqual(len(third), 1)
        self.assertEqual(len(fourth), 1)
        self.assertEqual(len(fifth), 0)

        self.assertIn(self.first_thread, first)
        self.assertIn(self.second_thread, second)
        self.assertIn(self.second_thread, third)
        self.assertIn(self.second_thread, fourth)


class MessageManagerSingleUsersTestCase(Base):

    def setUp(self):
        super(MessageManagerSingleUsersTestCase, self).setUp()
        self.test_subject = "test subject"
        self.test_content = "test content"
        self.sender = self.first_user
        self.to_users = [self.second_user, self.third_user]
        self.message = models.Message.objects.new_message(
            from_user=self.sender,
            subject=self.test_subject,
            content=self.test_content,
            to_users=self.to_users
        )

    def test_new_message_has_thread(self):
        self.assertIsNotNone(self.message.thread)

    def test_new_message_thread_has_users(self):
        for user_profile in self.to_users:
            self.message.thread.single_users.get(id=user_profile.id)

    def test_new_message_thread_has_no_groups(self):
        self.assertEqual(self.message.thread.group_users.count(), 0)

    def test_new_message_thread_has_subject(self):
        self.assertEqual(self.message.thread.subject, self.test_subject)

    def test_new_message_has_content(self):
        self.assertEqual(self.message.content, self.test_content)

    def test_new_message_sender_visibility_is_read(self):
        user_thread = self.message.sender.userthread_set.get(
            thread=self.message.thread)
        self.assertFalse(user_thread.unread)

    def test_new_message_recipients_visibility_is_unread(self):
        recipient_user_threads = self.message.thread.userthread_set.exclude(
            user=self.sender)
        for user_thread in recipient_user_threads:
            self.assertTrue(user_thread.unread)

    def test_new_message_is_not_deleted_for_any_recipient(self):
        for user_thread in self.message.thread.userthread_set.all():
            self.assertFalse(user_thread.deleted)

    def test_new_message_sends_signal(self):
        with mock.patch.object(managers.message_sent,
                               "send", autospec=True) as mock_signal_send:
            models.Message.objects.new_message(
                from_user=self.sender,
                subject=self.test_subject,
                content=self.test_content,
                to_users=self.to_users
            )
            self.assertTrue(mock_signal_send.called)


class MessageManagerSingleUsersReplyTestCase(Base):
    """Test stuff related to replying to a message"""

    def setUp(self):
        super(MessageManagerSingleUsersReplyTestCase, self).setUp()
        self.test_subject = "test subject"
        self.test_content = "test content"
        self.test_reply = "test reply"
        self.sender = self.first_user
        self.reply_sender = self.third_user
        self.to_users = [self.second_user, self.third_user]
        self.message = models.Message.objects.new_message(
            from_user=self.sender,
            subject=self.test_subject,
            content=self.test_content,
            to_users=self.to_users
        )
        self.reply = models.Message.objects.new_reply(
            thread=self.message.thread,
            user=self.reply_sender,
            content=self.test_reply
        )

    def test_new_reply_belongs_to_thread(self):
        self.assertIs(self.reply.thread, self.message.thread)

    def test_new_reply_has_content(self):
        self.assertEqual(self.reply.content, self.test_reply)

    def test_new_reply_sender_visibility_is_read(self):
        user_thread = self.reply.sender.userthread_set.get(
            thread=self.message.thread)
        self.assertFalse(user_thread.unread)

    def test_new_reply_recipients_visibility_is_unread(self):
        recipient_user_threads = self.reply.thread.userthread_set.exclude(
            user=self.reply_sender)
        for user_thread in recipient_user_threads:
            self.assertTrue(user_thread.unread)

    def test_new_reply_is_not_deleted_for_any_recipient(self):
        for user_thread in self.reply.thread.userthread_set.all():
            self.assertFalse(user_thread.deleted)


class MessageManagerGroupsTestCase(Base):
    """Tests for when messages are sent to groups"""

    def setUp(self):
        super(MessageManagerGroupsTestCase, self).setUp()
        self.test_subject = "test subject"
        self.test_content = "test content"
        self.sender = self.first_user
        self.to_groups = [self.first_group_profile, self.second_group_profile]
        self.message = models.Message.objects.new_message(
            from_user=self.sender,
            subject=self.test_subject,
            content=self.test_content,
            to_groups=self.to_groups
        )

    def test_new_message_thread_has_users(self):
        expected_members = []
        for group_profile in self.to_groups:
            group_members = group_profile.group.user_set.filter(is_active=True)
            expected_members.extend(group_members)
        for thread_member in self.message.thread.groupmemberthread_set.all():
            self.assertIn(thread_member.user, expected_members)

    def test_new_message_thread_has_groups(self):
        for group_profile in self.to_groups:
            self.assertIn(
                group_profile.group, self.message.thread.registered_groups)
        self.assertEqual(
            len(self.message.thread.registered_groups),
            2
        )

    def test_new_message_thread_does_not_have_inactive_users(self):
        thread_members = get_user_model().objects.filter(
            groupmemberthread__thread=self.message.thread)
        self.assertNotIn(self.inactive_user, thread_members)

    def test_new_message_sender_visibility_is_read(self):
        user_thread = self.message.sender.userthread_set.get(
            thread=self.message.thread)
        self.assertFalse(user_thread.unread)

    def test_new_message_recipients_visibility_is_unread(self):
        recipients = self.message.thread.groupmemberthread_set.exclude(
            user=self.sender)
        for user_thread in recipients:
            self.assertTrue(user_thread.unread)

    def test_new_message_is_not_deleted_for_any_recipient(self):
        for member_thread in self.message.thread.groupmemberthread_set.all():
            self.assertFalse(member_thread.deleted)
