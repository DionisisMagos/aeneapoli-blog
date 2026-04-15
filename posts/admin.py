import json
import time

from django.contrib import admin
from django import forms
from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django.urls import path, reverse

from cloudinary import config as cloudinary_config
from cloudinary.utils import api_sign_request

from .models import Post, Category, PostImage

class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 20
    max_num = 30
    fields = ('image', 'caption')
    can_delete = True

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'published', 'created')
    list_filter = ('published', 'categories', 'created')
    search_fields = ('title', 'excerpt', 'content')
    prepopulated_fields = {'slug': ('title',)}
    inlines = (PostImageInline,)  # Ξαναενεργοποίηση inline για τα 20 slots
    change_form_template = 'admin/posts/post/change_form.html'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<path:object_id>/upload-images/',
                self.admin_site.admin_view(self.upload_images_view),
                name='posts_post_upload_images',
            ),
            path(
                '<path:object_id>/upload-images/delete/',
                self.admin_site.admin_view(self.delete_image),
                name='posts_post_delete_image',
            ),
            path(
                '<path:object_id>/upload-signature/',
                self.admin_site.admin_view(self.upload_signature),
                name='posts_post_upload_signature',
            ),
        ]
        return custom_urls + urls

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['upload_images_url'] = reverse(
            'admin:posts_post_upload_images', args=[object_id]
        )
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def upload_images_view(self, request, object_id):
        post = get_object_or_404(Post, pk=object_id)

        if request.method == 'POST':
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return HttpResponseBadRequest('Invalid JSON payload')

            images = data.get('images', [])
            created = 0
            for image_data in images:
                public_id = image_data.get('public_id')
                if not public_id:
                    continue
                caption = image_data.get('caption', '')
                PostImage.objects.create(post=post, image=public_id, caption=caption)
                created += 1

            return JsonResponse({'ok': True, 'created': created})

        cloud_name = cloudinary_config().cloud_name
        return render(
            request,
            'admin/posts/post/upload_slots.html',
            {
                'post': post,
                'cloudinary_cloud_name': cloud_name,
                'signature_url': reverse(
                    'admin:posts_post_upload_signature', args=[object_id]
                ),
                'save_url': reverse(
                    'admin:posts_post_upload_images', args=[object_id]
                ),
                'post_admin_url': reverse('admin:posts_post_change', args=[object_id]),
            },
        )

    def delete_image(self, request, object_id):
        if request.method != 'POST':
            return JsonResponse({'ok': False, 'error': 'Only POST allowed'}, status=400)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'ok': False, 'error': 'Invalid JSON'}, status=400)

        image_id = data.get('image_id')
        if not image_id:
            return JsonResponse({'ok': False, 'error': 'No image_id provided'}, status=400)

        try:
            image = PostImage.objects.get(pk=image_id, post_id=object_id)
            image.delete()
            return JsonResponse({'ok': True, 'message': 'Image deleted'})
        except PostImage.DoesNotExist:
            return JsonResponse({'ok': False, 'error': 'Image not found'}, status=404)

    def upload_signature(self, request, object_id):
        if request.method != 'GET':
            return HttpResponseBadRequest('Only GET allowed')

        cloud_name = cloudinary_config().cloud_name
        api_key = cloudinary_config().api_key
        api_secret = cloudinary_config().api_secret

        if not cloud_name or not api_key or not api_secret:
            return JsonResponse(
                {
                    'ok': False,
                    'error': 'Cloudinary credentials are not configured.',
                },
                status=500,
            )

        timestamp = int(time.time())
        params = {'timestamp': timestamp, 'folder': 'aeneapoli/gallery'}
        signature = api_sign_request(params, api_secret)

        return JsonResponse(
            {
                'ok': True,
                'api_key': api_key,
                'timestamp': timestamp,
                'signature': signature,
            }
        )

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
