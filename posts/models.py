# posts/models.py
from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from io import BytesIO
from django.core.files.base import ContentFile
from PIL import Image
from pathlib import Path

def compress_image(uploaded_file, max_size=1600, quality=85):
    """
    Μικραίνει & συμπιέζει την εικόνα σε JPEG.
    Επιστρέφει ContentFile έτοιμο για αποθήκευση.
    """
    img = Image.open(uploaded_file)
    # Μετατροπή σε RGB (για JPEG)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    # Μείωση μεγέθους, διατηρώντας αναλογία
    img.thumbnail((max_size, max_size), Image.LANCZOS)
    buf = BytesIO()
    img.save(buf, format="JPEG", optimize=True, quality=quality)
    buf.seek(0)
    return ContentFile(buf.getvalue())

class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    class Meta:
        verbose_name = 'Κατηγορία'
        verbose_name_plural = 'Κατηγορίες'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Post(models.Model):
    title = models.CharField('Τίτλος', max_length=160)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    excerpt = models.CharField('Περίληψη', max_length=240, blank=True)
    content = models.TextField('Κείμενο')
    cover = models.ImageField('Εξώφυλλο', upload_to='covers/', blank=True, null=True)
    categories = models.ManyToManyField(Category, related_name='posts', blank=True)
    published = models.BooleanField('Δημοσιευμένο', default=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']
        verbose_name = 'Ανάρτηση'
        verbose_name_plural = 'Αναρτήσεις'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        # Αν υπάρχει νέο cover, συμπίεσέ το πριν το ανεβάσουμε
        if self.cover and hasattr(self.cover, "file"):
            try:
                compressed = compress_image(self.cover.file, max_size=1600, quality=85)
                stem = Path(self.cover.name).stem or "cover"
                # αποθηκεύουμε ως .jpg για σιγουριά
                self.cover.save(f"{stem}.jpg", compressed, save=False)
            except Exception:
                # αν κάτι πάει στραβά, προχώρησε χωρίς συμπίεση
                pass
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('posts:detail', kwargs={'slug': self.slug})

    def get_cover_url(self):
        try:
            if self.cover and getattr(self.cover, "name", ""):
                return self.cover.url
        except Exception:
            return None
        return None
