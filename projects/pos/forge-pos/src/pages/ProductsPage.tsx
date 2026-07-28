import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import ProductManager from './ProductManager';
import Inventory from './Inventory';
import Recipes from './Recipes';

type ProductsTab = 'manager' | 'inventory' | 'recipes';

const productsTabs: { key: ProductsTab; labelKey: string; icon: string }[] = [
  { key: 'manager', labelKey: 'nav.productManager', icon: 'clipboard-list' },
  { key: 'inventory', labelKey: 'nav.inventory', icon: 'package' },
  { key: 'recipes', labelKey: 'nav.recipes', icon: 'flask' },
];

/**
 * Merged Products page with tab navigation between ProductManager, Inventory, and Recipes.
 * Each sub-page manages its own PageLayout, so this wrapper only provides the
 * tab bar — no outer PageLayout to avoid double-nesting.
 */
export default function ProductsPage() {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState<ProductsTab>('manager');

  return (
    <>
      {/* ── Fixed Tab Navigation ── */}
      <div className="sticky top-0 z-20 bg-base-200/80 backdrop-blur-md border-b border-base-300/50">
        <div className="max-w-7xl mx-auto px-4 py-3">
          <div className="tabs tabs-boxed gap-1" role="tablist">
            {productsTabs.map(tab => (
              <button
                key={tab.key}
                type="button"
                role="tab"
                className={`tab gap-2 ${activeTab === tab.key ? 'tab-active' : ''}`}
                onClick={() => setActiveTab(tab.key)}
                aria-selected={activeTab === tab.key}
                aria-controls={`products-panel-${tab.key}`}
              >
                <span className={`icon-[tabler--${tab.icon}] w-4 h-4`} />
                <span className="hidden sm:inline">{t(tab.labelKey)}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* ── Tab Content — each sub-page has its own PageLayout ── */}
      {activeTab === 'manager' && (
        <div id="products-panel-manager" role="tabpanel" aria-labelledby="products-tab-manager">
          <ProductManager />
        </div>
      )}
      {activeTab === 'inventory' && (
        <div id="products-panel-inventory" role="tabpanel" aria-labelledby="products-tab-inventory">
          <Inventory />
        </div>
      )}
      {activeTab === 'recipes' && (
        <div id="products-panel-recipes" role="tabpanel" aria-labelledby="products-tab-recipes">
          <Recipes />
        </div>
      )}
    </>
  );
}
