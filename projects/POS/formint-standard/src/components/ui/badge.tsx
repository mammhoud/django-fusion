import { mergeProps } from "@base-ui/react/merge-props"
import { useRender } from "@base-ui/react/use-render"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const badgeVariants = cva(
  "group/badge inline-flex h-5 w-fit shrink-0 items-center justify-center gap-1 overflow-hidden rounded-4xl border border-transparent px-2 py-0.5 text-xs font-medium whitespace-nowrap transition-all focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50 has-data-[icon=inline-end]:pr-1.5 has-data-[icon=inline-start]:pl-1.5 aria-invalid:border-destructive aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 [&>svg]:pointer-events-none [&>svg]:size-3!",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground [a]:hover:bg-primary/80",
        secondary:
          "bg-secondary text-secondary-foreground [a]:hover:bg-secondary/80",
        destructive:
          "bg-destructive/10 text-destructive focus-visible:ring-destructive/20 dark:bg-destructive/20 dark:focus-visible:ring-destructive/40 [a]:hover:bg-destructive/20",
        outline:
          "border-border text-foreground [a]:hover:bg-muted [a]:hover:text-muted-foreground",
        ghost:
          "hover:bg-muted hover:text-muted-foreground dark:hover:bg-muted/50",
        link: "text-primary underline-offset-4 hover:underline",
        // ── Semantic states (Formint design language — verdigris/amber) ──
        success: "bg-success text-success-content [a]:hover:bg-success/80",
        warning: "bg-warning text-warning-content [a]:hover:bg-warning/80",
        info: "bg-info text-info-content [a]:hover:bg-info/80",
        neutral: "bg-neutral text-neutral-content [a]:hover:bg-neutral/80",
        // ── Soft variants — translucent tint so they read in both modes ──
        "soft": "bg-primary/10 text-primary [a]:hover:bg-primary/15",
        "soft-secondary": "bg-secondary/10 text-secondary [a]:hover:bg-secondary/15",
        "soft-success": "bg-success/10 text-success [a]:hover:bg-success/15",
        "soft-warning": "bg-warning/15 text-warning [a]:hover:bg-warning/20",
        "soft-info": "bg-info/10 text-info [a]:hover:bg-info/15",
        "soft-neutral": "bg-neutral/10 text-neutral [a]:hover:bg-neutral/15",
        "soft-destructive": "bg-destructive/10 text-destructive [a]:hover:bg-destructive/15",
      },
      size: {
        default: "h-5 px-2 py-0.5 text-xs",
        sm: "h-4 px-1.5 text-[10px]",
        lg: "h-6 px-2.5 py-1 text-sm",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

function Badge({
  className,
  variant = "default",
  size = "default",
  render,
  ...props
}: useRender.ComponentProps<"span"> & VariantProps<typeof badgeVariants>) {
  return useRender({
    defaultTagName: "span",
    props: mergeProps<"span">(
      {
        className: cn(badgeVariants({ variant, size }), className),
      },
      props
    ),
    render,
    state: {
      slot: "badge",
      variant,
      size,
    },
  })
}

export { Badge, badgeVariants }
