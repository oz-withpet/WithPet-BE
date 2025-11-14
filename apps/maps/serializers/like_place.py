from rest_framework import serializers
from ..models.store import LikePlace
from .store import StoreSerializer


class LikePlaceSerializer(serializers.ModelSerializer):
    store = StoreSerializer(read_only=True)
    store_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = LikePlace
        fields = ['id', 'store', 'store_id', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)