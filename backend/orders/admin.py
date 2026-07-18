from django.contrib import admin

from .models import IdempotencyKey, Order, OrderItem, OutboxEvent


class OrderItemInline(admin.TabularInline):
    model = OrderItem


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "restaurant", "status", "total_cents", "created_at"]
    list_filter = ["status"]
    inlines = [OrderItemInline]


admin.site.register(IdempotencyKey)
admin.site.register(OutboxEvent)
