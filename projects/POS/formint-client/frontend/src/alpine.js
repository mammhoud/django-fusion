// Alpine entrypoint for the Formint Café storefront — registers the
// Intersect + Collapse plugins (consumed via astro.config.mjs as '@/alpine').
import intersect from '@alpinejs/intersect';
import collapse from '@alpinejs/collapse';

export default function setup(alpine) {
  alpine.plugin(intersect);
  alpine.plugin(collapse);
}
