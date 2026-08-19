export default defineAppConfig({
  site: {
    name: 'Structa Cloud Documentation',
  },

  seo: {
    title: 'Structa Cloud Documentation',
    description:
      'Engineering guides, architecture references, deployment runbooks, and product documentation for Structa Cloud.',
    titleTemplate: '%s · Structa Cloud',
  },

  header: {
    title: 'Structa Cloud',
    logo: {
      light: '/logo/structa-mark.svg',
      dark: '/logo/structa-mark.svg',
      alt: 'Structa Cloud',
      favicon: '/logo/structa-mark.svg',
    },
  },

  docus: {
    locale: 'en',
    colorMode: 'dark',
    shortcuts: {
      toggleColorMode: 'd',
    },
  },

  navigation: {
    sub: 'header',
  },

  search: {
    fts: true,
  },

  toc: {
    title: 'On this page',
  },

  github: {
    url: 'https://github.com/mammhoud/structa.cloud',
    branch: 'generic',
    rootDir: 'docs',
  },

  socials: {
    github: 'https://github.com/mammhoud/structa.cloud',
  },
});
