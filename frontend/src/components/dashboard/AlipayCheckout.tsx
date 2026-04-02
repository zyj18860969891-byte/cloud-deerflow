'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { AlertCircle, Loader2, ExternalLink } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface AlipayCheckoutProps {
  plan: string;
  planName: string;
  price: number;
  currency: string;
  onSuccess?: () => void;
  onError?: (error: string) => void;
}

export function AlipayCheckout({
  plan,
  planName,
  price,
  currency,
  onSuccess,
  onError,
}: AlipayCheckoutProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [paymentUrl, setPaymentUrl] = useState<string | null>(null);

  const handleAlipayCheckout = async () => {
    try {
      setLoading(true);
      setError(null);

      const returnUrl = `${window.location.origin}/subscription/success`;

      const response = await fetch('/api/subscription/checkout-alipay', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          plan,
          return_url: returnUrl,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to create Alipay payment');
      }

      const { payment_url } = await response.json();
      setPaymentUrl(payment_url);

      // Redirect to Alipay payment page
      if (payment_url) {
        window.location.href = payment_url;
      }

      if (onSuccess) {
        onSuccess();
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred';
      setError(errorMessage);
      if (onError) {
        onError(errorMessage);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Alipay Payment</CardTitle>
        <CardDescription>{planName} Plan - ¥{price.toFixed(2)}</CardDescription>
      </CardHeader>

      <CardContent className="space-y-4">
        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <div className="space-y-2">
          <p className="text-sm text-gray-600">Plan: {planName}</p>
          <p className="text-2xl font-bold">¥{price.toFixed(2)}</p>
          <p className="text-sm text-gray-600">Billed quarterly (every 90 days)</p>
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded p-3">
          <p className="text-sm text-blue-800">
            You will be redirected to Alipay to complete the payment securely.
          </p>
        </div>

        <Button
          onClick={handleAlipayCheckout}
          disabled={loading}
          className="w-full"
          size="lg"
        >
          {loading && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
          {loading ? 'Processing...' : 'Pay with Alipay'}
        </Button>

        {paymentUrl && (
          <Button
            onClick={() => {
              window.location.href = paymentUrl;
            }}
            variant="outline"
            className="w-full"
          >
            <ExternalLink className="h-4 w-4 mr-2" />
            Continue to Alipay
          </Button>
        )}

        <p className="text-xs text-gray-500 text-center">
          Secure payment powered by Alipay
        </p>
      </CardContent>
    </Card>
  );
}
