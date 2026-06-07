/**
 * Course Catalog HTMX JavaScript
 * Handles interactions, view toggling, and HTMX event subscriptions
 * Merged with CTC Research app patterns
 */

(function() {
  'use strict';

  /**
   * Initialize course catalog functionality
   */
  function initCourseCatalog() {
    // View toggle functionality
    const viewToggleButtons = document.querySelectorAll('[data-view]');

    viewToggleButtons.forEach(button => {
      button.addEventListener('click', function(e) {
        // Update active state
        viewToggleButtons.forEach(btn => {
          btn.classList.remove('rbt-course-view-toggle__button--active');
        });
        this.classList.add('rbt-course-view-toggle__button--active');
      });
    });

    // Initialize course actions
    initializeCourseActions();
  }

  /**
   * Initialize interactive course elements
   */
  function initializeCourseActions() {
    const courseCards = document.querySelectorAll('[data-course-id]');

    courseCards.forEach(card => {
      // Wishlist buttons
      const wishlistBtn = card.querySelector('[hx-post*="wishlist_toggle"]');
      if (wishlistBtn) {
        wishlistBtn.addEventListener('click', function(e) {
          e.preventDefault();
          this.classList.toggle('rbt-course-card__wishlist--active');
          const icon = this.querySelector('i');
          if (icon) {
            icon.classList.toggle('filled');
          }
        });
      }

      // Enroll buttons
      const enrollBtn = card.querySelector('[hx-get*="enrollment_form"]');
      if (enrollBtn) {
        enrollBtn.addEventListener('click', function(e) {
          e.preventDefault();
          showEnrollmentModal(this.getAttribute('data-course-id'));
        });
      }
    });
  }

  /**
   * Show enrollment modal
   * @param {string} courseId - Course ID
   */
  function showEnrollmentModal(courseId) {
    // Implementation will depend on modal framework
    if (typeof htmx !== 'undefined') {
      htmx.ajax('GET', `/courses/${courseId}/enrollment/`, '#modal-container');
    }
  }

  /**
   * Validate filter form before submission
   */
  function initializeFilterForm() {
    const filterForm = document.querySelector('.rbt-course-filters__form');
    if (filterForm) {
      filterForm.addEventListener('submit', function(e) {
        const priceMin = this.querySelector('[name="price_min"]');
        const priceMax = this.querySelector('[name="price_max"]');

        if (priceMin && priceMax && priceMin.value && priceMax.value) {
          if (parseInt(priceMin.value) > parseInt(priceMax.value)) {
            e.preventDefault();
            showNotification(
              'Invalid price range',
              'Minimum price cannot be greater than maximum price',
              'error'
            );
            return false;
          }
        }
      });
    }
  }

  /**
   * Show notification (requires notification component)
   */
  function showNotification(title, message, type = 'info') {
    console.log(`[${type.toUpperCase()}] ${title}: ${message}`);
    // TODO: Integrate with CTC notification component
  }

  /**
   * Handle search form submission
   */
  function initializeSearchForm() {
    const searchForm = document.querySelector('.rbt-course-search');
    if (searchForm) {
      const input = searchForm.querySelector('.rbt-course-search__input');
      if (input) {
        // Add real-time search suggestions if needed
        input.addEventListener('focus', function() {
          // Could show recent searches or popular courses
        });
      }
    }
  }

  /**
   * HTMX Event Listeners
   */
  function setupHTMXListeners() {
    if (typeof htmx === 'undefined') {
      return;
    }

    // After swap event - reinitialize new elements
    htmx.on('htmx:afterSwap', function(e) {
      if (e.detail.target.id === 'course-results') {
        initializeCourseActions();
      }
    });

    // Request error handling
    htmx.on('htmx:responseError', function(e) {
      showNotification(
        'Error',
        'Failed to load courses. Please try again.',
        'error'
      );
    });

    // Request timeout
    htmx.on('htmx:timeout', function(e) {
      showNotification(
        'Timeout',
        'Request timed out. Please try again.',
        'error'
      );
    });
  }

  /**
   * Keyboard navigation
   */
  function initializeKeyboardNavigation() {
    document.addEventListener('keydown', function(e) {
      // Escape key to close modals/filters
      if (e.key === 'Escape') {
        const filters = document.querySelector('#course-filters');
        if (filters && !filters.classList.contains('rbt-course-filters--hidden')) {
          filters.classList.add('rbt-course-filters--hidden');
        }
      }

      // Ctrl/Cmd + K to focus search
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('.rbt-course-search__input');
        if (searchInput) {
          searchInput.focus();
        }
      }
    });
  }

  /**
   * Initialize on DOM ready
   */
  document.addEventListener('DOMContentLoaded', function() {
    initCourseCatalog();
    initializeFilterForm();
    initializeSearchForm();
    setupHTMXListeners();
    initializeKeyboardNavigation();
  });

  // Also initialize if DOM is already loaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', arguments.callee);
  } else {
    initCourseCatalog();
    initializeFilterForm();
    initializeSearchForm();
    setupHTMXListeners();
    initializeKeyboardNavigation();
  }
})();
