"use client"

import * as React from "react"
import { X } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"

interface AlertDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  children: React.ReactNode
}

const AlertDialog = React.forwardRef<HTMLDivElement, AlertDialogProps>(
  ({ open, onOpenChange, children }, ref) => {
    if (!open) return null

    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center">
        <div 
          className="fixed inset-0 bg-black/50" 
          onClick={() => onOpenChange(false)}
        />
        <div ref={ref} className="relative z-50 w-full max-w-lg p-4">
          {children}
        </div>
      </div>
    )
  }
)
AlertDialog.displayName = "AlertDialog"

interface AlertDialogContentProps extends React.HTMLAttributes<HTMLDivElement> {}

const AlertDialogContent = React.forwardRef<HTMLDivElement, AlertDialogContentProps>(
  ({ className, children, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        "relative bg-background p-6 rounded-lg shadow-lg",
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
)
AlertDialogContent.displayName = "AlertDialogContent"

interface AlertDialogHeaderProps extends React.HTMLAttributes<HTMLDivElement> {}

const AlertDialogHeader = React.forwardRef<HTMLDivElement, AlertDialogHeaderProps>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn("flex flex-col space-y-2 text-center sm:text-left", className)}
      {...props}
    />
  )
)
AlertDialogHeader.displayName = "AlertDialogHeader"

interface AlertDialogFooterProps extends React.HTMLAttributes<HTMLDivElement> {}

const AlertDialogFooter = React.forwardRef<HTMLDivElement, AlertDialogFooterProps>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        "flex flex-col-reverse sm:flex-row sm:justify-end sm:space-x-2",
        className
      )}
      {...props}
    />
  )
)
AlertDialogFooter.displayName = "AlertDialogFooter"

interface AlertDialogTitleProps extends React.HTMLAttributes<HTMLHeadingElement> {}

const AlertDialogTitle = React.forwardRef<HTMLHeadingElement, AlertDialogTitleProps>(
  ({ className, ...props }, ref) => (
    <h2
      ref={ref}
      className={cn("text-lg font-semibold", className)}
      {...props}
    />
  )
)
AlertDialogTitle.displayName = "AlertDialogTitle"

interface AlertDialogDescriptionProps extends React.HTMLAttributes<HTMLParagraphElement> {}

const AlertDialogDescription = React.forwardRef<HTMLParagraphElement, AlertDialogDescriptionProps>(
  ({ className, ...props }, ref) => (
    <p
      ref={ref}
      className={cn("text-sm text-muted-foreground", className)}
      {...props}
    />
  )
)
AlertDialogDescription.displayName = "AlertDialogDescription"

interface AlertDialogActionProps extends React.ComponentPropsWithoutRef<typeof Button> {}

const AlertDialogAction = React.forwardRef<HTMLButtonElement, AlertDialogActionProps>(
  ({ className, ...props }, ref) => (
    <Button
      ref={ref}
      className={cn("bg-red-600 hover:bg-red-700", className)}
      {...props}
    />
  )
)
AlertDialogAction.displayName = "AlertDialogAction"

interface AlertDialogCancelProps extends React.ComponentPropsWithoutRef<typeof Button> {}

const AlertDialogCancel = React.forwardRef<HTMLButtonElement, AlertDialogCancelProps>(
  ({ className, ...props }, ref) => (
    <Button
      ref={ref}
      variant="outline"
      {...props}
    />
  )
)
AlertDialogCancel.displayName = "AlertDialogCancel"

export {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
}