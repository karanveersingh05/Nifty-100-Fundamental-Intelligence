from rest_framework import serializers
from .models import DimCompany, FactMLScores, FactCashFlow

class FactCashFlowSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactCashFlow
        fields = '__all__'

class FactMLScoresSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactMLScores
        fields = '__all__'

class DimCompanySerializer(serializers.ModelSerializer):
    latest_health_label = serializers.SerializerMethodField()

    class Meta:
        model = DimCompany
        fields = ['symbol', 'company_name', 'sector', 'sub_sector', 'latest_health_label']

    def get_latest_health_label(self, obj):
        try:
            latest_score = FactMLScores.objects.filter(symbol=obj).order_by('-computed_at').first()
            return latest_score.health_label if latest_score else None
        except Exception:
            return None
