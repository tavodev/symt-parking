from django.test import TestCase
from django.utils import timezone

from apps.stores.models import Store, CommercialUnit, UnitOccupancy
from apps.locations.models import Location
from apps.stores.selectors import (
    store_get_all,
    store_get_active,
    store_get_by_id,
    store_search_by_name,
    commercial_unit_get_all,
    commercial_unit_get_by_id,
    commercial_unit_get_by_location,
    commercial_unit_search,
    commercial_unit_get_available,
    unit_occupancy_get_all,
    unit_occupancy_get_by_id,
    unit_occupancy_get_active,
    unit_occupancy_get_by_store,
    unit_occupancy_get_by_unit,
    unit_occupancy_get_historical,
    get_current_store_for_unit,
)


class StoreSelectorsTestCase(TestCase):
    def setUp(self):
        self.store_active = Store.objects.create(name="Tienda Activa", is_active=True)
        self.store_inactive = Store.objects.create(name="Tienda Inactiva", is_active=False)
        self.store_test = Store.objects.create(name="Test Store", is_active=True)

    def test_store_get_all(self):
        stores = store_get_all()
        self.assertEqual(stores.count(), 3)
        # Verificar orden por created_at descendente
        self.assertEqual(stores.first(), self.store_test)

    def test_store_get_active(self):
        active_stores = store_get_active()
        self.assertEqual(active_stores.count(), 2)
        self.assertIn(self.store_active, active_stores)
        self.assertIn(self.store_test, active_stores)
        self.assertNotIn(self.store_inactive, active_stores)

    def test_store_get_by_id(self):
        store = store_get_by_id(self.store_active.pk)
        self.assertEqual(store, self.store_active)

    def test_store_search_by_name(self):
        results = store_search_by_name("Test")
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first(), self.store_test)
        
        results = store_search_by_name("Tienda")
        self.assertEqual(results.count(), 2)


class CommercialUnitSelectorsTestCase(TestCase):
    def setUp(self):
        self.location1 = Location.objects.create(
            name="Mall Centro", 
            address="Centro Ciudad",
            capacity=100,
            tolerance_minutes=15
        )
        self.location2 = Location.objects.create(
            name="Mall Norte", 
            address="Norte Ciudad",
            capacity=200,
            tolerance_minutes=20
        )
        
        self.unit1 = CommercialUnit.objects.create(location=self.location1, code="Local-101")
        self.unit2 = CommercialUnit.objects.create(location=self.location1, code="Local-102")
        self.unit3 = CommercialUnit.objects.create(location=self.location2, code="Kiosko-A")

        self.store = Store.objects.create(name="Test Store", is_active=True)

    def test_commercial_unit_get_all(self):
        units = commercial_unit_get_all()
        self.assertEqual(units.count(), 3)

    def test_commercial_unit_get_by_id(self):
        unit = commercial_unit_get_by_id(self.unit1.pk)
        self.assertEqual(unit, self.unit1)
        self.assertEqual(unit.location.name, "Mall Centro")

    def test_commercial_unit_get_by_location(self):
        units = commercial_unit_get_by_location(self.location1)
        self.assertEqual(units.count(), 2)
        self.assertIn(self.unit1, units)
        self.assertIn(self.unit2, units)
        self.assertNotIn(self.unit3, units)

    def test_commercial_unit_search(self):
        results = commercial_unit_search("Local")
        self.assertEqual(results.count(), 2)
        
        results = commercial_unit_search("Mall Centro")
        self.assertEqual(results.count(), 2)
        
        results = commercial_unit_search("Kiosko")
        self.assertEqual(results.count(), 1)

    def test_commercial_unit_get_available(self):
        # Inicialmente todas están disponibles
        available = commercial_unit_get_available()
        self.assertEqual(available.count(), 3)

        # Crear ocupación activa
        UnitOccupancy.objects.create(
            unit=self.unit1,
            store=self.store,
            start_date=timezone.now()
        )

        # Ahora unit1 no debe estar disponible
        available = commercial_unit_get_available()
        self.assertEqual(available.count(), 2)
        self.assertNotIn(self.unit1, available)


class UnitOccupancySelectorsTestCase(TestCase):
    def setUp(self):
        self.location = Location.objects.create(
            name="Test Location",
            address="Test Address", 
            capacity=50,
            tolerance_minutes=15
        )
        self.unit1 = CommercialUnit.objects.create(location=self.location, code="Unit-1")
        self.unit2 = CommercialUnit.objects.create(location=self.location, code="Unit-2")
        
        self.store1 = Store.objects.create(name="Store 1", is_active=True)
        self.store2 = Store.objects.create(name="Store 2", is_active=True)

        # Ocupación activa
        self.active_occupancy = UnitOccupancy.objects.create(
            unit=self.unit1,
            store=self.store1,
            start_date=timezone.now() - timezone.timedelta(days=30)
        )

        # Ocupación histórica
        self.historical_occupancy = UnitOccupancy.objects.create(
            unit=self.unit1,
            store=self.store2,
            start_date=timezone.now() - timezone.timedelta(days=100),
            end_date=timezone.now() - timezone.timedelta(days=50)
        )

    def test_unit_occupancy_get_all(self):
        occupancies = unit_occupancy_get_all()
        self.assertEqual(occupancies.count(), 2)

    def test_unit_occupancy_get_by_id(self):
        occupancy = unit_occupancy_get_by_id(self.active_occupancy.pk)
        self.assertEqual(occupancy, self.active_occupancy)

    def test_unit_occupancy_get_active(self):
        active = unit_occupancy_get_active()
        self.assertEqual(active.count(), 1)
        self.assertEqual(active.first(), self.active_occupancy)

    def test_unit_occupancy_get_by_store(self):
        store1_occupancies = unit_occupancy_get_by_store(self.store1)
        self.assertEqual(store1_occupancies.count(), 1)
        self.assertEqual(store1_occupancies.first(), self.active_occupancy)

        store2_occupancies = unit_occupancy_get_by_store(self.store2)
        self.assertEqual(store2_occupancies.count(), 1)
        self.assertEqual(store2_occupancies.first(), self.historical_occupancy)

    def test_unit_occupancy_get_by_unit(self):
        unit1_occupancies = unit_occupancy_get_by_unit(self.unit1)
        self.assertEqual(unit1_occupancies.count(), 2)

        unit2_occupancies = unit_occupancy_get_by_unit(self.unit2)
        self.assertEqual(unit2_occupancies.count(), 0)

    def test_unit_occupancy_get_historical(self):
        historical = unit_occupancy_get_historical()
        self.assertEqual(historical.count(), 1)
        self.assertEqual(historical.first(), self.historical_occupancy)

    def test_get_current_store_for_unit(self):
        # Unit1 debe tener store1 actual
        current_store = get_current_store_for_unit(self.unit1)
        self.assertEqual(current_store, self.store1)

        # Unit2 no debe tener store actual
        current_store = get_current_store_for_unit(self.unit2)
        self.assertIsNone(current_store)

        # Test con fecha específica (pasado cuando store2 ocupaba unit1)
        past_date = timezone.now() - timezone.timedelta(days=75)
        past_store = get_current_store_for_unit(self.unit1, at=past_date)
        self.assertEqual(past_store, self.store2)