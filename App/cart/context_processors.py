from .models import Cart, CartItems
from .views import _cart_id


def counter(request):
    """
    Context processor to calculate and pass cart item count to all templates.
    
    Behavior:
    - For authenticated users: Count items from their user account
    - For anonymous users: Count items from their session-based cart
    - Excludes admin pages to avoid unnecessary database queries
    - Returns 0 if no cart or items exist
    
    Returns:
        dict: Contains 'cart_count' with total quantity of all items in cart
    """
    cart_count = 0
    
    # Skip processing for admin pages to avoid unnecessary queries
    if 'admin' in request.path:
        return {}
    
    try:
        # AUTHENTICATED USER: Get cart items linked to the user account
        if request.user.is_authenticated:
            # Count items directly from user
            cart_items = CartItems.objects.filter(user=request.user, is_active=True)
            for cart_item in cart_items:
                cart_count += cart_item.quantity
        
        # ANONYMOUS USER: Get cart items from session-based cart
        else:
            # Get cart using session key
            cart = Cart.objects.get(cart_id=_cart_id(request))
            # Count items in this session cart
            cart_items = CartItems.objects.filter(cart=cart, is_active=True)
            for cart_item in cart_items:
                cart_count += cart_item.quantity
    
    except Cart.DoesNotExist:
        # No session cart exists yet (user hasn't added items)
        cart_count = 0
    except Exception as e:
        # Gracefully handle any other errors
        cart_count = 0
    
    return dict(cart_count=cart_count)