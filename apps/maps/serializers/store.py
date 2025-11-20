from rest_framework import serializers
from ..models import Store


class StoreSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    name = serializers.CharField(source='store_name', read_only=True)

    distance = serializers.FloatField(read_only=True, required=False)
    distance_text = serializers.SerializerMethodField()
    class Meta:
        model = Store
        fields = [
            'id',
            'name',
            'category',
            'address',
            'phone',
            'tags',
            'operating_information',
            'kakao_place_id',
            'distance',
            'distance_text',
        ]
    def get_category(self, obj):
        return {
            'code': obj.category_code,
            'name': obj.category_name
        }

    def get_address(self, obj):
        return {
            'province': obj.province,
            'district': obj.district,
            'neighborhood': obj.neighborhood,
            'detail': obj.detail_address,
            'full_address': obj.road_address or f"{obj.province} {obj.district} {obj.neighborhood} {obj.detail_address}",
            'latitude': float(obj.latitude),
            'longitude': float(obj.longitude),
        }

    def get_distance_text(self, obj):
        distance = getattr(obj, 'distance', None)
        if distance is None:
            return None

        if distance < 1:
            return f"{int(distance * 1000)}m"
        else:
            return f"{distance:.1f}km"


class StoreListSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='store_name')
    category_name = serializers.CharField()

    distance = serializers.FloatField(read_only=True)

    class Meta:
        model = Store
        fields = [
            'id',
            'name',
            'category_name',
            'province',
            'district',
            'phone',
            'latitude',
            'longitude',
            'distance',
        ]

    def get_category(self, obj):
        return {
            'code': obj.category_code,
            'name': obj.category_name
        }

class StoreNearbySerializer(serializers.ModelSerializer):
    #근처매장조회
    name = serializers.CharField(source='store_name', read_only=True)
    category = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()

    distance = serializers.FloatField(read_only=True)
    distance_text = serializers.SerializerMethodField()

    class Meta:
        model = Store
        fields = [
            'id',
            'name',
            'category',
            'address',
            'phone',
            'distance',
            'distance_text',
        ]

    def get_category(self, obj):
        return {
            'code': obj.category_code,
            'name': obj.category_name
        }

    def get_address(self, obj):
        return {
            'full_address': obj.road_address or f"{obj.province} {obj.district} {obj.neighborhood}",
            'latitude': float(obj.latitude),
            'longitude': float(obj.longitude),
        }

    def get_distance_text(self, obj):
        distance = getattr(obj, 'distance', None)
        if distance is None:
            return None

        if distance < 1:
            # 1km 미만은 m로 표시
            return f"{int(distance * 1000)}m"
        else:
            # 1km 이상은 km로 표시
            return f"{distance:.1f}km"