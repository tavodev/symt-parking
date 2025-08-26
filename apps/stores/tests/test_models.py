from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.utils import IntegrityError

from apps.stores.models import Store, CommercialUnit, UnitOccupancy
from apps.locations.models import Location


class StoreModelTestCase(TestCase):
    def test_store_creation(self):
        store = Store.objects.create(name="Test Store", is_active=True)
        self.assertEqual(store.name, "Test Store")
        self.assertTrue(store.is_active)
        self.assertIsNotNone(store.id)  # UUID debe ser generado
        self.assertIsNotNone(store.created_at)
        self.assertIsNotNone(store.updated_at)

    def test_store_str_representation(self):
        store = Store.objects.create(name="Test Store", is_active=True)
        self.assertEqual(str(store), "Test Store")

    def test_store_default_active_state(self):
        store = Store.objects.create(name="Default Store")
        self.assertTrue(store.is_active)  # Default debe ser True

    def test_store_inactive(self):
        store = Store.objects.create(name="Inactive Store", is_active=False)
        self.assertFalse(store.is_active)


class CommercialUnitModelTestCase(TestCase):
    def setUp(self):
        self.location = Location.objects.create(
            name="Test Location",
            address="Test Address",
            capacity=100,
            tolerance_minutes=15
        )

    def test_commercial_unit_creation(self):
        unit = CommercialUnit.objects.create(
            location=self.location,
            code="Unit-101"
        )
        self.assertEqual(unit.code, "Unit-101")
        self.assertEqual(unit.location, self.location)
        self.assertIsNotNone(unit.id)  # UUID debe ser generado
        self.assertIsNotNone(unit.created_at)

    def test_commercial_unit_str_representation(self):
        unit = CommercialUnit.objects.create(
            location=self.location,
            code="Unit-101"
        )
        expected = f"{self.location.name} - Unit-101"
        self.assertEqual(str(unit), expected)

    def test_commercial_unit_unique_together_constraint(self):
        # Crear primera unidad
        CommercialUnit.objects.create(
            location=self.location,
            code="Unit-101"
        )
        
        # Intentar crear otra unidad con el mismo código en la misma ubicación
        with self.assertRaises(IntegrityError):
            CommercialUnit.objects.create(
                location=self.location,
                code="Unit-101"
            )

    def test_commercial_unit_same_code_different_location(self):
        location2 = Location.objects.create(
            name="Another Location",
            address="Another Address",
            capacity=50,
            tolerance_minutes=10
        )
        
        # Crear unidades con el mismo código en diferentes ubicaciones (debe funcionar)
        unit1 = CommercialUnit.objects.create(
            location=self.location,
            code="Unit-101"
        )
        unit2 = CommercialUnit.objects.create(
            location=location2,
            code="Unit-101"
        )
        
        self.assertNotEqual(unit1.id, unit2.id)
        self.assertEqual(unit1.code, unit2.code)


class UnitOccupancyModelTestCase(TestCase):
    def setUp(self):
        self.location = Location.objects.create(
            name="Test Location",
            address="Test Address",
            capacity=100,
            tolerance_minutes=15
        )
        self.unit = CommercialUnit.objects.create(
            location=self.location,
            code="Unit-101"
        )
        self.store = Store.objects.create(name="Test Store", is_active=True)

    def test_unit_occupancy_creation(self):
        start_date = timezone.now()
        occupancy = UnitOccupancy.objects.create(
            unit=self.unit,
            store=self.store,
            start_date=start_date
        )
        
        self.assertEqual(occupancy.unit, self.unit)
        self.assertEqual(occupancy.store, self.store)
        self.assertEqual(occupancy.start_date, start_date)
        self.assertIsNone(occupancy.end_date)  # Default None para ocupación vigente

    def test_unit_occupancy_str_representation(self):
        start_date = timezone.now()
        occupancy = UnitOccupancy.objects.create(
            unit=self.unit,
            store=self.store,
            start_date=start_date
        )
        
        expected = f"{self.unit} -> {self.store} ({start_date.isoformat()} - present)"
        self.assertEqual(str(occupancy), expected)

    def test_unit_occupancy_str_with_end_date(self):
        start_date = timezone.now()
        end_date = start_date + timezone.timedelta(days=30)
        
        occupancy = UnitOccupancy.objects.create(
            unit=self.unit,
            store=self.store,
            start_date=start_date,
            end_date=end_date
        )
        
        expected = f"{self.unit} -> {self.store} ({start_date.isoformat()} - {end_date.isoformat()})"
        self.assertEqual(str(occupancy), expected)

    def test_is_active_at_method(self):
        start_date = timezone.now() - timezone.timedelta(days=10)
        end_date = timezone.now() + timezone.timedelta(days=10)
        
        # Ocupación con fecha de fin
        occupancy = UnitOccupancy.objects.create(
            unit=self.unit,
            store=self.store,
            start_date=start_date,
            end_date=end_date
        )
        
        # Debe estar activa ahora
        self.assertTrue(occupancy.is_active_at())
        
        # No debe estar activa en el futuro
        future_date = timezone.now() + timezone.timedelta(days=20)
        self.assertFalse(occupancy.is_active_at(future_date))
        
        # No debe estar activa en el pasado
        past_date = timezone.now() - timezone.timedelta(days=20)
        self.assertFalse(occupancy.is_active_at(past_date))

    def test_is_active_at_method_open_ended(self):
        start_date = timezone.now() - timezone.timedelta(days=10)
        
        # Ocupación sin fecha de fin (vigente)
        occupancy = UnitOccupancy.objects.create(
            unit=self.unit,
            store=self.store,
            start_date=start_date
        )
        
        # Debe estar activa ahora
        self.assertTrue(occupancy.is_active_at())
        
        # Debe estar activa en el futuro
        future_date = timezone.now() + timezone.timedelta(days=20)
        self.assertTrue(occupancy.is_active_at(future_date))
        
        # No debe estar activa antes del inicio
        past_date = timezone.now() - timezone.timedelta(days=20)
        self.assertFalse(occupancy.is_active_at(past_date))

    def test_clean_method_end_date_validation(self):
        start_date = timezone.now()
        # end_date antes que start_date debe fallar
        end_date = start_date - timezone.timedelta(days=1)
        
        occupancy = UnitOccupancy(
            unit=self.unit,
            store=self.store,
            start_date=start_date,
            end_date=end_date
        )
        
        with self.assertRaises(ValidationError) as cm:
            occupancy.clean()
        
        self.assertIn('end_date', cm.exception.error_dict)

    def test_clean_method_overlap_validation(self):
        start_date = timezone.now()
        
        # Crear primera ocupación
        UnitOccupancy.objects.create(
            unit=self.unit,
            store=self.store,
            start_date=start_date
        )
        
        # Intentar crear ocupación que se solape
        overlapping_occupancy = UnitOccupancy(
            unit=self.unit,
            store=self.store,
            start_date=start_date + timezone.timedelta(days=5)  # Se solapa con la vigente
        )
        
        with self.assertRaises(ValidationError) as cm:
            overlapping_occupancy.clean()
        
        self.assertIn("se solapa", str(cm.exception))

    def test_clean_method_no_overlap_different_units(self):
        # Crear otra unidad
        unit2 = CommercialUnit.objects.create(
            location=self.location,
            code="Unit-102"
        )
        
        start_date = timezone.now()
        
        # Crear ocupación en primera unidad
        UnitOccupancy.objects.create(
            unit=self.unit,
            store=self.store,
            start_date=start_date
        )
        
        # Crear ocupación en segunda unidad (no debe haber problema)
        occupancy2 = UnitOccupancy(
            unit=unit2,
            store=self.store,
            start_date=start_date
        )
        
        try:
            occupancy2.clean()  # No debe lanzar excepción
        except ValidationError:
            self.fail("clean() raised ValidationError unexpectedly!")

    def test_clean_method_sequential_occupancies(self):
        start_date1 = timezone.now()
        end_date1 = start_date1 + timezone.timedelta(days=30)
        start_date2 = end_date1 + timezone.timedelta(days=1)
        
        # Crear primera ocupación (finalizada)
        UnitOccupancy.objects.create(
            unit=self.unit,
            store=self.store,
            start_date=start_date1,
            end_date=end_date1
        )
        
        # Crear segunda ocupación secuencial (no debe haber problema)
        occupancy2 = UnitOccupancy(
            unit=self.unit,
            store=self.store,
            start_date=start_date2
        )
        
        try:
            occupancy2.clean()  # No debe lanzar excepción
        except ValidationError:
            self.fail("clean() raised ValidationError unexpectedly!")