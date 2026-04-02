'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { AlertCircle, ChevronDown, Plus, Building2 } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';

interface Tenant {
  id: string;
  name: string;
  email: string;
  status: string;
  subscription_plan?: string;
}

interface TenantSwitcherProps {
  currentTenantId?: string;
  onTenantChange?: (tenantId: string) => void;
  showAddTenant?: boolean;
}

export function TenantSwitcher({
  currentTenantId,
  onTenantChange,
  showAddTenant = true,
}: TenantSwitcherProps) {
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTenant, setSelectedTenant] = useState<Tenant | null>(null);
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [newTenantName, setNewTenantName] = useState('');
  const [newTenantEmail, setNewTenantEmail] = useState('');
  const router = useRouter();

  useEffect(() => {
    const fetchTenants = async () => {
      try {
        setLoading(true);
        const response = await fetch('/api/tenants');
        if (!response.ok) {
          throw new Error('Failed to fetch tenants');
        }
        const data = await response.json();
        setTenants(data);
        
        // Set selected tenant
        if (currentTenantId) {
          const tenant = data.find((t: Tenant) => t.id === currentTenantId);
          setSelectedTenant(tenant || data[0]);
        } else {
          setSelectedTenant(data[0]);
        }
        
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchTenants();
  }, [currentTenantId]);

  const handleTenantSelect = (tenant: Tenant) => {
    setSelectedTenant(tenant);
    if (onTenantChange) {
      onTenantChange(tenant.id);
    }
    router.refresh();
  };

  const handleAddTenant = async () => {
    if (!newTenantName || !newTenantEmail) {
      return;
    }

    try {
      const response = await fetch('/api/tenants', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: newTenantName,
          email: newTenantEmail,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to create tenant');
      }

      const newTenant = await response.json();
      setTenants([...tenants, newTenant]);
      setSelectedTenant(newTenant);
      setShowAddDialog(false);
      setNewTenantName('');
      setNewTenantEmail('');
      
      if (onTenantChange) {
        onTenantChange(newTenant.id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create tenant');
    }
  };

  if (loading) {
    return <div className="text-gray-600">Loading...</div>;
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
    <div className="space-y-4">
      {/* Tenant Selector */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Building2 className="h-5 w-5" />
            Current Organization
          </CardTitle>
          <CardDescription>Switch between your organizations</CardDescription>
        </CardHeader>

        <CardContent>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" className="w-full justify-between">
                <div className="text-left">
                  <p className="font-semibold">{selectedTenant?.name || 'Select Tenant'}</p>
                  <p className="text-xs text-gray-600">{selectedTenant?.email}</p>
                </div>
                <ChevronDown className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>

            <DropdownMenuContent className="w-56">
              <DropdownMenuLabel>Your Organizations</DropdownMenuLabel>
              <DropdownMenuSeparator />

              {tenants.map((tenant) => (
                <DropdownMenuItem
                  key={tenant.id}
                  onClick={() => handleTenantSelect(tenant)}
                  className="cursor-pointer"
                >
                  <div className="flex-1">
                    <p className="font-medium">{tenant.name}</p>
                    <p className="text-xs text-gray-600">{tenant.email}</p>
                  </div>
                  {selectedTenant?.id === tenant.id && (
                    <Badge variant="secondary" className="ml-2">
                      Active
                    </Badge>
                  )}
                  {tenant.subscription_plan && (
                    <Badge variant="outline" className="ml-2">
                      {tenant.subscription_plan}
                    </Badge>
                  )}
                </DropdownMenuItem>
              ))}

              {showAddTenant && (
                <>
                  <DropdownMenuSeparator />
                  <Dialog open={showAddDialog} onOpenChange={setShowAddDialog}>
                    <DialogTrigger asChild>
                      <DropdownMenuItem
                        onSelect={(e) => {
                          e.preventDefault();
                          setShowAddDialog(true);
                        }}
                      >
                        <Plus className="h-4 w-4 mr-2" />
                        Add New Organization
                      </DropdownMenuItem>
                    </DialogTrigger>

                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>Create New Organization</DialogTitle>
                        <DialogDescription>
                          Create a new organization to manage separate projects and billing.
                        </DialogDescription>
                      </DialogHeader>

                      <div className="space-y-4">
                        <div>
                          <label className="text-sm font-medium">Organization Name</label>
                          <Input
                            placeholder="My Company"
                            value={newTenantName}
                            onChange={(e) => setNewTenantName(e.target.value)}
                          />
                        </div>

                        <div>
                          <label className="text-sm font-medium">Email Address</label>
                          <Input
                            type="email"
                            placeholder="admin@company.com"
                            value={newTenantEmail}
                            onChange={(e) => setNewTenantEmail(e.target.value)}
                          />
                        </div>

                        <Button
                          onClick={handleAddTenant}
                          disabled={!newTenantName || !newTenantEmail}
                          className="w-full"
                        >
                          Create Organization
                        </Button>
                      </div>
                    </DialogContent>
                  </Dialog>
                </>
              )}
            </DropdownMenuContent>
          </DropdownMenu>
        </CardContent>
      </Card>

      {/* Quick Stats */}
      {selectedTenant && (
        <Card>
          <CardHeader>
            <CardTitle>Organization Status</CardTitle>
          </CardHeader>

          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Status</p>
                <Badge variant="outline">{selectedTenant.status}</Badge>
              </div>

              {selectedTenant.subscription_plan && (
                <div>
                  <p className="text-sm text-gray-600">Plan</p>
                  <Badge>{selectedTenant.subscription_plan}</Badge>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
