from django.contrib import admin

from .models import AdSlot, Creative, SponsoredRow


@admin.register(AdSlot)
class AdSlotAdmin(admin.ModelAdmin):
    list_display = ["code", "__str__"]
    search_fields = ["code"]


@admin.register(Creative)
class CreativeAdmin(admin.ModelAdmin):
    list_display = ["name", "slot", "is_active", "starts_at", "ends_at"]
    list_editable = ["is_active"]
    list_filter = ["slot", "is_active"]
    list_select_related = ["slot"]
    search_fields = ["name", "link", "alt_text"]


@admin.register(SponsoredRow)
class SponsoredRowAdmin(admin.ModelAdmin):
    list_display = ["title", "sponsor_name", "is_active", "starts_at", "ends_at"]
    list_editable = ["is_active"]
    list_filter = ["is_active"]
    search_fields = ["title", "sponsor_name"]
    filter_horizontal = ["movies"]
