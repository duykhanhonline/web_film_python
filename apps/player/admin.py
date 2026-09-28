from django.contrib import admin

from .models import WatchProgress


@admin.register(WatchProgress)
class WatchProgressAdmin(admin.ModelAdmin):
    list_display = ["user", "episode", "position_seconds", "updated_at"]
    list_filter = ["updated_at"]
    list_select_related = ["user", "episode__season__movie"]
    search_fields = ["user__username", "user__phone", "episode__season__movie__title"]
    autocomplete_fields = ["user", "episode"]
