from django.contrib import admin
from .models import Campaign, EmailLog

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'created_by', 'created_at')
    list_filter = ('status', 'created_at')
    filter_horizontal = ('segments',) # Interface facile pour choisir les segments
    search_fields = ('name', 'subject')

@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'client', 'status', 'sent_at')
    list_filter = ('status',)
    raw_id_fields = ('client',) # Indispensable pour 1M de clients