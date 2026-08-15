/**
 * FlyonUI TypeScript declarations
 * =================================
 * Provides type definitions for FlyonUI's global static methods and
 * jQuery/DataTable/Dropzone integration points.
 */

import type { IStaticMethods } from "flyonui/flyonui";

declare global {
  interface Window {
    HSStaticMethods: IStaticMethods;
    _: typeof import("lodash");
    $: typeof import("jquery");
    jQuery: typeof import("jquery");
    DataTable: unknown;
    Dropzone: unknown;
  }
}

export {};
