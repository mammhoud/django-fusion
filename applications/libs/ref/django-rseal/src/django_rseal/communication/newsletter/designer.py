"""Email design and marketing template tools."""
import logging
import re

logger = logging.getLogger(__name__)

class EmailDesigner:
    """
    Marketing email designer with brand styling support.

    Usage:
        designer = EmailDesigner()
        html = designer.render_marketing_email("newsletter/email/weekly.html", context)
        branded = designer.apply_brand_styles(html, brand_config)
    """

    def render_marketing_email(self, template_name: str, context: dict, request=None) -> str:
        """Render a marketing email template to HTML string."""
        from django.template.loader import render_to_string
        try:
            return render_to_string(template_name, context, request=request)
        except Exception as e:
            logger.error(f"Failed to render marketing email template {template_name}: {e}")
            raise

    def apply_brand_styles(self, html: str, brand_config: dict) -> str:
        """
        Apply brand colors and fonts to an HTML email.

        Args:
            html: Raw HTML string
            brand_config: Dict with keys: primary_color, font_family, logo_url, company_name
        """
        primary_color = brand_config.get("primary_color", "#2563eb")
        font_family = brand_config.get("font_family", "sans-serif")

        # Inject brand CSS variables
        brand_css = f"""
        <style>
        :root {{
            --brand-primary: {primary_color};
            --brand-font: {font_family};
        }}
        body {{ font-family: {font_family}; }}
        .btn-primary {{ background-color: {primary_color}; }}
        a {{ color: {primary_color}; }}
        </style>
        """

        if "<head>" in html:
            html = html.replace("<head>", f"<head>{brand_css}", 1)
        else:
            html = brand_css + html

        # Replace logo placeholder
        if "logo_url" in brand_config:
            html = html.replace("{{BRAND_LOGO}}", brand_config["logo_url"])
        if "company_name" in brand_config:
            html = html.replace("{{COMPANY_NAME}}", brand_config["company_name"])

        return html

    def generate_text_version(self, html: str) -> str:
        """Convert HTML email to plain text version."""
        # Remove style/script blocks
        text = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
        # Convert links
        text = re.sub(r'<a[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', r'\2 (\1)', text)
        # Remove remaining tags
        text = re.sub(r'<[^>]+>', '', text)
        # Clean whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        return text.strip()
