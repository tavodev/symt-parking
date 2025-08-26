from ..models import Location

def locations_get_all():
    return Location.objects.all().order_by('-created_at')