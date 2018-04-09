from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from django.contrib.auth.decorators import login_required

from user_messages.forms import MessageReplyForm, NewMessageForm
from user_messages.models import Message
from user_messages.models import Thread
from user_messages.models import UserThread
from user_messages.models import GroupMemberThread


@login_required
def inbox(request, template_name="user_messages/inbox.html"):
    return render(
        request,
        template_name,
        context={
            "threads_all": Thread.objects.sorted_active_threads(request.user),
            "threads_unread" : Thread.objects.sorted_unread_threads(
                request.user),
        }
    )


@login_required
def thread_detail(request, thread_id,
                  template_name="user_messages/thread_detail.html"):
    thread = get_object_or_404(
        Thread.objects.active_threads(request.user),
        pk=thread_id
    )
    if request.method == "POST":
        #form = form_class(request.POST, user=request.user, thread=thread)
        form = MessageReplyForm(request.POST, user=request.user, thread=thread)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("messages_inbox"))
    else:
        form = MessageReplyForm(user=request.user, thread=thread)
        thread.userthread_set.filter(user=request.user).update(unread=False)
    return render(request, template_name, context={
        "thread": thread,
        "form": form
    })


@login_required
def message_create(request, user_id=None, group_id=None,
                   template_name="user_messages/message_create.html"):
    subject = request.GET['subject'] if 'subject' in request.GET else ''
    content = request.GET['content'] if 'content' in request.GET else ''
    initial = {
        "to_users": [user_id],
        "to_groups": [group_id],
        "subject": subject,
        "content": content,
    }
    if request.method == "POST":
        form = NewMessageForm(
            request.POST, current_user=request.user, initial=initial)
        if form.is_valid():
            message = Message.objects.new_message(
                from_user=request.user,
                to_users=form.cleaned_data["to_users"],
                to_groups=form.cleaned_data["to_groups"],
                subject=form.cleaned_data["subject"],
                content=form.cleaned_data["content"]
            )
            return HttpResponseRedirect(message.get_absolute_url())
    else:
        form = NewMessageForm(current_user=request.user, initial=initial)
    return render(
        request,
        template_name,
        context={"form": form}
    )


@login_required
@require_POST
def thread_delete(request, thread_id):
    thread = get_object_or_404(
        Thread.objects.active_threads(request.user),
        pk=thread_id
    )
    try:
        user_thread = thread.userthread_set.get(user=request.user)
        user_thread.deleted = True
        user_thread.save()
    except UserThread.DoesNotExist:
        # user is not participating in the discussion as standalone
        # might part of one of the thread's groups though
        pass
    try:
        member_threads = thread.groupmemberthread_set.filter(user=request.user)
        member_threads.update(deleted=True)
    except GroupMemberThread.DoesNotExist:
        # user is not part of any groups that are in the discussion
        pass
    return HttpResponseRedirect(reverse("messages_inbox"))
