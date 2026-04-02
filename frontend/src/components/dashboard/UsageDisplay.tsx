'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { AlertCircle, Loader2, TrendingUp } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface UsageMetrics {
  api_calls_used: number;
  api_calls_limit: number;
  storage_used: number;
  storage_limit: number;
  compute_hours_used: number;
  compute_hours_limit: number;
}

interface UsageDisplayProps {
  refreshInterval?: number;
  onWebSocketError?: (error: string) => void;
}

export function UsageDisplay({
  refreshInterval = 30000,
  onWebSocketError,
}: UsageDisplayProps) {
  const [metrics, setMetrics] = useState<UsageMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        setLoading(true);
        const response = await fetch('/api/subscription/usage');
        if (!response.ok) {
          throw new Error('Failed to fetch usage metrics');
        }
        const data = await response.json();
        setMetrics(data);
        setLastUpdated(new Date());
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    // Initial fetch
    fetchMetrics();

    // Set up polling interval
    const interval = setInterval(fetchMetrics, refreshInterval);
    return () => clearInterval(interval);
  }, [refreshInterval]);

  // WebSocket real-time updates
  useEffect(() => {
    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const ws = new WebSocket(`${protocol}//${window.location.host}/ws/usage`);

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        setMetrics(data);
        setLastUpdated(new Date());
      };

      ws.onerror = (err) => {
        console.warn('WebSocket error:', err);
        if (onWebSocketError) {
          onWebSocketError('Real-time updates unavailable, using polling mode');
        }
      };

      return () => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.close();
        }
      };
    } catch (err) {
      console.warn('WebSocket connection failed:', err);
    }
  }, [onWebSocketError]);

  if (loading && !metrics) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  if (!metrics) {
    return null;
  }

  const apiCallsPercent = metrics.api_calls_limit > 0 
    ? (metrics.api_calls_used / metrics.api_calls_limit) * 100 
    : 0;
  const storagePercent = metrics.storage_limit > 0 
    ? (metrics.storage_used / metrics.storage_limit) * 100 
    : 0;
  const computePercent = metrics.compute_hours_limit > 0 
    ? (metrics.compute_hours_used / metrics.compute_hours_limit) * 100 
    : 0;

  const getProgressColor = (percent: number) => {
    if (percent >= 90) return 'bg-red-500';
    if (percent >= 70) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Current Usage</CardTitle>
          <CardDescription>
            {lastUpdated && `Last updated: ${lastUpdated.toLocaleTimeString()}`}
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-6">
          {/* API Calls */}
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <label className="font-semibold">API Calls</label>
              <span className="text-sm text-gray-600">
                {metrics.api_calls_used.toLocaleString()} / {
                  metrics.api_calls_limit > 0 
                    ? metrics.api_calls_limit.toLocaleString()
                    : 'Unlimited'
                }
              </span>
            </div>
            {metrics.api_calls_limit > 0 && (
              <Progress 
                value={Math.min(apiCallsPercent, 100)} 
                className="h-2"
              />
            )}
            <p className="text-xs text-gray-500">
              {apiCallsPercent.toFixed(1)}% used
            </p>
          </div>

          {/* Storage */}
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <label className="font-semibold">Storage</label>
              <span className="text-sm text-gray-600">
                {metrics.storage_used.toFixed(2)} GB / {
                  metrics.storage_limit > 0 
                    ? `${metrics.storage_limit.toFixed(2)} GB`
                    : 'Unlimited'
                }
              </span>
            </div>
            {metrics.storage_limit > 0 && (
              <Progress 
                value={Math.min(storagePercent, 100)} 
                className="h-2"
              />
            )}
            <p className="text-xs text-gray-500">
              {storagePercent.toFixed(1)}% used
            </p>
          </div>

          {/* Compute Hours */}
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <label className="font-semibold">Compute Hours</label>
              <span className="text-sm text-gray-600">
                {metrics.compute_hours_used.toFixed(2)} h / {
                  metrics.compute_hours_limit > 0 
                    ? `${metrics.compute_hours_limit.toFixed(2)} h`
                    : 'Unlimited'
                }
              </span>
            </div>
            {metrics.compute_hours_limit > 0 && (
              <Progress 
                value={Math.min(computePercent, 100)} 
                className="h-2"
              />
            )}
            <p className="text-xs text-gray-500">
              {computePercent.toFixed(1)}% used
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Usage Tips */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Usage Tips
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2 text-sm text-gray-600">
            <li>• Usage is calculated quarterly and resets at the start of each billing period</li>
            <li>• Enterprise plans have unlimited resources</li>
            <li>• Consider upgrading your plan if you're approaching limits</li>
            <li>• Contact support for custom usage limits</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
