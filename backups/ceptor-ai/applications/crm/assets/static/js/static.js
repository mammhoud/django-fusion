/**
 * @file crm/assets/static/js/static.js
 * "static" webpack entry — produces static-[hash].css via MiniCssExtractPlugin.
 *
 * Referenced from every CRM skeleton template via:
 *   {% render_bundle 'static' 'css' %}
 *   {% render_bundle 'static' 'js' %}
 */

// ── Vendor CSS ────────────────────────────────────────────────────────────
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';
import 'animate.css/animate.min.css';

// ── Site SCSS ─────────────────────────────────────────────────────────────
import '../styles/main.scss';
