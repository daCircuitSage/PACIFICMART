from .models import UserProfile

def user_profile(request):
    """
    Context processor to make user profile available in all templates
    """
    if request.user.is_authenticated:
        try:
            userprofile = UserProfile.objects.get(user=request.user)
            return {
                'userprofile': userprofile,
            }
        except UserProfile.DoesNotExist:
            # Create a profile if it doesn't exist
            userprofile = UserProfile.objects.create(user=request.user)
            return {
                'userprofile': userprofile,
            }
    
    return {}
