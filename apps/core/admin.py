from django.contrib import admin

from .models import SoftDeleteModel, TimeStampedModel

# Note: TimeStampedModel and SoftDeleteModel are abstract models
# They don't need to be registered in admin as they are not actual database tables
# They are used as base classes for other models

# If you want to create a custom admin for any specific functionality,
# you can add it here. For example, if you want to create a custom admin
# for managing soft-deleted records, you could do something like:


class SoftDeleteModelAdmin(admin.ModelAdmin):
    """
    Base admin class for models that inherit from SoftDeleteModel.
    Provides functionality to filter and manage soft-deleted records.
    """

    list_filter = ("is_deleted", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at", "deleted_at")

    def get_queryset(self, request):
        """Override to include soft-deleted records in admin."""
        return self.model.all_objects.get_queryset()

    def soft_delete(self, request, queryset):
        """Action to soft delete selected records."""
        count = queryset.count()
        for obj in queryset:
            obj.delete()  # This will call the custom delete method
        self.message_user(request, f"{count} records have been soft deleted.")

    soft_delete.short_description = "Soft delete selected records"

    def hard_delete(self, request, queryset):
        """Action to permanently delete selected records."""
        count = queryset.count()
        for obj in queryset:
            obj.hard_delete()  # This will call the hard_delete method
        self.message_user(request, f"{count} records have been permanently deleted.")

    hard_delete.short_description = "Permanently delete selected records"

    def restore(self, request, queryset):
        """Action to restore soft-deleted records."""
        count = queryset.count()
        for obj in queryset:
            obj.is_deleted = False
            obj.deleted_at = None
            obj.save()
        self.message_user(request, f"{count} records have been restored.")

    restore.short_description = "Restore selected records"

    actions = ["soft_delete", "hard_delete", "restore"]


# You can use this base class in other admin files by inheriting from it:
# class MyModelAdmin(SoftDeleteModelAdmin):
#     pass
