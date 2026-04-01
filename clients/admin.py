from django.contrib import admin
from .models import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'country', 'city', 'created_at')
    list_filter = ('gender', 'country', 'created_at')
    search_fields = ('email', 'last_name', 'phone')
    ordering = ('-created_at',)
    
    # Très important pour la performance sur 1M de lignes
    list_per_page = 50 
    show_full_result_count = False # Évite un COUNT(*) lourd en SQL