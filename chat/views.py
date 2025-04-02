from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Q

from .models import DirectMessage, CommunityMessage


@login_required
def direct_messages(request):
    """Show list of conversations"""
    # Get distinct users that the current user has conversations with
    senders = User.objects.filter(sent_messages__recipient=request.user).distinct()
    recipients = User.objects.filter(received_messages__sender=request.user).distinct()
    
    # Combine the two querysets and remove duplicates
    contacts = (senders | recipients).distinct()
    
    context = {
        'contacts': contacts
    }
    
    return render(request, 'chat/direct_messages.html', context)


@login_required
def direct_message_conversation(request, username):
    """Show conversation with specific user"""
    contact = get_object_or_404(User, username=username)
    
    # Get all messages between current user and contact
    messages_list = DirectMessage.objects.filter(
        Q(sender=request.user, recipient=contact) | 
        Q(sender=contact, recipient=request.user)
    ).order_by('timestamp')
    
    # Mark received messages as read
    unread_messages = messages_list.filter(recipient=request.user, is_read=False)
    for msg in unread_messages:
        msg.is_read = True
        msg.save()
    
    context = {
        'contact': contact,
        'messages': messages_list
    }
    
    return render(request, 'chat/direct_message_conversation.html', context)


@login_required
def send_direct_message(request):
    """Send direct message to another user"""
    if request.method != 'POST':
        return redirect('direct_messages')
    
    recipient_username = request.POST.get('recipient')
    message_content = request.POST.get('content')
    attachment = request.FILES.get('attachment', None)
    
    if not recipient_username or not message_content:
        messages.error(request, "Both recipient and message content are required.")
        return redirect('direct_messages')
    
    try:
        recipient = User.objects.get(username=recipient_username)
        
        # Create message
        message = DirectMessage(
            sender=request.user,
            recipient=recipient,
            content=message_content
        )
        
        if attachment:
            message.attachment = attachment
        
        message.save()
        
        return redirect('direct_message_conversation', username=recipient_username)
    
    except User.DoesNotExist:
        messages.error(request, f"User '{recipient_username}' does not exist.")
        return redirect('direct_messages')


@login_required
def delete_direct_message(request, message_id):
    """Delete a direct message (only sender can delete)"""
    message = get_object_or_404(DirectMessage, id=message_id)
    
    # Check if current user is the sender
    if message.sender != request.user:
        return HttpResponseForbidden("You can only delete your own messages.")
    
    recipient_username = message.recipient.username
    message.delete()
    
    if request.is_ajax():
        return JsonResponse({'success': True})
    
    return redirect('direct_message_conversation', username=recipient_username)


@login_required
def community_chat(request):
    """Show community chat"""
    messages_list = CommunityMessage.objects.all().order_by('timestamp')
    
    context = {
        'messages': messages_list
    }
    
    return render(request, 'chat/community.html', context)


@login_required
def send_community_message(request):
    """Send message to community chat"""
    if request.method != 'POST':
        return redirect('community_chat')
    
    message_content = request.POST.get('content')
    attachment = request.FILES.get('attachment', None)
    
    if not message_content:
        messages.error(request, "Message content is required.")
        return redirect('community_chat')
    
    # Create message
    message = CommunityMessage(
        sender=request.user,
        content=message_content
    )
    
    if attachment:
        message.attachment = attachment
    
    message.save()
    
    return redirect('community_chat')


@login_required
def delete_community_message(request, message_id):
    """Delete a community message (only sender or superuser can delete)"""
    message = get_object_or_404(CommunityMessage, id=message_id)
    
    # Check if current user is the sender or a superuser
    if message.sender != request.user and not request.user.is_superuser:
        return HttpResponseForbidden("You can only delete your own messages.")
    
    message.delete()
    
    if request.is_ajax():
        return JsonResponse({'success': True})
    
    return redirect('community_chat')
