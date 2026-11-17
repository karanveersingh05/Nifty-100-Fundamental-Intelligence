from rest_framework.throttling import BaseThrottle
from django.core.cache import cache
import time

class TierRateThrottle(BaseThrottle):
    def allow_request(self, request, view):
        # We need the api_key object from auth
        if not request.user:
            return True # Not authenticated via our custom auth? Let other layers handle or deny.

        api_key = request.user # It's stored as user tuple in BaseAuthentication
        
        limits = {
            'BASIC': {'min': 10, 'hour': 100, 'day': 500},
            'PRO': {'min': 60, 'hour': 1000, 'day': 10000},
            'ENTERPRISE': {'min': 300, 'hour': 10000, 'day': 100000},
        }

        tier = api_key.tier
        limit_min = limits.get(tier, limits['BASIC'])['min']
        
        # We just implement per-minute for demo, proper would do all 3
        ident = api_key.key_id
        cache_key = f"throttle_{ident}_min"
        
        history = cache.get(cache_key, [])
        now = time.time()
        
        # Drop requests older than 60 seconds
        history = [timestamp for timestamp in history if timestamp > now - 60]
        
        if len(history) >= limit_min:
            return False
            
        history.insert(0, now)
        cache.set(cache_key, history, 60)
        return True

    def wait(self):
        return 60
