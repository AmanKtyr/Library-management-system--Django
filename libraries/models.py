from django.db import models
from django.conf import settings
from django.utils.text import slugify

class Library(models.Model):
    """Model representing a library branch."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    address = models.TextField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    opening_hours = models.TextField(blank=True, null=True)
    established_date = models.DateField(blank=True, null=True)
    image = models.ImageField(upload_to='library_images/', blank=True, null=True)

    # Library admin is a user with LIBRARY_ADMIN role
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='administered_libraries',
        limit_choices_to={'user_type': 'LIBRARY_ADMIN'}
    )

    # Staff members are users with STAFF role
    staff = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='staffed_libraries',
        limit_choices_to={'user_type': 'STAFF'},
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Library"
        verbose_name_plural = "Libraries"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
