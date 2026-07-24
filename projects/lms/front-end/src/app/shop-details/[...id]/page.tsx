'use client';

import { useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { HiStar, HiShoppingCart, HiHeart, HiShare, HiCheck, HiMinus, HiPlus, HiArrowLeft } from 'react-icons/hi';
import { useGetProductQuery } from '@/store/api/endpoints/shop';
import LoadingSkeleton from '@/components/ui/LoadingSkeleton';
import ErrorState from '@/components/ui/ErrorState';

const mockProduct = {
  id: '1',
  name: 'LMS Premium Hoodie',
  price: 49.99,
  original_price: 69.99,
  description: 'Premium quality hoodie featuring the LMS logo. Made from 100% organic cotton with a comfortable fit perfect for studying or relaxing.',
  images: [
    'https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=600',
    'https://images.unsplash.com/photo-1578768079052-aa76e52ff62e?w=600',
    'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=600',
  ],
  rating: 4.8,
  reviewCount: 124,
  category: 'Apparel',
  inStock: true,
  colors: ['Black', 'Navy', 'Gray'],
  sizes: ['S', 'M', 'L', 'XL', '2XL'],
  features: [
    '100% Organic Cotton',
    'Premium Quality Print',
    'Ribbed Cuffs and Hem',
    'Machine Washable',
    'Unisex Fit',
  ],
  reviews: [
    { id: 'r1', author: 'Alex K.', rating: 5, text: 'Great quality hoodie! The material is soft and the print looks amazing.', date: '2 weeks ago' },
    { id: 'r2', author: 'Maria S.', rating: 4, text: 'Love the design. Runs slightly large but that\'s how I like it.', date: '1 month ago' },
    { id: 'r3', author: 'James R.', rating: 5, text: 'Perfect for long study sessions. Comfortable and stylish.', date: '2 months ago' },
  ],
};

export default function ShopDetailsPage() {
  const params = useParams();
  const productId = Number(params?.id?.[0]) || 1;
  const { data: product, isLoading } = useGetProductQuery(productId);

  const [selectedImage, setSelectedImage] = useState(0);
  const [selectedColor, setSelectedColor] = useState(0);
  const [selectedSize, setSelectedSize] = useState(2);
  const [quantity, setQuantity] = useState(1);
  const [addedToCart, setAddedToCart] = useState(false);

  const displayProduct = (product || mockProduct) as any;

  if (isLoading && !product) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 py-10">
          <LoadingSkeleton variant="detail" />
        </div>
      </div>
    );
  }

  if (!product && !mockProduct) {
    return <ErrorState fullPage message="Product not found." />;
  }

  const handleAddToCart = () => {
    setAddedToCart(true);
    setTimeout(() => setAddedToCart(false), 2000);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Breadcrumb */}
        <div className="flex items-center gap-2 text-sm text-gray-500 mb-6">
          <Link href="/" className="hover:text-indigo-600">Home</Link>
          <span>/</span>
          <Link href="/shop" className="hover:text-indigo-600">Shop</Link>
          <span>/</span>
          <span className="text-gray-900 font-medium">{displayProduct.name}</span>
        </div>

        <Link href="/shop" className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-indigo-600 mb-6 transition-colors">
          <HiArrowLeft className="w-4 h-4" />
          Back to Shop
        </Link>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
          {/* Image Gallery */}
          <div>
            <div className="aspect-square rounded-2xl overflow-hidden bg-white mb-4 shadow-sm">
              <img
                src={displayProduct.images?.[selectedImage] || mockProduct.images[selectedImage]}
                alt={displayProduct.name}
                className="w-full h-full object-cover hover:scale-105 transition-transform duration-500"
              />
            </div>
            <div className="flex gap-3">
              {(displayProduct.images || mockProduct.images).map((img: string, i: number) => (
                <button
                  key={i}
                  onClick={() => setSelectedImage(i)}
                  className={`w-20 h-20 rounded-xl overflow-hidden border-2 transition-all
                    ${selectedImage === i ? 'border-indigo-600 shadow-md' : 'border-gray-200 hover:border-gray-300'}`}
                >
                  <img src={img} alt="" className="w-full h-full object-cover" />
                </button>
              ))}
            </div>
          </div>

          {/* Product Info */}
          <div>
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-indigo-600 font-medium mb-1">{displayProduct.category || mockProduct.category}</p>
                <h1 className="text-3xl font-bold text-gray-900 mb-2">{displayProduct.name}</h1>
                <div className="flex items-center gap-3 mb-4">
                  <div className="flex items-center gap-1">
                    {[...Array(5)].map((_, i) => (
                      <HiStar key={i} className={`w-4 h-4 ${i < Math.floor(displayProduct.rating || mockProduct.rating) ? 'text-yellow-400' : 'text-gray-200'}`} />
                    ))}
                  </div>
                  <span className="text-sm text-gray-500">({mockProduct.reviewCount} reviews)</span>
                </div>
              </div>
              <div className="flex gap-2">
                <button className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors">
                  <HiHeart className="w-5 h-5" />
                </button>
                <button className="p-2 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors">
                  <HiShare className="w-5 h-5" />
                </button>
              </div>
            </div>

            <div className="flex items-baseline gap-3 mb-6">
              <span className="text-3xl font-bold text-gray-900">${displayProduct.price || mockProduct.price}</span>
              {displayProduct.original_price && (
                <span className="text-lg text-gray-400 line-through">${displayProduct.original_price}</span>
              )}
              {displayProduct.original_price && (
                <span className="text-sm font-medium text-green-600 bg-green-50 px-2 py-0.5 rounded-full">
                  Save ${((displayProduct.original_price - displayProduct.price) || 20).toFixed(0)}
                </span>
              )}
            </div>

            <p className="text-gray-600 leading-relaxed mb-8">{displayProduct.description || mockProduct.description}</p>

            {/* Features */}
            <div className="mb-8">
              <h3 className="font-semibold text-gray-900 mb-3">Features</h3>
              <ul className="space-y-2">
                {(displayProduct.features || mockProduct.features).map((f: string, i: number) => (
                  <li key={i} className="flex items-center gap-2 text-sm text-gray-600">
                    <HiCheck className="w-4 h-4 text-green-500 flex-shrink-0" />
                    {f}
                  </li>
                ))}
              </ul>
            </div>

            {/* Color Selection */}
            <div className="mb-6">
              <h3 className="font-semibold text-gray-900 mb-3">Color: <span className="text-gray-500 font-normal">{(mockProduct.colors)[selectedColor]}</span></h3>
              <div className="flex gap-2">
                {mockProduct.colors.map((color, i) => (
                  <button
                    key={color}
                    onClick={() => setSelectedColor(i)}
                    className={`px-4 py-2 text-sm rounded-lg border transition-all
                      ${selectedColor === i ? 'border-indigo-600 bg-indigo-50 text-indigo-700' : 'border-gray-200 text-gray-600 hover:border-gray-300'}`}
                  >
                    {color}
                  </button>
                ))}
              </div>
            </div>

            {/* Size Selection */}
            <div className="mb-8">
              <h3 className="font-semibold text-gray-900 mb-3">Size: <span className="text-gray-500 font-normal">{(mockProduct.sizes)[selectedSize]}</span></h3>
              <div className="flex gap-2">
                {mockProduct.sizes.map((size, i) => (
                  <button
                    key={size}
                    onClick={() => setSelectedSize(i)}
                    className={`w-12 h-12 text-sm font-medium rounded-lg border transition-all
                      ${selectedSize === i ? 'border-indigo-600 bg-indigo-50 text-indigo-700' : 'border-gray-200 text-gray-600 hover:border-gray-300'}`}
                  >
                    {size}
                  </button>
                ))}
              </div>
            </div>

            {/* Quantity & Add to Cart */}
            <div className="flex items-center gap-4 mb-8">
              <div className="flex items-center border border-gray-200 rounded-xl">
                <button
                  onClick={() => setQuantity(Math.max(1, quantity - 1))}
                  className="p-3 text-gray-500 hover:text-gray-700 hover:bg-gray-50 transition-colors rounded-l-xl"
                >
                  <HiMinus className="w-4 h-4" />
                </button>
                <span className="px-6 font-medium text-gray-900 min-w-[3rem] text-center">{quantity}</span>
                <button
                  onClick={() => setQuantity(Math.min(10, quantity + 1))}
                  className="p-3 text-gray-500 hover:text-gray-700 hover:bg-gray-50 transition-colors rounded-r-xl"
                >
                  <HiPlus className="w-4 h-4" />
                </button>
              </div>

              <button
                onClick={handleAddToCart}
                className={`flex-1 flex items-center justify-center gap-2 py-3 rounded-xl font-medium text-sm transition-all
                  ${addedToCart
                    ? 'bg-green-600 text-white'
                    : 'bg-indigo-600 text-white hover:bg-indigo-700 hover:shadow-lg'}`}
              >
                {addedToCart ? (
                  <><HiCheck className="w-5 h-5" /> Added to Cart</>
                ) : (
                  <><HiShoppingCart className="w-5 h-5" /> Add to Cart</>
                )}
              </button>
            </div>

            {/* Stock Status */}
            <div className="flex items-center gap-2 text-sm mb-8">
              {displayProduct.inStock !== false ? (
                <>
                  <span className="w-2 h-2 bg-green-500 rounded-full" />
                  <span className="text-green-600 font-medium">In Stock</span>
                  <span className="text-gray-400">— Ready to ship</span>
                </>
              ) : (
                <>
                  <span className="w-2 h-2 bg-red-500 rounded-full" />
                  <span className="text-red-600 font-medium">Out of Stock</span>
                </>
              )}
            </div>

            {/* Reviews */}
            <div className="border-t border-gray-200 pt-8">
              <h3 className="font-semibold text-gray-900 mb-4">Customer Reviews</h3>
              <div className="space-y-4">
                {mockProduct.reviews.map((review) => (
                  <div key={review.id} className="bg-white border border-gray-200 rounded-xl p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-gray-900 text-sm">{review.author}</span>
                      <span className="text-xs text-gray-400">{review.date}</span>
                    </div>
                    <div className="flex items-center gap-1 mb-2">
                      {[...Array(5)].map((_, i) => (
                        <HiStar key={i} className={`w-3.5 h-3.5 ${i < review.rating ? 'text-yellow-400' : 'text-gray-200'}`} />
                      ))}
                    </div>
                    <p className="text-sm text-gray-600">{review.text}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
