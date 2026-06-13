/**
 * @file ctc-research/assets/static/js/static.js
 * "static" webpack entry — produces static-[hash].css via MiniCssExtractPlugin.
 *
 * This is the CSS/vendor-CSS entry point referenced by every skeleton template via:
 *   {% render_bundle 'static' 'css' %}
 *   {% render_bundle 'static' 'js' %}
 *
 * Vendor CSS libraries are imported from node_modules (no ~ required in webpack 5).
 * Site-specific SCSS is imported via path relative to this file.
 * Shared SCSS is imported via the ~shared alias (→ assets/static/).
 */

// ── Vendor CSS ─────────────────────────────────────────────────────────────
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';
import 'animate.css/animate.min.css';
import 'owl.carousel/dist/assets/owl.carousel.min.css';
import 'owl.carousel/dist/assets/owl.theme.default.min.css';
import 'magnific-popup/dist/magnific-popup.css';
import 'swiper/swiper-bundle.css';
import 'scrollcue/scrollCue.css';
import 'glightbox/dist/css/glightbox.min.css';
import 'slick-carousel/slick/slick.css';
import 'aos/dist/aos.css';
