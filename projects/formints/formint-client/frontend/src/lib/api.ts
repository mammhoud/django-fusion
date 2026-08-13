/**
 * FormintC purchase-app API client — fetches the menu catalog from the Django
 * backend. Includes a static fallback so `astro build` never fails when the
 * backend is offline (the seeded menu is mirrored below).
 */
import { API_BASE, SHOP_NAME, SHOP_TAGLINE } from './site';

export interface ShopInfo {
  name: string;
  tagline: string;
  order_types: { value: string; label: string }[];
}

export interface CategoryData {
  id: number;
  name: string;
  slug: string;
  glyph: string;
  description: string;
}

export interface ProductData {
  id: number;
  name: string;
  slug: string;
  description: string;
  price: string;
  compare_at_price: string | null;
  image_url: string;
  unit: string;
  category: string;
  tags: string[];
  is_featured: boolean;
}

export interface CatalogData {
  shop: ShopInfo;
  categories: CategoryData[];
  products: ProductData[];
}

export const FALLBACK_CATALOG: CatalogData = {
  shop: {
    name: SHOP_NAME,
    tagline: SHOP_TAGLINE,
    order_types: [
      { value: 'dine_in', label: 'Dine in' },
      { value: 'takeaway', label: 'Takeaway' },
      { value: 'delivery', label: 'Delivery' },
    ],
  },
  categories: [
    { id: 1, name: 'Coffee', slug: 'coffee', glyph: 'cup', description: 'Single-origin beans, roasted weekly.' },
    { id: 2, name: 'Pastries', slug: 'pastries', glyph: 'cake', description: 'Baked in-house before sunrise.' },
    { id: 3, name: 'Breakfast', slug: 'breakfast', glyph: 'sun', description: 'Served until 12:30 every day.' },
    { id: 4, name: 'Lunch', slug: 'lunch', glyph: 'bowl', description: 'Light plates from noon until close.' },
    { id: 5, name: 'Tea', slug: 'tea', glyph: 'leaf', description: 'Loose-leaf and ceremonial-grade brews.' },
    { id: 6, name: 'Smoothies', slug: 'smoothies', glyph: 'blend', description: 'Cold-pressed fruit, blended on demand.' },
    { id: 7, name: 'Desserts', slug: 'desserts', glyph: 'slice', description: 'From the pastry case, all day.' },
  ],
  products: [
    { id: 1, name: 'Espresso', slug: 'espresso', description: 'A 28 g double shot pulled to a honey-thick crema.', price: '3.50', compare_at_price: null, image_url: 'https://images.unsplash.com/photo-1510707577719-ae7c14805e3a?auto=format&fit=crop&w=600&q=80', unit: 'cup', category: 'coffee', tags: ['strong', 'double-shot'], is_featured: true },
    { id: 2, name: 'Flat White', slug: 'flat-white', description: 'Double ristretto under a thin layer of micro-foam.', price: '4.80', compare_at_price: null, image_url: 'https://images.unsplash.com/photo-1461023058943-07fcbe16d735?auto=format&fit=crop&w=600&q=80', unit: 'cup', category: 'coffee', tags: ['velvety'], is_featured: true },
    { id: 3, name: 'Pour Over — Yirgacheffe', slug: 'pour-over-yirgacheffe', description: 'Ethiopian beans, 4:6 method, jasmine + bergamot.', price: '5.90', compare_at_price: null, image_url: '', unit: 'cup', category: 'coffee', tags: ['single-origin', 'floral'], is_featured: false },
    { id: 4, name: 'Cold Brew Tonic', slug: 'cold-brew-tonic', description: '18-hour steep over soda water with an orange twist.', price: '6.40', compare_at_price: '7.00', image_url: '', unit: 'glass', category: 'coffee', tags: ['refreshing', 'sparkling'], is_featured: false },
    { id: 5, name: 'Mocha', slug: 'mocha', description: 'Double espresso, single-origin cocoa, steamed milk.', price: '5.20', compare_at_price: '5.80', image_url: '', unit: 'cup', category: 'coffee', tags: ['sweet', 'classic'], is_featured: false },
    { id: 6, name: 'Almond Croissant', slug: 'almond-croissant', description: '72-hour laminated dough, frangipane centre.', price: '4.20', compare_at_price: null, image_url: 'https://images.unsplash.com/photo-1555507036-ab1f4038808a?auto=format&fit=crop&w=600&q=80', unit: 'each', category: 'pastries', tags: ['buttery', 'laminated'], is_featured: true },
    { id: 7, name: 'Cinnamon Knot', slug: 'cinnamon-knot', description: 'Knot of brioche, Saigon cinnamon, vanilla glaze.', price: '3.90', compare_at_price: null, image_url: '', unit: 'each', category: 'pastries', tags: ['spiced'], is_featured: true },
    { id: 8, name: 'Cardamom Bun', slug: 'cardamom-bun', description: 'Swedish-style with crushed cardamom in the dough.', price: '4.40', compare_at_price: null, image_url: '', unit: 'each', category: 'pastries', tags: ['aromatic'], is_featured: false },
    { id: 9, name: 'Shakshuka', slug: 'shakshuka', description: 'Slow eggs in spiced tomato-pepper stew, sourdough.', price: '9.80', compare_at_price: null, image_url: '', unit: 'plate', category: 'breakfast', tags: ['hearty'], is_featured: true },
    { id: 10, name: 'Avocado Smash', slug: 'avocado-smash', description: 'Pea-topped smashed avocado on seeded toast.', price: '8.60', compare_at_price: null, image_url: '', unit: 'plate', category: 'breakfast', tags: ['veggie'], is_featured: true },
    { id: 11, name: 'French Toast Brioche', slug: 'french-toast-brioche', description: 'Brioche, crème anglaise, roasted plum compote.', price: '7.90', compare_at_price: null, image_url: '', unit: 'plate', category: 'breakfast', tags: ['sweet'], is_featured: false },
    { id: 12, name: 'Harissa Chicken Bowl', slug: 'harissa-chicken-bowl', description: 'Grilled harissa chicken, freekeh, pickled onion.', price: '12.40', compare_at_price: null, image_url: '', unit: 'bowl', category: 'lunch', tags: ['protein'], is_featured: true },
    { id: 13, name: 'Roasted Tomato Soup', slug: 'roasted-tomato-soup', description: 'Charred tomatoes, basil oil, grilled cheese crouton.', price: '6.20', compare_at_price: null, image_url: '', unit: 'bowl', category: 'lunch', tags: ['comfort'], is_featured: true },
    { id: 14, name: 'Halloumi Sourdough', slug: 'halloumi-sourdough', description: 'Seared halloumi, chilli honey, rocket on sourdough.', price: '10.10', compare_at_price: null, image_url: '', unit: 'plate', category: 'lunch', tags: ['veggie'], is_featured: false },
    { id: 15, name: 'Matcha Latte', slug: 'matcha-latte', description: 'Ceremonial-grade matcha, oat milk, fine sugar.', price: '4.90', compare_at_price: '5.50', image_url: 'https://images.unsplash.com/photo-1515823064-d6e0c04616a7?auto=format&fit=crop&w=600&q=80', unit: 'cup', category: 'tea', tags: ['matcha', 'creamy'], is_featured: true },
    { id: 16, name: 'Earl Grey', slug: 'earl-grey', description: 'A bold Ceylon black scented with bergamot.', price: '3.80', compare_at_price: null, image_url: '', unit: 'cup', category: 'tea', tags: ['classic', 'bergamot'], is_featured: true },
    { id: 17, name: 'Chai Latte', slug: 'chai-latte', description: 'Masala chai concentrate, steamed milk, honey.', price: '4.60', compare_at_price: null, image_url: '', unit: 'cup', category: 'tea', tags: ['spiced', 'creamy'], is_featured: false },
    { id: 18, name: 'Jasmine Green', slug: 'jasmine-green', description: 'Jasmine-scented green buds, brewed to order.', price: '3.90', compare_at_price: null, image_url: '', unit: 'pot', category: 'tea', tags: ['floral', 'delicate'], is_featured: false },
    { id: 19, name: 'Mango Tango', slug: 'mango-tango', description: 'Alphonso mango, passion fruit, coconut water.', price: '6.90', compare_at_price: null, image_url: 'https://images.unsplash.com/photo-1502741224143-90386d7f8c39?auto=format&fit=crop&w=600&q=80', unit: 'glass', category: 'smoothies', tags: ['tropical', 'vegan'], is_featured: true },
    { id: 20, name: 'Berry Blast', slug: 'berry-blast', description: 'Strawberry, blueberry, blackberry, Greek yoghurt.', price: '6.50', compare_at_price: null, image_url: '', unit: 'glass', category: 'smoothies', tags: ['berry', 'antioxidant'], is_featured: true },
    { id: 21, name: 'Green Detox', slug: 'green-detox', description: 'Spinach, green apple, cucumber, ginger, lime.', price: '7.20', compare_at_price: null, image_url: '', unit: 'glass', category: 'smoothies', tags: ['green', 'fresh'], is_featured: false },
    { id: 22, name: 'Basque Cheesecake', slug: 'basque-cheesecake', description: 'Caramelised surface, molten centre, sea salt.', price: '6.80', compare_at_price: '7.50', image_url: 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=600&q=80', unit: 'slice', category: 'desserts', tags: ['burnt-top', 'creamy'], is_featured: true },
    { id: 23, name: 'Tiramisu Pot', slug: 'tiramisu-pot', description: 'Espresso-soaked savoiardi, whipped mascarpone.', price: '5.90', compare_at_price: null, image_url: '', unit: 'pot', category: 'desserts', tags: ['coffee', 'mascarpone'], is_featured: true },
    { id: 24, name: 'Salted Brownie', slug: 'salted-brownie', description: 'Dark chocolate, caramel ripple, flaky salt.', price: '4.50', compare_at_price: null, image_url: '', unit: 'each', category: 'desserts', tags: ['fudgy', 'salty'], is_featured: false },
  ],
};

async function fetchJSON<T>(path: string): Promise<T> {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, { headers: { Accept: 'application/json' } });
  if (!res.ok) {
    throw new Error(`API ${path} returned ${res.status}`);
  }
  return res.json() as Promise<T>;
}

/** Fetch the full catalog from Django (fallback to the static seed). */
export async function fetchCatalog(): Promise<CatalogData> {
  try {
    return await fetchJSON<CatalogData>('/api/catalog/');
  } catch {
    return FALLBACK_CATALOG;
  }
}

/** Fetch auth status (backed by the Django session). */
export interface AuthStatus {
  authenticated: boolean;
  user: { email: string; display: string } | null;
}

export async function fetchAuthStatus(): Promise<AuthStatus> {
  try {
    return await fetchJSON<AuthStatus>('/apis/auth/status/');
  } catch {
    return { authenticated: false, user: null };
  }
}
