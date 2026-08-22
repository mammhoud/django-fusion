/**
 * @formints/design-system — Admin CRUD Bento Example
 * 
 * Example admin CRUD page layout using bento grid.
 * Demonstrates how to compose bento components for data management.
 */

import React, { useState } from 'react';
import {
  BentoGrid,
  BentoItem,
  BentoSection,
  BezelWidget,
  CompactButton,
  CompactInput,
  CompactBadge,
  CompactRow,
  CompactModal,
  CompactLabel,
} from '../src';

interface Product {
  id: number;
  name: string;
  price: number;
  stock: number;
  category: string;
  status: 'active' | 'inactive';
}

const mockProducts: Product[] = [
  { id: 1, name: 'Classic Burger', price: 12.99, stock: 45, category: 'Mains', status: 'active' },
  { id: 2, name: 'Caesar Salad', price: 8.99, stock: 30, category: 'Starters', status: 'active' },
  { id: 3, name: 'Margherita Pizza', price: 14.99, stock: 0, category: 'Mains', status: 'inactive' },
  { id: 4, name: 'Iced Coffee', price: 4.99, stock: 120, category: 'Drinks', status: 'active' },
  { id: 5, name: 'Tiramisu', price: 6.99, stock: 15, category: 'Desserts', status: 'active' },
];

export default function AdminCrudBentoExample() {
  const [search, setSearch] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);

  const filteredProducts = mockProducts.filter((p) =>
    p.name.toLowerCase().includes(search.toLowerCase())
  );

  const stats = {
    total: mockProducts.length,
    active: mockProducts.filter((p) => p.status === 'active').length,
    lowStock: mockProducts.filter((p) => p.stock < 20).length,
    categories: new Set(mockProducts.map((p) => p.category)).size,
  };

  return (
    <div className="p-6 space-y-8">
      {/* ── Eyebrow Tag ── */}
      <div className="flex items-center gap-2">
        <span className="inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-[10px] uppercase tracking-[0.2em] font-medium bg-info/10 text-info">
          <span className="ri-box-line ri-12px" />
          Product Management
        </span>
      </div>

      {/* ── Stats Section — Dense Bento ── */}
      <BentoSection title="Overview" accentColor="info">
        <BentoGrid variant="dense" gap="sm">
          <BentoItem accent="primary">
            <BezelWidget
              title="Total Products"
              value={stats.total}
              icon={<span className="ri-box-line" />}
              color="primary"
              compact
            />
          </BentoItem>
          <BentoItem accent="success">
            <BezelWidget
              title="Active"
              value={stats.active}
              icon={<span className="ri-checkbox-circle-line" />}
              color="success"
              compact
            />
          </BentoItem>
          <BentoItem accent="warning">
            <BezelWidget
              title="Low Stock"
              value={stats.lowStock}
              icon={<span className="ri-alert-line" />}
              color="warning"
              compact
            />
          </BentoItem>
          <BentoItem accent="info">
            <BezelWidget
              title="Categories"
              value={stats.categories}
              icon={<span className="ri-folder-line" />}
              color="info"
              compact
            />
          </BentoItem>
        </BentoGrid>
      </BentoSection>

      {/* ── Products Table Section — Editorial Layout ── */}
      <BentoSection
        title="Products"
        eyebrow="Manage your inventory"
        actions={
          <CompactButton
            variant="primary"
            size="sm"
            icon={<span className="ri-add-line" />}
            label="Add Product"
            onClick={() => setShowAddModal(true)}
          />
        }
      >
        <BentoGrid variant="editorial" gap="md">
          {/* Main table - spans 8 cols */}
          <BentoItem colSpan={8}>
            <div className="space-y-4">
              {/* Search bar */}
              <div className="flex items-center gap-2">
                <div className="relative flex-1">
                  <span className="ri-search-line absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-base-content/50" />
                  <input
                    type="text"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    placeholder="Search products..."
                    className="w-full h-8 text-xs pl-8 pr-3 bg-base-100 border border-base-300/50 rounded-lg focus:border-primary focus:ring-1 focus:ring-primary/20"
                  />
                </div>
                <span className="text-[10px] text-base-content/40 whitespace-nowrap">
                  {filteredProducts.length}/{mockProducts.length}
                </span>
              </div>

              {/* Table header */}
              <div className="hidden sm:grid grid-cols-4 gap-3 px-3 py-2 border-b border-base-300/30 text-[10px] font-medium text-base-content/50 uppercase tracking-wider">
                <span>Name</span>
                <span>Price</span>
                <span>Stock</span>
                <span>Status</span>
              </div>

              {/* Table rows */}
              <div className="space-y-1">
                {filteredProducts.map((product) => (
                  <CompactRow
                    key={product.id}
                    hover
                    onClick={() => setSelectedProduct(product)}
                  >
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-medium truncate">{product.name}</p>
                      <p className="text-[10px] text-base-content/50">{product.category}</p>
                    </div>
                    <div className="text-xs tabular-nums">${product.price.toFixed(2)}</div>
                    <div className="text-xs tabular-nums">{product.stock}</div>
                    <CompactBadge
                      variant={product.status === 'active' ? 'success' : 'neutral'}
                      size="xs"
                    >
                      {product.status}
                    </CompactBadge>
                  </CompactRow>
                ))}
              </div>

              {/* Empty state */}
              {filteredProducts.length === 0 && (
                <div className="text-center py-8">
                  <p className="text-xs text-base-content/50">No products found</p>
                </div>
              )}
            </div>
          </BentoItem>

          {/* Sidebar - spans 4 cols */}
          <BentoItem colSpan={4} hover>
            <div className="space-y-4">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-base-content/50">
                Quick Stats
              </h3>

              <div className="space-y-3">
                <div className="p-3 rounded-lg bg-base-200/50">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-[10px] text-base-content/50">Revenue Today</span>
                    <span className="text-[10px] text-success">+12%</span>
                  </div>
                  <p className="text-lg font-bold tabular-nums">$1,245</p>
                </div>

                <div className="p-3 rounded-lg bg-base-200/50">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-[10px] text-base-content/50">Orders</span>
                    <span className="text-[10px] text-info">+8%</span>
                  </div>
                  <p className="text-lg font-bold tabular-nums">42</p>
                </div>

                <div className="p-3 rounded-lg bg-base-200/50">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-[10px] text-base-content/50">Avg Order</span>
                    <span className="text-[10px] text-warning">-2%</span>
                  </div>
                  <p className="text-lg font-bold tabular-nums">$29.64</p>
                </div>
              </div>

              <div className="pt-2 border-t border-base-300/30">
                <h4 className="text-[10px] font-medium text-base-content/50 uppercase tracking-wider mb-2">
                  Top Category
                </h4>
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-lg bg-info/10 flex items-center justify-center">
                    <span className="ri-restaurant-line text-info text-xs" />
                  </div>
                  <div>
                    <p className="text-xs font-medium">Mains</p>
                    <p className="text-[10px] text-base-content/50">65% of sales</p>
                  </div>
                </div>
              </div>
            </div>
          </BentoItem>
        </BentoGrid>
      </BentoSection>

      {/* ── Add Product Modal ── */}
      <CompactModal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        title="Add Product"
        subtitle="Create a new product in your inventory"
        size="sm"
        actions={
          <>
            <CompactButton
              variant="ghost"
              size="sm"
              onClick={() => setShowAddModal(false)}
            >
              Cancel
            </CompactButton>
            <CompactButton
              variant="primary"
              size="sm"
              icon={<span className="ri-save-line" />}
              label="Save"
            />
          </>
        }
      >
        <div className="space-y-3">
          <div>
            <CompactLabel required>Name</CompactLabel>
            <CompactInput
              label=""
              placeholder="Product name"
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <CompactLabel required>Price</CompactLabel>
              <CompactInput
                label=""
                type="number"
                placeholder="0.00"
              />
            </div>
            <div>
              <CompactLabel required>Stock</CompactLabel>
              <CompactInput
                label=""
                type="number"
                placeholder="0"
              />
            </div>
          </div>
          <div>
            <CompactLabel>Category</CompactLabel>
            <CompactInput
              label=""
              placeholder="Select category"
            />
          </div>
        </div>
      </CompactModal>

      {/* ── Product Detail Modal ── */}
      <CompactModal
        isOpen={!!selectedProduct}
        onClose={() => setSelectedProduct(null)}
        title={selectedProduct?.name || ''}
        subtitle={selectedProduct?.category}
        size="md"
        actions={
          <>
            <CompactButton
              variant="danger"
              size="sm"
              icon={<span className="ri-delete-bin-line" />}
              label="Delete"
            />
            <CompactButton
              variant="primary"
              size="sm"
              icon={<span className="ri-edit-line" />}
              label="Edit"
            />
          </>
        }
      >
        {selectedProduct && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-[10px] text-base-content/50 uppercase tracking-wider">Price</p>
                <p className="text-lg font-bold tabular-nums">${selectedProduct.price.toFixed(2)}</p>
              </div>
              <div>
                <p className="text-[10px] text-base-content/50 uppercase tracking-wider">Stock</p>
                <p className="text-lg font-bold tabular-nums">{selectedProduct.stock}</p>
              </div>
            </div>
            <div>
              <p className="text-[10px] text-base-content/50 uppercase tracking-wider">Status</p>
              <CompactBadge
                variant={selectedProduct.status === 'active' ? 'success' : 'neutral'}
                size="sm"
              >
                {selectedProduct.status}
              </CompactBadge>
            </div>
          </div>
        )}
      </CompactModal>
    </div>
  );
}
