'use client';

import React from 'react';
import Link from 'next/link';

interface Product {
  id: number; title: string; slug: string; description: string;
  price: string; image_url: string | null;
}

export default function ProductsPage() {
  const [products, setProducts] = React.useState<Product[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5075/apis';

  React.useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${API}/products`);
        if (!res.ok) throw new Error(`API error ${res.status}`);
        const json = await res.json();
        setProducts(json.data || []);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load products');
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      <section className="bg-gradient-to-r from-purple-700 to-violet-800 text-white py-16" style={{ background: 'linear-gradient(135deg, #7c3aed 0%, #5b21b6 100%)' }}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">Products</h1>
          <p className="text-lg text-purple-200 max-w-2xl mx-auto">
            Explore our products and solutions
          </p>
        </div>
      </section>

      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="bg-white rounded-xl shadow-sm p-6 space-y-3">
                <div className="fusion-skeleton h-48 w-full rounded-lg" />
                <div className="fusion-skeleton h-6 w-3/4" />
                <div className="fusion-skeleton h-4 w-full" />
                <div className="fusion-skeleton h-8 w-1/4" />
              </div>
            ))}
          </div>
        ) : error ? (
          <div className="text-center py-16">
            <p className="text-red-500 mb-4">{error}</p>
            <button onClick={() => window.location.reload()} className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700">Retry</button>
          </div>
        ) : products.length === 0 ? (
          <div className="text-center py-16 text-gray-500">
            <p className="text-xl">No products available</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {products.map(product => (
              <div key={product.id} className="bg-white rounded-xl shadow-sm overflow-hidden hover:shadow-md transition-shadow">
                {product.image_url ? (
                  <div className="h-56 overflow-hidden">
                    <img src={product.image_url} alt={product.title} className="w-full h-full object-cover" />
                  </div>
                ) : (
                  <div className="h-56 flex items-center justify-center bg-gradient-to-br from-purple-100 to-violet-200">
                    <span className="text-purple-400 text-5xl">📦</span>
                  </div>
                )}
                <div className="p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">{product.title}</h3>
                  <p className="text-sm text-gray-600 line-clamp-3 mb-4">{product.description}</p>
                  {product.price && (
                    <div className="flex items-center justify-between">
                      <span className="text-2xl font-bold text-purple-700">${product.price}</span>
                      <Link href={`/contact`} className="px-4 py-2 bg-purple-600 text-white text-sm font-medium rounded-lg hover:bg-purple-700 transition-colors">
                        Inquire
                      </Link>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
