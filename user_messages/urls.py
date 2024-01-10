from django.urls import re_path
from . import views

urlpatterns = [  # "user_messages.views",
    re_path(r"^inbox/$", views.inbox, name="messages_inbox"),
    re_path(r"^create/$", views.message_create, name="message_create"),
    re_path(r"^create/(?P<user_id>\d+)/$", views.message_create, name="message_create"),
    re_path(r"^create/_multiple/$", views.message_create, name="message_create_multiple"),
    re_path(r"^thread/(?P<thread_id>\d+)/$", views.thread_detail,
        name="messages_thread_detail"),
    re_path(r"^thread/(?P<thread_id>\d+)/delete/$", views.thread_delete,
        name="messages_thread_delete"),
]
