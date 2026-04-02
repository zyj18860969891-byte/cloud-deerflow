/**
 * 租户相关的 API 钩子和工具函数
 */

import { useCallback, useEffect, useState } from "react"

/**
 * 租户信息接口
 */
export interface Tenant {
  id: string
  name: string
  description?: string
  status: "active" | "inactive"
  createdAt: string
  updatedAt?: string
}

/**
 * 租户响应接口
 */
interface TenantsResponse {
  tenants: Tenant[]
  total: number
}

/**
 * 使用租户列表的 React Hook
 */
export function useTenants() {
  const [tenants, setTenants] = useState<Tenant[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const fetchTenants = useCallback(async () => {
    try {
      setIsLoading(true)
      setError(null)

      const response = await fetch("/api/tenants", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      })

      if (!response.ok) {
        throw new Error(`Failed to fetch tenants: ${response.statusText}`)
      }

      const data: TenantsResponse = await response.json()
      setTenants(data.tenants || [])
    } catch (err) {
      setError(err instanceof Error ? err : new Error(String(err)))
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    void fetchTenants()
  }, [fetchTenants])

  return { tenants, isLoading, error, refetch: fetchTenants }
}

/**
 * 使用当前租户的 React Hook
 */
export function useCurrentTenant() {
  const [currentTenant, setCurrentTenant] = useState<Tenant | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    const fetchCurrentTenant = async () => {
      try {
        setIsLoading(true)
        setError(null)

        const response = await fetch("/api/tenants/current", {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        })

        if (!response.ok) {
          throw new Error(
            `Failed to fetch current tenant: ${response.statusText}`
          )
        }

        const data = await response.json()
        setCurrentTenant(data)
      } catch (err) {
        setError(err instanceof Error ? err : new Error(String(err)))
      } finally {
        setIsLoading(false)
      }
    }

    void fetchCurrentTenant()
  }, [])

  return { currentTenant, isLoading, error }
}

/**
 * 租户 API 客户端
 */
export class TenantAPI {
  private baseUrl = "/api/tenants"

  /**
   * 获取所有租户
   */
  async getAllTenants(): Promise<Tenant[]> {
    const response = await fetch(this.baseUrl, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    })

    if (!response.ok) {
      throw new Error(`Failed to fetch tenants: ${response.statusText}`)
    }

    const data: TenantsResponse = await response.json()
    return data.tenants || []
  }

  /**
   * 获取当前租户
   */
  async getCurrentTenant(): Promise<Tenant> {
    const response = await fetch(`${this.baseUrl}/current`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    })

    if (!response.ok) {
      throw new Error(`Failed to fetch current tenant: ${response.statusText}`)
    }

    return response.json()
  }

  /**
   * 获取指定租户
   */
  async getTenant(tenantId: string): Promise<Tenant> {
    const response = await fetch(`${this.baseUrl}/${tenantId}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    })

    if (!response.ok) {
      throw new Error(`Failed to fetch tenant: ${response.statusText}`)
    }

    return response.json()
  }

  /**
   * 切换租户
   */
  async switchTenant(tenantId: string): Promise<Tenant> {
    const response = await fetch(`${this.baseUrl}/${tenantId}/switch`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    })

    if (!response.ok) {
      throw new Error(`Failed to switch tenant: ${response.statusText}`)
    }

    return response.json()
  }

  /**
   * 创建新租户（仅管理员）
   */
  async createTenant(data: {
    name: string
    description?: string
  }): Promise<Tenant> {
    const response = await fetch(this.baseUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    })

    if (!response.ok) {
      throw new Error(`Failed to create tenant: ${response.statusText}`)
    }

    return response.json()
  }

  /**
   * 更新租户信息（仅管理员）
   */
  async updateTenant(
    tenantId: string,
    data: Partial<Omit<Tenant, "id" | "createdAt">>
  ): Promise<Tenant> {
    const response = await fetch(`${this.baseUrl}/${tenantId}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    })

    if (!response.ok) {
      throw new Error(`Failed to update tenant: ${response.statusText}`)
    }

    return response.json()
  }

  /**
   * 删除租户（仅管理员）
   */
  async deleteTenant(tenantId: string): Promise<void> {
    const response = await fetch(`${this.baseUrl}/${tenantId}`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
      },
    })

    if (!response.ok) {
      throw new Error(`Failed to delete tenant: ${response.statusText}`)
    }
  }
}

// 创建全局租户 API 实例
export const tenantAPI = new TenantAPI()
