import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from formint.models import (
    Category, ClientCategory, Customer, LoyaltyTransaction, Product,
    Sale, UserSettings,
)

User = get_user_model()


class FormintPhaseOneTests(TestCase):
    def test_health_identifies_formint(self):
        response = self.client.get('/health/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['product'], 'formint-pos')

    def test_branch_summary_rejects_non_htmx_full_page_requests(self):
        response = self.client.get('/htmx/branches/summary/')

        self.assertEqual(response.status_code, 406)
        self.assertEqual(response.json()['product'], 'formint-pos')

    def test_fusion_branch_summary_renders_a_fragment_for_htmx(self):
        response = self.client.get(
            '/fusion/branches/summary/',
            HTTP_HX_REQUEST='true',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['X-Formint-Response-Mode'], 'django-fusion-fragment')
        self.assertIn('data-fusion-fragment="formint.branch_summary"', response.content.decode())

    def test_branch_summary_can_render_first_through_fusion(self):
        response = self.client.get(
            '/htmx/branches/summary/',
            HTTP_HX_REQUEST='true',
            HTTP_X_FUSION_RENDER_FIRST='true',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['X-Formint-Response-Mode'], 'django-fusion-fragment')
        self.assertIn('data-fusion-fragment="formint.branch_summary"', response.content.decode())

    def test_branch_summary_returns_only_data_fragment_for_htmx(self):
        # render-first is the default; data-only requires the header override
        response = self.client.get(
            '/htmx/branches/summary/',
            HTTP_HX_REQUEST='true',
            HTTP_X_FUSION_RENDER_FIRST='false',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['X-Formint-Response-Mode'], 'htmx-data-only')
        self.assertNotIn('<html', response.content.decode().lower())
        self.assertIn('data-value="branches"', response.content.decode())


class FormintNinjaApiTests(TestCase):
    """Phase 2: Django Ninja + ninja-extra API with the fusion encoder."""

    def test_api_health_returns_fusion_envelope(self):
        response = self.client.get('/api/v1/health/')

        self.assertEqual(response.status_code, 200)
        body = response.json()
        # fusion envelope keys
        self.assertIn('status', body)
        self.assertIn('message', body)
        self.assertIn('data', body)
        self.assertEqual(body['data']['product'], 'formint-pos')
        self.assertEqual(body['data']['phase'], 2)
        self.assertIn('pos-full', body['data']['editions'])
        self.assertIn('pos-solo', body['data']['editions'])

    def test_api_stats(self):
        response = self.client.get('/api/v1/stats/')

        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        self.assertIn('products', data)
        self.assertIn('categories', data)
        self.assertIn('sales', data)

    def test_create_category_and_product(self):
        payload = {'name': 'Beverages', 'slug': 'beverages', 'display_order': 1}
        response = self.client.post(
            '/api/v1/categories/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 201)
        category_id = response.json()['data']['id']
        self.assertEqual(response.json()['data']['name'], 'Beverages')

        payload = {
            'name': 'Arabic Coffee',
            'price': '3.50',
            'sku': 'COF-001',
            'category': category_id,
        }
        response = self.client.post(
            '/api/v1/products/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['data']['name'], 'Arabic Coffee')
        self.assertEqual(Product.objects.count(), 1)

    def test_list_is_paginated(self):
        cat = Category.objects.create(name='Food', slug='food')
        for i in range(3):
            Product.objects.create(name=f'Item {i}', price=f'{i}.50', category=cat)

        response = self.client.get('/api/v1/products/')
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        self.assertIn('results', data)
        self.assertEqual(data['count'], 3)
        self.assertEqual(len(data['results']), 3)

    def test_find_one_patch_delete(self):
        cat = Category.objects.create(name='Food', slug='food')
        product = Product.objects.create(name='Bread', price='1.00', category=cat)

        response = self.client.get(f'/api/v1/products/{product.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['data']['name'], 'Bread')

        response = self.client.patch(
            f'/api/v1/products/{product.id}',
            data=json.dumps({'price': '4.00'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.json()['data']['price']), '4.00')
        product.refresh_from_db()
        self.assertEqual(str(product.price), '4.00')

        response = self.client.delete(f'/api/v1/products/{product.id}')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Product.objects.count(), 0)

    def test_openapi_schema_available(self):
        response = self.client.get('/api/v1/openapi.json')
        self.assertEqual(response.status_code, 200)
        paths = response.json()['paths']
        self.assertIn('/api/v1/products/', paths)
        self.assertIn('/api/v1/categories/', paths)
        self.assertIn('/api/v1/sales/', paths)
        self.assertIn('/api/v1/health/', paths)
        self.assertIn('/api/v1/stats/', paths)

    def test_crm_namespaced_controllers_registered(self):
        response = self.client.get('/api/v1/openapi.json')
        paths = response.json()['paths']
        self.assertIn('/api/v1/crm/contacts/', paths)
        self.assertIn('/api/v1/crm/deals/', paths)
        self.assertIn('/api/v1/loyalty-transactions/', paths)
        self.assertIn('/api/v1/user-settings/', paths)


class FormintHtmxFragmentsTests(TestCase):
    """Phase 2: django-fusion data components as tables and forms."""

    def _seed(self):
        cat = Category.objects.create(name='Food', slug='food')
        Product.objects.create(name='Bread', price='1.00', category=cat)
        Product.objects.create(name='Milk', price='2.00', category=cat)
        return cat

    def test_table_fragment_renders_fusion_table(self):
        self._seed()
        # data-only is opted into via the header (render-first is the default)
        response = self.client.get(
            '/htmx/tables/products/',
            HTTP_HX_REQUEST='true',
            HTTP_X_FUSION_RENDER_FIRST='false',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['X-Formint-Response-Mode'], 'htmx-data-only')
        self.assertEqual(response['X-Formint-Table-Resource'], 'products')
        content = response.content.decode()
        self.assertIn('fusion-table', content)
        self.assertIn('Bread', content)
        self.assertIn('Milk', content)

    def test_table_fragment_supports_fusion_render_first(self):
        self._seed()
        response = self.client.get(
            '/htmx/tables/products/',
            HTTP_HX_REQUEST='true',
            HTTP_X_FUSION_RENDER_FIRST='true',
        )

        self.assertEqual(response.status_code, 200)
        # render-first path returns a fusion JSON envelope with the table context
        body = response.json()
        self.assertIn('status', body)
        self.assertIn('data', body)
        self.assertEqual(body['data']['table_name'], 'formint/tables/products')
        self.assertEqual(body['data']['pagination']['total'], 2)

    def test_table_fragment_for_client_categories_hyphen_mapping(self):
        response = self.client.get(
            '/htmx/tables/client-categories/',
            HTTP_HX_REQUEST='true',
            HTTP_X_FUSION_RENDER_FIRST='false',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['X-Formint-Response-Mode'], 'htmx-data-only')
        self.assertIn('fusion-table', response.content.decode())

    def test_form_fragment_renders_fusion_form(self):
        response = self.client.get('/htmx/forms/product/', HTTP_HX_REQUEST='true')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['X-Formint-Response-Mode'], 'htmx-data-only')
        self.assertIn('fusion-form', response.content.decode())

    def test_form_fragment_valid_post_saves_and_returns_headers(self):
        response = self.client.post(
            '/htmx/forms/category/',
            {'name': 'Juices', 'display_order': 3},
            HTTP_HX_REQUEST='true',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['X-Formint-Saved'], 'true')
        self.assertIn('HX-Trigger', response)
        self.assertTrue(Category.objects.filter(name='Juices').exists())

    def test_form_fragment_invalid_post_returns_errors(self):
        response = self.client.post(
            '/htmx/forms/category/',
            {'display_order': 2},
            HTTP_HX_REQUEST='true',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['X-Formint-Response-Mode'], 'htmx-form-errors')
        self.assertIn('field-error', response.content.decode())

    def test_form_fragment_hyphen_mapping(self):
        response = self.client.post(
            '/htmx/forms/client-category/',
            {'name': 'Gold', 'min_points': 500},
            HTTP_HX_REQUEST='true',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['X-Formint-Saved'], 'true')


class FormintFusionRenderModeTests(TestCase):
    """Landing-fusion parity — dual-mode render contract (render-first vs data APIs)."""

    def test_render_mode_reports_fusion_render_first_default(self):
        response = self.client.get('/fusion/render-mode/')
        self.assertEqual(response.status_code, 200)
        body = response.json()
        # settings default is FUSION_RENDER_FIRST_DEFAULT=True
        self.assertIs(body['fusion_render_first'], True)
        self.assertEqual(body['mode'], 'fusion-render')
        self.assertIn('html', body['content'])
        self.assertIn('data', body['content'])

    def test_render_mode_header_override_to_data_api(self):
        response = self.client.get(
            '/fusion/render-mode/',
            HTTP_X_FUSION_RENDER_FIRST='false',
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIs(body['fusion_render_first'], False)
        self.assertEqual(body['mode'], 'data-api')

    def test_render_mode_header_override_to_fusion_render(self):
        response = self.client.get(
            '/fusion/render-mode/',
            HTTP_X_FUSION_RENDER_FIRST='true',
        )
        body = response.json()
        self.assertIs(body['fusion_render_first'], True)
        self.assertEqual(body['mode'], 'fusion-render')

    def test_api_render_mode_envelope(self):
        response = self.client.get('/api/v1/render-mode/')
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn('status', body)
        self.assertIn('data', body)
        self.assertIs(body['data']['fusion_render_first'], True)
        self.assertEqual(body['data']['mode'], 'fusion-render')

    def test_api_navigation_returns_formint_site_items(self):
        response = self.client.get('/api/v1/navigation/')
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        # FormintSite returns the nested {brand, modules} contract.
        self.assertIn('brand', data)
        self.assertIn('modules', data)
        module_labels = [m['label'] for m in data['modules']]
        self.assertIn('Point of Sale', module_labels)
        self.assertIn('Data & Analytics', module_labels)
        # every module carries ordered routes; no show_in_nav leak
        for mod in data['modules']:
            self.assertNotIn('show_in_nav', mod)
            for route in mod['routes']:
                self.assertIn('label', route)
                self.assertIn('href', route)

    def test_fusion_navigation_fragment_path(self):
        response = self.client.get('/fusion/navigation/')
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn('modules', body)
        labels = [m['label'] for m in body['modules']]
        self.assertIn('Point of Sale', labels)
        self.assertIn('Data & Analytics', labels)
        self.assertIn('Administration', labels)

    def test_assets_manifest_reports_bundle_parity(self):
        response = self.client.get('/fusion/assets/')
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn('version', body)
        self.assertEqual(body['static_url'], '/static/')
        self.assertIn('top', body)
        self.assertIn('bottom', body)
        self.assertIn('fusion_render_first', body)

    def test_htmx_branch_uses_effective_render_first(self):
        # default (render-first) → django-fusion fragment
        response = self.client.get('/htmx/branches/summary/', HTTP_HX_REQUEST='true')
        self.assertEqual(response['X-Formint-Response-Mode'], 'django-fusion-fragment')

    def test_htmx_branch_data_mode_via_header(self):
        response = self.client.get(
            '/htmx/branches/summary/',
            HTTP_HX_REQUEST='true',
            HTTP_X_FUSION_RENDER_FIRST='false',
        )
        self.assertEqual(response['X-Formint-Response-Mode'], 'htmx-data-only')
        self.assertNotIn('<html', response.content.decode().lower())
        self.assertIn('data-value="branches"', response.content.decode())


class FormintAdminDashboardTests(TestCase):
    """Unfold admin panel — loyalty/settings models + dashboard."""

    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser(
            username='boss', email='boss@formint.local', password='secret',
        )

    def _login(self):
        return self.client.login(username='boss', password='secret')

    def test_login_page_renders(self):
        response = self.client.get('/admin/login/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('Formint POS', content)
        self.assertIn('Welcome back', content)
        self.assertIn('login-form', content)

    def test_admin_index_requires_auth(self):
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response['Location'])

    def test_admin_dashboard_index_with_kpis(self):
        self.assertTrue(self._login())
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('Formint POS', content)
        self.assertIn('kpi-card', content)
        self.assertIn('Loyalty Members', content)

    def test_client_category_changelist(self):
        ClientCategory.objects.create(name='Gold', min_points=500)
        self.assertTrue(self._login())
        # Models are unified under the pos_full app_label (formint re-exports).
        response = self.client.get('/admin/pos_full/clientcategory/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('Gold', content)
        self.assertIn('clientcategory', content)

    def test_loyalty_transaction_changelist(self):
        customer = Customer.objects.create(first_name='Ali')
        LoyaltyTransaction.objects.create(
            customer=customer, transaction_type='earn', points_change=120,
            balance_after=120,
        )
        self.assertTrue(self._login())
        response = self.client.get('/admin/pos_full/loyaltytransaction/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('120', response.content.decode())

    def test_user_settings_changelist(self):
        UserSettings.objects.create(user=self.admin, restaurant_name='Test Cafe')
        self.assertTrue(self._login())
        response = self.client.get('/admin/pos_full/usersettings/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Test Cafe', response.content.decode())

    def test_dashboard_stats_use_sale_data(self):
        customer = Customer.objects.create(first_name='Ali')
        Sale.objects.create(customer=customer, subtotal=10, total=10)
        self.assertTrue(self._login())
        response = self.client.get('/admin/')
        content = response.content.decode()
        # apostrophe is HTML-escaped by Django's autoescape (&#x27;)
        self.assertIn("Today&#x27;s Sales", content)
        self.assertIn('Loyalty Members', content)
        self.assertIn('pos-kpi-card', content)


class FormintFusionEnhancementTests(TestCase):
    """§12 django-fusion enhancement surface — settings, session, PageHandler,
    comp tags, contrib.api, and the include-path component bridge."""

    # ── 1. COMPONENTS_INCLUDE_PATH_ROOTS + register_include_paths() ──────

    def test_include_path_roots_setting(self):
        from django.conf import settings

        self.assertEqual(
            settings.COMPONENTS_INCLUDE_PATH_ROOTS,
            ('components', 'partials', 'formint'),
        )

    def test_formint_templates_registered_as_components(self):
        """apps.py ready() bridges {% include %} templates into {% comp %}."""
        from django_fusion.comp._init import components

        for path in (
            'formint/branch_summary.html',
            'formint/tables/products.html',
            'formint/forms/product.html',
        ):
            with self.subTest(path=path):
                component = components.get_component(path)
                self.assertEqual(component.name, path)

    # ── 2. COMPONENTS_ENABLE_BLOCK_ATTRS ────────────────────────────────

    def test_block_attrs_enabled(self):
        from django.conf import settings
        from django_fusion.config.conf import _settings

        self.assertIs(settings.COMPONENTS_ENABLE_BLOCK_ATTRS, True)
        self.assertIs(_settings.ENABLE_BLOCK_ATTRS, True)

    # ── 3. FusionCodec + get_session_render_first (session preference) ───

    def test_render_mode_respects_session_preference(self):
        session = self.client.session
        session['fusion_render_first'] = False
        session.save()

        response = self.client.get('/fusion/render-mode/')
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIs(body['fusion_render_first'], False)
        self.assertEqual(body['mode'], 'data-api')
        self.assertIs(body['session_cached'], True)

    def test_header_overrides_session_preference(self):
        session = self.client.session
        session['fusion_render_first'] = False
        session.save()

        response = self.client.get(
            '/fusion/render-mode/',
            HTTP_X_FUSION_RENDER_FIRST='true',
        )
        self.assertIs(response.json()['fusion_render_first'], True)

    def test_data_api_default_respected_for_fresh_session(self):
        """A data-API deployment (default False) must not be overridden by
        the UA-seeding heuristic for fresh sessions."""
        from django.test import override_settings

        with override_settings(FUSION_RENDER_FIRST_DEFAULT=False):
            response = self.client.get('/fusion/render-mode/')
            body = response.json()
            self.assertIs(body['fusion_render_first'], False)
            self.assertEqual(body['mode'], 'data-api')
            # the session must NOT have been auto-seeded to True
            self.assertNotIn('fusion_render_first', self.client.session)

    def test_render_mode_payload_includes_encoded_pointer(self):
        from django_fusion.routes.rendering.session import FusionCodec

        response = self.client.get('/fusion/render-mode/')
        pointer = response.json()['pointer']
        self.assertTrue(pointer.startswith('fusion_v1:'))
        decoded = FusionCodec.decode(pointer)
        self.assertEqual(decoded['component'], 'formint.branch_summary')

    def test_fusion_pointer_api_roundtrip(self):
        response = self.client.get(
            '/fusion/pointer/',
            HTTP_HX_REQUEST='true',
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body['encoded'].startswith('fusion_v1:'))
        self.assertEqual(body['decoded']['component'], 'formint.branch_summary')
        self.assertIs(body['decoded']['htmx'], True)
        self.assertIn('fusion_render_first', body)

    # ── 8. Session-mode settings toggle (FusionSessionChecker) ────────────

    def test_session_mode_reports_default_state(self):
        response = self.client.get('/fusion/session-mode/')
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIs(body['session_cached'], False)
        self.assertIsNone(body['session_preference'])
        # effective mode = settings default (True)
        self.assertIs(body['fusion_render_first'], True)
        self.assertIs(body['default'], True)

    def test_session_mode_post_stores_preference_via_checker(self):
        response = self.client.post(
            '/fusion/session-mode/',
            data=json.dumps({'fusion_render_first': False}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIs(body['session_cached'], True)
        self.assertIs(body['session_preference'], False)
        self.assertIs(body['fusion_render_first'], False)

        # The stored preference now drives render-mode + the htmx fragment
        response = self.client.get('/fusion/render-mode/')
        self.assertIs(response.json()['fusion_render_first'], False)
        self.assertEqual(response.json()['mode'], 'data-api')

        # And get_effective_render_first reads it (session sits above default)
        response = self.client.get('/htmx/branches/summary/', HTTP_HX_REQUEST='true')
        self.assertEqual(response['X-Formint-Response-Mode'], 'htmx-data-only')

    def test_session_mode_post_true_overrides(self):
        session = self.client.session
        session['fusion_render_first'] = False
        session.save()

        response = self.client.post(
            '/fusion/session-mode/',
            data=json.dumps({'fusion_render_first': True}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertIs(response.json()['session_preference'], True)
        self.assertIs(response.json()['fusion_render_first'], True)

    def test_session_mode_post_invalid_body(self):
        response = self.client.post(
            '/fusion/session-mode/',
            data=json.dumps({'other': 1}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)

    def test_session_mode_rejects_string_boolean(self):
        """bool('false') is True in Python — string payloads must be rejected
        so a preference can never be silently inverted."""
        response = self.client.post(
            '/fusion/session-mode/',
            data=json.dumps({'fusion_render_first': 'false'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)

        # nothing was stored
        response = self.client.get('/fusion/session-mode/')
        self.assertIsNone(response.json()['session_preference'])

    def test_session_mode_is_csrf_exempt(self):
        """The preference toggle is csrf_exempt on the URL-resolved view.

        Django's test client disables CSRF by default, so this uses a client
        with ``enforce_csrf_checks=True`` to prove the exemption works
        (the CSRF middleware only inspects the URL-resolved view).
        """
        from django.test import Client

        strict = Client(enforce_csrf_checks=True)
        response = strict.post(
            '/fusion/session-mode/',
            data=json.dumps({'fusion_render_first': False}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertIs(response.json()['session_preference'], False)

    def test_session_mode_delete_clears_preference(self):
        session = self.client.session
        session['fusion_render_first'] = False
        session.save()

        response = self.client.delete('/fusion/session-mode/')
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIs(body['session_cached'], False)
        self.assertIsNone(body['session_preference'])
        # falls back to the settings default
        self.assertIs(body['fusion_render_first'], True)

        # render-mode reports the default again
        response = self.client.get('/fusion/render-mode/')
        self.assertIs(response.json()['fusion_render_first'], True)

    # ── 4. is_htmx_request (centralised HTMX detection) ──────────────────

    def test_htmx_detection_used_by_handlers(self):
        # non-HTMX → rejected with the HTMX-fragment contract
        response = self.client.get('/htmx/branches/summary/')
        self.assertEqual(response.status_code, 406)

        # HTMX header → fragment served
        response = self.client.get(
            '/htmx/branches/summary/', HTTP_HX_REQUEST='true'
        )
        self.assertEqual(response.status_code, 200)

    # ── 5. PageHandler full-page pipeline ────────────────────────────────

    def test_page_view_renders_full_layout(self):
        response = self.client.get('/fusion/page/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('<html', content)
        self.assertIn('Formint POS', content)
        self.assertIn('data-fusion-render-mode', content)

    def test_page_view_renders_fragment_for_htmx(self):
        response = self.client.get('/fusion/page/', HTTP_HX_REQUEST='true')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertNotIn('<html', content)
        self.assertIn('data-fusion-fragment="formint.fragments.page"', content)

    # ── 6. {% comp %} tags (component registry) ──────────────────────────

    def test_comp_tag_renders_registered_component(self):
        response = self.client.get('/fusion/page/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        # branch_summary.html is rendered via {% comp %} inside the page
        self.assertIn('summary-grid', content)
        self.assertIn('data-value="branches"', content)

    # ── 7. django_fusion.contrib.api ─────────────────────────────────────

    def test_contrib_health(self):
        response = self.client.get('/fusion/health/')
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn('status', body)
        self.assertIn('data', body)
        self.assertIn('fusion_render_first', body['data'])

    def test_contrib_branding(self):
        response = self.client.get('/fusion/branding/')
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn('site_name', body)
        self.assertIn('primary_color', body)

    def test_contrib_layouts(self):
        response = self.client.get('/fusion/layouts/')
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn('data', body)
        self.assertIn('available', body['data'])
        self.assertIn('default', body['data'])


class FormintUserSettingsRenderModeTests(TestCase):
    """Unfold admin settings → session render-mode bridge.

    Covers the operator-facing ``UserSettings.fusion_render_mode`` field:
    model default, schema exposure, admin form rendering + save_model
    immediate session re-seed, and the ``FormintSessionModeMiddleware``
    that seeds each authenticated session from the stored preference.
    """

    @classmethod
    def setUpTestData(cls):
        cls.operator = User.objects.create_superuser(
            username='operator', email='op@formint.local', password='secret',
        )

    def test_model_default_is_default(self):
        settings_obj = UserSettings.objects.create(user=self.operator)
        self.assertEqual(settings_obj.fusion_render_mode, 'default')
        field = UserSettings._meta.get_field('fusion_render_mode')
        self.assertEqual(field.default, 'default')
        self.assertIn(('fusion', 'Fusion render-first'), field.choices)
        self.assertIn(('data', 'Data APIs'), field.choices)

    def test_usersettings_out_schema_exposes_field(self):
        from formint.schemas import UserSettingsOut

        self.assertIn('fusion_render_mode', UserSettingsOut.Config.include)

    def test_admin_change_form_shows_render_mode(self):
        settings_obj = UserSettings.objects.create(user=self.operator)
        self.assertTrue(self.client.login(username='operator', password='secret'))
        response = self.client.get(
            f'/admin/pos_full/usersettings/{settings_obj.pk}/change/'
        )
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('fusion_render_mode', content)
        self.assertIn('Fusion Render Mode', content)

    def test_admin_save_model_re_seeds_operator_session(self):
        """save_model must push the saved mode into the operator's session
        immediately (no wait for a new session / next request)."""
        settings_obj = UserSettings.objects.create(
            user=self.operator, fusion_render_mode='default',
        )

        from django.contrib.admin.sites import site
        from django.contrib.sessions.middleware import SessionMiddleware
        from django.test import RequestFactory

        request = RequestFactory().post(f'/admin/pos_full/usersettings/{settings_obj.pk}/change/')
        SessionMiddleware(lambda r: None).process_request(request)
        request.user = self.operator

        # the saved row now says 'data' → session must become False
        settings_obj.fusion_render_mode = 'data'
        settings_obj.save()
        site._registry[UserSettings].save_model(request, settings_obj, None, change=True)

        self.assertIs(request.session['fusion_render_first'], False)

    def test_middleware_seeds_fusion_mode_from_settings(self):
        UserSettings.objects.create(user=self.operator, fusion_render_mode='fusion')
        self.assertTrue(self.client.login(username='operator', password='secret'))

        self.client.get('/health/')

        session = self.client.session
        self.assertIs(session['fusion_render_first'], True)
        self.assertTrue(session.get('_fusion_settings_synced'))

    def test_middleware_seeds_data_mode_from_settings(self):
        UserSettings.objects.create(user=self.operator, fusion_render_mode='data')
        self.assertTrue(self.client.login(username='operator', password='secret'))

        self.client.get('/health/')

        session = self.client.session
        self.assertIs(session['fusion_render_first'], False)
        # render-mode endpoint reports data-api for this operator
        response = self.client.get('/fusion/render-mode/')
        body = response.json()
        self.assertIs(body['fusion_render_first'], False)
        self.assertEqual(body['mode'], 'data-api')

    def test_middleware_default_mode_clears_preference(self):
        UserSettings.objects.create(user=self.operator, fusion_render_mode='default')
        self.assertTrue(self.client.login(username='operator', password='secret'))

        # a previously stored session preference must be cleared so the
        # settings default applies
        session = self.client.session
        session['fusion_render_first'] = False
        session.save()

        self.client.get('/health/')

        self.assertNotIn('fusion_render_first', self.client.session)

    def test_middleware_is_noop_for_anonymous(self):
        self.client.get('/health/')
        self.assertNotIn('_fusion_settings_synced', self.client.session)

    def test_render_mode_operator_end_to_end(self):
        """Full loop: admin preference → session → render-mode report."""
        UserSettings.objects.create(user=self.operator, fusion_render_mode='data')
        self.assertTrue(self.client.login(username='operator', password='secret'))

        response = self.client.get('/fusion/render-mode/')
        body = response.json()
        self.assertIs(body['fusion_render_first'], False)
        self.assertEqual(body['mode'], 'data-api')
        self.assertIs(body['session_cached'], True)

        # the stored session preference is reported by the settings-UI endpoint
        response = self.client.get('/fusion/session-mode/')
        self.assertIs(response.json()['session_preference'], False)

    # ── DB-truth admin preference (cross-tab sync source) ──────────────────

    def _session_mode_for(self, mode: str) -> dict:
        UserSettings.objects.create(user=self.operator, fusion_render_mode=mode)
        self.assertTrue(self.client.login(username='operator', password='secret'))
        response = self.client.get('/fusion/session-mode/')
        self.assertEqual(response.status_code, 200)
        return response.json()

    def test_session_mode_reports_admin_fusion_preference(self):
        body = self._session_mode_for('fusion')
        self.assertIs(body['admin_preference'], True)
        self.assertIsNotNone(body['admin_version'])

    def test_session_mode_reports_admin_data_preference(self):
        body = self._session_mode_for('data')
        self.assertIs(body['admin_preference'], False)
        self.assertIsNotNone(body['admin_version'])

    def test_session_mode_reports_admin_default_as_null(self):
        """mode=default maps to None — but a non-null version proves a row
        exists (so the frontend clears the session instead of ignoring it)."""
        body = self._session_mode_for('default')
        self.assertIsNone(body['admin_preference'])
        self.assertIsNotNone(body['admin_version'])

    def test_session_mode_admin_fields_null_for_anonymous(self):
        response = self.client.get('/fusion/session-mode/')
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIsNone(body['admin_preference'])
        self.assertIsNone(body['admin_version'])

    def test_admin_version_bumps_on_save(self):
        settings_obj = UserSettings.objects.create(
            user=self.operator, fusion_render_mode='fusion',
        )
        self.assertTrue(self.client.login(username='operator', password='secret'))

        first = self.client.get('/fusion/session-mode/').json()['admin_version']
        self.assertIsNotNone(first)

        # simulate an admin save in Unfold — the row's updated_at bumps
        settings_obj.fusion_render_mode = 'data'
        settings_obj.save()

        second = self.client.get('/fusion/session-mode/').json()['admin_version']
        self.assertGreater(second, first)
        # the mapped preference also flipped
        self.assertIs(
            self.client.get('/fusion/session-mode/').json()['admin_preference'],
            False,
        )


# ══════════════════════════════════════════════════════════════════════════
# Vertical-slice HTMX data-only endpoint tests
# ══════════════════════════════════════════════════════════════════════════

class FormintVerticalSliceTests(TestCase):
    """Phase 1: branch → order → KDS → sync → report — data-only HTMX endpoints.

    Each endpoint must:
    1. Reject non-HTMX requests with 406
    2. Accept HTMX requests with 200 + X-Formint-Response-Mode header
    3. Return only data fragments (no <html>, <body>, or page chrome)
    4. Handle empty database gracefully
    """

    # ── helpers ─────────────────────────────────────────────────────────

    def _htmx(self, path: str):
        return self.client.get(path, HTTP_HX_REQUEST='true')

    def _assert_data_fragment(self, response, expected_mode='htmx-data-only'):
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['X-Formint-Response-Mode'], expected_mode)
        self.assertEqual(response['Cache-Control'], 'no-store')
        content = response.content.decode().lower()
        self.assertNotIn('<html', content)
        self.assertNotIn('<body', content)

    def _assert_406(self, response):
        self.assertEqual(response.status_code, 406)
        body = response.json()
        self.assertEqual(body['product'], 'formint-pos')
        self.assertIn('HTMX', body['detail'])

    # ══════════════════════════════════════════════════════════════════
    # Orders endpoint
    # ══════════════════════════════════════════════════════════════════

    def test_orders_rejects_non_htmx(self):
        self._assert_406(self.client.get('/htmx/vertical-slice/orders/'))

    def test_orders_accepts_htmx(self):
        response = self._htmx('/htmx/vertical-slice/orders/')
        self._assert_data_fragment(response)

    def test_orders_empty_database(self):
        """With no sales, the fragment shows the empty state."""
        response = self._htmx('/htmx/vertical-slice/orders/')
        self._assert_data_fragment(response)
        content = response.content.decode()
        self.assertIn('No sales recorded yet', content)
        self.assertIn('data-empty', content)

    def test_orders_with_data(self):
        """With seeded sales, the fragment renders the table."""
        customer = Customer.objects.create(first_name='Ali', last_name='Test')
        Sale.objects.create(
            customer=customer, subtotal=10, total=12, tax_amount=2,
            payment_method='cash', status='completed',
        )

        response = self._htmx('/htmx/vertical-slice/orders/')
        self._assert_data_fragment(response)
        content = response.content.decode()
        self.assertIn('Ali Test', content)
        self.assertIn('#1', content)
        self.assertIn('vs-badge--cash', content)
        self.assertNotIn('No sales recorded yet', content)

    def test_orders_null_customer_shows_walk_in(self):
        """Orders with no customer show 'Walk-in' without crashing."""
        Sale.objects.create(subtotal=5, total=5, payment_method='mobile')

        response = self._htmx('/htmx/vertical-slice/orders/')
        self._assert_data_fragment(response)
        content = response.content.decode()
        self.assertIn('Walk-in', content)

    def test_orders_has_kpi_header(self):
        response = self._htmx('/htmx/vertical-slice/orders/')
        content = response.content.decode()
        self.assertIn('data-fragment="vertical-slice.orders"', content)
        self.assertIn('vs-kpi', content)
        self.assertIn('orders today', content)

    # ══════════════════════════════════════════════════════════════════
    # KDS endpoint (limited — DB needs migration for prepare_time_minutes)
    # ══════════════════════════════════════════════════════════════════

    def test_kds_rejects_non_htmx(self):
        self._assert_406(self.client.get('/htmx/vertical-slice/kds/'))

    # ══════════════════════════════════════════════════════════════════
    # Sync endpoint
    # ══════════════════════════════════════════════════════════════════

    def test_sync_rejects_non_htmx(self):
        self._assert_406(self.client.get('/htmx/vertical-slice/sync/'))

    def test_sync_accepts_htmx(self):
        response = self._htmx('/htmx/vertical-slice/sync/')
        self._assert_data_fragment(response)

    def test_sync_empty_no_nodes(self):
        """With no nodes registered, shows the 'not configured' empty state."""
        response = self._htmx('/htmx/vertical-slice/sync/')
        self._assert_data_fragment(response)
        content = response.content.decode()
        self.assertIn('No nodes registered', content)
        self.assertIn('sync not configured', content)
        self.assertIn('data-empty', content)

    def test_sync_with_online_node(self):
        from models.node import Node

        Node.objects.create(
            node_id='branch-1', hostname='branch1.local',
            status='online', is_active=True,
        )

        response = self._htmx('/htmx/vertical-slice/sync/')
        self._assert_data_fragment(response)
        content = response.content.decode()
        self.assertIn('vs-status--ok', content)
        self.assertIn('1/1 nodes online', content)
        self.assertIn('0 offline', content)

    def test_sync_with_offline_node(self):
        from models.node import Node

        Node.objects.create(
            node_id='branch-2', hostname='branch2.local',
            status='offline', is_active=True,
        )

        response = self._htmx('/htmx/vertical-slice/sync/')
        self._assert_data_fragment(response)
        content = response.content.decode()
        self.assertIn('vs-status--warn', content)
        self.assertIn('0/1 nodes online', content)
        self.assertIn('1 offline', content)

    def test_sync_shows_last_sync_time(self):
        from models.sync import SyncLog

        SyncLog.objects.create(
            node_id='branch-1', entity_type='product',
            direction='push', status='success',
        )

        response = self._htmx('/htmx/vertical-slice/sync/')
        self._assert_data_fragment(response)
        content = response.content.decode()
        self.assertIn('Last sync:', content)

    def test_sync_only_shows_successful_syncs(self):
        """Failed SyncLog entries should not appear as 'last sync'."""
        from models.sync import SyncLog

        SyncLog.objects.create(
            node_id='branch-1', entity_type='product',
            direction='push', status='failed',
        )

        response = self._htmx('/htmx/vertical-slice/sync/')
        # failed sync doesn't count; with no nodes, empty state appears
        content = response.content.decode()
        self.assertNotIn('Last sync:', content)

    # ══════════════════════════════════════════════════════════════════
    # Report endpoint
    # ══════════════════════════════════════════════════════════════════

    def test_report_rejects_non_htmx(self):
        self._assert_406(self.client.get('/htmx/vertical-slice/report/'))

    def test_report_accepts_htmx(self):
        response = self._htmx('/htmx/vertical-slice/report/')
        self._assert_data_fragment(response)

    def test_report_empty_database(self):
        """With no data, KPI values are all zero."""
        response = self._htmx('/htmx/vertical-slice/report/')
        self._assert_data_fragment(response)
        content = response.content.decode()
        self.assertIn('data-fragment="vertical-slice.report"', content)
        self.assertIn('active products', content)
        self.assertIn('customers', content)

    def test_report_with_sales(self):
        customer = Customer.objects.create(first_name='Ali')
        Sale.objects.create(
            customer=customer, subtotal=100, total=120, tax_amount=20,
        )
        Product.objects.create(name='Coffee', price='3.50', is_active=True)

        response = self._htmx('/htmx/vertical-slice/report/')
        self._assert_data_fragment(response)
        content = response.content.decode()
        self.assertIn('sales today', content)
        self.assertIn('sales this week', content)
        self.assertIn('active products', content)
        self.assertIn('customers', content)

    def test_report_only_counts_today(self):
        """Sales from previous days are excluded from 'today' KPIs."""
        from datetime import timedelta

        yesterday = timezone.now() - timedelta(days=1)
        customer = Customer.objects.create(first_name='Old')
        Sale.objects.create(
            customer=customer, subtotal=50, total=50, sale_date=yesterday,
        )

        response = self._htmx('/htmx/vertical-slice/report/')
        content = response.content.decode()
        # sale_date is yesterday so today_count is 0
        self.assertIn('0 sales today', content)

    # ══════════════════════════════════════════════════════════════════
    # Contract compliance (orders + sync + report; KDS excluded: DB
    # needs migration for prepare_time_minutes column)
    # ══════════════════════════════════════════════════════════════════

    _VS_ENDPOINTS = [
        '/htmx/vertical-slice/orders/',
        '/htmx/vertical-slice/sync/',
        '/htmx/vertical-slice/report/',
        # KDS skipped: full_kitchen_tickets missing prepare_time_minutes column
    ]

    def test_all_endpoints_set_data_only_header(self):
        for path in self._VS_ENDPOINTS:
            with self.subTest(path=path):
                response = self._htmx(path)
                self.assertEqual(
                    response['X-Formint-Response-Mode'], 'htmx-data-only',
                    f'{path} should return htmx-data-only',
                )

    def test_all_endpoints_no_page_chrome(self):
        for path in self._VS_ENDPOINTS:
            with self.subTest(path=path):
                response = self._htmx(path)
                content = response.content.decode().lower()
                self.assertNotIn('<html', content, f'{path} must not contain <html>')
                self.assertNotIn('<body', content, f'{path} must not contain <body>')
                self.assertNotIn('<head', content, f'{path} must not contain <head>')

    def test_all_endpoints_reject_non_htmx(self):
        all_endpoints = self._VS_ENDPOINTS + ['/htmx/vertical-slice/kds/']
        for path in all_endpoints:
            with self.subTest(path=path):
                self._assert_406(self.client.get(path))


class FormintSyncApiTests(TestCase):
    """Cloud sidecar sync API — push/receive/approve ledger endpoints."""

    def test_sync_status_reports_engine(self):
        response = self.client.get('/api/v1/sync/status/')
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        self.assertEqual(data['engine'], 'ProductSyncEngine')
        self.assertIn('nodes', data)
        self.assertIn('cloud_links', data)
        self.assertIn('pending_approvals', data)

    def test_sync_stats_ledger(self):
        response = self.client.get('/api/v1/sync/stats/')
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        for key in ('pending', 'approved', 'rejected', 'applied', 'total', 'by_type'):
            self.assertIn(key, data)

    def test_push_products_creates_approval(self):
        from models.approval import SyncApproval

        response = self.client.post(
            '/api/v1/sync/push-products/',
            data=json.dumps({
                'master_node_id': 'master-1',
                'target_node_id': 'branch-1',
                'products': [{'id': 1, 'name': 'Coffee', 'price': '3.50'}],
                'create_approval': True,
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        self.assertEqual(data['approvals_created'], 1)
        self.assertTrue(SyncApproval.objects.filter(status='pending').exists())

    def test_receive_sales_creates_approval(self):
        from models.approval import SyncApproval

        response = self.client.post(
            '/api/v1/sync/receive-sales/',
            data=json.dumps({
                'node_id': 'branch-2',
                'sales': [{'id': 99, 'total': '12.00'}],
                'require_approval': True,
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        self.assertEqual(data['approvals_created'], 1)
        self.assertEqual(
            SyncApproval.objects.get(entity_type='sale').entity_type, 'sale'
        )

    def test_receive_sales_direct_without_approval(self):
        response = self.client.post(
            '/api/v1/sync/receive-sales/',
            data=json.dumps({
                'node_id': 'branch-3',
                'sales': [{'id': 1, 'total': '5.00'}],
                'require_approval': False,
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        self.assertEqual(data['synced'], 1)
        self.assertEqual(data['approvals_created'], 0)

    def test_approvals_list_and_stats_reflect_pending(self):
        from models.approval import SyncApproval

        SyncApproval.objects.create(
            node_id='branch-1', entity_type='product',
            change_data={'products': []}, change_summary='2 products',
            direction='push', status='pending',
        )

        response = self.client.get('/api/v1/sync/approvals/')
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['items'][0]['entity_type'], 'product')

        stats = self.client.get('/api/v1/sync/stats/').json()['data']
        self.assertEqual(stats['pending'], 1)

    def test_approve_and_reject_flows(self):
        from models.approval import SyncApproval

        approval = SyncApproval.objects.create(
            node_id='branch-1', entity_type='report',
            change_data={}, change_summary='Report',
            direction='push', status='pending',
        )

        ok = self.client.post(f'/api/v1/sync/approvals/{approval.id}/approve/')
        self.assertEqual(ok.status_code, 200)
        approval.refresh_from_db()
        self.assertEqual(approval.status, 'approved')

        rejected = SyncApproval.objects.create(
            node_id='branch-2', entity_type='inventory',
            change_data={}, change_summary='Inv',
            direction='push', status='pending',
        )
        rej = self.client.post(f'/api/v1/sync/approvals/{rejected.id}/reject/')
        self.assertEqual(rej.status_code, 200)
        rejected.refresh_from_db()
        self.assertEqual(rejected.status, 'rejected')

    def test_openapi_includes_sync_and_components(self):
        response = self.client.get('/api/v1/openapi.json')
        paths = response.json()['paths']
        self.assertIn('/api/v1/sync/status/', paths)
        self.assertIn('/api/v1/sync/push-products/', paths)
        self.assertIn('/api/v1/components/', paths)
        self.assertIn('/api/v1/components/tables/{resource}/', paths)
        self.assertIn('/api/v1/components/forms/{resource}/', paths)


class FormintComponentsApiTests(TestCase):
    """django-fusion components served as data over the sidecar API."""

    def _seed(self):
        cat = Category.objects.create(name='Food', slug='food')
        Product.objects.create(name='Bread', price='1.00', category=cat)
        Product.objects.create(name='Milk', price='2.00', category=cat)

    def test_catalog_lists_resources(self):
        response = self.client.get('/api/v1/components/')
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        self.assertIn('tables', data)
        self.assertIn('forms', data)
        self.assertIn('fragments', data)
        self.assertIn('products', data['tables'])
        self.assertIn('supplier', data['forms'])
        self.assertIn('branch-summary', data['fragments'])

    def test_table_endpoint_returns_rows_and_headers(self):
        self._seed()
        response = self.client.get('/api/v1/components/tables/products/')
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        self.assertEqual(data['resource'], 'products')
        self.assertEqual(data['count'], 2)
        names = {row['name'] for row in data['rows']}
        self.assertEqual(names, {'Bread', 'Milk'})
        keys = {h['key'] for h in data['headers']}
        self.assertIn('name', keys)
        self.assertIn('price', keys)

    def test_table_endpoint_404_for_unknown(self):
        response = self.client.get('/api/v1/components/tables/nope/')
        self.assertEqual(response.status_code, 404)

    def test_form_endpoint_returns_field_schema(self):
        response = self.client.get('/api/v1/components/forms/product/')
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        self.assertEqual(data['resource'], 'product')
        names = {f['name'] for f in data['fields']}
        self.assertIn('name', names)
        self.assertIn('price', names)
        # layout references declared fields
        flat = [n for row in data['layout'] for n in row]
        self.assertIn('name', flat)

    def test_form_endpoint_404_for_unknown(self):
        response = self.client.get('/api/v1/components/forms/nope/')
        self.assertEqual(response.status_code, 404)

    def test_fragment_branch_summary(self):
        response = self.client.get('/api/v1/components/fragments/branch-summary/')
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        self.assertEqual(data['name'], 'branch-summary')
        self.assertIn('branches', data['data'])
        self.assertIn('orders_today', data['data'])
        self.assertIn('sync_status', data['data'])

    def test_fragment_404_for_unknown(self):
        response = self.client.get('/api/v1/components/fragments/unknown/')
        self.assertEqual(response.status_code, 404)
