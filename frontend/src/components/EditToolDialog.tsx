"use client"

import { useState, useEffect } from "react"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"
import { Textarea } from "@/components/ui/textarea"
import type { Tool } from "@/core/api/tools"
import { updateTool } from "@/core/api/tools"
import { useI18n } from "@/core/i18n/hooks"

/**
 * 编辑工具对话框组件
 */
interface EditToolDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  tool: Tool | null
  onSuccess: () => void
}

export function EditToolDialog({ open, onOpenChange, tool, onSuccess }: EditToolDialogProps) {
  const { t } = useI18n()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [formData, setFormData] = useState({
    name: "",
    description: "",
    tool_type: "custom" as "custom" | "mcp" | "builtin" | "agent",
    category: "",
    module_path: "",
    class_name: "",
    args_schema: "",
    enabled: true,
    tenant_scoped: false,
    required_roles: "",
    version: "1.0.0",
    version_notes: "",
  })

  // 当tool变化时更新表单
  useEffect(() => {
    if (tool) {
      setFormData({
        name: tool.name,
        description: tool.description,
        tool_type: tool.tool_type as "custom" | "mcp" | "builtin" | "agent",
        category: tool.category,
        module_path: tool.module_path,
        class_name: tool.class_name,
        args_schema: tool.args_schema ? JSON.stringify(tool.args_schema, null, 2) : "",
        enabled: tool.enabled,
        tenant_scoped: tool.tenant_scoped,
        required_roles: tool.required_roles?.join(", ") ?? "",
        version: tool.version,
        version_notes: tool.version_notes ?? "",
      })
    }
  }, [tool])

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value, type } = e.target
    if (type === "checkbox") {
      const checked = (e.target as HTMLInputElement).checked
      setFormData((prev) => ({ ...prev, [name]: checked }))
    } else {
      setFormData((prev) => ({ ...prev, [name]: value }))
    }
  }

  const handleSelectChange = (name: string, value: string) => {
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!tool) return

    setIsLoading(true)
    setError(null)

    try {
      const updateData: Partial<Tool> = {
        name: formData.name,
        description: formData.description,
        tool_type: formData.tool_type,
        category: formData.category,
        module_path: formData.module_path,
        class_name: formData.class_name,
        enabled: formData.enabled,
        tenant_scoped: formData.tenant_scoped,
        version: formData.version,
      }

      // 可选字段
      if (formData.args_schema) {
        try {
          updateData.args_schema = JSON.parse(formData.args_schema)
        } catch {
          throw new Error(t.tools.invalidJSONFormat)
        }
      }

      if (formData.required_roles) {
        updateData.required_roles = formData.required_roles.split(",").map(r => r.trim())
      }

      if (formData.version_notes) {
        updateData.version_notes = formData.version_notes
      }

      await updateTool(tool.id, updateData)
      onSuccess()
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setIsLoading(false)
    }
  }

  if (!tool) return null

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{t.tools.editTool}</DialogTitle>
          <DialogDescription>
            {t.tools.editToolDescription}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="p-3 text-sm text-red-500 bg-red-50 border border-red-200 rounded">
              {error}
            </div>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="name">{t.tools.name} *</Label>
              <Input
                id="name"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                required
                disabled={isLoading}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="tool_type">{t.tools.type} *</Label>
              <Select
                value={formData.tool_type}
                onValueChange={(value) => handleSelectChange("tool_type", value)}
                disabled={isLoading}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="custom">{t.tools.types.custom}</SelectItem>
                  <SelectItem value="mcp">{t.tools.types.mcp}</SelectItem>
                  <SelectItem value="builtin">{t.tools.types.builtin}</SelectItem>
                  <SelectItem value="agent">{t.tools.types.agent}</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">{t.tools.description} *</Label>
            <Textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              required
              disabled={isLoading}
              rows={3}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="category">{t.tools.category} *</Label>
              <Input
                id="category"
                name="category"
                value={formData.category}
                onChange={handleInputChange}
                required
                disabled={isLoading}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="version">{t.tools.version}</Label>
              <Input
                id="version"
                name="version"
                value={formData.version}
                onChange={handleInputChange}
                disabled={isLoading}
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="module_path">{t.tools.modulePath} *</Label>
              <Input
                id="module_path"
                name="module_path"
                value={formData.module_path}
                onChange={handleInputChange}
                required
                disabled={isLoading}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="class_name">{t.tools.className} *</Label>
              <Input
                id="class_name"
                name="class_name"
                value={formData.class_name}
                onChange={handleInputChange}
                required
                disabled={isLoading}
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="args_schema">{t.tools.argsSchema}</Label>
            <Textarea
              id="args_schema"
              name="args_schema"
              value={formData.args_schema}
              onChange={handleInputChange}
              disabled={isLoading}
              rows={4}
              placeholder='{"type": "object", "properties": {...}}'
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="required_roles">{t.tools.requiredRoles}</Label>
            <Input
              id="required_roles"
              name="required_roles"
              value={formData.required_roles}
              onChange={handleInputChange}
              disabled={isLoading}
              placeholder="admin, user, viewer"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="version_notes">{t.tools.versionNotes}</Label>
            <Textarea
              id="version_notes"
              name="version_notes"
              value={formData.version_notes}
              onChange={handleInputChange}
              disabled={isLoading}
              rows={2}
            />
          </div>

          <div className="flex items-center space-x-6">
            <div className="flex items-center space-x-2">
              <Switch
                id="enabled"
                name="enabled"
                checked={formData.enabled}
                onCheckedChange={(checked) => setFormData((prev) => ({ ...prev, enabled: checked }))}
                disabled={isLoading}
              />
              <Label htmlFor="enabled">{t.tools.enabled}</Label>
            </div>

            <div className="flex items-center space-x-2">
              <Switch
                id="tenant_scoped"
                name="tenant_scoped"
                checked={formData.tenant_scoped}
                onCheckedChange={(checked) => setFormData((prev) => ({ ...prev, tenant_scoped: checked }))}
                disabled={isLoading}
              />
              <Label htmlFor="tenant_scoped">{t.tools.tenantScoped}</Label>
            </div>
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={isLoading}
            >
              {t.common.cancel}
            </Button>
            <Button type="submit" disabled={isLoading}>
              {isLoading ? t.common.saving : t.common.save}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}