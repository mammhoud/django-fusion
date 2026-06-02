import { getComponentOverride, isComponentEnabled, mergeConfig } from './config.js';

const DEFAULT_COMPONENTS = new Map([
  ['animations.pageLoader', {
    usecase: 'animations',
    selectors: ['body'],
    loader: () => import('../plugins/pageLoader.js'),
    className: 'PageLoaderHandler',
    once: true,
  }],
  ['animations.backgroundImages', {
    usecase: 'animations',
    selectors: ['[data-bg-src]', '[data-background]'],
    loader: () => import('../plugins/backgroundImages.js'),
    className: 'BackgroundImages',
    once: true,
  }],
  ['landing.activeLinks', {
    usecase: 'landing',
    selectors: ['.landing-shell a[href]', '[data-usecase~="landing"] a[href]'],
    loader: () => import('../plugins/active-links.js'),
    className: 'ActiveLinksPlugin',
    once: true,
  }],
  ['landing.transparentHeaders', {
    usecase: 'landing',
    selectors: ['.transparent-light', '.transparent-dark'],
    loader: () => import('../plugins/transparentHeaders.js'),
    className: 'TransparentHeadersHandler',
    once: true,
  }],
  ['landing.scrollTracking', {
    usecase: 'landing',
    selectors: ['.landing-shell__section', '[data-scroll-track]'],
    loader: () => import('../plugins/scrollTracking.js'),
    className: 'ScrollTrackingPlugin',
    once: true,
  }],
  ['lms.accordion', {
    usecase: 'lms',
    selectors: ['.lms-shell .accordion', '.lms-shell [data-accordion]'],
    loader: () => import('../modules/components/accordion.init.js'),
    className: 'Accordion',
    once: true,
  }],
  ['lms.tabs', {
    usecase: 'lms',
    selectors: ['.lms-shell [data-tabs]', '.lms-shell .nav-tabs'],
    loader: () => import('../modules/components/tabs.init.js'),
    className: 'Tabs',
    once: true,
  }],
  ['lms.progress', {
    usecase: 'lms',
    selectors: ['.lms-shell .animated-progress', '.lms-shell [data-progress]'],
    loader: () => import('../modules/components/progress.init.js'),
    className: 'Progress',
    once: true,
  }],
  ['crm.activeLinks', {
    usecase: 'crm',
    selectors: ['.crm-shell a[href]', '[data-usecase~="crm"] a[href]'],
    loader: () => import('../plugins/active-links.js'),
    className: 'ActiveLinksPlugin',
    once: true,
  }],
  ['forms.manager', {
    usecase: 'forms',
    selectors: ['.form-stack form', '[data-usecase~="forms"] form'],
    loader: () => import('../modules/forms/formsManager.js'),
    className: 'FormsManager',
    once: true,
  }],
  ['modal.controller', {
    usecase: 'modal',
    selectors: ['.modal-shell__dialog', '.modal-dialog', '[data-modal-dialog]'],
    loader: () => import('../modules/components/modal.init.js'),
    className: 'ModalController',
  }],
  ['spa.activeLinks', {
    usecase: 'spa',
    selectors: ['.spa-shell a[href]', '[data-usecase~="spa"] a[href]'],
    loader: () => import('../plugins/active-links.js'),
    className: 'ActiveLinksPlugin',
    once: true,
  }],
  ['spa.scrollTracking', {
    usecase: 'spa',
    selectors: ['.spa-shell__view', '[data-spa-view]', '[data-scroll-track]'],
    loader: () => import('../plugins/scrollTracking.js'),
    className: 'ScrollTrackingPlugin',
    once: true,
  }],
]);

const instances = new Map();

function resolveSelectors(definition, override) {
  const selectors = override.selectors || definition.selectors || [];
  return Array.isArray(selectors) ? selectors : [selectors];
}

function getElements(selectors, root) {
  return selectors.flatMap((selector) => Array.from(root.querySelectorAll(selector)));
}

function getExport(module, className) {
  if (className && module[className]) return module[className];
  if (module.default) return module.default;
  return Object.values(module).find((value) => typeof value === 'function');
}

async function createInstance(Component, element, options, config = {}) {
  let instance;

  if (config.once || config.optionsOnly) {
    instance = new Component(options);
  } else {
    try {
      instance = new Component(element, options);
    } catch {
      instance = new Component(options);
    }
  }

  if (typeof instance.init === 'function') {
    await instance.init();
  } else if (typeof instance.initialize === 'function') {
    await instance.initialize();
  }

  return instance;
}

export async function initializeUsecaseComponents(usecase, root = document) {
  const initialized = [];

  for (const [componentId, definition] of DEFAULT_COMPONENTS) {
    if (definition.usecase !== usecase) continue;
    if (!isComponentEnabled(componentId, usecase, definition.enabled !== false)) continue;

    const override = getComponentOverride(componentId, usecase);
    const config = mergeConfig(definition, override);
    const selectors = resolveSelectors(definition, override);
    const elements = getElements(selectors, root);

    if (elements.length === 0 && config.requireElement !== false) continue;
    if (config.once && instances.has(componentId)) continue;

    try {
      const module = await config.loader();
      const Component = getExport(module, config.className);
      const options = mergeConfig(config.options || {}, override.options || {});
      const targets = config.once ? [elements[0] || root.documentElement] : elements;
      const componentInstances = [];

      if (typeof Component === 'function') {
        for (const element of targets) {
          componentInstances.push(await createInstance(Component, element, options, config));
        }
      }

      instances.set(componentId, componentInstances);
      initialized.push({ componentId, count: componentInstances.length });
    } catch (error) {
      if (window.STRUCTA_USECASE_CONFIG?.debug || window.STRUCTA_SITE_CONFIG?.usecases?.debug) {
        console.warn(`[usecases] ${componentId} failed`, error);
      }
    }
  }

  window.StructaUsecaseComponents = instances;
  return initialized;
}

export function getUsecaseComponentInstances(componentId) {
  return instances.get(componentId) || [];
}
