/**
 * Orders store — expanded-order state that survives view navigation.
 *
 * Kept in Pinia (rather than local component state) so that leaving the
 * Orders view and coming back preserves: which orders are expanded, the
 * already-fetched detail payloads (so expanded cards render instantly,
 * without refetching), per-order load failures, and the active status
 * filter. State lives for the app session; see the settings store for
 * disk persistence patterns.
 */
import { defineStore } from "pinia";
import type { SaleDetail } from "../api";

export const useOrdersStore = defineStore("orders", {
    state: () => ({
        /** Order ids currently expanded in the Orders view. */
        expandedIds: [] as number[],
        /** Full detail payloads keyed by order id — rendered on return. */
        details: {} as Record<number, SaleDetail>,
        /** Order ids whose detail fetch failed — show the list summary instead. */
        failedIds: [] as number[],
        /** Active status filter chip ("all" or a backend status key). */
        statusFilter: "all" as string,
    }),

    actions: {
        /** Toggle one order's expanded state. */
        toggle(id: number) {
            const idx = this.expandedIds.indexOf(id);
            if (idx !== -1) {
                this.expandedIds.splice(idx, 1);
            } else {
                this.expandedIds.push(id);
            }
        },

        /** Replace the expanded set wholesale (used by Expand all). */
        expandAll(ids: number[]) {
            this.expandedIds = [...ids];
        },

        collapseAll() {
            this.expandedIds = [];
        },

        /** Cache a fetched detail payload and clear any prior failure. */
        setDetail(detail: SaleDetail) {
            this.details[detail.id] = detail;
            this.clearFailed(detail.id);
        },

        markFailed(id: number) {
            if (!this.failedIds.includes(id)) {
                this.failedIds.push(id);
            }
        },

        clearFailed(id: number) {
            const fi = this.failedIds.indexOf(id);
            if (fi !== -1) {
                this.failedIds.splice(fi, 1);
            }
        },

        setStatusFilter(value: string) {
            this.statusFilter = value;
        },

        /** Drop expanded ids that no longer exist in the fetched list, and
         *  evict their cached details + failures so the store can't grow. */
        prune(validIds: number[]) {
            const valid = new Set(validIds);
            this.expandedIds = this.expandedIds.filter((id) => valid.has(id));
            for (const id of Object.keys(this.details)) {
                if (!valid.has(Number(id))) {
                    delete this.details[Number(id)];
                }
            }
            this.failedIds = this.failedIds.filter((id) => valid.has(id));
        },
    },
});
