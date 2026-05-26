from django.contrib import messages
from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django_osoul.comp.site import PageHandler

# Optional coupling to Core plugins
try:
    from plugins.products.services.cart_service import CartService
except ImportError:
    CartService = None

try:
    from django_rseal.workflows.pipelines.services.payments import PayPalGateway, StripeGateway
    from django_rseal.workflows.pipelines.site.payments import PaymentProcessingMixin
except ImportError:
    StripeGateway = None
    PayPalGateway = None
    class PaymentProcessingMixin:
        pass

from ..models import Course, Enrollment


class EnrollView(PaymentProcessingMixin, PageHandler):
    """
    Enrollment view with checkout functionality
    """
    page_title = "Enroll in Course"
    template_name = "profile/enroll_course.html"
    fragment_name = "profiles.enroll"
    layout_path = "profile/skeleton.html"

    def get(self, request: HttpRequest, *args, **kwargs):
        # Get the course from slug
        course_slug = kwargs.get('slug')
        self.course = get_object_or_404(Course, slug=course_slug)

        # Check if user is already enrolled
        if Enrollment.objects.filter(student=request.user, course=self.course).exists():
            messages.info(request, f"You are already enrolled in {self.course.title}")
            return redirect('profile:courses')

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.course
        context['user'] = self.request.user

        # Calculate tax (example: 10% tax)
        context['tax_rate'] = 0.10
        context['tax_amount'] = self.course.price * context['tax_rate']
        context['total_amount'] = self.course.price + context['tax_amount']

        # Add any coupon/discount logic here
        context['discount'] = 0.00
        context['final_amount'] = context['total_amount'] - context['discount']

        return context

    def post(self, request: HttpRequest, *args, **kwargs):
        """
        Handle enrollment and payment processing
        """
        course_slug = kwargs.get('slug')
        course = get_object_or_404(Course, slug=course_slug)

        # Check if already enrolled
        if Enrollment.objects.filter(student=request.user, course=course).exists():
            return JsonResponse({
                'status': 'error',
                'message': 'You are already enrolled in this course.'
            })

        # Handle different payment methods
        payment_method = request.POST.get('payment_method', 'stripe')

        # Process payment based on method
        if payment_method == 'stripe':
            # Process Stripe payment
            payment_result = self.process_stripe_payment(
                request,
                course.price,
                metadata={'course_id': str(course.id), 'user_id': str(request.user.id)}
            )
        elif payment_method == 'paypal':
            # Process PayPal payment
            payment_result = self.process_paypal_payment(
                request,
                course.price,
                metadata={'course_id': str(course.id), 'user_id': str(request.user.id)}
            )
        elif payment_method == 'free':
            # Free course enrollment
            payment_result = {'status': 'success', 'payment_id': 'FREE'}
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid payment method selected.'
            })

        if payment_result.get('status') == 'success':
            # Create enrollment record
            enrollment = Enrollment.objects.create(
                student=request.user,
                course=course,
                payment_status='completed',
                payment_id=payment_result.get('payment_id', ''),
                amount_paid=course.price if not course.is_free else 0.00,
                transaction_date=timezone.now()
            )

            # Send enrollment confirmation email
            self.send_enrollment_confirmation(request.user, course, enrollment)

            # Clear cache if needed
            self.clear_enrollment_cache(request.user)

            messages.success(request, f"Successfully enrolled in {course.title}!")

            if request.headers.get('HX-Request'):
                return JsonResponse({
                    'status': 'success',
                    'message': f'Successfully enrolled in {course.title}!',
                    'redirect_url': reverse('profile:courses')
                })
            return redirect('profile:courses')
        else:
            # Create failed enrollment record
            Enrollment.objects.create(
                student=request.user,
                course=course,
                payment_status='failed',
                payment_id=payment_result.get('payment_id', ''),
                amount_paid=0.00
            )

            error_message = payment_result.get('message', 'Payment failed. Please try again.')

            if request.headers.get('HX-Request'):
                return JsonResponse({
                    'status': 'error',
                    'message': error_message
                })
            messages.error(request, error_message)
            return self.get(request, *args, **kwargs)

    def send_enrollment_confirmation(self, user, course, enrollment):
        """
        Send enrollment confirmation email
        """
        # Implement email sending logic here
        # from django.core.mail import send_mail
        # subject = f"Enrollment Confirmation: {course.title}"
        # message = f"Hello {user.username},\n\nYou have successfully enrolled in {course.title}.\n\nThank you!"
        # send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
        pass

    def clear_enrollment_cache(self, user):
        """
        Clear cache related to user enrollments
        """
        from django.core.cache import cache
        from django.core.cache.utils import make_template_fragment_key

        # Clear courses count cache
        cache_key = f'user_{user.id}_courses_count'
        cache.delete(cache_key)

        # Clear any fragment cache
        fragment_key = make_template_fragment_key('user_enrollments', [user.id])
        cache.delete(fragment_key)


class EnrollmentSuccessView(PageHandler):
    """
    Enrollment success confirmation page
    """
    page_title = "Enrollment Successful"
    template_name = "profile/enrollment_success.html"
    fragment_name = "profiles.enrollment_success"
    layout_path = "profile/skeleton.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        enrollment_id = self.request.GET.get('enrollment_id')

        if enrollment_id:
            context['enrollment'] = get_object_or_404(
                Enrollment,
                id=enrollment_id,
                student=self.request.user
            )

        return context

# class CourseCartView(View):
#     # Template to use for HTMX response (cart count snippet)

#     def get(self, request, *args, **kwargs):
#         """Render cart items dynamically via HTMX or render the full cart page."""
#         base_cart = BaseCart(request)
#         cart_details = base_cart.get_cart_details()

#         # Apply coupon discount if available in session
#         coupon_code = request.session.get("coupon_code")
#         if coupon_code:
#             try:
#                 coupon = Coupon.objects.get(coupon_number=coupon_code)
#                 discount = coupon.discount  # Use the coupon discount value
#                 cart_details["total_price"] = max(0, cart_details["total_price"] - discount)
#                 cart_details["applied_coupon"] = coupon_code
#             except Coupon.DoesNotExist:
#                 # Remove coupon if it's no longer valid
#                 request.session.pop("coupon_code", None)

#         if request.headers.get("HX-Request"):
#             return render(request, "common/cart/cart_nav_items.html", cart_details)
#         return render(request, "common/cart/cart.html", cart_details)

#     def post(self, request, course_id):
#         """Add a course to the cart and update cart details."""
#         base_cart = BaseCart(request)
#         course = get_object_or_404(Course, id=course_id)

#         # Attempt to retrieve an existing cart item.
#         cart_item = CourseCartItem.objects.filter(cart=base_cart.cart, course=course).first()

#         if cart_item:
#             messages.info(request, "This course is already in your cart.")
#             # Render a message snippet and trigger a frontend event.
#             response = render(request, "utils/page_message.html")
#             response["HX-Trigger"] = "newMessage"
#             return response

#         # Create a new cart item if one doesn't exist.
#         cart_item = CourseCartItem.objects.create(
#             cart=base_cart.cart, course=course, quantity=1, price=course.price
#         )

#         # Log the updated cart details.
#         cart_details = base_cart.get_cart_details()
#         logger.info(f"Course added to cart: {cart_details}")

#         # If HTMX request, render the partial cart count template.
#         if request.headers.get("HX-Request"):
#             return render(request, "blocks/count.html", {"count": cart_details["cart_count"]})

#         # For non-HTMX requests, return the full cart details as JSON.
#         return JsonResponse(cart_details)

#     def delete(self, request, course_id):
#         """Remove a course from the cart."""
#         base_cart = BaseCart(request)
#         course = get_object_or_404(Course, id=course_id)
#         cart_item = get_object_or_404(CourseCartItem, cart=base_cart.cart, course=course)

#         cart_item.delete()
#         return HttpResponse(status=204)


# class CouponCheckView(View):
#     """Validate and apply a coupon, returning the result via HTMX or JSON."""

#     def post(self, request):
#         base_cart = BaseCart(request)
#         coupon_code = request.POST.get("coupon_code")
#         if not coupon_code:
#             return JsonResponse({"error": "No coupon code provided."}, status=400)
#         result = base_cart.apply_coupon(coupon_code)
#         return JsonResponse(result)


# class GenerateInvoiceView(View):
#     """
#     Generates an invoice from the cart details and clears the cart after checkout.
#     """

#     def get(self, request):
#         base_cart = BaseCart(request)
#         invoice_data = base_cart.generate_invoice()
#         return JsonResponse(invoice_data)


# class ClearCartView(View):
#     """
#     Clears all items from the cart.
#     """

#     def post(self, request):
#         base_cart = BaseCart(request)
#         base_cart.clear_cart()
#         return JsonResponse({"status": "Cart cleared."})
class PaymentHistoryView(PageHandler):
    """
    Dashboard view for user's payment and enrollment history.
    """
    page_title = "Payment History"
    template_name = "profile/payment_history.html"
    fragment_name = "profiles.payment_history"
    layout_path = "profile/skeleton.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Get all enrollments for the user, ordered by most recent
        enrollments = Enrollment.objects.filter(student=user).order_by('-enrolled_at')

        # Calculate summary stats
        total_spent = sum(e.amount_paid for e in enrollments if e.payment_status == 'completed')
        active_courses = enrollments.filter(status='active').count()
        completed_courses = enrollments.filter(status='completed').count()

        context.update({
            'enrollments': enrollments,
            'total_spent': total_spent,
            'active_courses': active_courses,
            'completed_courses': completed_courses,
        })

        return context
