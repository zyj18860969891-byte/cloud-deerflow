#!/usr/bin/env python
"""Check subscription module import."""

import sys
import traceback

try:
    from app.gateway.routes import subscription
    print('Subscription imported OK')
    print('Router prefix:', subscription.router.prefix)
    print('Number of routes:', len(subscription.router.routes))
    print('Routes:', [route.path for route in subscription.router.routes])
except Exception as e:
    print('Import error:')
    traceback.print_exc()