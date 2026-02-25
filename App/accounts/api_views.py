import json
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from .models import Account, EmailStatus

logger = logging.getLogger(__name__)

@require_GET
@csrf_exempt
def check_email_status(request):
    """
    API endpoint to check email sending status
    """
    email = request.GET.get('email')
    email_type = request.GET.get('type', 'verification')
    
    if not email:
        return JsonResponse({'status': 'error', 'message': 'Email parameter is required'}, status=400)
    
    try:
        user = Account.objects.get(email__iexact=email)
        email_status = EmailStatus.objects.filter(
            user=user, 
            email_type=email_type
        ).order_by('-created_at').first()
        
        if not email_status:
            return JsonResponse({
                'status': 'not_found',
                'message': 'No email record found'
            })
        
        response_data = {
            'status': email_status.status,
            'created_at': email_status.created_at.isoformat(),
            'sent_at': email_status.sent_at.isoformat() if email_status.sent_at else None,
            'retry_count': email_status.retry_count,
            'error_message': email_status.error_message if email_status.status == 'failed' else None
        }
        
        return JsonResponse(response_data)
        
    except Account.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)
    except Exception as e:
        logger.error(f"Error checking email status: {str(e)}")
        return JsonResponse({'status': 'error', 'message': 'Internal server error'}, status=500)
