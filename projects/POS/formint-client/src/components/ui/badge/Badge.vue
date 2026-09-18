<script setup lang="ts">
import { type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';
import { badgeVariants } from './badgeVariants';

type BadgeVariants = VariantProps<typeof badgeVariants>;

interface Props {
    variant?: BadgeVariants['variant'];
    class?: string;
}
const props = withDefaults(defineProps<Props>(), {
    variant: 'default',
});
</script>

<template>
    <div :class="cn(badgeVariants({ variant }), props.class)">
        <slot />
    </div>
</template>
