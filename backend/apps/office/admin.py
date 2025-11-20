from django.contrib import admin

from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'is_pinned', 'created_by', 'created_at', 'updated_at']
    list_filter = ['is_pinned', 'created_at']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']


