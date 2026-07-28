/* fusion/modal-close.js
 *
 * Global delegated click handler for the `[data-modal-close]` attribute.
 * Used by blog and portfolio fragment templates to close the unified
 * modal container (`#unified-modal-container`) without inline JS, so
 * the site remains compatible with strict Content-Security-Policy
 * headers that disallow `onclick=` attributes.
 *
 * Usage in a template:
 *
 *     <button type="button" class="modal-close" data-modal-close
 *             aria-label="Close">Close</button>
 *
 * The click on the button (or any descendant of an element carrying the
 * `data-modal-close` attribute) is intercepted; a `fusion:modal:close`
 * CustomEvent is dispatched on `#unified-modal-container` first (so
 * analytics / focus-restore listeners can read the container before it
 * is cleared) and then the container's `innerHTML` is cleared.
 *
 * Loaded once globally by the `{% block extra_scripts %}` in
 * `applications/assets/templates/ui/base_page.html`. Requires
 * `CustomEvent` (all modern browsers, IE ≥ 9).
 */
(function () {
  "use strict";

  function closeUnifiedModal() {
    var container = document.getElementById("unified-modal-container");
    if (!container) return;
    // Notify listeners BEFORE clearing the DOM so they can read state.
    container.dispatchEvent(
      new CustomEvent("fusion:modal:close", { bubbles: true, cancelable: true }),
    );
    container.innerHTML = "";
  }

  document.addEventListener("click", function (event) {
    var target = event.target;
    if (!target || !target.closest) return;
    if (target.closest("[data-modal-close]")) {
      event.preventDefault();
      closeUnifiedModal();
    }
  });
})();
