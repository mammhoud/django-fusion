export const usecaseConfig = {
  debug: false,
  components: {
    'landing.transparentHeaders': { enabled: true },
    'landing.scrollTracking': { enabled: true },
    'lms.accordion': { enabled: true },
    'lms.tabs': { enabled: true },
    'lms.progress': { enabled: true },
    'crm.activeLinks': { enabled: false },
  },
  usecases: {
    landing: {
      components: {
        'landing.activeLinks': { options: { activeClass: 'active' } },
      },
    },
    lms: {
      components: {
        'lms.accordion': { options: { containerSelector: '.lms-shell .accordion' } },
      },
    },
  },
};
