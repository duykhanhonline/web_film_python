from django.contrib import admin

from .models import Plan, Subscription


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ["name", "months", "price_vnd", "is_best_value", "is_active"]
    list_editable = ["is_active"]
    list_filter = ["is_active", "is_best_value"]
    search_fields = ["name"]


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ["user", "plan", "starts_at", "ends_at", "is_active"]
    list_filter = ["plan", "starts_at", "ends_at"]
    list_select_related = ["user", "plan"]
    search_fields = ["user__username", "user__phone", "user__email"]
    autocomplete_fields = ["user"]
    date_hierarchy = "starts_at"

    @admin.display(boolean=True, description="Đang hiệu lực")
    def is_active(self, obj: Subscription) -> bool:
        return obj.is_active
