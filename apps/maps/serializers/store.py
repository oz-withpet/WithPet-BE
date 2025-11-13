from rest_framework import serializers
from apps.maps.models import Store, Category


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['id', 'name']


class StoreSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    address = serializers.SerializerMethodField()
    distance = serializers.FloatField(read_only=True, required=False)

    class Meta:
        model = Store
        fields = ['id', 'name', 'category', 'address', 'phone', 'distance']

    def get_address(self, obj):
        return {
            'province': obj.province,
            'district': obj.district,
            'neighborhood': obj.neighborhood,
            'detail': obj.detail,
            'full_address': obj.full_address,
            'latitude': obj.latitude,
            'longtitude': obj.longitude,
        }
    # 주의: JSON에서 longtitude로 표기하려면 source='longitude' 사용