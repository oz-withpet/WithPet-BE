from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import ArrayField


class Store(models.Model):
    store_name = models.CharField(max_length=200)
    category_code = models.CharField(max_length=50, db_index=True)
    category_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    province_code = models.IntegerField(null=True, blank=True, db_index=True)
    province = models.CharField(max_length=50, db_index=True)
    district_code = models.IntegerField(null=True, blank=True, db_index=True)
    district = models.CharField(max_length=50, db_index=True)
    neighborhood_code = models.IntegerField(null=True, blank=True, db_index=True)
    neighborhood = models.CharField(max_length=50, db_index=True)
    detail_address = models.CharField(max_length=200)
    road_address = models.CharField(max_length=500)
    latitude = models.DecimalField(max_digits=10, decimal_places=8)
    longitude = models.DecimalField(max_digits=11, decimal_places=8)
    tags = ArrayField(
        models.CharField(max_length=50),
        blank=True,
        default=list
    )
    like_count = models.IntegerField(default=0)
    kakao_place_id = models.CharField(max_length=50, unique=True)
    operating_information = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    last_seen_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        db_table = 'pet_stores'
        app_label = 'maps'
        managed = False
        verbose_name = '매장'
        verbose_name_plural = '매장목록'

    def __str__(self):
        return self.store_name

    @property
    def name(self):
        return self.store_name

    @property
    def full_address_property(self):
        return self.road_address or f"{self.province} {self.district} {self.neighborhood} {self.detail_address}"

    @property
    def detail(self):
        return self.detail_address

    @property
    def category_obj(self):
        return {
            'code': self.category_code,
            'name': self.category_name
        }


class LikePlace(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='liked_places'
    )
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'like_places'
        app_label = 'maps'
        unique_together = ['user', 'store']
        verbose_name = '찜한 장소'
        verbose_name_plural = '찜한 장소들'

    def __str__(self):
        return f"{self.user.username} - {self.store.name}"