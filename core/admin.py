from django.contrib import admin
from .models import ContactMessage, RecentActivity, Transaction  # Ensure you import the Transaction model

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at')
    search_fields = ('name', 'email')

@admin.register(RecentActivity)
class RecentActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity', 'timestamp')
    list_filter = ('user', 'timestamp')
    search_fields = ('activity',)
    ordering = ('-timestamp',)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'amount', 'transaction_id', 'status', 'created_at', 'updated_at')  # Display these fields
    list_filter = ('status', 'created_at')  # Enable filtering by status and created_at
    search_fields = ('transaction_id', 'phone_number')  # Enable search by transaction_id and phone_number
    ordering = ('-created_at',)  # Default ordering by created_at descending

