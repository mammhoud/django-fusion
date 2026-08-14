import { useNuxt } from '@nuxt/kit'

export default defineNuxtConfig({
  extends: ['docus'],
  modules: [
    '@nuxtjs/i18n',
    // Docus registers its own locale/sitemap prerender hooks. Register this
    // final inline module after the layer modules so this deployment remains a
    // Nuxt server build instead of crawling hundreds of content pages.
    () => {
      const nuxt = useNuxt()
      nuxt.hook('nitro:config', (nitroConfig) => {
        nitroConfig.prerender = {
          crawlLinks: false,
          routes: [],
          failOnError: false,
        }
      })
      nuxt.hook('prerender:routes', ({ routes }) => {
        routes.clear()
      })
    },
  ],

  // The same generated site is served at /docs/ on media.structa.cloud and
  // at the root of docs.structa.cloud after Traefik removes /docs.
  app: {
    baseURL: process.env.NUXT_APP_BASE_URL || '/docs/',
  },

  i18n: {
    defaultLocale: 'en',
    strategy: 'prefix',
    locales: [
      { code: 'en', name: 'English', dir: 'ltr' },
      { code: 'ar', name: 'العربية', dir: 'rtl' },
    ],
    detectBrowserLanguage: {
      useCookie: true,
      cookieKey: 'structa-docs-locale',
      redirectOn: 'root',
    },
  },

  css: ['~/assets/css/docus.css'],

  // A prefixed site cannot safely emit its own robots.txt from the build;
  // the edge proxy owns that concern.
  robots: {
    robotsTxt: false,
  },

  // Keep Docus' LLM-ready output useful without requiring a deployment secret.
  llms: {
    domain: 'https://docs.structa.cloud',
    title: 'Structa Cloud Documentation',
    description: 'Engineering and product documentation for Structa Cloud.',
  },

  // The production deployment is a Nuxt server. Docus defaults to crawling
  // every content link during `nuxt build`, which is too expensive for this
  // repository-sized documentation tree and is unnecessary for SSR. Keep the
  // content database/search server-side and render routes on demand.
  nitro: {
    prerender: {
      crawlLinks: false,
      routes: [],
      failOnError: false,
    },
  },

  compatibilityDate: '2026-08-14',
});
