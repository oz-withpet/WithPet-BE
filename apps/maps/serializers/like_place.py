from rest_framework import serializers
from ..models.store import LikePlace
from ..serializers.store import StoreSerializer


class LikePlaceSerializer(serializers.ModelSerializer):
    store = StoreSerializer(read_only=True)

    class Meta:
        model = LikePlace
        fields = ['id', 'store', 'created_at']