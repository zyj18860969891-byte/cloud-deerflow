'use client';

import Link from 'next/link';
import { useState, useEffect } from 'react';

import { AlertCircle, CheckCircle, Clock, FileText } from 'lucide-react';

import { SubscriptionPlans } from '@/components/dashboard/SubscriptionPlans';
import { StripeCheckout } from '@/components/dashboard/StripeCheckout';
import { AlipayCheckout } from '@/components/dashboard/AlipayCheckout';
import { UsageDisplay } from '@/components/dashboard/UsageDisplay';
import { TenantSwitcher } from '@/components/dashboard/TenantSwitcher';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

interface SubscriptionInfo {
  id: number;
  plan: string;
  status: string;
  current_period_start: string;
  current_period_end: string;
  amount: number;
  currency: string;
  cancel_at_period_end: boolean;
}

interface CheckoutState {
  active: boolean;
  plan: SubscriptionPlanType | null;
  gateway: 'stripe' | 'alipay';
}

interface SubscriptionPlanType {
  id: string;
  name: string;
  description: string;
  billing_cycle: string;
  billing_days: number;
  pricing: Array<{
    gateway: 'stripe' | 'alipay';
    price: number;
    currency: string;
    price_id?: string;
  }>;
  features: string[];
}

export default function SubscriptionPage() {
  const [subscription, setSubscription] = useState<SubscriptionInfo | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [checkoutState, setCheckoutState] = useState<CheckoutState>({
    active: false,
    plan: null,
    gateway: 'stripe',
  });

  useEffect(() => {
    const fetchSubscription = async () => {
      try {
        const response = await fetch('/api/subscription/current');

        if (response.status === 404) {
          // No subscription yet
          setSubscription(null);
        } else if (response.ok) {
          const data = await response.json();
          setSubscription(data as SubscriptionInfo);
        } else {
          throw new Error('Failed to fetch subscription');
        }
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      }
    };

    void fetchSubscription();
  }, []);

  const handlePlanSelected = (plan: SubscriptionPlanType, gateway: 'stripe' | 'alipay') => {
    setCheckoutState({
      active: true,
      plan,
      gateway,
    });
  };

  const handleCheckoutSuccess = () => {
    // Refresh subscription info
    window.location.reload();
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container py-8">
        <div className="space-y-8">
          {/* Page Header */}
          <div>
            <h1 className="text-3xl font-bold">Subscription & Billing</h1>
            <p className="text-gray-600 mt-2">
              Manage your subscription, view usage, and handle billing settings
            </p>
          </div>

          {/* Organization Selector */}
          <section className="bg-white rounded-lg border p-6">
            <h2 className="text-lg font-semibold mb-4">Organization Management</h2>
            <TenantSwitcher showAddTenant={true} />
          </section>

          {/* Current Subscription */}
          {subscription && (
            <section className="space-y-4">
              <h2 className="text-lg font-semibold">Current Subscription</h2>
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <CheckCircle className="h-5 w-5 text-green-600" />
                    {subscription.plan.toUpperCase()} Plan
                  </CardTitle>
                  <CardDescription>
                    Status: <Badge variant="outline">{subscription.status}</Badge>
                  </CardDescription>
                </CardHeader>

                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <p className="text-sm text-gray-600">Billing Amount</p>
                      <p className="text-2xl font-bold">
                        {subscription.currency.toUpperCase()} {subscription.amount}
                      </p>
                      <p className="text-xs text-gray-500">per quarter (90 days)</p>
                    </div>

                    <div>
                      <p className="text-sm text-gray-600">Current Period</p>
                      <p className="font-semibold">
                        {formatDate(subscription.current_period_start)}
                      </p>
                      <p className="text-xs text-gray-500">
                        to {formatDate(subscription.current_period_end)}
                      </p>
                    </div>

                    <div>
                      <p className="text-sm text-gray-600">Days Remaining</p>
                      <p className="text-2xl font-bold">
                        {Math.ceil(
                          (new Date(subscription.current_period_end).getTime() -
                            new Date().getTime()) /
                            (1000 * 60 * 60 * 24)
                        )}
                      </p>
                      <p className="text-xs text-gray-500">days in current period</p>
                    </div>
                  </div>

                  {subscription.cancel_at_period_end && (
                    <Alert>
                      <Clock className="h-4 w-4" />
                      <AlertDescription>
                        Your subscription will be canceled at the end of the current billing period.
                      </AlertDescription>
                    </Alert>
                  )}

                  <div className="flex gap-2">
                    <Button variant="outline" asChild>
                      <Link href="/billing/invoices">
                        <FileText className="h-4 w-4 mr-2" />
                        View Invoices
                      </Link>
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </section>
          )}

          {/* Usage Metrics */}
          {subscription && (
            <section className="space-y-4">
              <h2 className="text-lg font-semibold">Usage & Quotas</h2>
              <UsageDisplay />
            </section>
          )}

          {/* Select New Plan or Upgrade */}
          {!checkoutState.active && (
            <section className="space-y-4">
              <h2 className="text-lg font-semibold">
                {subscription ? 'Upgrade Your Plan' : 'Select a Plan'}
              </h2>
              <SubscriptionPlans
                onPlanSelected={handlePlanSelected}
                currentPlan={subscription?.plan}
              />
            </section>
          )}

          {/* Checkout */}
          {checkoutState.active && checkoutState.plan && (
            <section className="space-y-4">
              <h2 className="text-lg font-semibold">Complete Your Purchase</h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Plan Summary */}
                <Card>
                  <CardHeader>
                    <CardTitle>Order Summary</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <p className="text-sm text-gray-600">Plan</p>
                      <p className="font-semibold">{checkoutState.plan.name}</p>
                    </div>

                    <div>
                      <p className="text-sm text-gray-600">Billing Cycle</p>
                      <p className="font-semibold">{checkoutState.plan.billing_days} days</p>
                    </div>

                    <div className="border-t pt-4">
                      <p className="text-sm text-gray-600">Total</p>
                      <p className="text-2xl font-bold">
                        {checkoutState.gateway === 'stripe' ? '$' : '¥'}
                        {checkoutState.plan.pricing
                          .find((p) => p.gateway === checkoutState.gateway)
                          ?.price.toFixed(2)}
                      </p>
                    </div>

                    <Button
                      variant="outline"
                      onClick={() =>
                        setCheckoutState({ active: false, plan: null, gateway: 'stripe' })
                      }
                      className="w-full"
                    >
                      Back to Plans
                    </Button>
                  </CardContent>
                </Card>

                {/* Payment Method */}
                {checkoutState.gateway === 'stripe' && (
                  <StripeCheckout
                    planId={checkoutState.plan?.id ?? ''}
                    priceId={
                      checkoutState.plan?.pricing.find(
                        (p) => p.gateway === 'stripe'
                      )?.price_id ?? ''
                    }
                    planName={checkoutState.plan?.name ?? ''}
                    price={
                      checkoutState.plan?.pricing.find((p) => p.gateway === 'stripe')
                        ?.price ?? 0
                    }
                    onSuccess={handleCheckoutSuccess}
                  />
                )}

                {checkoutState.gateway === 'alipay' && (
                  <AlipayCheckout
                    plan={checkoutState.plan?.id ?? ''}
                    planName={checkoutState.plan?.name ?? ''}
                    price={
                      checkoutState.plan?.pricing.find((p) => p.gateway === 'alipay')
                        ?.price ?? 0
                    }
                    currency="cny"
                    onSuccess={handleCheckoutSuccess}
                  />
                )}
              </div>
            </section>
          )}

          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
        </div>
      </div>
    </div>
  );
}

// Badge component helper (if not already available in your UI library)
interface BadgeProps {
  variant?: 'default' | 'outline';
  children: React.ReactNode;
}

function Badge({ variant = 'default', children }: BadgeProps) {
  const variants: Record<string, string> = {
    default: 'bg-blue-100 text-blue-800',
    outline: 'border border-gray-300 bg-white text-gray-800',
  };

  return <span className={`px-2 py-1 rounded text-xs font-medium ${variants[variant]}`}>{children}</span>;
}
