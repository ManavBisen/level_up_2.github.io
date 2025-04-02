from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseForbidden
from django.core.paginator import Paginator

from .models import DirectMessage, CommunityMessage
from .forms import DirectMessageForm, CommunityMessageForm, UserSearchForm
from users.models import Notification

@login_required
def inbox(request):
    """View user's inbox/conversations"""
    conversations = DirectMessage.get_conversations(request.user)
    
    # Search for users
    search_form = UserSearchForm(request.GET)
    search_results = []
    
    if search_form.is_valid() and search_form.cleaned_data.get('username'):
        search_term = search_form.cleaned_data.get('username')
        search_results = User.objects.filter(username__icontains=search_term).exclude(id=request.user.id)[:10]
    
    context = {
        'conversations': conversations,
        'search_form': search_form,
        'search_results': search_results,
    }
    return render(request, 'messaging/inbox.html', context)

@login_required
def direct_message(request, username):
    """View for direct messaging with a specific user"""
    # Get the other user
    receiver = get_object_or_404(User, username=username)
    
    # Handle message submission
    if request.method == 'POST':
        form = DirectMessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver = receiver
            message.save()
            
            # Create notification for receiver
            Notification.objects.create(
                user=receiver,
                message=f"New message from {request.user.username}: {message.content[:50]}..."
            )
            
            messages.success(request, "Message sent!")
            return redirect('direct_message', username=username)
    else:
        form = DirectMessageForm()
    
    # Get conversation
    conversation = DirectMessage.get_conversation(request.user, receiver)
    
    # Mark messages as read
    unread_messages = conversation.filter(receiver=request.user, is_read=False)
    unread_messages.update(is_read=True)
    
    context = {
        'form': form,
        'conversation': conversation,
        'receiver': receiver,
    }
    return render(request, 'messaging/direct_message.html', context)

@login_required
def delete_direct_message(request, message_id):
    """Delete a direct message"""
    message = get_object_or_404(DirectMessage, id=message_id)
    
    # Only allow sender to delete
    if message.sender != request.user:
        return HttpResponseForbidden("You cannot delete this message.")
    
    # Get username before deleting for redirect
    username = message.receiver.username
    
    message.delete()
    messages.success(request, "Message deleted!")
    return redirect('direct_message', username=username)

@login_required
def community(request):
    """View for community chat"""
    # Handle message submission
    if request.method == 'POST':
        form = CommunityMessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.save()
            messages.success(request, "Message posted to community!")
            return redirect('community')
    else:
        form = CommunityMessageForm()
    
    # Get community messages (paginated)
    community_messages = CommunityMessage.objects.all()
    paginator = Paginator(community_messages, 50)  # 50 messages per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'page_obj': page_obj,
    }
    return render(request, 'messaging/community.html', context)

@login_required
def delete_community_message(request, message_id):
    """Delete a community message"""
    message = get_object_or_404(CommunityMessage, id=message_id)
    
    # Only allow sender or superuser to delete
    if message.sender != request.user and not request.user.is_staff:
        return HttpResponseForbidden("You cannot delete this message.")
    
    message.delete()
    messages.success(request, "Message deleted!")
    return redirect('community')

@login_required
def unread_message_count(request):
    """API to get unread message count for the current user"""
    count = DirectMessage.objects.filter(receiver=request.user, is_read=False).count()
    return JsonResponse({'count': count})
