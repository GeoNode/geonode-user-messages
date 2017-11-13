from django.contrib import admin
from django.contrib.admin import StackedInline

from . import models


class UserThreadInline(StackedInline):
    model = models.UserThread
    extra = 0


class GroupMemberThreadInline(StackedInline):
    model = models.GroupMemberThread
    extra = 0


class MessageInline(StackedInline):
    model = models.Message
    extra = 0


class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'thread')
    list_display_links = ('id',)


class ThreadAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'num_messages', 'num_users',)
    list_display_links = ('id',)
    inlines = (MessageInline, UserThreadInline, GroupMemberThreadInline,)


class UserThreadAdmin(admin.ModelAdmin):
    list_display = ('id',)
    list_display_links = ('id',)


admin.site.register(models.Message, MessageAdmin)
admin.site.register(models.Thread, ThreadAdmin)
admin.site.register(models.UserThread, UserThreadAdmin)
