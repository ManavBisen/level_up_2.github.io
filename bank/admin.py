from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'amount', 'timestamp', 'description')
    search_fields = ('sender__username', 'recipient__username', 'description')
    list_filter = ('timestamp',)
