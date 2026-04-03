#!/usr/bin/env python3
"""测试CSRF配置"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'packages', 'harness'))

from app.gateway.security.config import SecurityConfig

config = SecurityConfig.from_env()
print("CSRF exempt paths:")
for path in config.csrf_exempt_paths:
    print(f"  - {path}")

print(f"\nCSRF enabled: {config.csrf_enabled}")
