'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { AlertCircle, Loader2, Check } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface PlanPricing {
  gateway: 'stripe' | 'alipay';
  price: number;
  currency: string;
  price_id?: string;
}

interface SubscriptionPlan {
  id: string;
  name: string;
  description: string;
  billing_cycle: string;
  billing_days: number;
  pricing: PlanPricing[];
  features: string[];
}

interface PaymentMethod {
  gateway: string;
  name: string;
  description: string;
  currencies: string[];
  regions: string[];
}

interface SubscriptionPlansProps {
  onPlanSelected?: (plan: SubscriptionPlan, paymentGateway: 'stripe' | 'alipay') => void;
  currentPlan?: string;
  isLoading?: boolean;
}

export function SubscriptionPlans({
  onPlanSelected,
  currentPlan,
  isLoading = false,
}: SubscriptionPlansProps) {
  const [plans, setPlans] = useState<SubscriptionPlan[]>([]);
  const [paymentMethods, setPaymentMethods] = useState<PaymentMethod[]>([]);
  const [selectedGateway, setSelectedGateway] = useState<'stripe' | 'alipay'>('stripe');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedPlan, setSelectedPlan] = useState<string | null>(null);

  useEffect(() => {
    const fetchPlans = async () => {
      try {
        setLoading(true);
        const response = await fetch('/api/subscription/plans');
        if (!response.ok) {
          throw new Error('Failed to fetch subscription plans');
        }
        const data = await response.json();
        setPlans(data.plans);
        setPaymentMethods(data.payment_methods);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchPlans();
  }, []);

  const handlePlanSelect = (plan: SubscriptionPlan) => {
    setSelectedPlan(plan.id);
    if (onPlanSelected) {
      onPlanSelected(plan, selectedGateway);
    }
  };

  if (loading) {
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

  return (
    <div className="space-y-8">
      {/* Payment Gateway Selection */}
      <div className="rounded-lg border bg-card p-4">
        <h3 className="font-semibold mb-4">Select Payment Method</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {paymentMethods.map((method) => (
            <button
              key={method.gateway}
              onClick={() => setSelectedGateway(method.gateway as 'stripe' | 'alipay')}
              className={`p-4 rounded-lg border-2 transition-all ${
                selectedGateway === method.gateway
                  ? 'border-primary bg-primary/5'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="text-left">
                  <div className="font-semibold">{method.name}</div>
                  <div className="text-sm text-gray-600">{method.description}</div>
                  <div className="text-xs text-gray-500 mt-2">
                    {method.currencies.join(', ')} • {method.regions.join(', ')}
                  </div>
                </div>
                {selectedGateway === method.gateway && (
                  <Check className="h-5 w-5 text-primary" />
                )}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Subscription Plans */}
      <div className="space-y-4">
        <h2 className="text-2xl font-bold">Choose Your Plan</h2>
        <p className="text-gray-600">All plans include quarterly billing (90 days)</p>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {plans.map((plan) => {
            const pricingForGateway = plan.pricing.find(p => p.gateway === selectedGateway);
            const isCurrentPlan = currentPlan === plan.id;

            return (
              <Card
                key={plan.id}
                className={`relative transition-all ${
                  selectedPlan === plan.id ? 'ring-2 ring-primary' : ''
                } ${isCurrentPlan ? 'border-primary' : ''}`}
              >
                {isCurrentPlan && (
                  <Badge className="absolute top-4 right-4" variant="secondary">
                    Current Plan
                  </Badge>
                )}

                <CardHeader>
                  <CardTitle>{plan.name}</CardTitle>
                  <CardDescription>{plan.description}</CardDescription>
                </CardHeader>

                <CardContent className="space-y-4">
                  {/* Pricing */}
                  {pricingForGateway && (
                    <div className="space-y-2">
                      <div className="text-3xl font-bold">
                        ¥{pricingForGateway.price.toFixed(2)}
                        {selectedGateway === 'stripe' ? '$' : ''}
                      </div>
                      <p className="text-sm text-gray-600">
                        per {plan.billing_days} days
                      </p>
                    </div>
                  )}

                  {/* Features */}
                  <div className="space-y-2">
                    {plan.features.map((feature, idx) => (
                      <div key={idx} className="flex items-center text-sm">
                        <Check className="h-4 w-4 mr-2 text-green-600" />
                        {feature}
                      </div>
                    ))}
                  </div>

                  {/* Button */}
                  <Button
                    onClick={() => handlePlanSelect(plan)}
                    disabled={isLoading || isCurrentPlan}
                    className="w-full"
                    variant={isCurrentPlan ? 'outline' : 'default'}
                  >
                    {isCurrentPlan ? 'Current Plan' : 'Select Plan'}
                  </Button>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>
    </div>
  );
}
