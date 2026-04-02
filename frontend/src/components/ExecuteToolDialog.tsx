"use client"

import { Play, Loader2, CheckCircle, XCircle } from "lucide-react"
import { useState } from "react"

import {
  Alert,
  AlertDescription,
} from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import type { Tool } from "@/core/api/tools"
import { executeTool } from "@/core/api/tools"
import { useI18n } from "@/core/i18n/hooks"

/**
 * 执行工具对话框组件
 */
interface ExecuteToolDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  tool: Tool | null
  onSuccess: () => void
}

export function ExecuteToolDialog({ open, onOpenChange, tool, onSuccess }: ExecuteToolDialogProps) {
  const { t } = useI18n()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<unknown>(null)

  const [inputParams, setInputParams] = useState("{}")

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputParams(e.target.value)
    setError(null)
    setResult(null)
  }

  const handleExecute = async () => {
    if (!tool) return

    setIsLoading(true)
    setError(null)
    setResult(null)

    try {
      let params: Record<string, unknown> = {}
      if (inputParams.trim()) {
        try {
          params = JSON.parse(inputParams)
        } catch {
          throw new Error(t.tools.invalidJSONFormat)
        }
      }

      const execution = await executeTool(tool.id, { input_params: params })
      setResult(execution.output)
      
      if (execution.error) {
        setError(execution.error)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setIsLoading(false)
    }
  }

  const handleClose = () => {
    onOpenChange(false)
    // 延迟调用onSuccess，以便父组件刷新数据
    setTimeout(() => {
      onSuccess()
    }, 100)
    
    // 重置状态
    setInputParams("{}")
    setResult(null)
    setError(null)
  }

  const renderResult = () => {
    if (!result && !error) return null

    if (error) {
      return (
        <Alert variant="destructive">
          <XCircle className="h-4 w-4" />
          <AlertDescription>
            <div className="space-y-2">
              <div className="font-medium">{t.tools.executionFailed}</div>
              <pre className="text-xs bg-red-50 p-2 rounded overflow-auto max-h-64">
                {error}
              </pre>
            </div>
          </AlertDescription>
        </Alert>
      )
    }

    if (result) {
      return (
        <Alert variant="default" className="bg-green-50 border-green-200">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertDescription>
            <div className="space-y-2">
              <div className="font-medium text-green-800">{t.tools.executionSuccess}</div>
              <pre className="text-xs bg-green-100 p-2 rounded overflow-auto max-h-64">
                {JSON.stringify(result, null, 2)}
              </pre>
            </div>
          </AlertDescription>
        </Alert>
      )
    }

    return null
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{t.tools.executeTool}</DialogTitle>
          <DialogDescription>
            {t.tools.executeToolDescription.replace("{tool}", tool?.name ?? "")}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* 工具信息 */}
          <div className="bg-muted p-3 rounded">
            <div className="font-medium">{tool?.name}</div>
            <div className="text-sm text-muted-foreground">{tool?.description}</div>
            {tool?.args_schema && (
              <div className="mt-2">
                <div className="text-xs font-medium text-muted-foreground mb-1">
                  {t.tools.expectedParameters}:
                </div>
                <pre className="text-xs bg-background p-2 rounded overflow-auto max-h-32">
                  {JSON.stringify(tool.args_schema, null, 2)}
                </pre>
              </div>
            )}
          </div>

          {/* 输入参数 */}
          <div className="space-y-2">
            <Label htmlFor="input_params">{t.tools.inputParameters}</Label>
            <Textarea
              id="input_params"
              value={inputParams}
              onChange={handleInputChange}
              disabled={isLoading}
              rows={6}
              placeholder='{"key": "value"}'
              className="font-mono text-sm"
            />
            <div className="text-xs text-muted-foreground">
              {t.tools.inputParametersHint}
            </div>
          </div>

          {/* 执行结果或错误 */}
          {renderResult()}

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={handleClose}
              disabled={isLoading}
            >
              {t.common.close}
            </Button>
            <Button onClick={handleExecute} disabled={isLoading || !tool?.enabled}>
              {isLoading ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  {t.tools.executing}
                </>
              ) : (
                <>
                  <Play className="h-4 w-4 mr-2" />
                  {t.tools.executeTool}
                </>
              )}
            </Button>
          </DialogFooter>
        </div>
      </DialogContent>
    </Dialog>
  )
}