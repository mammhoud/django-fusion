# Forge POS — Modal System Reference

> **Components:** `src/components/ui/Modal.tsx` (extended) · `src/components/ui/ModalProvider.tsx` (`useModal`)
> **Styles:** `assets/styles/components/_modal.css` (BEM)

---

## Overview

Forge POS has **two complementary ways** to show a modal:

1. **Declarative** — render `<Modal isOpen={…} onClose={…}>` in JSX (the classic approach, used by ProductManager, Settings, etc.).
2. **Imperative** — call `useModal().openModal({…})` from anywhere inside `<ModalProvider>` (no local `isOpen` state, ideal for confirmations and global dialogs).

Both render the same extended BEM dialog frame, so every feature (sizes, positions, variants, focus trap, ESC, backdrop) works identically either way.

> **htmx / Alpine.js option:** the FlyonUI component library this app is built on also ships **htmx** and **Alpine.js** as alternative JS engines for its modals. The BEM markup below is engine-agnostic — see [Web deployments (htmx / Alpine.js)](#web-deployments-htmx--alpinejs) for how to drive the same markup in server-rendered pages.

---

## Extended `<Modal>` Component

### Props

| Prop | Type | Default | Purpose |
|------|------|---------|---------|
| `isOpen` | `boolean` | — | Show/hide |
| `onClose` | `() => void` | — | Close handler |
| `title` / `subtitle` / `headerIcon` | — | — | Header content |
| `size` | `sm \| md \| lg \| xl \| full` | `md` | Width modifier `.modal--{size}` |
| `position` | `center \| top \| bottom \| left \| right` | `center` | `.modal--{position}` (left/right = full-height side sheets) |
| `variant` | `default \| danger \| warning \| success \| info` | `default` | Semantic accent (`.modal--variant--{variant}`) |
| `borderColor` | `string` | — | Legacy accent border (ConfirmDialog) |
| `scroll` | `boolean` | `false` | Independent body scroll (pins header/footer) |
| `noPad` | `boolean` | `false` | Remove content padding |
| `footerAlign` | `start \| between \| center \| end` | `end` | Footer alignment |
| `closeOnBackdrop` | `boolean` | `true` | Close on overlay click |
| `escapeClosable` | `boolean` | `true` | Close on `Escape` |
| `dismissible` | `boolean` | `true` | Show the header ✕ button |
| `focusTrap` | `boolean` | `true` | Trap Tab focus inside the dialog |
| `initialFocusRef` | `Ref<HTMLElement>` | first focusable | Element focused on open |
| `className` / `contentClassName` / `contentTestId` | — | — | Extras |

### Features built in

- **Focus management** — moves focus into the dialog on open (first focusable, or `initialFocusRef`) and restores it on close.
- **Focus trap** — Tab/Shift+Tab cycle within the dialog.
- **Escape key** — closes unless `escapeClosable={false}`.
- **Positions** — `top`/`bottom` pin to the edge (still centered horizontally); `left`/`right` render full-height side sheets with slide-in animations.
- **Variants** — colored top accent + title tint using the semantic tokens (danger/warning/success/info).

### Example — confirm dialog (declarative)

```tsx
<Modal
  isOpen={showDelete}
  onClose={() => setShowDelete(false)}
  title={t('productManager.deleteTitle')}
  size="sm"
  variant="danger"
  footer={
    <>
      <button onClick={() => setShowDelete(false)} className="btn btn-ghost flex-1">Cancel</button>
      <button onClick={handleDelete} className="btn btn-error flex-1">Delete</button>
    </>
  }
>
  <p>{t('productManager.deleteConfirm')} <strong>{name}</strong>?</p>
</Modal>
```

### Example — side sheet

```tsx
<Modal isOpen onClose={close} title="Order Details" position="right" size="md" scroll>
  …long content…
</Modal>
```

---

## `ModalProvider` + `useModal` (imperative)

Wrap the app (or a subtree) in `<ModalProvider>` — already wired globally in `src/main.tsx` and in the test harness (`src/test/test-utils.tsx`).

### API

| Member | Signature | Purpose |
|--------|-----------|---------|
| `openModal` | `(config: ModalConfig) => string` | Open a dialog, returns its id |
| `closeModal` | `(id: string) => void` | Close by id |
| `closeAllModals` | `() => void` | Close everything |

`ModalConfig` accepts the same props as `<Modal>` plus:
- `id?: string` — stable id (auto-generated otherwise)
- `content?: ReactNode \| (close) => ReactNode` — body (render-prop gets a close fn)
- `footer?: ReactNode \| (close) => ReactNode` — footer actions

### Example — programmatic confirm

```tsx
import { useModal } from '../components/ui/ModalProvider';

function useDeleteConfirm() {
  const { openModal } = useModal();
  const confirmDelete = (item, onConfirm) => {
    openModal({
      title: 'Delete item?',
      size: 'sm',
      variant: 'danger',
      content: (close) => <p>Are you sure you want to delete <strong>{item}</strong>?</p>,
      footer: (close) => (
        <>
          <button onClick={close} className="btn btn-ghost flex-1">Cancel</button>
          <button
            onClick={() => { close(); onConfirm(); }}
            className="btn btn-error flex-1"
          >
            Delete
          </button>
        </>
      ),
    });
  };
  return confirmDelete;
}
```

---

## Web Deployments (htmx / Alpine.js)

FlyonUI — the component library behind Forge POS styling — supports **htmx** and **Alpine.js** as JS engines for its modals. This is useful when the same POS is embedded in a server-rendered web app (e.g. a Django/Wagtail deployment) rather than the Tauri desktop shell.

### Option A — htmx (`hx-*` attributes)

```html
<!-- Button that loads the dialog markup via AJAX and opens it -->
<button
  class="btn btn-primary"
  data-hs-overlay="#my-modal"
  hx-get="/modals/confirm-delete/42"
  hx-target="#my-modal-content"
  hx-swap="innerHTML"
>
  Delete
</button>

<!-- Static dialog shell — the SAME BEM frame used in React -->
<div id="my-modal" class="modal modal--sm modal--enter hidden">
  <div class="modal__overlay" data-hs-overlay-close></div>
  <div class="modal__content" id="my-modal-content">
    <!-- htmx swaps this region -->
  </div>
</div>
```

### Option B — Alpine.js (`x-data` / `x-show`)

```html
<div x-data="{ open: false }">
  <button class="btn btn-primary" @click="open = true">Delete</button>

  <div x-show="open" x-cloak class="modal modal--sm modal--enter" role="dialog" aria-modal="true">
    <div class="modal__overlay" @click="open = false"></div>
    <div class="modal__content">
      <div class="modal__header">
        <h2 class="modal__title">Delete item?</h2>
        <button class="modal__close" @click="open = false" aria-label="Close">
          <span class="icon-[tabler--x] modal__close-icon"></span>
        </button>
      </div>
      <div class="modal__body">Are you sure?</div>
      <div class="modal__footer modal__footer--between">
        <button class="btn btn-ghost" @click="open = false">Cancel</button>
        <button class="btn btn-error" @click="open = false">Delete</button>
      </div>
    </div>
  </div>
</div>
```

> The CSS classes (`.modal`, `.modal__content`, `.modal--enter`, …) are pure BEM and need **zero JS** to look right — the htmx/Alpine layer only handles *open/close behaviour*. Both snippets reuse the exact same markup the React component renders.

---

## References

- `src/components/ui/Modal.tsx` — extended component source
- `src/components/ui/ModalProvider.tsx` — provider + `useModal`
- `assets/styles/components/_modal.css` — BEM styles, positions, variants, animations
- `src/components/ui/ConfirmDialog.tsx` — reference declarative implementation
- `src/test/components/Modal.test.tsx` / `ModalProvider.test.tsx` — behaviour specs
- [`docs/color-palette.md`](color-palette.md) — theme tokens the variants use
- [`docs/pages-options.md`](pages-options.md) — where modals appear per page
- [FlyonUI modal docs](https://flyonui.com/docs/overlay/modal) — htmx/Alpine integration details
