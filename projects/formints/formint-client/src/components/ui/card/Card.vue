<script setup lang="ts">
import { cn } from '@/lib/utils';

interface Props {
    class?: string;
}
const props = defineProps<Props>();
</script>

<template>
    <div
        :class="
            cn(
                'rounded-[1.25rem] border border-border/70 bg-card text-card-foreground shadow-[0_24px_48px_-24px_hsl(var(--pos-ink)/0.12)]',
                props.class,
            )
        "
    >
        <slot />
    </div>
</template>
