from .models import KhojTheSearch
from rest_framework import serializers

class KhojAndSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = KhojTheSearch
        fields = ['int_list', 'created_at']

