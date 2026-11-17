from django.db import models
import uuid

class APIKey(models.Model):
    TIER_CHOICES = (
        ('BASIC', 'Basic'),
        ('PRO', 'Pro'),
        ('ENTERPRISE', 'Enterprise'),
    )
    key_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key_secret_hash = models.CharField(max_length=255)
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default='BASIC')
    partner_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Webhook(models.Model):
    partner = models.ForeignKey(APIKey, on_delete=models.CASCADE)
    url = models.URLField()
    event_type = models.CharField(max_length=50) # 'score_updated', 'anomaly_flagged'
    is_active = models.BooleanField(default=True)
