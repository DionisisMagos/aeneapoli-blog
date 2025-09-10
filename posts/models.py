from django.db import models
from django.utils.text import slugify
from django.urls import reverse

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
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('posts:detail', kwargs={'slug': self.slug})
    
    def get_cover_url(self):
        """
        Επιστρέφει ασφαλώς το URL του cover ή None αν δεν υπάρχει/δεν είναι προσβάσιμο.
        Αποφεύγει ValueError όταν λείπει το αρχείο.
        """
        try:
            if self.cover and getattr(self.cover, "name", ""):
                return self.cover.url
        except Exception:
            return None
        return None
