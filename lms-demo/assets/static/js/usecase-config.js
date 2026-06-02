export const usecaseConfig = {
  debug: false,
  components: {
    'landing.transparentHeaders': { enabled: false },
    'landing.scrollTracking': { enabled: true },
    'lms.accordion': { enabled: true },
    'lms.tabs': { enabled: true },
    'lms.progress': { enabled: true },
    'crm.activeLinks': { enabled: false },
  },
  usecases: {
    lms: {
      components: {
        'lms.progress': {
          selectors: ['.lms-shell [data-progress]', '.lms-shell .animated-progress'],
        },
      },
    },
  },
};
