<script setup lang="ts">
import { cn } from '@/lib/utils';

interface Props {
    class?: string;
    type?: string;
    placeholder?: string;
}
const props = withDefaults(defineProps<Props>(), {
    type: 'text',
    placeholder: '',
});

const model = defineModel<string>();
</script>

<template>
    <input
        v-model="model"
        :type="props.type"
        :placeholder="props.placeholder"
        :class="
            cn(
                'flex h-10 w-full rounded-xl border border-input bg-background px-3.5 py-2 text-sm shadow-sm transition-all duration-300 placeholder:text-muted-foreground/70 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/40 disabled:cursor-not-allowed disabled:opacity-50 file:border-0 file:bg-transparent file:text-sm file:font-medium file:text-foreground',
                props.class,
            )
        "
    />
</template>
