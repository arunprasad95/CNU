from django.contrib import admin

from .models import Restaurant, Review, Category ,Image


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'neighbourhood',
                    'address', 'city', 'state',
                    'postal_code', 'latitude', 'longitude',
                    'stars', '_categories', 'review_count',
                    'is_open', 'deleted','images_added']

    list_filter = ['city', 'is_open', 'categories']

    def delete_queryset(self, request, queryset):
        for item in queryset:
            item.delete()


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'count_businesses']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'restaurant', 'date', 'stars', 'text']

    list_filter = ['restaurant']

    def get_readonly_fields(self, request, obj=None):
        if (obj):
            return ['id', 'restaurant', 'date', 'stars', 'text']
        else:
            return []

    def has_delete_permission(self, request, obj=None):
        return False
@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['id' ,'restaurant','url']