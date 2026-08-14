/**
 * Ticket store — the register's open order, persisted across view switches.
 *
 * Kept in Pinia (rather than local component state) so that navigating from
 * the menu to the dashboard or orders and back preserves the built ticket:
 * quantities, order type, payment method, notes and ready time. The store is
 * intentionally agnostic of the catalog — price math stays in the view that
 * has the product list loaded.
 */
import { defineStore } from "pinia";

export const useTicketStore = defineStore("ticket", {
    state: () => ({
        /** Product id → quantity on the open ticket. */
        quantities: {} as Record<number, number>,
        orderType: "takeaway",
        paymentMethod: "cash",
        customerName: "",
        notes: "",
        readyAt: "",
        /** Reference of the last placed order (drives the success state). */
        lastReference: "",
        /** Monotonic counter bumped on every placed order — views watch it to refetch. */
        dataVersion: 0,
    }),

    getters: {
        totalItems(state): number {
            return Object.values(state.quantities).reduce((a, b) => a + b, 0);
        },
        isEmpty(): boolean {
            return this.totalItems === 0;
        },
    },

    actions: {
        add(productId: number) {
            this.quantities = {
                ...this.quantities,
                [productId]: (this.quantities[productId] ?? 0) + 1,
            };
        },

        remove(productId: number) {
            const next = { ...this.quantities };
            if ((next[productId] ?? 0) <= 1) {
                delete next[productId];
            } else {
                next[productId] -= 1;
            }
            this.quantities = next;
        },

        /** Reset the ticket after a successful order. */
        clear() {
            this.quantities = {};
            this.customerName = "";
            this.notes = "";
            this.readyAt = "";
        },

        setOrderType(value: string) {
            this.orderType = value;
        },

        setPaymentMethod(value: string) {
            this.paymentMethod = value;
        },

        /** Record a successfully placed order — bumps the refresh signal for Dashboard/Orders. */
        recordPlacedOrder(reference: string) {
            this.lastReference = reference;
            this.dataVersion += 1;
        },
    },
});
