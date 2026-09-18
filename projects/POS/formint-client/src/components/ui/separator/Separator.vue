<script setup lang="ts">
import { Separator as SeparatorPrimitive } from 'reka-ui';
import { cn } from '@/lib/utils';

interface Props {
    class?: string;
    orientation?: 'horizontal' | 'vertical';
    decorative?: boolean;
}
const props = withDefaults(defineProps<Props>(), {
    orientation: 'horizontal',
    decorative: true,
});
</script>

<template>
    <SeparatorPrimitive
        :class="
            cn(
                'shrink-0 bg-border',
                props.orientation === 'vertical' ? 'h-full w-px' : 'h-px w-full',
                props.class,
            )
        "
        :orientation="props.orientation"
        :decorative="props.decorative"
    />
</template>
