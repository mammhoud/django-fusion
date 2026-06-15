/**
 * Alpine.js Filterable List Component
 * Provides tag-based filtering for blog and portfolio content
 * Used with filter_form.html template
 */

export function filterableList(config = {}) {
  return {
    // State
    selectedTags: [],
    currentQ: '',
    allTags: [],
    isLoading: false,
    tagsParam: '',

    // Config
    storageKey: config.storageKey || 'filterableList',
    persist: config.persist !== false,

    /**
     * Initialize component
     * - Read initial state from URL query params
     * - Optionally restore from localStorage
     * - Parse tags from data-tags attribute
     */
    init() {
      // Parse tags from data-tags attribute
      const tagsJson = this.$el.getAttribute('data-tags');
      if (tagsJson) {
        try {
          this.allTags = JSON.parse(tagsJson);
          console.log(`✅ Loaded ${this.allTags.length} tags for filtering`);
        } catch (e) {
          console.error('Failed to parse tags JSON:', e);
          this.allTags = [];
        }
      } else {
        console.warn('No tags data found in filter form');
      }

      // Read initial state from URL
      const params = new URLSearchParams(window.location.search);
      const tagsParam = params.get('tags');
      const qParam = params.get('q');

      if (tagsParam) {
        this.selectedTags = tagsParam.split(',').filter(t => t.trim());
      }
      if (qParam) {
        this.currentQ = qParam;
      }

      // Optionally restore from localStorage
      if (this.persist) {
        const saved = localStorage.getItem(this.storageKey);
        if (saved) {
          try {
            const savedTags = JSON.parse(saved);
            // Only restore if URL doesn't have tags
            if (!tagsParam && Array.isArray(savedTags)) {
              this.selectedTags = savedTags;
            }
          } catch (e) {
            console.error('Failed to restore saved filters:', e);
          }
        }
      }

      this.updateTagsParam();

      // Listen for history restoration (browser back/forward)
      window.addEventListener('htmx:historyRestore', () => {
        this.syncStateFromUrl();
      });

      // Also listen for popstate (non-HTMX history navigation)
      window.addEventListener('popstate', () => {
        this.syncStateFromUrl();
      });

      console.log('✅ filterableList initialized');
    },

    /**
     * Sync state from current URL
     * Called on browser back/forward navigation
     */
    syncStateFromUrl() {
      const params = new URLSearchParams(window.location.search);
      const tagsParam = params.get('tags');
      const qParam = params.get('q');

      if (tagsParam) {
        this.selectedTags = tagsParam.split(',').filter(t => t.trim());
      } else {
        this.selectedTags = [];
      }

      this.currentQ = qParam || '';
      this.updateTagsParam();
    },

    /**
     * Update tags parameter for form submission
     */
    updateTagsParam() {
      this.tagsParam = this.selectedTags.join(',');
    },

    /**
     * Toggle a tag on/off
     * Triggers form submission via $nextTick to ensure hidden input is updated
     */
    toggleTag(tag) {
      const idx = this.selectedTags.indexOf(tag);
      if (idx === -1) {
        this.selectedTags.push(tag);
      } else {
        this.selectedTags.splice(idx, 1);
      }

      this.updateTagsParam();
      this.saveFilters();

      // Submit form after state updates
      this.$nextTick(() => {
        if (this.$refs.filterForm) {
          this.$refs.filterForm.requestSubmit();
        }
      });
    },

    /**
     * Clear all selected tags
     */
    clearTags() {
      this.selectedTags = [];
      this.updateTagsParam();
      this.saveFilters();

      this.$nextTick(() => {
        if (this.$refs.filterForm) {
          this.$refs.filterForm.requestSubmit();
        }
      });
    },

    /**
     * Check if a tag is selected
     */
    isSelected(tag) {
      return this.selectedTags.includes(tag);
    },

    /**
     * Save current filters to localStorage
     */
    saveFilters() {
      if (this.persist) {
        localStorage.setItem(
          this.storageKey,
          JSON.stringify(this.selectedTags)
        );
      }
    },

    /**
     * Clear saved filters from localStorage
     */
    clearSaved() {
      if (this.persist) {
        localStorage.removeItem(this.storageKey);
      }
    },
  };
}
