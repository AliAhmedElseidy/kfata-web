"""Opt-in loopback preview. Never imported by production settings."""
from config.settings.dev import *

ROOT_URLCONF = 'tools.scene.preview_urls'
SITE_INDEXABLE = False
