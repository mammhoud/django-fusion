import type Alpine from 'alpinejs';
import collapse from '@alpinejs/collapse';
import intersect from '@alpinejs/intersect';

// Loop-CRM Alpine entrypoint — Collapse + Intersect are required for
// x-collapse accordions and x-intersect reveals to behave (same as
// landing-fusion's src/alpine.ts). @astrojs/alpinejs calls this default
// export with Alpine and starts Alpine itself on DOMContentLoaded, so we
// must NOT call Alpine.start() here (that would initialize it twice).
export default function loopAlpine(alpine: typeof Alpine) {
  alpine.plugin(collapse);
  alpine.plugin(intersect);
}
