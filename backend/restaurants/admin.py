from django.contrib import admin

from .models import MenuItem, MenuSection, Restaurant


class MenuSectionInline(admin.TabularInline):
    model = MenuSection


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ["name", "city", "cuisine", "is_active"]
    list_filter = ["city", "cuisine"]
    search_fields = ["name"]
    inlines = [MenuSectionInline]


admin.site.register(MenuItem)
