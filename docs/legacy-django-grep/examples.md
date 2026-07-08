# Real-World Examples

This document provides complete, real-world examples of using django-fusion in your Django projects.

## Table of Contents

- [Blog Application](#blog-application)
- [E-commerce Product Management](#e-commerce-product-management)
- [User Profile System](#user-profile-system)
- [API Endpoints](#api-endpoints)
- [Management Commands](#management-commands)

---

## Blog Application

Complete blog application using django-fusion mixins and utilities.

### Models

```python
from django.db import models
from django.contrib.auth.models import User
from django_fusion.models import TimestampedModel, SoftDeleteModel, NoteMixin
from django_fusion.utils import slugify_unique

class Article(TimestampedModel, SoftDeleteModel, NoteMixin):
    """Blog article with timestamps, soft delete, and notes."""

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    content = models.TextField()
    excerpt = models.TextField(blank=True)
    featured_image = models.ImageField(upload_to='articles/', blank=True)
    status = models.CharField(
        max_length=20,
        choices=[('draft', 'Draft'), ('published', 'Published')],
        default='draft'
    )
    views = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_unique(Article, self.title)
        if not self.excerpt:
            from django_fusion.utils import truncate_words
            self.excerpt = truncate_words(self.content, 50)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
```

### Views

```python
from django.views.generic import ListView, DetailView, CreateView
from django_fusion.views import MessageMixin, ProfileContextMixin
from .models import Article

class ArticleListView(ListView):
    model = Article
    template_name = 'blog/article_list.html'
    context_object_name = 'articles'
    paginate_by = 10

    def get_queryset(self):
        return Article.objects.filter(
            status='published',
            is_deleted=False
        ).order_by('-created_at')


class ArticleDetailView(DetailView):
    model = Article
    template_name = 'blog/article_detail.html'
    context_object_name = 'article'

    def get_object(self):
        obj = super().get_object()
        # Increment views
        obj.views += 1
        obj.save(update_fields=['views'])
        return obj


class ArticleCreateView(MessageMixin, ProfileContextMixin, CreateView):
    model = Article
    fields = ['title', 'content', 'featured_image', 'status']
    template_name = 'blog/article_form.html'
    success_message = "Article created successfully!"
    success_url = '/blog/'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
```

### Templates

```django
{% load django_fusion_tags %}

<!-- article_list.html -->
<div class="articles">
    {% for article in articles %}
        <article class="article-card">
            <h2>{{ article.title }}</h2>
            <p class="meta">
                By {{ article.author.get_full_name }}
                • {{ article.created_at|relative_time }}
                • {{ article.views }} views
            </p>
            <p>{{ article.excerpt|truncate_chars:200 }}</p>
            <a href="{% url 'article_detail' article.slug %}">Read more</a>
        </article>
    {% endfor %}
</div>

{% render_pagination page_obj request %}
```

---

## E-commerce Product Management

Product catalog with pricing and inventory.

### Models

```python
from django.db import models
from django_fusion.models import TimestampedModel, SoftDeleteModel, UUIDPrimaryKeyModel

class Product(TimestampedModel, SoftDeleteModel, UUIDPrimaryKeyModel):
    """Product with UUID primary key and soft delete."""

    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')

    @property
    def is_in_stock(self):
        return self.stock > 0 and not self.is_deleted

    @property
    def discount_percentage(self):
        if hasattr(self, 'discount') and self.discount:
            return (self.discount.amount / self.price) * 100
        return 0

    def __str__(self):
        return self.name
```

### Views

```python
from django.views.generic import ListView, DetailView
from django_fusion.views import JSONResponseMixin
from django_fusion.utils import success_response, error_response
from .models import Product

class ProductListView(ListView):
    model = Product
    template_name = 'shop/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.filter(
            is_deleted=False,
            stock__gt=0
        ).order_by('-created_at')


class ProductAPIView(JSONResponseMixin, DetailView):
    model = Product

    def get(self, request, *args, **kwargs):
        product = self.get_object()

        if product.is_deleted:
            return self.error_response(
                message="Product not found",
                status=404
            )

        return self.success_response(
            data={
                'id': str(product.id),
                'name': product.name,
                'price': float(product.price),
                'stock': product.stock,
                'in_stock': product.is_in_stock,
                'discount': product.discount_percentage
            }
        )
```

### Templates

```django
{% load django_fusion_tags %}

<!-- product_list.html -->
<div class="products">
    {% for product in products %}
        <div class="product-card">
            <img src="{{ product.image.url }}" alt="{{ product.name }}">
            <h3>{{ product.name }}</h3>
            <p class="price">{{ product.price|format_currency }}</p>

            {% if product.discount_percentage > 0 %}
                <p class="discount">
                    Save {{ product.discount_percentage|floatformat:0 }}%
                </p>
            {% endif %}

            <p class="stock">
                {% if product.stock > 0 %}
                    {{ product.stock }} in stock
                {% else %}
                    Out of stock
                {% endif %}
            </p>

            <a href="{% url 'product_detail' product.slug %}" class="btn">
                View Details
            </a>
        </div>
    {% endfor %}
</div>
```

---

## User Profile System

Complete user profile with certifications and courses.

### Models

```python
from django.db import models
from django.contrib.auth.models import User
from django_fusion.models import (
    TimestampedModel,
    CertificateMixin,
    CourseMixin,
    MessageMixin
)

class UserProfile(
    TimestampedModel,
    CertificateMixin,
    CourseMixin,
    MessageMixin
):
    """User profile with certificates, courses, and messaging."""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    website = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)

    @property
    def completion_percentage(self):
        fields = ['bio', 'avatar', 'website', 'linkedin_url', 'github_url']
        filled = sum(1 for field in fields if getattr(self, field))
        return (filled / len(fields)) * 100

    def __str__(self):
        return f"{self.user.get_full_name()}'s Profile"
```

### Views

```python
from django.views.generic import TemplateView, UpdateView
from django_fusion.views import ProfileDashboardMixin, MessageMixin
from .models import UserProfile

class ProfileDashboardView(ProfileDashboardMixin, TemplateView):
    template_name = 'profile/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        profile = UserProfile.objects.get(user=self.request.user)

        context.update({
            'profile': profile,
            'certificates': profile.valid_certificates,
            'active_courses': profile.active_enrollments,
            'unread_messages': profile.unread_message_count,
            'completion': profile.completion_percentage
        })

        return context


class ProfileUpdateView(MessageMixin, UpdateView):
    model = UserProfile
    fields = ['bio', 'avatar', 'website', 'linkedin_url', 'github_url']
    template_name = 'profile/edit.html'
    success_message = "Profile updated successfully!"
    success_url = '/profile/'

    def get_object(self):
        return UserProfile.objects.get(user=self.request.user)
```

### Templates

```django
{% load django_fusion_tags %}

<!-- dashboard.html -->
<div class="dashboard">
    <div class="profile-header">
        <img src="{{ profile.avatar.url }}" alt="Avatar">
        <h1>{{ user.get_full_name }}</h1>
        <p>Member since {{ profile.created_at|relative_time }}</p>
    </div>

    <div class="metrics">
        {% for metric in metrics %}
            <div class="metric-card">
                <h3>{{ metric.value }}</h3>
                <p>{{ metric.label }}</p>
            </div>
        {% endfor %}
    </div>

    <div class="certificates">
        <h2>Certificates</h2>
        {% for cert in certificates %}
            <div class="cert-card">
                <h4>{{ cert.name }}</h4>
                <p>Expires {{ cert.expiry_date|relative_time }}</p>
            </div>
        {% endfor %}
    </div>

    <div class="courses">
        <h2>Active Courses</h2>
        {% for enrollment in active_courses %}
            <div class="course-card">
                <h4>{{ enrollment.course.name }}</h4>
                <div class="progress">
                    <div class="progress-bar" style="width: {{ enrollment.progress }}%">
                        {{ enrollment.progress }}%
                    </div>
                </div>
            </div>
        {% endfor %}
    </div>
</div>
```

---

## API Endpoints

RESTful API using django-fusion utilities.

```python
from django.views import View
from django_fusion.views import JSONResponseMixin
from django_fusion.utils import (
    success_response,
    error_response,
    validate_email_format
)
from .models import User

class UserAPIView(JSONResponseMixin, View):
    def get(self, request, user_id):
        """Get user details."""
        try:
            user = User.objects.get(id=user_id)
            return self.success_response(
                data={
                    'id': user.id,
                    'email': user.email,
                    'name': user.get_full_name()
                }
            )
        except User.DoesNotExist:
            return self.error_response(
                message="User not found",
                status=404
            )

    def post(self, request):
        """Create new user."""
        email = request.POST.get('email')
        name = request.POST.get('name')

        # Validate
        if not validate_email_format(email):
            return self.error_response(
                message="Validation failed",
                errors={'email': 'Invalid email format'},
                status=400
            )

        # Create user
        user = User.objects.create(email=email, name=name)

        return self.success_response(
            data={'id': user.id, 'email': user.email},
            message="User created successfully",
            status=201
        )

    def put(self, request, user_id):
        """Update user."""
        try:
            user = User.objects.get(id=user_id)
            user.name = request.POST.get('name', user.name)
            user.save()

            return self.success_response(
                data={'id': user.id, 'name': user.name},
                message="User updated successfully"
            )
        except User.DoesNotExist:
            return self.error_response(
                message="User not found",
                status=404
            )

    def delete(self, request, user_id):
        """Delete user (soft delete)."""
        try:
            user = User.objects.get(id=user_id)
            user.soft_delete()

            return self.success_response(
                message="User deleted successfully"
            )
        except User.DoesNotExist:
            return self.error_response(
                message="User not found",
                status=404
            )
```

---

## Management Commands

Data import/export commands.

```python
from django_fusion.management import LoggingCommand
from myapp.models import Product
import csv

class Command(LoggingCommand):
    help = "Import products from CSV"

    def add_arguments(self, parser):
        parser.add_argument('file', type=str, help='CSV file path')
        parser.add_argument('--dry-run', action='store_true', help='Dry run mode')

    def handle(self, *args, **options):
        file_path = options['file']
        dry_run = options['dry_run']

        with self.log_context(operation="import_products", file=file_path):
            self.log_info(f"Reading file: {file_path}")

            try:
                with open(file_path, 'r') as f:
                    reader = csv.DictReader(f)
                    products = list(reader)

                self.log_info(f"Found {len(products)} products")

                if dry_run:
                    self.log_warning("DRY RUN MODE - No changes will be made")

                created = 0
                updated = 0
                errors = 0

                for product_data in self.progress_bar(products, prefix="Processing"):
                    with self.log_context(sku=product_data.get('sku')):
                        try:
                            if not dry_run:
                                product, created_flag = Product.objects.update_or_create(
                                    sku=product_data['sku'],
                                    defaults=product_data
                                )

                                if created_flag:
                                    created += 1
                                else:
                                    updated += 1

                        except Exception as e:
                            self.log_error(f"Error processing product: {e}")
                            errors += 1

                self.log_success(
                    f"Import complete: {created} created, {updated} updated, {errors} errors"
                )

            except FileNotFoundError:
                self.handle_error(f"File not found: {file_path}", exit_code=1)
            except Exception as e:
                self.handle_error(e, exit_code=1)
```

---

## Related Documentation

- [Model Mixins](models.md)
- [View Mixins](views.md)
- [Utility Functions](utils.md)
- [Template Tags](templatetags.md)
- [Management Commands](management.md)
