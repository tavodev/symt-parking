from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.stores.models import Store, CommercialUnit, UnitOccupancy
from apps.locations.models import Location

User = get_user_model()


class BaseViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(email='test@example.com', password='testpass123')
        
        self.location = Location.objects.create(
            name="Test Location",
            address="Test Address",
            capacity=100,
            tolerance_minutes=15
        )


class StoreViewsTestCase(BaseViewTestCase):
    def setUp(self):
        super().setUp()
        self.store = Store.objects.create(name="Test Store", is_active=True)

    def test_store_list_view(self):
        url = reverse('dashboard:stores:list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Store")

    def test_store_create_view_get(self):
        url = reverse('dashboard:stores:create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Crear Tienda")

    def test_store_create_view_post(self):
        url = reverse('dashboard:stores:create')
        data = {
            'name': 'Nueva Tienda',
            'is_active': True
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        self.assertTrue(Store.objects.filter(name='Nueva Tienda').exists())

    def test_store_detail_view(self):
        url = reverse('dashboard:stores:detail', kwargs={'pk': self.store.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Store")

    def test_store_update_view_get(self):
        url = reverse('dashboard:stores:update', kwargs={'pk': self.store.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Store")

    def test_store_update_view_post(self):
        url = reverse('dashboard:stores:update', kwargs={'pk': self.store.pk})
        data = {
            'name': 'Tienda Actualizada',
            'is_active': False
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.store.refresh_from_db()
        self.assertEqual(self.store.name, 'Tienda Actualizada')
        self.assertFalse(self.store.is_active)

    def test_store_delete_view_get(self):
        url = reverse('dashboard:stores:delete', kwargs={'pk': self.store.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Store")

    def test_store_delete_view_post(self):
        url = reverse('dashboard:stores:delete', kwargs={'pk': self.store.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Store.objects.filter(pk=self.store.pk).exists())


class CommercialUnitViewsTestCase(BaseViewTestCase):
    def setUp(self):
        super().setUp()
        self.unit = CommercialUnit.objects.create(
            location=self.location,
            code="Test-Unit"
        )

    def test_commercial_unit_list_view(self):
        url = reverse('dashboard:commercial_units:list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test-Unit")

    def test_commercial_unit_create_view_get(self):
        url = reverse('dashboard:commercial_units:create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Crear Unidad")

    def test_commercial_unit_create_view_post(self):
        url = reverse('dashboard:commercial_units:create')
        data = {
            'location': self.location.pk,
            'code': 'Nueva-Unidad'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(CommercialUnit.objects.filter(code='Nueva-Unidad').exists())

    def test_commercial_unit_detail_view(self):
        url = reverse('dashboard:commercial_units:detail', kwargs={'pk': self.unit.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test-Unit")

    def test_commercial_unit_update_view(self):
        url = reverse('dashboard:commercial_units:update', kwargs={'pk': self.unit.pk})
        data = {
            'location': self.location.pk,
            'code': 'Unidad-Actualizada'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.unit.refresh_from_db()
        self.assertEqual(self.unit.code, 'Unidad-Actualizada')

    def test_commercial_unit_delete_view(self):
        url = reverse('dashboard:commercial_units:delete', kwargs={'pk': self.unit.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(CommercialUnit.objects.filter(pk=self.unit.pk).exists())


class UnitOccupancyViewsTestCase(BaseViewTestCase):
    def setUp(self):
        super().setUp()
        self.store = Store.objects.create(name="Test Store", is_active=True)
        self.unit = CommercialUnit.objects.create(
            location=self.location,
            code="Test-Unit"
        )
        self.occupancy = UnitOccupancy.objects.create(
            unit=self.unit,
            store=self.store,
            start_date=timezone.now()
        )

    def test_unit_occupancy_list_view(self):
        url = reverse('dashboard:unit_occupancies:list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Store")
        self.assertContains(response, "Test-Unit")

    def test_unit_occupancy_create_view_get(self):
        url = reverse('dashboard:unit_occupancies:create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Crear Ocupación")

    def test_unit_occupancy_create_view_post_valid(self):
        # Crear otra unidad para la nueva ocupación
        unit2 = CommercialUnit.objects.create(
            location=self.location,
            code="Unit-2"
        )
        
        url = reverse('dashboard:unit_occupancies:create')
        start_date = timezone.now()
        data = {
            'unit': unit2.pk,
            'store': self.store.pk,
            'start_date': start_date.strftime('%Y-%m-%dT%H:%M'),
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            UnitOccupancy.objects.filter(unit=unit2, store=self.store).exists()
        )

    def test_unit_occupancy_create_view_post_overlap_validation(self):
        # Intentar crear ocupación que se solape con la existente
        url = reverse('dashboard:unit_occupancies:create')
        start_date = timezone.now()
        data = {
            'unit': self.unit.pk,  # Misma unidad que ya está ocupada
            'store': self.store.pk,
            'start_date': start_date.strftime('%Y-%m-%dT%H:%M'),
        }
        response = self.client.post(url, data)
        # Debería fallar la validación y mostrar el formulario con errores
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "se solapa")

    def test_unit_occupancy_detail_view(self):
        url = reverse('dashboard:unit_occupancies:detail', kwargs={'pk': self.occupancy.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Store")
        self.assertContains(response, "Test-Unit")

    def test_unit_occupancy_update_view(self):
        url = reverse('dashboard:unit_occupancies:update', kwargs={'pk': self.occupancy.pk})
        end_date = timezone.now() + timezone.timedelta(days=1)
        data = {
            'unit': self.unit.pk,
            'store': self.store.pk,
            'start_date': self.occupancy.start_date.strftime('%Y-%m-%dT%H:%M'),
            'end_date': end_date.strftime('%Y-%m-%dT%H:%M'),
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.occupancy.refresh_from_db()
        self.assertIsNotNone(self.occupancy.end_date)

    def test_unit_occupancy_delete_view(self):
        url = reverse('dashboard:unit_occupancies:delete', kwargs={'pk': self.occupancy.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(UnitOccupancy.objects.filter(pk=self.occupancy.pk).exists())


class ViewsRequireLoginTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_store_views_require_login(self):
        urls = [
            reverse('dashboard:stores:list'),
            reverse('dashboard:stores:create'),
        ]
        
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_commercial_unit_views_require_login(self):
        urls = [
            reverse('dashboard:commercial_units:list'),
            reverse('dashboard:commercial_units:create'),
        ]
        
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_unit_occupancy_views_require_login(self):
        urls = [
            reverse('dashboard:unit_occupancies:list'),
            reverse('dashboard:unit_occupancies:create'),
        ]
        
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)  # Redirect to login