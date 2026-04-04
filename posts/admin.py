from django.contrib import admin
from .models import Post, Category, PostImage

class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 1
    max_num = 30
    fields = ('image', 'caption')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'published', 'created')
    list_filter = ('published', 'categories', 'created')
    search_fields = ('title', 'excerpt', 'content')
    prepopulated_fields = {'slug': ('title',)}
    inlines = (PostImageInline,)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
