'use client';

import { useState } from 'react';
import { loadStripe } from '@stripe/js';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { AlertCircle, Loader2 } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface StripeCheckoutProps {
  planId: string;
  priceId: string;
  planName: string;
  price: number;
  onSuccess?: () => void;
  onError?: (error: string) => void;
}

export function StripeCheckout({
  planId,
  priceId,
  planName,
  price,
  onSuccess,
  onError,
}: StripeCheckoutProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCheckout = async () => {
    try {
      setLoading(true);
      setError(null);

      // Create checkout session
      const response = await fetch('/api/subscription/checkout', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          plan_id: planId,
          price_id: priceId,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to create checkout session');
      }

      const { client_secret } = await response.json();

      // Load Stripe
      const stripe = await loadStripe(
        process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY
      );

      if (!stripe) {
        throw new Error('Failed to load Stripe');
      }

      // Redirect to Stripe Checkout
      const { error: stripeError } = await stripe.redirectToCheckout({
        clientSecret: client_secret,
      });

      if (stripeError) {
        throw new Error(stripeError.message);
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
        <CardTitle>Payment Details</CardTitle>
        <CardDescription>{planName} Plan - ${price.toFixed(2)}</CardDescription>
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
          <p className="text-2xl font-bold">${price.toFixed(2)}</p>
          <p className="text-sm text-gray-600">Billed quarterly (every 90 days)</p>
        </div>

        <Button
          onClick={handleCheckout}
          disabled={loading}
          className="w-full"
          size="lg"
        >
          {loading && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
          {loading ? 'Processing...' : 'Continue to Payment'}
        </Button>

        <p className="text-xs text-gray-500 text-center">
          Secure payment powered by Stripe
        </p>
      </CardContent>
    </Card>
  );
}
