/**
 * @file theme/layouts/index.js
 * Unified layout exports — all page layout classes in one place.
 *
 * BaseLayout / PagesManager / LayoutManager originate in base.layout.js.
 * Each concrete layout (App, Auth, Landing, Notifications, Profile) extends BaseLayout.
 */

// Foundation
export {
  BaseLayout,
  PagesManager,
  LayoutManager,
  pagesManager,
  layoutManager,
} from './base.layout.js';

// Concrete layouts
export { AppLayout }           from './app.layout.js';
export { AuthLayout }          from './auth.layout.js';
export { LandingLayout }       from './landing.layout.js';
export { NotificationsLayout } from './notifications.layout.js';
export { ProfileLayout }       from './profile.layout.js';
