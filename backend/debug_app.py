#!/usr/bin/env python
"""Debug app creation and router registration."""

import sys
import traceback

try:
    from app.gateway.app import create_app
    print('Creating app...')
    app = create_app()
    print('App created successfully')
    
    # Debug: print app.routes type and content
    print(f'app.routes type: {type(app.routes)}')
    print(f'app.routes length: {len(app.routes)}')
    
    # Get all routes from app
    all_routes = []
    for route in app.routes:
        print(f'Route: {route}, type: {type(route)}')
        if hasattr(route, 'path'):
            all_routes.append(route.path)
        elif hasattr(route, 'routes'):
            # It's a router
            for r in route.routes:
                if hasattr(r, 'path'):
                    all_routes.append(r.path)
    
    print(f'Total routes: {len(all_routes)}')
    print('All routes:')
    for route in sorted(all_routes):
        print(f'  {route}')
    
    # Check for subscription routes
    subscription_routes = [r for r in all_routes if 'subscription' in r.lower()]
    print(f'Subscription routes: {subscription_routes}')
    
except Exception as e:
    print('Error during app creation:')
    traceback.print_exc()