from django.contrib import admin
from .models import Segment

@admin.register(Segment)
class SegmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_customer_count', 'created_by', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')

    def get_customer_count(self, obj):
        # Utilise la @property customer_count définie dans le modèle
        return obj.customer_count
    get_customer_count.short_description = "Nombre de clients"