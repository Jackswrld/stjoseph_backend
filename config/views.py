from django.http import JsonResponse


def health(request):
    """Cheap "I am awake" check for the uptime monitor.

    It must never touch the database, so Neon is free to sleep.
    """
    return JsonResponse({"status": "ok"})