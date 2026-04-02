"use client"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Separator } from "@/components/ui/separator"
import type { Tool } from "@/core/api/tools"
import { useI18n } from "@/core/i18n/hooks"

/**
 * 查看工具详情对话框组件
 */
interface ViewToolDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  tool: Tool | null
}

export function ViewToolDialog({ open, onOpenChange, tool }: ViewToolDialogProps) {
  const { t } = useI18n()

  if (!tool) return null

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

  const renderTypeBadge = (toolType: string) => {
    const variants: Record<string, "default" | "secondary" | "outline" | "destructive"> = {
      custom: "default",
      mcp: "secondary",
      builtin: "outline",
      agent: "default",
    }
    return <Badge variant={variants[toolType] ?? "outline"}>{toolType}</Badge>
  }

  const formatDate = (dateString?: string) => {
    if (!dateString) return "-"
    return new Date(dateString).toLocaleString()
  }

  const formatJSON = (obj?: Record<string, unknown>) => {
    if (!obj) return "-"
    return JSON.stringify(obj, null, 2)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{t.tools.toolDetails}</DialogTitle>
          <DialogDescription>
            {t.tools.toolDetailsDescription}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* 基本信息 */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">{tool.name}</h3>
              <div className="flex items-center space-x-2">
                {renderTypeBadge(tool.tool_type)}
                {renderStatusBadge(tool.enabled)}
              </div>
            </div>
            
            <p className="text-sm text-muted-foreground">{tool.description}</p>
          </div>

          <Separator />

          {/* 详细信息 */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <div className="text-sm font-medium text-muted-foreground">{t.tools.category}</div>
              <div>{tool.category}</div>
            </div>

            <div className="space-y-2">
              <div className="text-sm font-medium text-muted-foreground">{t.tools.version}</div>
              <div>{tool.version}</div>
            </div>

            <div className="space-y-2">
              <div className="text-sm font-medium text-muted-foreground">{t.tools.modulePath}</div>
              <div className="font-mono text-sm">{tool.module_path}</div>
            </div>

            <div className="space-y-2">
              <div className="text-sm font-medium text-muted-foreground">{t.tools.className}</div>
              <div className="font-mono text-sm">{tool.class_name}</div>
            </div>

            <div className="space-y-2">
              <div className="text-sm font-medium text-muted-foreground">{t.tools.createdAt}</div>
              <div>{formatDate(tool.created_at)}</div>
            </div>

            <div className="space-y-2">
              <div className="text-sm font-medium text-muted-foreground">{t.tools.updatedAt}</div>
              <div>{formatDate(tool.updated_at)}</div>
            </div>

            <div className="space-y-2">
              <div className="text-sm font-medium text-muted-foreground">{t.tools.isBuiltin}</div>
              <div>{tool.is_builtin ? t.common.yes : t.common.no}</div>
            </div>

            <div className="space-y-2">
              <div className="text-sm font-medium text-muted-foreground">{t.tools.isSystem}</div>
              <div>{tool.is_system ? t.common.yes : t.common.no}</div>
            </div>

            <div className="space-y-2">
              <div className="text-sm font-medium text-muted-foreground">{t.tools.tenantScoped}</div>
              <div>{tool.tenant_scoped ? t.common.yes : t.common.no}</div>
            </div>

            <div className="space-y-2">
              <div className="text-sm font-medium text-muted-foreground">{t.tools.createdFromConfig}</div>
              <div>{tool.created_from_config ?? "-"}</div>
            </div>
          </div>

          <Separator />

          {/* 标签和角色 */}
          <div className="space-y-4">
            <div className="space-y-2">
              <div className="text-sm font-medium text-muted-foreground">{t.tools.tags}</div>
              <div className="bg-muted p-3 rounded font-mono text-sm">
                {formatJSON(tool.tags)}
              </div>
            </div>

            <div className="space-y-2">
              <div className="text-sm font-medium text-muted-foreground">{t.tools.argsSchema}</div>
              <div className="bg-muted p-3 rounded font-mono text-sm max-h-40 overflow-auto">
                {formatJSON(tool.args_schema)}
              </div>
            </div>

            <div className="space-y-2">
              <div className="text-sm font-medium text-muted-foreground">{t.tools.requiredRoles}</div>
              <div className="flex flex-wrap gap-1">
                {tool.required_roles && tool.required_roles.length > 0 ? (
                  tool.required_roles.map((role) => (
                    <Badge key={role} variant="outline">{role}</Badge>
                  ))
                ) : (
                  <span className="text-muted-foreground">{t.common.none}</span>
                )}
              </div>
            </div>
          </div>

          <Separator />

          {/* 统计信息 */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">{t.tools.statistics}</h3>
            <div className="grid grid-cols-4 gap-4">
              <div className="bg-muted p-4 rounded-lg text-center">
                <div className="text-2xl font-bold">{tool.total_executions}</div>
                <div className="text-sm text-muted-foreground">{t.tools.totalExecutions}</div>
              </div>
              <div className="bg-muted p-4 rounded-lg text-center">
                <div className="text-2xl font-bold text-green-600">{tool.successful_executions}</div>
                <div className="text-sm text-muted-foreground">{t.tools.successfulExecutions}</div>
              </div>
              <div className="bg-muted p-4 rounded-lg text-center">
                <div className="text-2xl font-bold text-red-600">{tool.failed_executions}</div>
                <div className="text-sm text-muted-foreground">{t.tools.failedExecutions}</div>
              </div>
              <div className="bg-muted p-4 rounded-lg text-center">
                <div className="text-2xl font-bold">
                  {tool.total_executions > 0 ? ((tool.successful_executions / tool.total_executions) * 100).toFixed(1) : "0"}%
                </div>
                <div className="text-sm text-muted-foreground">{t.tools.successRate}</div>
              </div>
            </div>

            {tool.avg_execution_time && (
              <div className="text-sm text-muted-foreground">
                {t.tools.avgExecutionTime}: {tool.avg_execution_time.toFixed(2)}s
              </div>
            )}

            {tool.last_executed_at && (
              <div className="text-sm text-muted-foreground">
                {t.tools.lastExecutedAt}: {formatDate(tool.last_executed_at)}
              </div>
            )}
          </div>

          {tool.version_notes && (
            <>
              <Separator />
              <div className="space-y-2">
                <div className="text-sm font-medium text-muted-foreground">{t.tools.versionNotes}</div>
                <div className="text-sm">{tool.version_notes}</div>
              </div>
            </>
          )}
        </div>

        <DialogFooter>
          <Button onClick={() => onOpenChange(false)}>
            {t.common.close}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}