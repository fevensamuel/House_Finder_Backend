from rest_framework import serializers
from .models import RefundRequest

class RefundRequestSerializer(serializers.ModelSerializer):
    refund_amount = serializers.SerializerMethodField()
    is_within_window = serializers.SerializerMethodField()

    class Meta:
        model = RefundRequest
        fields = '__all__'

    def get_refund_amount(self, obj):
        return obj.refund_amount

    def get_is_within_window(self, obj):
        return obj.is_within_window