#!/usr/bin/env python
"""Debug app creation and router registration."""

import sys
import traceback

try:
    # Import the create_app function
    from app.gateway.app import create_app
    
    # Create the app
    print("Creating app...")
    app = create_app()
    print("App created successfully")
    
    # Get all routes
    all_routes = []
    for route in app.routes:
        if hasattr(route, 'path'):
            all_routes.append(route.path)
    
    print(f"\nTotal routes: {len(all_routes)}")
    print("\nAll routes:")
    for route in sorted(all_routes):
        print(f"  {route}")
    
    # Check for subscription routes
    subscription_routes = [r for r in all_routes if 'subscription' in r.lower()]
    print(f"\nSubscription routes: {len(subscription_routes)}")
    for route in subscription_routes:
        print(f"  {route}")
    
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()