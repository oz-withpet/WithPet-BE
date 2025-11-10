from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = "categories"
        verbose_name = "서비스 별 항목"
        verbose_name_plural = "서비스 별 항목 목록"

    def __str__(self):
        return self.name

class Store(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="store")
    province = models.CharField(max_length=50, db_index=True)
    district = models.CharField(max_length=50, db_index=True)
    neighborhood = models.CharField(max_length=50, db_index=True)
    detail_address = models.CharField(max_length=200, db_index=True)

    latitude = models.DecimalField(max_digits=10, decimal_places=8)
    longtitude = models.DecimalField(max_digits=11, decimal_places=8)

    phone = models.CharField(max_length=20, blank=True)
    #검색어 추가방법모색
    class Meta:
        db_table = "stores"
        verbose_name = "매장"
        verbose_name_plural = "매장 목록"
        indexes = [
            models.Index(fields=["province", "district", "neighborhood", "detail_address","category"]),
            models.Index(fields=["category", "province", "district", "neighborhood", "detail_address"]),
        ]
    def __str__(self):
        return self.name

