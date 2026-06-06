from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.views import View
from django_osoul.site import PageHandler

from plugins.products.services.cart_service import CartService


class CartView(PageHandler):
    """
    Shopping cart view handler.
    """

    page_title = _("Shopping Cart")
    template_name = "common/partials/cart_items.html"

    def get_context_data(self, request: HttpRequest, **kwargs):
        """
        Get context data for the cart view.
        """
        context = super().get_context_data(**kwargs)
        context['cart_items'] = self._get_cart_items(request)
        return context

    def _get_cart_items(self, request: HttpRequest):
        """
        Retrieve cart items using CartService.
        """
        if request.user.is_authenticated:
            cart = CartService.get_or_create_cart(request)
            items = []
            for item in cart.items.all():
                product_data = {
                    'id': item.id,
                    'name': item.product_name,
                    'description': item.product_description,
                    'price': float(item.price),
                }

                items.append({
                    'id': item.id,
                    'product': product_data,
                    'quantity': item.quantity,
                    'total_price': float(item.total_price),
                })
            return items
        else:
            cart = request.session.get('cart', {})
            items = []
            for product_id, item_data in cart.items():
                items.append({
                    'id': product_id,
                    'product': {
                        'id': product_id,
                        'name': item_data.get('name', _('Product')),
                        'description': item_data.get('description', ''),
                        'price': float(item_data.get('price', 0)),
                        'image': item_data.get('image'),
                    },
                    'quantity': item_data.get('quantity', 1),
                    'total_price': float(item_data.get('price', 0)) * item_data.get('quantity', 1),
                })
            return items


class CartCountView(View):
    """
    Return cart item count.
    """

    def get(self, request: HttpRequest):
        """
        Get cart item count.
        """
        count = CartService.get_cart_count(request)
        return render(request, 'common/partials/cart_count.html', {'count': count})


class CartSubtotalView(View):
    """
    Return cart subtotal.
    """

    def get(self, request: HttpRequest):
        """
        Get cart subtotal.
        """
        if request.user.is_authenticated:
            cart = CartService.get_or_create_cart(request)
            subtotal = float(cart.total_price)
        else:
            cart = request.session.get('cart', {})
            subtotal = sum(
                float(item.get('price', 0)) * item.get('quantity', 1)
                for item in cart.values()
            )
        return render(request, 'common/partials/cart_subtotal.html', {'subtotal': subtotal})


class CartUpdateQuantityView(View):
    """
    Update cart item quantity.
    """

    def post(self, request: HttpRequest, item_id: str):
        """
        Update quantity of a cart item.
        """
        action = request.POST.get('action', 'increase')

        if request.user.is_authenticated:
            # Handle DB items
            cart = CartService.get_or_create_cart(request)
            try:
                item = cart.items.get(id=item_id)
                if action == 'increase':
                    item.quantity += 1
                elif action == 'decrease':
                    item.quantity = max(1, item.quantity - 1)
                item.save()
            except Exception:
                pass
        else:
            # Handle session items
            cart = request.session.get('cart', {})
            if item_id in cart:
                if action == 'increase':
                    cart[item_id]['quantity'] = cart[item_id].get('quantity', 1) + 1
                elif action == 'decrease':
                    cart[item_id]['quantity'] = max(1, cart[item_id].get('quantity', 1) - 1)
                request.session['cart'] = cart
                request.session.modified = True

        # Return updated cart items
        cart_view = CartView()
        context = cart_view.get_context_data(request)
        return render(request, 'common/partials/cart_items.html', context)


class CartRemoveItemView(View):
    """
    Remove item from cart.
    """

    def delete(self, request: HttpRequest, item_id: str):
        """
        Remove an item from the cart.
        """
        if request.user.is_authenticated:
            cart = CartService.get_or_create_cart(request)
            cart.items.filter(id=item_id).delete()
        else:
            cart = request.session.get('cart', {})
            if item_id in cart:
                del cart[item_id]
                request.session['cart'] = cart
                request.session.modified = True

        # Return updated cart items
        cart_view = CartView()
        context = cart_view.get_context_data(request)
        return render(request, 'common/partials/cart_items.html', context)


class CartAddItemView(View):
    """
    Add item to cart.
    """

    def post(self, request: HttpRequest):
        """
        Add an item to the cart.
        """
    def post(self, request: HttpRequest):
        """
        Add an item to the cart.
        """
        product_name = request.POST.get('product_name', _('Product'))
        product_id = request.POST.get('product_id', '0')
        price = float(request.POST.get('price', 0))
        quantity = int(request.POST.get('quantity', 1))
        description = request.POST.get('description', '')

        if request.user.is_authenticated:
            cart = CartService.get_or_create_cart(request)
            CartService.add_item(cart, product_name, price, quantity, description)
            count = cart.total_items
        else:
            cart_data = request.session.get('cart', {})
            # Use name as key or id if available
            key = product_id if product_id != '0' else product_name
            if key in cart_data:
                cart_data[key]['quantity'] += quantity
            else:
                cart_data[key] = {
                    'name': product_name,
                    'price': price,
                    'quantity': quantity,
                    'description': description
                }
            request.session['cart'] = cart_data
            request.session.modified = True
            count = sum(item.get('quantity', 1) for item in cart_data.values())

        return JsonResponse({
            'status': 'success',
            'message': _('Item added to cart'),
            'count': count,
        })


class CheckoutView(PageHandler):
    """
    Checkout page view.
    """

    page_title = _("Checkout")
    template_name = "common/checkout.html"

    def get_context_data(self, request: HttpRequest, **kwargs):
        """
        Get checkout context.
        """
        context = super().get_context_data(**kwargs)

        # Get cart items
        cart_view = CartView()
        cart_items = cart_view._get_cart_items(request)

        # Calculate totals
        subtotal = sum(item['total_price'] for item in cart_items)
        # Assuming no tax for now, or just show summary
        total = subtotal

        context.update({
            'cart_items': cart_items,
            'subtotal': subtotal,
            'total': total,
        })

        return context
