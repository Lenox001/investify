from django.contrib import admin
from .models import ContactMessage, RecentActivity, Investment, Transaction

class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at')
    search_fields = ['name', 'email']
    list_filter = ('created_at',)

class RecentActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity', 'timestamp')
    search_fields = ['activity']
    list_filter = ('timestamp',)

class InvestmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'maturity_date', 'progress')
    search_fields = ['user__username', 'amount']
    list_filter = ('maturity_date',)

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user', 'amount', 'status', 'created_at')
    search_fields = ['transaction_id', 'user__username']
    list_filter = ('status', 'created_at')

admin.site.register(ContactMessage, ContactMessageAdmin)
admin.site.register(RecentActivity, RecentActivityAdmin)
admin.site.register(Investment, InvestmentAdmin)
admin.site.register(Transaction, TransactionAdmin)
