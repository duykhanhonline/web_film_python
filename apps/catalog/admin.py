from django.contrib import admin

from .models import Banner, Country, Episode, Genre, Movie, MyListItem, Season


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "order"]
    list_editable = ["order"]
    prepopulated_fields = {"slug": ["name"]}
    search_fields = ["name"]


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ["name"]}
    search_fields = ["name"]


class SeasonInline(admin.TabularInline):
    model = Season
    extra = 0
    show_change_link = True


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ["title", "original_title", "kind", "country", "year", "access", "view_count"]
    list_filter = ["kind", "access", "country", "genres", "age_rating", "year"]
    search_fields = ["title", "original_title", "search_text", "slug"]
    list_select_related = ["country"]
    filter_horizontal = ["genres"]
    readonly_fields = ["created_at", "updated_at"]
    inlines = [SeasonInline]
    fieldsets = [
        (None, {"fields": ["title", "original_title", "slug", "kind", "access", "synopsis"]}),
        ("Phân loại", {"fields": ["country", "genres", "year", "age_rating"]}),
        ("Âm thanh", {"fields": ["has_vietsub", "has_thuyet_minh", "has_long_tieng"]}),
        ("Hình ảnh và trailer", {"fields": ["poster", "backdrop", "trailer"]}),
        (
            "Thời lượng và lịch chiếu",
            {"fields": ["duration_minutes", "total_episodes", "schedule_text"]},
        ),
        ("Thống kê", {"fields": ["view_count", "created_at", "updated_at"]}),
    ]


class EpisodeInline(admin.TabularInline):
    model = Episode
    extra = 1
    fields = ["number", "title", "video", "duration", "intro_end", "published_at"]


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ["movie", "number", "title"]
    list_select_related = ["movie"]
    search_fields = ["movie__title", "movie__search_text"]
    autocomplete_fields = ["movie"]
    inlines = [EpisodeInline]


@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ["__str__", "season", "number", "duration", "published_at"]
    list_filter = ["published_at", "season__movie__kind"]
    list_select_related = ["season__movie"]
    search_fields = ["title", "season__movie__title", "season__movie__search_text"]
    autocomplete_fields = ["season"]
    date_hierarchy = "published_at"


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ["__str__", "order", "is_active", "is_sponsored", "starts_at", "ends_at"]
    list_editable = ["order", "is_active"]
    list_filter = ["is_active"]
    list_select_related = ["movie"]
    search_fields = ["title", "sponsor_name", "movie__title"]
    autocomplete_fields = ["movie"]

    @admin.display(boolean=True, description="Quảng cáo")
    def is_sponsored(self, obj: Banner) -> bool:
        return obj.is_sponsored


@admin.register(MyListItem)
class MyListItemAdmin(admin.ModelAdmin):
    list_display = ["user", "movie", "created_at"]
    list_select_related = ["user", "movie"]
    search_fields = ["user__username", "user__phone", "movie__title"]
    autocomplete_fields = ["user", "movie"]
