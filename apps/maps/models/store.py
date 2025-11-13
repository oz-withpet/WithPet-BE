from django.db import models
from apps.maps.managers.store import StoreManager


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = 'categories'
        verbose_name = '카테고리'
        verbose_name_plural = '카테고리목록'
        app_label = 'maps'

    def __str__(self):
        return self.name


class Store(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='stores')
    province = models.CharField(max_length=50, db_index=True)
    district = models.CharField(max_length=50, db_index=True)
    neighborhood = models.CharField(max_length=50, db_index=True)
    detail = models.CharField(max_length=200)
    full_address = models.CharField(max_length=500)
    latitude = models.DecimalField(max_digits=10, decimal_places=8)
    longitude = models.DecimalField(max_digits=11, decimal_places=8)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = StoreManager()

    class Meta:
        db_table = 'stores'
        verbose_name = '매장'
        verbose_name_plural = '매장목록'

    def __str__(self):
        return self.name