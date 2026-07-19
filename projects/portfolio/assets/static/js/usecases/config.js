export const usecaseConfig = {
  debug: false,
  components: {
    'animations.backgroundImages': { enabled: true },
    'spa.activeLinks': { enabled: true },
    'spa.scrollTracking': { enabled: true },
    'landing.activeLinks': { enabled: false },
    'lms.accordion': { enabled: false },
    'lms.tabs': { enabled: false },
    'lms.progress': { enabled: false },
    'crm.activeLinks': { enabled: false },
  },
  usecases: {
    spa: {
      components: {
        'spa.activeLinks': {
          options: {
            activeClass: 'active',
            exactActiveClass: 'is-current',
          },
        },
      },
    },
  },
};
