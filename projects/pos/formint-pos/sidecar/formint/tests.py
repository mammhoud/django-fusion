import json

from django.contrib.auth import get_user_model
from django.test import TestCase

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
        response = self.client.get('/api/v1/health')

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
        response = self.client.get('/api/v1/stats')

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
        self.assertIn('/api/v1/health', paths)
        self.assertIn('/api/v1/stats', paths)

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
        response = self.client.get('/api/v1/render-mode')
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn('status', body)
        self.assertIn('data', body)
        self.assertIs(body['data']['fusion_render_first'], True)
        self.assertEqual(body['data']['mode'], 'fusion-render')

    def test_api_navigation_returns_formint_site_items(self):
        response = self.client.get('/api/v1/navigation')
        self.assertEqual(response.status_code, 200)
        items = response.json()['data']['nav_items']
        labels = [item['label'] for item in items]
        self.assertIn('Home', labels)
        self.assertIn('Data', labels)
        # show_in_nav is filtered out of the payload
        self.assertTrue(all('show_in_nav' not in item for item in items))

    def test_fusion_navigation_fragment_path(self):
        response = self.client.get('/fusion/navigation/')
        self.assertEqual(response.status_code, 200)
        items = response.json()['nav_items']
        self.assertEqual([item['label'] for item in items], ['Home', 'Data', 'Admin'])

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
