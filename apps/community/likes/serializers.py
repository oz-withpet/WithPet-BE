from rest_framework import serializers

class LikeStatusOut(serializers.Serializer):
    is_liked = serializers.BooleanField()
    like_count = serializers.IntegerField()
