import time
import hmac
import hashlib
from rest_framework import authentication
from rest_framework import exceptions
from django.core.cache import cache
from .models import APIKey

class HMACAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        key_id = request.headers.get('X-API-Key-ID')
        timestamp = request.headers.get('X-Timestamp')
        signature = request.headers.get('X-Signature')
        nonce = request.headers.get('X-Nonce')

        if not all([key_id, timestamp, signature, nonce]):
            return None

        # Replay attack prevention: check nonce in cache
        if cache.get(f"nonce_{nonce}"):
            raise exceptions.AuthenticationFailed('Invalid nonce.')
        
        try:
            # Replay attack prevention: check timestamp
            current_time = int(time.time())
            if current_time - int(timestamp) > 300:
                raise exceptions.AuthenticationFailed('Request expired.')
        except ValueError:
            raise exceptions.AuthenticationFailed('Invalid timestamp.')

        try:
            api_key = APIKey.objects.get(key_id=key_id, is_active=True)
        except APIKey.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid API Key.')

        # Construct payload to hash
        # Assuming we sign method + url + timestamp + body(if exists, skipped for simplicity here)
        payload = f"{request.method}{request.get_full_path()}{timestamp}".encode('utf-8')
        secret = api_key.key_secret_hash.encode('utf-8')

        expected_signature = hmac.new(secret, payload, hashlib.sha256).hexdigest()

        if not hmac.compare_digest(expected_signature, signature):
            raise exceptions.AuthenticationFailed('Invalid signature.')

        # Store nonce
        cache.set(f"nonce_{nonce}", True, timeout=300)

        return (api_key, None)
