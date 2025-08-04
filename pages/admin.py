# admin.py
from django.contrib import admin
from .models import (
    MembershipApplication,
    Event,
)

# admin.py (Optional: for managing applications in Django admin)
from django.contrib import admin
from .models import MembershipApplication

@admin.register(MembershipApplication)
class MembershipApplicationAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'region', 'status', 'created_at']
    list_filter = ['status', 'region', 'education', 'gender', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'date_of_birth', 'gender', 'id_number')
        }),
        ('Background', {
            'fields': ('current_address', 'region', 'district', 'education', 'occupation')
        }),
        ('Experience & Skills', {
            'fields': ('work_experience', 'skills', 'languages')
        }),
        ('Motivation', {
            'fields': ('why_join', 'contribution', 'expectations', 'referral')
        }),
        ('Status', {
            'fields': ('agree_terms', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(self.readonly_fields)
        if obj:  # Editing existing object
            readonly_fields.extend(['email', 'id_number'])  # Make unique fields readonly when editing
        return readonly_fields

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'description', 'created_at') # Use the correct field name here
    ordering = ('created_at',)
    list_filter = ('event_type', 'status', 'is_online')
    search_fields = ('title', 'description', 'location')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-date',)


