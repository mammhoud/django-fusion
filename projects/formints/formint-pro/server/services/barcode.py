"""POS Full — barcode scan support (Barcode Scanner P1).

A hardware/device scanner emits a barcode string; the POS resolves it to a
product and (optionally) prints a scannable label.

* ``resolve_product`` — exact barcode match with SKU fallback.
* ``barcode_label_svg`` — render a Code128 SVG label via ``python-barcode``
  (lazy import, so the server runs without the optional dependency).
"""

from __future__ import annotations

import logging

logger = logging.getLogger("pos.barcode")


def resolve_product(barcode_value: str):
    """Return the Product whose ``barcode`` (or ``sku``) matches, else None."""
    from models.pos import Product

    value = (barcode_value or "").strip()
    if not value:
        return None

    product = Product.objects.filter(barcode=value).first()
    if product is not None:
        return product
    # SKU fallback — legacy barcodes are often stored in the SKU field.
    return Product.objects.filter(sku=value).first()


def barcode_label_svg(value: str) -> str:
    """Render a Code128 SVG label for ``value``.

    Raises ``ImportError`` when ``python-barcode`` is not installed (the
    dependency is optional; callers should degrade gracefully).
    """
    import io

    import barcode as barcode_lib  # noqa: F401 — optional dependency
    from barcode.writer import SVGWriter

    code = barcode_lib.get("code128", value, writer=SVGWriter())
    buffer = io.BytesIO()
    code.write(buffer)
    return buffer.getvalue().decode("utf-8")
