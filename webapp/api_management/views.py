from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import uuid
from .auth import HMACAuthentication
from .throttles import TierRateThrottle
from .models import APIKey, Webhook
from companies.models import DimCompany, FactMLScores, FactCashFlow, FactBalanceSheet, FactProfitLoss, FactAnalysis, FactProsCons
from companies.serializers import DimCompanySerializer, FactMLScoresSerializer

class FullCompanyDataView(APIView):
    authentication_classes = [HMACAuthentication]
    throttle_classes = [TierRateThrottle]

    def get(self, request, symbol):
        try:
            company = DimCompany.objects.get(symbol=symbol)
            serializer = DimCompanySerializer(company)
            # Fetch other data logically
            return Response({"symbol": symbol, "data": serializer.data})
        except DimCompany.DoesNotExist:
            return Response({"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND)


class BulkFinancialsView(APIView):
    authentication_classes = [HMACAuthentication]
    throttle_classes = [TierRateThrottle]

    def get(self, request):
        symbols = request.query_params.get('symbols', '').split(',')
        companies = DimCompany.objects.filter(symbol__in=symbols)
        return Response({"count": companies.count(), "data": DimCompanySerializer(companies, many=True).data})

class ScreenerAPIView(APIView):
    authentication_classes = [HMACAuthentication]
    throttle_classes = [TierRateThrottle]

    def get(self, request):
        return Response({"results": []})

class ScoresAPIView(APIView):
    authentication_classes = [HMACAuthentication]
    throttle_classes = [TierRateThrottle]

    def get(self, request):
        scores = FactMLScores.objects.all()[:100]
        return Response({"scores": FactMLScoresSerializer(scores, many=True).data})

class APIKeyManageView(APIView):
    def post(self, request):
        # In a real scenario, this would be admin-only or a partner sign-up endpoint.
        key_id = uuid.uuid4()
        key_secret = str(uuid.uuid4())
        
        # Hash the secret before saving
        import hashlib
        key_secret_hash = hashlib.sha256(key_secret.encode('utf-8')).hexdigest()
        
        APIKey.objects.create(
            key_id=key_id,
            key_secret_hash=key_secret_hash,
            partner_name=request.data.get('partner_name', 'Default Partner'),
            tier='BASIC'
        )
        
        # Display secret ONCE!
        return Response({"key_id": str(key_id), "key_secret": key_secret})

class WebhookManageView(APIView):
    authentication_classes = [HMACAuthentication]
    throttle_classes = [TierRateThrottle]

    def post(self, request):
        url = request.data.get('url')
        event_type = request.data.get('event_type')
        api_key = request.user
        
        Webhook.objects.create(partner=api_key, url=url, event_type=event_type)
        return Response({"status": "subscribed", "url": url, "event_type": event_type})

