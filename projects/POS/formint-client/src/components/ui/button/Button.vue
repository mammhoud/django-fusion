<script setup lang="ts">
import { Primitive, type PrimitiveProps } from 'reka-ui';
import { type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';
import { buttonVariants } from './buttonVariants';

type ButtonVariants = VariantProps<typeof buttonVariants>;

interface Props extends PrimitiveProps {
    variant?: ButtonVariants['variant'];
    size?: ButtonVariants['size'];
    class?: string;
}

const props = withDefaults(defineProps<Props>(), {
    as: 'button',
    variant: 'default',
    size: 'default',
});
</script>

<template>
    <Primitive
        :as="as"
        :as-child="asChild"
        :class="cn(buttonVariants({ variant, size }), props.class)"
    >
        <slot />
    </Primitive>
</template>
