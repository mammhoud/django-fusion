"""Form mixins for the django-fusion management layer."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Field, Layout, Submit
from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe


class BaseFormMixin:
    """Add Bootstrap 5 classes and HTMX attribute helpers to forms."""

    hx_post = None
    hx_target = None
    hx_swap = None
    hx_trigger = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper_attrs: dict = {}
        self._apply_htmx_attrs()
        self._apply_bootstrap_attrs()

    def _apply_htmx_attrs(self) -> None:
        for attr, val in [
            ("hx-post", self.hx_post),
            ("hx-target", self.hx_target),
            ("hx-swap", self.hx_swap),
            ("hx-trigger", self.hx_trigger),
        ]:
            if val:
                self.helper_attrs[attr] = val

    def _apply_bootstrap_attrs(self) -> None:
        for _name, field in self.fields.items():
            cls = field.widget.attrs.get("class", "")
            if isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect)):
                if "form-check-input" not in cls:
                    field.widget.attrs["class"] = f"{cls} form-check-input".strip()
            elif isinstance(field.widget, (forms.Select, forms.SelectMultiple)):
                if "form-select" not in cls:
                    field.widget.attrs["class"] = f"{cls} form-select".strip()
            else:
                if "form-control" not in cls:
                    field.widget.attrs["class"] = f"{cls} form-control".strip()

    def get_form_attrs(self) -> dict:
        return self.helper_attrs


class BaseForm(BaseFormMixin, forms.Form):
    """Standard base form."""


class BaseModelForm(BaseFormMixin, forms.ModelForm):
    """Standard base model form."""



class BaseStyledForm:
    """
    Base class providing styling configuration for both Bootstrap and Tailwind.
    Enhanced with better field detection and validation support.
    """

    def __init__(self, *args, **kwargs):
        # Get styling configuration from kwargs or settings
        self.style_framework = kwargs.pop(
            "style_framework", getattr(settings, "STYLES_FRAMEWORK", "bootstrap")
        )
        self.css_prefix = kwargs.pop("css_prefix", getattr(settings, "STYLES_PREFIX", ""))

        # Initialize validation state
        self.validation_applied = False

        # Framework-specific configurations
        self.styling_config = {
            "bootstrap": self.get_bootstrap_config(),
            "tailwind": self.get_tailwind_config(),
        }

        super().__init__(*args, **kwargs)

    def get_bootstrap_config(self):
        """Bootstrap 5 styling configuration."""
        return {
            # Form structure
            "form": {
                "class": "needs-validation",
                "novalidate": True,
                "wrapper_class": "",
                "row_class": "row g-3",
                "col_full": "col-12",
                "col_half": "col-md-6",
                "col_third": "col-md-4",
            },
            # Labels
            "label": {
                "class": "form-label",
                "required_class": "text-danger",
                "optional_class": "text-muted",
            },
            # Input fields
            "input": {
                "base_class": "form-control",
                "size_class": {
                    "sm": "form-control-sm",
                    "lg": "form-control-lg",
                    "default": "",
                },
                "type_class": {
                    "text": "",
                    "email": "",
                    "password": "password-input",
                    "number": "",
                    "tel": "",
                    "url": "",
                    "file": "form-control-file",
                    "select": "form-select",
                    "textarea": "form-control",
                    "checkbox": "form-check-input",
                    "radio": "form-check-input",
                    "range": "form-range",
                },
                "disabled_class": "disabled",
                "readonly_class": "readonly",
            },
            # Validation states
            "validation": {
                "valid": "is-valid",
                "invalid": "is-invalid",
                "feedback_valid": "valid-feedback",
                "feedback_invalid": "invalid-feedback",
                "touched": "was-validated",
            },
            # Buttons
            "button": {
                "base_class": "btn",
                "type_class": {
                    "primary": "btn-primary",
                    "secondary": "btn-secondary",
                    "success": "btn-success",
                    "danger": "btn-danger",
                    "warning": "btn-warning",
                    "info": "btn-info",
                    "light": "btn-light",
                    "dark": "btn-dark",
                    "link": "btn-link",
                    "outline_primary": "btn-outline-primary",
                    "outline_secondary": "btn-outline-secondary",
                },
                "size_class": {
                    "sm": "btn-sm",
                    "lg": "btn-lg",
                    "default": "",
                },
                "block_class": "btn-block w-100",
                "disabled_class": "disabled",
            },
            # Layout helpers
            "helper": {
                "field_class": "mb-3",
                "label_class": "form-label fw-semibold",
                "help_text_class": "form-text text-muted",
                "error_class": "invalid-feedback",
                "success_class": "valid-feedback",
            },
            # Form groups
            "group": {
                "form_group": "form-group",
                "form_check": "form-check",
                "form_check_input": "form-check-input",
                "form_check_label": "form-check-label",
                "form_check_inline": "form-check-inline",
                "input_group": "input-group",
                "input_group_text": "input-group-text",
                "form_floating": "form-floating",
                "form_text": "form-text",
            },
            # Icons
            "icon": {
                "prefix_class": "form-control-icon",
                "position_class": {
                    "left": "has-left-icon",
                    "right": "has-right-icon",
                },
            },
        }

    def get_tailwind_config(self):
        """Tailwind CSS styling configuration."""
        prefix = f"{self.css_prefix}" if self.css_prefix else ""

        return {
            # Form structure
            "form": {
                "class": f"{prefix}space-y-6",
                "novalidate": False,
                "wrapper_class": f"{prefix}max-w-md {prefix}mx-auto",
                "row_class": f"{prefix}grid {prefix}grid-cols-1 {prefix}gap-4",
                "col_full": f"{prefix}col-span-1",
                "col_half": f"{prefix}sm:col-span-1",
                "col_third": f"{prefix}sm:col-span-1",
            },
            # Labels
            "label": {
                "class": f"{prefix}block {prefix}text-sm {prefix}font-medium {prefix}text-gray-700",
                "required_class": f"{prefix}text-red-500",
                "optional_class": f"{prefix}text-gray-400",
            },
            # Input fields
            "input": {
                "base_class": f"{prefix}mt-1 {prefix}block {prefix}w-full {prefix}rounded-md "
                f"{prefix}border-gray-300 {prefix}shadow-sm "
                f"focus:{prefix}border-indigo-500 focus:{prefix}ring-indigo-500 "
                f"{prefix}sm:text-sm",
                "size_class": {
                    "sm": f"{prefix}py-1 {prefix}px-2 {prefix}text-xs",
                    "lg": f"{prefix}py-3 {prefix}px-4 {prefix}text-base",
                    "default": f"{prefix}py-2 {prefix}px-3",
                },
                "type_class": {
                    "text": "",
                    "email": "",
                    "password": f"{prefix}password-input",
                    "number": "",
                    "tel": "",
                    "url": "",
                    "file": f"{prefix}file:{prefix}border-0 {prefix}file:{prefix}bg-gray-100 "
                    f"{prefix}file:{prefix}py-2 {prefix}file:{prefix}px-3",
                    "select": f"{prefix}pr-10",
                    "textarea": f"{prefix}resize-none",
                    "checkbox": f"{prefix}h-4 {prefix}w-4 {prefix}text-indigo-600 {prefix}rounded "
                    f"{prefix}border-gray-300 focus:{prefix}ring-indigo-500",
                    "radio": f"{prefix}h-4 {prefix}w-4 {prefix}text-indigo-600 {prefix}border-gray-300",
                },
                "disabled_class": f"{prefix}bg-gray-100 {prefix}cursor-not-allowed",
                "readonly_class": f"{prefix}bg-gray-50",
            },
            # Validation states
            "validation": {
                "valid": f"{prefix}border-green-300 {prefix}text-green-900 "
                f"focus:{prefix}border-green-500 focus:{prefix}ring-green-500",
                "invalid": f"{prefix}border-red-300 {prefix}text-red-900 {prefix}placeholder-red-300 "
                f"focus:{prefix}border-red-500 focus:{prefix}ring-red-500",
                "feedback_valid": f"{prefix}mt-2 {prefix}text-sm {prefix}text-green-600",
                "feedback_invalid": f"{prefix}mt-2 {prefix}text-sm {prefix}text-red-600",
                "touched": "",
            },
            # Buttons
            "button": {
                "base_class": f"{prefix}inline-flex {prefix}justify-center {prefix}rounded-md {prefix}border "
                f"{prefix}shadow-sm {prefix}px-4 {prefix}py-2 {prefix}text-base {prefix}font-medium "
                f"{prefix}focus:{prefix}outline-none {prefix}focus:{prefix}ring-2 "
                f"{prefix}focus:{prefix}ring-offset-2 {prefix}sm:text-sm",
                "type_class": {
                    "primary": f"{prefix}border-transparent {prefix}bg-indigo-600 "
                    f"{prefix}text-white hover:{prefix}bg-indigo-700 "
                    f"{prefix}focus:{prefix}ring-indigo-500",
                    "secondary": f"{prefix}border-gray-300 {prefix}bg-white "
                    f"{prefix}text-gray-700 hover:{prefix}bg-gray-50 "
                    f"{prefix}focus:{prefix}ring-gray-500",
                    "success": f"{prefix}border-transparent {prefix}bg-green-600 "
                    f"{prefix}text-white hover:{prefix}bg-green-700 "
                    f"{prefix}focus:{prefix}ring-green-500",
                    "danger": f"{prefix}border-transparent {prefix}bg-red-600 "
                    f"{prefix}text-white hover:{prefix}bg-red-700 "
                    f"{prefix}focus:{prefix}ring-red-500",
                },
                "size_class": {
                    "sm": f"{prefix}px-3 {prefix}py-1 {prefix}text-sm",
                    "lg": f"{prefix}px-6 {prefix}py-3 {prefix}text-base",
                    "default": f"{prefix}px-4 {prefix}py-2",
                },
                "block_class": f"{prefix}w-full",
                "disabled_class": f"{prefix}opacity-50 {prefix}cursor-not-allowed",
            },
            # Layout helpers
            "helper": {
                "field_class": f"{prefix}space-y-1",
                "label_class": f"{prefix}block {prefix}text-sm {prefix}font-medium {prefix}text-gray-700",
                "help_text_class": f"{prefix}mt-2 {prefix}text-sm {prefix}text-gray-500",
                "error_class": f"{prefix}mt-2 {prefix}text-sm {prefix}text-red-600",
                "success_class": f"{prefix}mt-2 {prefix}text-sm {prefix}text-green-600",
            },
            # Form groups
            "group": {
                "form_group": f"{prefix}form-group",
                "form_check": f"{prefix}flex {prefix}items-center",
                "form_check_input": f"{prefix}mr-2",
                "form_check_label": f"{prefix}text-sm {prefix}text-gray-700",
                "form_check_inline": f"{prefix}inline-flex {prefix}items-center {prefix}mr-4",
                "input_group": f"{prefix}flex {prefix}rounded-md {prefix}shadow-sm",
                "input_group_text": f"{prefix}inline-flex {prefix}items-center {prefix}px-3 "
                f"{prefix}border {prefix}border-r-0 {prefix}border-gray-300 "
                f"{prefix}bg-gray-50 {prefix}text-gray-500 {prefix}sm:text-sm",
                "form_floating": f"{prefix}relative",
            },
            # Icons
            "icon": {
                "prefix_class": f"{prefix}form-control-icon",
                "position_class": {
                    "left": f"{prefix}pl-10",
                    "right": f"{prefix}pr-10",
                },
            },
        }

    def get_styling(self, category, key=None, default=None):
        """Get styling configuration for current framework."""
        config = self.styling_config.get(self.style_framework, {})
        if category not in config:
            return default

        if key:
            return config[category].get(key, default)
        return config[category]

    def detect_field_type(self, field):
        """Detect field type from widget."""
        widget = field.widget

        if isinstance(widget, forms.PasswordInput):
            return "password"
        elif isinstance(widget, forms.EmailInput):
            return "email"
        elif isinstance(widget, forms.Textarea):
            return "textarea"
        elif isinstance(widget, forms.CheckboxInput):
            return "checkbox"
        elif isinstance(widget, forms.RadioSelect):
            return "radio"
        elif isinstance(widget, forms.Select):
            return "select"
        elif isinstance(widget, forms.NumberInput):
            return "number"
        elif isinstance(widget, forms.URLInput):
            return "url"
        elif isinstance(widget, forms.FileInput):
            return "file"
        elif hasattr(widget, "input_type"):
            return widget.input_type
        else:
            return "text"

    def apply_field_styling(
        self,
        field,
        field_type=None,
        size="default",
        placeholder=None,
        icon=None,
        icon_position="left",
        disabled=False,
        readonly=False,
        **kwargs,
    ):
        """Apply styling to a form field."""
        if field_type is None:
            field_type = self.detect_field_type(field)

        # Get base classes
        base_class = self.get_styling("input", "base_class", "")
        type_class = self.get_styling("input", "type_class", {}).get(field_type, "")
        size_class = self.get_styling("input", "size_class", {}).get(size, "")

        # Build class list
        classes = [base_class, type_class, size_class]

        # Add icon classes if specified
        if icon:
            icon_prefix = self.get_styling("icon", "prefix_class", "")
            icon_position_class = self.get_styling("icon", "position_class", {}).get(
                icon_position, ""
            )
            classes.extend([icon_prefix, icon_position_class])

        # Add disabled/readonly classes
        if disabled:
            disabled_class = self.get_styling("input", "disabled_class", "")
            classes.append(disabled_class)
            field.widget.attrs["disabled"] = "disabled"

        if readonly:
            readonly_class = self.get_styling("input", "readonly_class", "")
            classes.append(readonly_class)
            field.widget.attrs["readonly"] = "readonly"

        # Add extra classes from kwargs
        extra_classes = kwargs.get("class", "")
        if extra_classes:
            classes.append(extra_classes)

        # Filter out empty strings and join
        field_classes = " ".join(filter(None, classes)).strip()

        # Update widget attributes
        if "class" in field.widget.attrs:
            existing_classes = field.widget.attrs["class"]
            # Merge classes, avoiding duplicates
            existing_set = set(existing_classes.split())
            new_set = set(field_classes.split())
            field.widget.attrs["class"] = " ".join(existing_set.union(new_set))
        else:
            field.widget.attrs["class"] = field_classes

        # Add placeholder
        if placeholder:
            field.widget.attrs["placeholder"] = placeholder

        # Add data attributes for BEM methodology
        field.widget.attrs["data-bem-block"] = "form"
        field.widget.attrs["data-bem-element"] = "input"
        if field_type:
            field.widget.attrs["data-bem-modifier"] = field_type

        # Add validation attributes
        if not self.validation_applied:
            field.widget.attrs["data-validation"] = "true"

    def apply_validation_styling(self, is_valid=True, field_name=None, message=None):
        """Apply validation styling to a field or the entire form."""
        if field_name and field_name in self.fields:
            field = self.fields[field_name]
            validation_class = self.get_styling(
                "validation", "valid" if is_valid else "invalid", ""
            )

            if "class" in field.widget.attrs:
                # Remove existing validation classes
                current_classes = field.widget.attrs["class"]
                current_classes = (
                    current_classes.replace(self.get_styling("validation", "valid", ""), "")
                    .replace(self.get_styling("validation", "invalid", ""), "")
                    .strip()
                )

                # Add new validation class
                field.widget.attrs["class"] = f"{current_classes} {validation_class}".strip()
            else:
                field.widget.attrs["class"] = validation_class

            self.validation_applied = True
            return True

        return False

    def get_validation_message_class(self, is_valid=True):
        """Get CSS class for validation messages."""
        return self.get_styling(
            "validation", "feedback_valid" if is_valid else "feedback_invalid", ""
        )

    def apply_button_styling(
        self, button_type="primary", size="default", block=False, disabled=False, **kwargs
    ):
        """Generate CSS classes for a button."""
        base_class = self.get_styling("button", "base_class", "")
        type_class = self.get_styling("button", "type_class", {}).get(button_type, "")
        size_class = self.get_styling("button", "size_class", {}).get(size, "")
        block_class = self.get_styling("button", "block_class", "") if block else ""
        disabled_class = self.get_styling("button", "disabled_class", "") if disabled else ""

        classes = [base_class, type_class, size_class, block_class, disabled_class]
        extra_classes = kwargs.get("class", "")
        if extra_classes:
            classes.append(extra_classes)

        return " ".join(filter(None, classes)).strip()



class SecurityMixin:
    """Mixin providing security features for forms."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_security_fields()

    def add_security_fields(self):
        """Add security-related fields to form."""
        # Honeypot field for bot protection
        self.fields["security_check"] = forms.CharField(
            required=False, widget=forms.HiddenInput(), label="", help_text=""
        )

        # Timestamp to prevent replay attacks
        self.fields["timestamp"] = forms.CharField(
            widget=forms.HiddenInput(), initial=self.get_timestamp_hash()
        )

    def get_timestamp_hash(self):
        """Generate timestamp hash for form validation."""
        import hashlib
        import time

        timestamp = str(int(time.time()))
        return hashlib.sha256(timestamp.encode()).hexdigest()[:10]

    def clean_security_check(self):
        """Clean security check field (honeypot)."""
        data = self.cleaned_data.get("security_check", "")
        if data:  # Bots will fill this field
            raise forms.ValidationError("Security check failed.")
        return data


class LayoutMixin:
    """Mixin providing layout configuration for forms."""

    def setup_layout(self, fields, submit_text=None, show_links=True):
        """Setup form layout with proper styling."""
        self.get_styling("form")
        helper = self.get_form_helper()

        layout_fields = []

        for field_name in fields:
            if field_name in self.fields:
                field = self.fields[field_name]

                # Determine field type for styling
                if isinstance(field.widget, forms.CheckboxInput):
                    field_type = "checkbox"
                elif isinstance(field.widget, forms.RadioSelect):
                    field_type = "radio"
                elif isinstance(field.widget, forms.Select):
                    field_type = "select"
                elif isinstance(field.widget, forms.Textarea):
                    field_type = "textarea"
                else:
                    field_type = (
                        field.widget.input_type if hasattr(field.widget, "input_type") else "text"
                    )

                # Apply styling
                self.apply_field_styling(field, field_type=field_type, placeholder=field.label)

                # Add to layout
                layout_fields.append(Field(field_name))

        # Add submit button
        if submit_text:
            button_class = self.get_styling("button", "class")
            button_type_class = self.get_styling("button", "types").get("primary", "")
            button_size_class = self.get_styling("button", "size_class").get("default", "")
            button_block_class = self.get_styling("button", "block_class", "")

            button_classes = (
                f"{button_class} {button_type_class} {button_size_class} {button_block_class}"
            )

            layout_fields.append(Submit("submit", submit_text, css_class=button_classes.strip()))

        # Add links if needed
        if show_links and hasattr(self, "get_form_links"):
            layout_fields.extend(self.get_form_links())

        helper.layout = Layout(*layout_fields)
        self.helper = helper

    def get_form_helper(self):
        """Get form helper with configured styling."""
        helper = FormHelper()
        helper.form_method = "post"
        helper.form_class = self.get_styling("form", "class", "")
        helper.label_class = self.get_styling("label", "class", "")
        helper.field_class = self.get_styling("helper", "field_class", "")
        return helper

    def get_form_links(self):
        """Get form navigation links."""
        links = []
        style = self.get_styling("button", "types")

        if hasattr(self, "login_url"):
            links.append(
                HTML(f'''
                    <div class="text-center mt-3">
                        <a href="{self.login_url}"
                           class="text-decoration-none {style.get("secondary", "")}">
                            Already have an account? Sign in
                        </a>
                    </div>
                ''')
            )

        return links


class ValidationMixin:
    """Mixin providing enhanced validation capabilities."""

    def add_error_highlighting(self):
        """Add CSS classes for error highlighting."""
        for field_name, errors in self.errors.items():
            if field_name in self.fields:
                field = self.fields[field_name]
                invalid_class = self.get_styling("validation", "invalid", "")

                if "class" in field.widget.attrs:
                    field.widget.attrs["class"] += f" {invalid_class}"
                else:
                    field.widget.attrs["class"] = invalid_class

    def get_field_with_errors(self, field_name):
        """Get field HTML with error messages."""
        field = self[field_name]
        errors = self.errors.get(field_name, [])

        if errors:
            error_class = self.get_styling("validation", "feedback_invalid", "")
            error_html = f'<div class="{error_class}">{" ".join(errors)}</div>'
            return mark_safe(f"{field}{error_html}")
        return field



class PasswordVerificationMixin:
    """
    Mixin for forms that require password verification (two password fields).
    """

    def clean(self):
        """Validate that both password fields match."""
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error("password2", "Passwords do not match. Please enter the same password in both fields.")

        return cleaned_data
