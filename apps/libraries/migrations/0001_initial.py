# Generated by Django 5.2 on 2025-04-25 07:34

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Library',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(blank=True, max_length=120, unique=True)),
                ('address', models.TextField()),
                ('city', models.CharField(max_length=50)),
                ('state', models.CharField(max_length=50)),
                ('postal_code', models.CharField(max_length=20)),
                ('country', models.CharField(max_length=50)),
                ('phone', models.CharField(max_length=20)),
                ('email', models.EmailField(max_length=254)),
                ('website', models.URLField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('opening_hours', models.TextField(blank=True, null=True)),
                ('established_date', models.DateField(blank=True, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='library_images/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('admin', models.ForeignKey(limit_choices_to={'user_type': 'LIBRARY_ADMIN'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='administered_libraries', to=settings.AUTH_USER_MODEL)),
                ('staff', models.ManyToManyField(blank=True, limit_choices_to={'user_type': 'STAFF'}, related_name='staffed_libraries', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Library',
                'verbose_name_plural': 'Libraries',
                'ordering': ['name'],
            },
        ),
    ]
