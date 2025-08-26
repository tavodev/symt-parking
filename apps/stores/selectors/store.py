from django.db.models import QuerySet

from ..models import Store


def store_get_all() -> QuerySet[Store]:
    """Obtiene todas las tiendas ordenadas por fecha de creación."""
    return Store.objects.all().order_by('-created_at')


def store_get_active() -> QuerySet[Store]:
    """Obtiene todas las tiendas activas ordenadas por fecha de creación."""
    return Store.objects.filter(is_active=True).order_by('-created_at')


def store_get_by_id(store_id: str) -> Store:
    """Obtiene una tienda por su ID."""
    return Store.objects.get(pk=store_id)


def store_search_by_name(name: str) -> QuerySet[Store]:
    """Busca tiendas por nombre (contiene)."""
    return Store.objects.filter(name__icontains=name).order_by('-created_at')