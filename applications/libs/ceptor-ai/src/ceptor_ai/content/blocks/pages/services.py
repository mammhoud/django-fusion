from django.utils.translation import gettext_lazy as _
from wagtail import blocks


class PricingBlock(blocks.StructBlock):
    """
    Defines a pricing plan for services or products.
    """

    plan_name = blocks.CharBlock(required=True, label=_("Plan Name"))

    price = blocks.DecimalBlock(
        required=True,
        max_digits=10,
        decimal_places=2,
        label=_("Price"),
    )

    currency = blocks.CharBlock(
        default="$",
        max_length=5,
        required=False,
        label=_("Currency Symbol"),
        help_text=_("Currency symbol to display before the price."),
    )

    duration = blocks.CharBlock(
        required=False,
        label=_("Duration"),
        help_text=_("E.g. 'per month', 'per year', or 'one-time'."),
    )

    description = blocks.TextBlock(
        required=False,
        label=_("Plan Description"),
        help_text=_("Short description of what the plan offers."),
    )

    features = blocks.ListBlock(
        blocks.CharBlock(label=_("Feature")),
        required=False,
        label=_("Features List"),
        help_text=_("List of included features for this plan."),
    )

    is_featured = blocks.BooleanBlock(
        required=False,
        default=False,
        label=_("Highlight Plan"),
        help_text=_("Mark this plan as featured for emphasis."),
    )

    class Meta:
        icon = "tag"
        label = _("Pricing Plan")
        help_text = _("Displays a single pricing plan with its features.")


class PricingTable(blocks.StreamBlock):
    """
    Stream of multiple pricing plans.
    """

    plan = PricingBlock()

    class Meta:
        icon = "table"
        label = _("Pricing Plans")
        help_text = _("Display one or more pricing tiers or plans.")

class ServicesSectionBlock(blocks.StructBlock):
    """
    Services section using a single dropdown (ForeignKey-like) to select a Service.
    """

    subtitle = blocks.CharBlock(max_length=100, required=False)
    title = blocks.CharBlock(max_length=200, required=True)


    class Meta:
        icon = "cog"
        label = _("Services Section")
