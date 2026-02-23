"""
Context processors for passing global template data
"""
from django.contrib.auth.decorators import login_required
from .models import Notification


def customer_notifications(request):
    """
    Add unread notifications to template context for authenticated customers
    """
    context = {
        'unread_notifications': [],
        'unread_notification_count': 0,
    }
    
    if request.user.is_authenticated:
        # Get unread notifications
        unread = Notification.objects.filter(
            customer=request.user,
            is_read=False
        ).order_by('-created_at')
        
        context['unread_notifications'] = unread[:5]  # Show latest 5
        context['unread_notification_count'] = Notification.objects.filter(
            customer=request.user,
            is_read=False
        ).count()
    
    return context
