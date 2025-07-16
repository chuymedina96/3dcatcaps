from rest_framework import serializers
from .models import CapOrder

class CapOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = CapOrder
        fields = '__all__'
