from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock

from ..base import BaseBlock

__all__ = ["MapBlock"]


class MapBlock(BaseBlock):
    """
    Enhanced map block with multiple provider support and advanced options.
    """

    map_provider = blocks.ChoiceBlock(
        choices=[
            ("google", _("Google Maps")),
            ("openstreetmap", _("OpenStreetMap")),
            ("mapbox", _("Mapbox")),
            ("leaflet", _("Leaflet")),
        ],
        default="google",
        label=_("Map Provider"),
    )

    # Address for geocoding
    address = blocks.TextBlock(
        required=False,
        label=_("Physical Address"),
        help_text=_("Used for geocoding if coordinates not provided"),
    )

    # Coordinates (alternative to address)
    latitude = blocks.DecimalBlock(
        required=False,
        min_value=-90,
        max_value=90,
        decimal_places=6,
        label=_("Latitude"),
        help_text=_("Decimal degrees, e.g., 40.7128"),
    )

    longitude = blocks.DecimalBlock(
        required=False,
        min_value=-180,
        max_value=180,
        decimal_places=6,
        label=_("Longitude"),
        help_text=_("Decimal degrees, e.g., -74.0060"),
    )

    # Display options
    zoom_level = blocks.IntegerBlock(
        default=15,
        min_value=1,
        max_value=20,
        label=_("Zoom Level"),
        help_text=_("1 (world) to 20 (building)"),
    )

    map_height = blocks.CharBlock(
        default="400px",
        max_length=20,
        label=_("Map Height"),
        help_text=_("CSS height value, e.g., 400px, 50vh, 30rem"),
    )

    show_marker = blocks.BooleanBlock(default=True, label=_("Show Location Marker"))

    marker_title = blocks.CharBlock(
        required=False, max_length=200, default=_("Our Location"), label=_("Marker Title")
    )

    # Interactive features
    enable_scroll_wheel = blocks.BooleanBlock(
        default=True, label=_("Enable Scroll Zoom"), help_text=_("Allow zooming with mouse wheel")
    )

    enable_fullscreen = blocks.BooleanBlock(default=True, label=_("Enable Fullscreen"))

    show_street_view = blocks.BooleanBlock(default=False, label=_("Show Street View Button"))

    # Multiple markers support
    additional_markers = blocks.ListBlock(
        blocks.StructBlock(
            [
                ("title", blocks.CharBlock(max_length=100)),
                ("address", blocks.TextBlock()),
                ("latitude", blocks.DecimalBlock(min_value=-90, max_value=90, decimal_places=6)),
                ("longitude", blocks.DecimalBlock(min_value=-180, max_value=180, decimal_places=6)),
            ]
        ),
        required=False,
        label=_("Additional Locations"),
        help_text=_("Add multiple markers on the map"),
    )

    # Custom styling
    map_style = blocks.ChoiceBlock(
        choices=[
            ("standard", _("Standard")),
            ("silver", _("Silver")),
            ("retro", _("Retro")),
            ("dark", _("Dark")),
            ("night", _("Night")),
            ("aubergine", _("Aubergine")),
        ],
        default="standard",
        label=_("Map Style"),
        help_text=_("Color theme for the map"),
    )

    # Custom marker icon
    custom_marker_icon = ImageChooserBlock(
        required=False,
        label=_("Custom Marker Icon"),
        help_text=_("Custom image for location marker"),
    )

    # Info window content
    info_window_content = blocks.RichTextBlock(
        required=False,
        features=["bold", "italic", "link"],
        label=_("Info Window Content"),
        help_text=_("Content shown when clicking the marker"),
    )

    class Meta:
        icon = "site"
        label = _("Interactive Map")
        # template was: blocks/map_block.html
        group = _("Media")

    def clean(self, value):
        cleaned_data = super().clean(value)

        # Validate that either address or coordinates are provided
        if not cleaned_data.get("address") and not (
            cleaned_data.get("latitude") and cleaned_data.get("longitude")
        ):
            raise blocks.ValidationError(
                _("Please provide either an address or both latitude and longitude.")
            )

        return cleaned_data
