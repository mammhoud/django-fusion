const DEFAULT_CONFIG = {
  debug: false,
  components: {},
  usecases: {},
};

function plainObject(value) {
  return value && typeof value === 'object' && !Array.isArray(value);
}

export function mergeConfig(...configs) {
  return configs.reduce((merged, config) => {
    if (!plainObject(config)) return merged;

    for (const [key, value] of Object.entries(config)) {
      if (plainObject(value) && plainObject(merged[key])) {
        merged[key] = mergeConfig(merged[key], value);
      } else if (plainObject(value)) {
        merged[key] = mergeConfig({}, value);
      } else {
        merged[key] = value;
      }
    }

    return merged;
  }, {});
}

export function getUsecaseConfig() {
  return mergeConfig(
    DEFAULT_CONFIG,
    window.STRUCTA_USECASE_CONFIG || {},
    window.STRUCTA_SITE_CONFIG?.usecases || {},
  );
}

export function getComponentOverride(componentId, usecase) {
  const config = getUsecaseConfig();
  return mergeConfig(
    config.components?.[componentId] || {},
    config.usecases?.[usecase]?.components?.[componentId] || {},
  );
}

export function isComponentEnabled(componentId, usecase, defaultEnabled = true) {
  const override = getComponentOverride(componentId, usecase);

  if (override === false || override.enabled === false) {
    return false;
  }

  if (override === true || override.enabled === true) {
    return true;
  }

  return defaultEnabled;
}
