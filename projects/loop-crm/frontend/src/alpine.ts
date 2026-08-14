import Alpine from 'alpinejs';
import collapse from '@alpinejs/collapse';
import intersect from '@alpinejs/intersect';

// Loop-CRM Alpine entrypoint — Collapse + Intersect are required for
// x-collapse accordions and x-intersect reveals to behave (same as
// landing-fusion's src/alpine.ts).
Alpine.plugin(collapse);
Alpine.plugin(intersect);

window.Alpine = Alpine;
Alpine.start();
