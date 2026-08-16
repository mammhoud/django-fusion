import { cva } from 'class-variance-authority';

export const badgeVariants = cva(
    'inline-flex items-center rounded-full border px-2.5 py-0.5 text-[0.65rem] font-semibold uppercase tracking-widest transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2',
    {
        variants: {
            variant: {
                default: 'border-transparent bg-primary text-primary-foreground shadow',
                secondary: 'border-transparent bg-secondary text-secondary-foreground',
                destructive:
                    'border-transparent bg-destructive text-destructive-foreground shadow',
                outline: 'border-border text-foreground',
                success: 'border-transparent bg-success/15 text-success',
                warning: 'border-transparent bg-warning/15 text-warning',
            },
        },
        defaultVariants: {
            variant: 'default',
        },
    },
);
