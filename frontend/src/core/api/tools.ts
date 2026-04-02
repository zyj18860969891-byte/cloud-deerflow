/**
 * 工具管理相关的 API 钩子和工具函数
 */

import { useCallback, useEffect, useState } from "react"

/**
 * 工具接口
 */
export interface Tool {
  id: string
  name: string
  description: string
  tool_type: string
  category: string
  tags?: Record<string, unknown>
  module_path: string
  class_name: string
  args_schema?: Record<string, unknown>
  enabled: boolean
  is_builtin: boolean
  is_system: boolean
  required_roles?: string[]
  tenant_scoped: boolean
  total_executions: number
  successful_executions: number
  failed_executions: number
  last_executed_at?: string
  avg_execution_time?: number
  version: string
  version_notes?: string
  created_from_config?: string
  created_at: string
  updated_at: string
  deleted_at?: string
}

/**
 * 工具权限接口
 */
export interface ToolPermission {
  role: string
  can_execute: boolean
  can_view: boolean
  can_edit: boolean
  can_delete: boolean
  max_calls_per_day?: number
  allowed_tenants?: string[]
}

/**
 * 工具创建请求接口
 */
export interface ToolCreate {
  name: string
  description: string
  tool_type: "custom" | "mcp" | "builtin" | "agent"
  category: string
  tags?: Record<string, unknown>
  module_path: string
  class_name: string
  args_schema?: Record<string, unknown>
  enabled?: boolean
  tenant_scoped?: boolean
  required_roles?: string[]
  version?: string
  version_notes?: string
  created_from_config?: string
}

/**
 * 工具更新请求接口
 */
export interface ToolUpdate {
  name?: string
  description?: string
  tool_type?: string
  category?: string
  tags?: Record<string, unknown>
  module_path?: string
  class_name?: string
  args_schema?: Record<string, unknown>
  enabled?: boolean
  tenant_scoped?: boolean
  required_roles?: string[]
  version?: string
  version_notes?: string
  created_from_config?: string
}

/**
 * 工具执行记录接口
 */
export interface ToolExecution {
  id: string
  tool_id: string
  thread_id?: string
  user_id?: string
  tenant_id?: string
  input_params?: Record<string, unknown>
  output?: Record<string, unknown>
  error?: string
  execution_time?: number
  started_at: string
  completed_at?: string
  status: "running" | "success" | "failed" | "cancelled"
  execution_metadata?: Record<string, unknown>
}

/**
 * 工具执行请求接口
 */
export interface ToolExecutionRequest {
  input_params: Record<string, unknown>
  thread_id?: string
  tenant_id?: string
}

/**
 * 工具统计信息接口
 */
export interface ToolStatistics {
  total_tools: number
  total_executions: number
  success_rate: number
  avg_execution_time: number
  most_used_tools: Array<{
    tool_id: string
    tool_name: string
    execution_count: number
  }>
  executions_by_status: Record<string, number>
  executions_by_date: Array<{
    date: string
    count: number
  }>
}

/**
 * 分页响应接口
 */
interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

/**
 * 工具列表查询参数
 */
export interface ToolListParams {
  page?: number
  page_size?: number
  tool_type?: string
  category?: string
  enabled?: boolean
  search?: string
  sort_by?: string
  sort_order?: "asc" | "desc"
}

/**
 * 工具管理 API 响应
 */
interface ToolsResponse extends PaginatedResponse<Tool> {}
interface ToolExecutionsResponse extends PaginatedResponse<ToolExecution> {}

/**
 * 工具 API 基础路径
 */
const TOOLS_API_BASE = "/api/tools"

/**
 * 获取工具列表
 */
export async function fetchTools(params: ToolListParams = {}): Promise<ToolsResponse> {
  const { page = 1, page_size = 20, ...filters } = params
  const searchParams = new URLSearchParams()
  
  searchParams.append("page", page.toString())
  searchParams.append("page_size", page_size.toString())
  
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== "") {
      searchParams.append(key, value.toString())
    }
  })

  const response = await fetch(`${TOOLS_API_BASE}?${searchParams.toString()}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  })

  if (!response.ok) {
    throw new Error(`Failed to fetch tools: ${response.statusText}`)
  }

  return response.json()
}

/**
 * 获取单个工具详情
 */
export async function fetchTool(id: string): Promise<Tool> {
  const response = await fetch(`${TOOLS_API_BASE}/${id}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  })

  if (!response.ok) {
    throw new Error(`Failed to fetch tool: ${response.statusText}`)
  }

  return response.json()
}

/**
 * 创建工具
 */
export async function createTool(tool: ToolCreate): Promise<Tool> {
  const response = await fetch(TOOLS_API_BASE, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(tool),
  })

  if (!response.ok) {
    const error = await response.text()
    throw new Error(`Failed to create tool: ${error}`)
  }

  return response.json()
}

/**
 * 更新工具
 */
export async function updateTool(id: string, tool: ToolUpdate): Promise<Tool> {
  const response = await fetch(`${TOOLS_API_BASE}/${id}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(tool),
  })

  if (!response.ok) {
    const error = await response.text()
    throw new Error(`Failed to update tool: ${error}`)
  }

  return response.json()
}

/**
 * 删除工具
 */
export async function deleteTool(id: string, hard = false): Promise<void> {
  const searchParams = new URLSearchParams()
  if (hard) {
    searchParams.append("hard", "true")
  }

  const response = await fetch(`${TOOLS_API_BASE}/${id}?${searchParams.toString()}`, {
    method: "DELETE",
    headers: {
      "Content-Type": "application/json",
    },
  })

  if (!response.ok) {
    const error = await response.text()
    throw new Error(`Failed to delete tool: ${error}`)
  }
}

/**
 * 执行工具
 */
export async function executeTool(id: string, request: ToolExecutionRequest): Promise<ToolExecution> {
  const response = await fetch(`${TOOLS_API_BASE}/${id}/execute`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  })

  if (!response.ok) {
    const error = await response.text()
    throw new Error(`Failed to execute tool: ${error}`)
  }

  return response.json()
}

/**
 * 获取工具执行历史
 */
export async function fetchToolExecutions(
  toolId: string,
  params: { page?: number; page_size?: number } = {}
): Promise<ToolExecutionsResponse> {
  const { page = 1, page_size = 20 } = params
  const searchParams = new URLSearchParams()
  searchParams.append("page", page.toString())
  searchParams.append("page_size", page_size.toString())

  const response = await fetch(`${TOOLS_API_BASE}/${toolId}/executions?${searchParams.toString()}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  })

  if (!response.ok) {
    throw new Error(`Failed to fetch tool executions: ${response.statusText}`)
  }

  return response.json()
}

/**
 * 获取工具统计信息
 */
export async function fetchToolStatistics(): Promise<ToolStatistics> {
  const response = await fetch(`${TOOLS_API_BASE}/statistics`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  })

  if (!response.ok) {
    throw new Error(`Failed to fetch tool statistics: ${response.statusText}`)
  }

  return response.json()
}

/**
 * 获取工具权限
 */
export async function fetchToolPermissions(toolId: string): Promise<ToolPermission[]> {
  const response = await fetch(`${TOOLS_API_BASE}/${toolId}/permissions`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  })

  if (!response.ok) {
    throw new Error(`Failed to fetch tool permissions: ${response.statusText}`)
  }

  return response.json()
}

/**
 * 更新工具权限
 */
export async function updateToolPermissions(
  toolId: string,
  permissions: Array<{
    role: string
    can_execute: boolean
    can_view: boolean
    can_edit: boolean
    can_delete: boolean
    max_calls_per_day?: number
    allowed_tenants?: string[]
  }>
): Promise<void> {
  const response = await fetch(`${TOOLS_API_BASE}/${toolId}/permissions`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(permissions),
  })

  if (!response.ok) {
    const error = await response.text()
    throw new Error(`Failed to update tool permissions: ${error}`)
  }
}

// ========== React Hooks ==========

/**
 * 使用工具列表的 React Hook
 */
export function useTools(initialParams: ToolListParams = {}) {
  const [tools, setTools] = useState<Tool[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)
  const [pagination, setPagination] = useState({
    page: 1,
    page_size: 20,
    total: 0,
    total_pages: 0,
  })
  const [params, setParams] = useState<ToolListParams>(initialParams)

  const fetchToolsData = useCallback(async (currentParams: ToolListParams) => {
    try {
      setIsLoading(true)
      setError(null)

      const { page = 1, page_size = 20, ...filters } = currentParams
      const response = await fetchTools({ ...filters, page, page_size })
      
      setTools(response.items)
      setPagination({
        page: response.page,
        page_size: response.page_size,
        total: response.total,
        total_pages: response.total_pages,
      })
    } catch (err) {
      setError(err instanceof Error ? err : new Error(String(err)))
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    void fetchToolsData(params)
  }, [params, fetchToolsData])

  const updateParams = useCallback((newParams: Partial<ToolListParams>) => {
    setParams((prev) => ({ ...prev, ...newParams }))
  }, [])

  const refetch = useCallback(() => {
    void fetchToolsData(params)
  }, [params, fetchToolsData])

  return {
    tools,
    isLoading,
    error,
    pagination,
    params,
    updateParams,
    refetch,
  }
}

/**
 * 使用单个工具的 React Hook
 */
export function useTool(toolId: string) {
  const [tool, setTool] = useState<Tool | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    if (!toolId) return

    const fetchToolData = async () => {
      try {
        setIsLoading(true)
        setError(null)
        const data = await fetchTool(toolId)
        setTool(data)
      } catch (err) {
        setError(err instanceof Error ? err : new Error(String(err)))
      } finally {
        setIsLoading(false)
      }
    }

    void fetchToolData()
  }, [toolId])

  const refetch = useCallback(async () => {
    if (!toolId) return
    try {
      setIsLoading(true)
      setError(null)
      const data = await fetchTool(toolId)
      setTool(data)
    } catch (err) {
      setError(err instanceof Error ? err : new Error(String(err)))
    } finally {
      setIsLoading(false)
    }
  }, [toolId])

  return {
    tool,
    isLoading,
    error,
    refetch,
  }
}

/**
 * 使用工具统计信息的 React Hook
 */
export function useToolStatistics() {
  const [statistics, setStatistics] = useState<ToolStatistics | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    const fetchStatistics = async () => {
      try {
        setIsLoading(true)
        setError(null)
        const data = await fetchToolStatistics()
        setStatistics(data)
      } catch (err) {
        setError(err instanceof Error ? err : new Error(String(err)))
      } finally {
        setIsLoading(false)
      }
    }

    void fetchStatistics()
  }, [])

  const refetch = useCallback(async () => {
    try {
      setIsLoading(true)
      setError(null)
      const data = await fetchToolStatistics()
      setStatistics(data)
    } catch (err) {
      setError(err instanceof Error ? err : new Error(String(err)))
    } finally {
      setIsLoading(false)
    }
  }, [])

  return {
    statistics,
    isLoading,
    error,
    refetch,
  }
}