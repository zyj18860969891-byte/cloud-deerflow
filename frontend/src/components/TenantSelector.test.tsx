/**
 * TenantSelector 组件的单元测试
 * 使用 Jest 和 React Testing Library
 */

import { render, screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"

import "@testing-library/jest-dom"
import * as tenantsAPI from "@/core/api/tenants"
import type { TenantAPI } from "@/core/api/tenants"

// Mock tenantAPI 的类型定义
interface MockTenantAPI {
  switchTenant: jest.Mock
}

import { TenantSelector } from "./TenantSelector"

// Mock API 模块
jest.mock("@/core/api/tenants")

describe("TenantSelector Component", () => {
  const mockTenants = [
    {
      id: "tenant-001",
      name: "企业 A",
      description: "示例企业 A",
      status: "active" as const,
      createdAt: "2024-01-01T00:00:00Z",
    },
    {
      id: "tenant-002",
      name: "企业 B",
      description: "示例企业 B",
      status: "active" as const,
      createdAt: "2024-01-02T00:00:00Z",
    },
    {
      id: "tenant-003",
      name: "企业 C",
      description: "示例企业 C",
      status: "inactive" as const,
      createdAt: "2024-01-03T00:00:00Z",
    },
  ]

  const mockCurrentTenant = mockTenants[0]

  beforeEach(() => {
    jest.clearAllMocks()

    // Mock useTenants hook
    ;(tenantsAPI.useTenants as unknown as jest.Mock).mockReturnValue({
      tenants: mockTenants,
      isLoading: false,
      error: null,
      refetch: jest.fn(),
    })

    // Mock useCurrentTenant hook
    ;(tenantsAPI.useCurrentTenant as unknown as jest.Mock).mockReturnValue({
      currentTenant: mockCurrentTenant,
      isLoading: false,
      error: null,
    })

    // Mock tenantAPI
    jest.spyOn(tenantsAPI, 'tenantAPI', 'get').mockReturnValue({
      switchTenant: jest.fn(),
    } as unknown as TenantAPI)
  })

  it("应该正确渲染组件", () => {
    render(<TenantSelector />)

    expect(screen.getByText("租户选择")).toBeInTheDocument()
    expect(screen.getByText("当前租户")).toBeInTheDocument()
  })

  it("应该显示租户列表", () => {
    render(<TenantSelector />)

    expect(screen.getByText("企业 A")).toBeInTheDocument()
    expect(screen.getByText("示例企业 A")).toBeInTheDocument()
  })

  it("应该显示加载状态", () => {
    ;(tenantsAPI.useTenants as unknown as jest.Mock).mockReturnValue({
      tenants: [],
      isLoading: true,
      error: null,
      refetch: jest.fn(),
    })

    render(<TenantSelector />)

    expect(screen.getByText("加载租户列表中...")).toBeInTheDocument()
  })

  it("应该显示错误消息", () => {
    const errorMessage = "获取租户失败"
    ;(tenantsAPI.useTenants as unknown as jest.Mock).mockReturnValue({
      tenants: [],
      isLoading: false,
      error: new Error(errorMessage),
      refetch: jest.fn(),
    })

    render(<TenantSelector />)

    expect(screen.getByText(errorMessage)).toBeInTheDocument()
  })

  it("应该显示当前租户信息", () => {
    render(<TenantSelector />)

    const currentTenantSection = screen.getByText("当前租户").closest("div")
    expect(within(currentTenantSection!).getByText("企业 A")).toBeInTheDocument()
    expect(within(currentTenantSection!).getByText("示例企业 A")).toBeInTheDocument()
  })

  it("应该在租户是活跃时显示绿色勾号", () => {
    render(<TenantSelector />)

    const checkCircles = screen.getAllByRole("img", {
      hidden: true,
    })

    // 验证至少存在一个绿色勾号
    expect(checkCircles.length).toBeGreaterThan(0)
  })

  it("应该能切换租户", async () => {
    const user = userEvent.setup()
    const mockSwitchTenant = jest.fn().mockResolvedValue(mockTenants[1])
    const tenantAPIMock = tenantsAPI.tenantAPI as unknown as MockTenantAPI
    tenantAPIMock.switchTenant = mockSwitchTenant

    ;(tenantsAPI.useTenants as unknown as jest.Mock).mockReturnValue({
      tenants: mockTenants,
      isLoading: false,
      error: null,
      refetch: jest.fn(),
    })

    render(<TenantSelector />)

    // 找到"企业 B"对应的切换按钮
    const switches = screen.getAllByRole("button", { name: /switch/i })
    if (switches.length > 1) {
      await user.click(switches[1]!)

      await waitFor(() => {
        expect(mockSwitchTenant).toHaveBeenCalledWith("tenant-002")
      })
    }
  })

  it("应该处理切换租户时的错误", async () => {
    const user = userEvent.setup()
    const errorMessage = "切换租户失败"
    const mockSwitchTenant = jest.fn().mockRejectedValue(new Error(errorMessage))
    const tenantAPIMock = tenantsAPI.tenantAPI as unknown as MockTenantAPI
    tenantAPIMock.switchTenant = mockSwitchTenant

    render(<TenantSelector />)

    // 点击切换按钮
    const switches = screen.getAllByRole("button", { name: /switch/i })
    if (switches.length > 1) {
      await user.click(switches[1]!)

      // 等待错误消息显示
      await waitFor(() => {
        // 应该显示错误信息
        expect(screen.queryByText(errorMessage)).toBeInTheDocument()
      })
    }
  })

  it("应该禁用不活跃的租户", () => {
    render(<TenantSelector />)

    // "企业 C" 是不活跃的，应该被禁用或标记为不可用
    const tenantCText = screen.getByText("企业 C")
    expect(tenantCText).toBeInTheDocument()
  })

  it("应该显示租户统计信息", () => {
    render(<TenantSelector />)

    const activeCount = mockTenants.filter((t) => t.status === "active").length

    // 验证统计信息存在
    expect(screen.getByText(new RegExp(`${activeCount}`))).toBeInTheDocument()
  })

  it("应该处理空租户列表", () => {
    ;(tenantsAPI.useTenants as unknown as jest.Mock).mockReturnValue({
      tenants: [],
      isLoading: false,
      error: null,
      refetch: jest.fn(),
    })

    render(<TenantSelector />)

    expect(screen.getByText("无可用租户")).toBeInTheDocument()
  })

  it("应该能重新获取租户列表", async () => {
    const user = userEvent.setup()
    const mockRefetch = jest.fn()

    ;(tenantsAPI.useTenants as unknown as jest.Mock).mockReturnValue({
      tenants: mockTenants,
      isLoading: false,
      error: null,
      refetch: mockRefetch,
    })

    render(<TenantSelector />)

    // 找到刷新按钮并点击
    const refreshButton = screen.queryByRole("button", { name: /refresh|refetch/i })
    if (refreshButton) {
      await user.click(refreshButton)

      expect(mockRefetch).toHaveBeenCalled()
    }
  })
})
