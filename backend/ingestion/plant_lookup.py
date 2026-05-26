from tenants.models import Plant

_cache: dict[str, str] = {}


def get_plant_label(werks: str, client_id=None) -> str:
    code = (werks or "").strip()
    if not code:
        return ""
    key = f"{client_id}:{code}"
    if key in _cache:
        return _cache[key]
    qs = Plant.objects.filter(code=code)
    if client_id:
        plant = qs.filter(client_id=client_id).first() or qs.filter(client__isnull=True).first()
    else:
        plant = qs.first()
    label = f"{code} ({plant.name})" if plant else code
    _cache[key] = label
    return label


def clear_plant_cache():
    _cache.clear()
