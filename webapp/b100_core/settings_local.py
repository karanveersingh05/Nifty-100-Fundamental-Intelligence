"""
Local (no-Docker) settings — SQLite + in-memory cache.
Import everything from the main settings, then override only the parts
that normally need Docker containers (PostgreSQL, Redis).
"""

from .settings import *          # noqa: F401,F403
import os

# ── Database: SQLite instead of PostgreSQL ──────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, '..', 'data', 'b100_local.sqlite3'),
    }
}

# ── Cache: in-process memory instead of Redis ───────────────────────
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'b100-local',
    }
}
