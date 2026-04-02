"use client"

import { Plus, Search, MoreVertical, Edit, Trash2, Play, Eye } from "lucide-react"
import { useState } from "react"

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Input } from "@/components/ui/input"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import type { Tool } from "@/core/api/tools"
import { useTools } from "@/core/api/tools"
import { useI18n } from "@/core/i18n/hooks"

// 导入对话框组件
import { EditToolDialog } from "./EditToolDialog"
import { ExecuteToolDialog } from "./ExecuteToolDialog"
import { CreateToolDialog } from "./ToolCreateDialog"
import { ViewToolDialog } from "./ViewToolDialog"

/**
 * 工具管理列表组件
 *
 * 功能：
 * - 显示工具列表，支持搜索和过滤
 * - 工具操作：查看详情、编辑、删除、执行
 * - 分页显示
 * - 创建新工具
 */
export function ToolManagementPanel() {
  const { t } = useI18n()
  const { tools, isLoading, error, pagination, updateParams, refetch } = useTools()
  
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedTool, setSelectedTool] = useState<Tool | null>(null)
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [isViewDialogOpen, setIsViewDialogOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)
  const [isExecuteDialogOpen, setIsExecuteDialogOpen] = useState(false)

  // 搜索处理
  const handleSearch = (value: string) => {
    setSearchQuery(value)
    updateParams({ search: value, page: 1 }) // 重置到第一页
  }

  // 工具操作处理
  const handleViewTool = (tool: Tool) => {
    setSelectedTool(tool)
    setIsViewDialogOpen(true)
  }

  const handleEditTool = (tool: Tool) => {
    setSelectedTool(tool)
    setIsEditDialogOpen(true)
  }

  const handleDeleteTool = (tool: Tool) => {
    setSelectedTool(tool)
    setIsDeleteDialogOpen(true)
  }

  const handleExecuteTool = (tool: Tool) => {
    setSelectedTool(tool)
    setIsExecuteDialogOpen(true)
  }

  const handleCreateNew = () => {
    setIsCreateDialogOpen(true)
  }

  const handleToolCreated = () => {
    setIsCreateDialogOpen(false)
    refetch()
  }

  const handleToolUpdated = () => {
    setIsEditDialogOpen(false)
    refetch()
  }

  const handleToolDeleted = async () => {
    if (!selectedTool) return
    try {
      // TODO: 调用删除API
      // await deleteTool(selectedTool.id)
      refetch()
    } catch (err) {
      console.error("Failed to delete tool:", err)
    } finally {
      setIsDeleteDialogOpen(false)
      setSelectedTool(null)
    }
  }

  const handleToolExecuted = () => {
    setIsExecuteDialogOpen(false)
    refetch()
  }

  // 渲染状态标签
  const renderStatusBadge = (enabled: boolean) => {
    return enabled ? (
      <Badge variant="default" className="bg-green-500">
        {t.tools.enabled}
      </Badge>
    ) : (
      <Badge variant="secondary" className="bg-gray-500">
        {t.tools.disabled}
      </Badge>
    )
  }

  // 渲染工具类型标签
  const renderTypeBadge = (toolType: string) => {
    const variants: Record<string, "default" | "secondary" | "outline" | "destructive"> = {
      custom: "default",
      mcp: "secondary",
      builtin: "outline",
      agent: "default",
    }
    return <Badge variant={variants[toolType] ?? "outline"}>{toolType}</Badge>
  }

  if (isLoading && tools.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          <p className="mt-2 text-sm text-muted-foreground">{t.common.loading}</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <p className="text-red-500">{t.common.error}: {error.message}</p>
          <Button onClick={refetch} variant="outline" className="mt-2">
            {t.common.retry}
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* 头部操作栏 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className="relative w-64">
            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder={t.tools.searchPlaceholder}
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              className="pl-8"
            />
          </div>
        </div>
        <Button onClick={handleCreateNew}>
          <Plus className="h-4 w-4 mr-2" />
          {t.tools.createTool}
        </Button>
      </div>

      {/* 工具列表 */}
      <Card>
        <CardHeader>
            <CardTitle>{t.tools.toolList} ({pagination.total ?? 0})</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{t.tools.name}</TableHead>
                <TableHead>{t.tools.type}</TableHead>
                <TableHead>{t.tools.category}</TableHead>
                <TableHead>{t.tools.status}</TableHead>
                <TableHead>{t.tools.executions}</TableHead>
                <TableHead>{t.tools.version}</TableHead>
                <TableHead className="text-right">{t.common.actions}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {tools.map((tool) => (
                <TableRow key={tool.id}>
                  <TableCell>
                    <div>
                      <div className="font-medium">{tool.name}</div>
                      <div className="text-sm text-muted-foreground truncate max-w-xs">
                        {tool.description}
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>{renderTypeBadge(tool.tool_type)}</TableCell>
                  <TableCell>{tool.category}</TableCell>
                  <TableCell>{renderStatusBadge(tool.enabled)}</TableCell>
                  <TableCell>
                    <div className="text-sm">
                      <div>{tool.total_executions}</div>
                      <div className="text-xs text-muted-foreground">
                        {t.tools.successRate}: {tool.total_executions > 0 ? ((tool.successful_executions / tool.total_executions) * 100).toFixed(1) : 0}%
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>{tool.version}</TableCell>
                  <TableCell className="text-right">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="sm">
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => handleViewTool(tool)}>
                          <Eye className="h-4 w-4 mr-2" />
                          {t.common.view}
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => handleEditTool(tool)}>
                          <Edit className="h-4 w-4 mr-2" />
                          {t.common.edit}
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => handleExecuteTool(tool)}>
                          <Play className="h-4 w-4 mr-2" />
                          {t.tools.executeTool}
                        </DropdownMenuItem>
                        <DropdownMenuItem 
                          onClick={() => handleDeleteTool(tool)}
                          className="text-red-600"
                        >
                          <Trash2 className="h-4 w-4 mr-2" />
                          {t.common.delete}
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>

          {tools.length === 0 && (
            <div className="text-center py-8 text-muted-foreground">
              {t.tools.noToolsFound}
            </div>
          )}
        </CardContent>
      </Card>

      {/* 分页 */}
      {pagination.total_pages > 1 && (
        <div className="flex items-center justify-between">
          <div className="text-sm text-muted-foreground">
            {t.common.showing} {pagination.page} / {pagination.total_pages} ({t.common.total} {pagination.total})
          </div>
          <div className="flex space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => updateParams({ page: pagination.page - 1 })}
              disabled={pagination.page <= 1}
            >
              {t.common.previous}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => updateParams({ page: pagination.page + 1 })}
              disabled={pagination.page >= pagination.total_pages}
            >
              {t.common.next}
            </Button>
          </div>
        </div>
      )}

      {/* 创建工具对话框 */}
      <CreateToolDialog
        open={isCreateDialogOpen}
        onOpenChange={setIsCreateDialogOpen}
        onSuccess={handleToolCreated}
      />

      {/* 查看工具对话框 */}
      <ViewToolDialog
        open={isViewDialogOpen}
        onOpenChange={setIsViewDialogOpen}
        tool={selectedTool}
      />

      {/* 编辑工具对话框 */}
      <EditToolDialog
        open={isEditDialogOpen}
        onOpenChange={setIsEditDialogOpen}
        tool={selectedTool}
        onSuccess={handleToolUpdated}
      />

      {/* 删除确认对话框 */}
      <AlertDialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>{t.tools.confirmDeleteTitle}</AlertDialogTitle>
            <AlertDialogDescription>
              {t.tools.confirmDeleteDescription.replace("{name}", selectedTool?.name ?? "")}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>{t.common.cancel}</AlertDialogCancel>
            <AlertDialogAction onClick={handleToolDeleted} className="bg-red-600 hover:bg-red-700">
              {t.common.delete}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* 执行工具对话框 */}
      <ExecuteToolDialog
        open={isExecuteDialogOpen}
        onOpenChange={setIsExecuteDialogOpen}
        tool={selectedTool}
        onSuccess={handleToolExecuted}
      />
    </div>
  )
}