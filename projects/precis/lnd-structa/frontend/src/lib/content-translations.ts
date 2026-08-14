import type { LangCode } from './translations';
import type { PageData } from './api';

/**
 * Static content is a resilience layer, not a second CMS. Wagtail remains the
 * source of truth; these concise English/Arabic entries keep the Astro shell
 * useful during an API outage and document the public content contract.
 */
const CONTENT: Record<'en' | 'ar', Record<string, Partial<PageData>>> = {
  en: {
    home: {
      slug: 'home', title: 'Home', type: 'HomePage', show_in_nav: true,
      seo_title: 'Structa Cloud', search_description: 'Digital products for teams serving the Gulf, Levant, and North Africa.',
      hero: { badge: 'structa.cloud · digital product partner', title: 'Digital products for', subtitle: 'We help teams serving the Gulf, Levant, and North Africa launch clear, bilingual services that feel fast and stay easy to operate.', primary_cta: { label: 'Explore products', href: '/products/' }, secondary_cta: { label: 'Work with us', href: '/contact/' } },
      cta: { title: 'A useful first release beats a noisy roadmap', subtitle: 'We start with the customer journey, launch a focused slice, and leave your team with the content and tools to keep improving it.' },
    },
    about: {
      slug: 'about', title: 'About', type: 'AboutPage', show_in_nav: true,
      seo_title: 'About · Structa Cloud', search_description: 'A digital product partner for teams across the MENA region.',
      hero: { badge: 'product partnership', title: 'A clearer path to market', subtitle: 'We connect strategy, design, and delivery for teams building services in Arabic and English.' },
    },
    services: { slug: 'services', title: 'Services', type: 'ServicesPage', show_in_nav: true, seo_title: 'Services · Structa Cloud', search_description: 'Digital products and bilingual experiences for teams across MENA.', hero: { title: 'From idea to market', subtitle: 'Focused digital services that are fast to visit and easy for your team to operate.' } },
    products: { slug: 'products', title: 'Products', type: 'ProductsPage', show_in_nav: true, seo_title: 'Products · Structa Cloud', search_description: 'Practical products for selling, learning, publishing, and serving customers.', hero: { title: 'Products ready to grow', subtitle: 'Tools and platforms that help teams sell, teach, publish, and serve customers.' } },
    features: { slug: 'features', title: 'Features', type: 'FeaturesPage', show_in_nav: true, seo_title: 'Features · Structa Cloud', search_description: 'A calm product foundation with clear content and a fast first visit.', hero: { title: 'Fast from the first visit', subtitle: 'A content system and experience designed for performance, clarity, and Arabic-English delivery.' } },
    blog: { slug: 'blog', title: 'Blog', type: 'BlogPage', show_in_nav: true, seo_title: 'Blog · Structa Cloud', search_description: 'Practical notes on digital products, performance, and content for MENA teams.', hero: { title: 'Ideas from real launches', subtitle: 'Practical notes on digital services, fast first visits, and content teams that stay in control.' } },
    pricing: { slug: 'pricing', title: 'Pricing', type: 'PricingPage', show_in_nav: true, seo_title: 'Pricing · Structa Cloud', search_description: 'Choose a product, then choose an edition.', hero: { title: 'Choose a product, then an edition', subtitle: 'Start free and scale as your project grows.' } },
    contact: { slug: 'contact', title: 'Contact', type: 'ContactPage', show_in_nav: true, seo_title: 'Contact · Structa Cloud', search_description: 'Tell us what you are building.', hero: { title: 'Let’s talk', subtitle: 'Send a message and we will get back to you.' } },
    faq: { slug: 'faq', title: 'FAQ', type: 'FaqPage', show_in_nav: false, seo_title: 'FAQ · Structa Cloud', search_description: 'Clear answers about the stack and products.', hero: { title: 'Frequently asked questions', subtitle: 'Clear answers about the stack, products, and editions.' } },
    privacy: { slug: 'privacy', title: 'Privacy', type: 'PrivacyPage', show_in_nav: false, seo_title: 'Privacy · Structa Cloud', search_description: 'How Structa Cloud handles information.', hero: { title: 'Privacy policy', subtitle: 'We keep data collection minimal by design.' } },
    brand: { slug: 'brand', title: 'Brand', type: 'BrandPage', show_in_nav: false, seo_title: 'Brand · Structa Cloud', search_description: 'The identity system behind Structa Cloud products.', hero: { title: 'One family, many marks', subtitle: 'The visual identity system for Structa Cloud products.' } },
  },
  ar: {
    home: { slug: 'home', title: 'الرئيسية', type: 'HomePage', show_in_nav: true, seo_title: 'Structa Cloud', search_description: 'منتجات رقمية للفرق التي تخدم أسواق الخليج والمشرق وشمال أفريقيا.', hero: { badge: 'structa.cloud · شريك المنتجات الرقمية', title: 'منتجات رقمية تنمو مع السوق', subtitle: 'نساعد الفرق على إطلاق تجارب عربية وإنجليزية واضحة وسريعة وقابلة للتوسع.', primary_cta: { label: 'استكشف المنتجات', href: '/products/' }, secondary_cta: { label: 'اعمل معنا', href: '/contact/' } }, cta: { title: 'ابدأ من احتياج حقيقي', subtitle: 'نحوّل الفكرة أو النظام الحالي إلى تجربة عملية يمكن لفريقك امتلاكها.' } },
    about: { slug: 'about', title: 'من نحن', type: 'AboutPage', show_in_nav: true, seo_title: 'من نحن · Structa Cloud', search_description: 'شريك منتجات رقمية للفرق في منطقة الشرق الأوسط وشمال أفريقيا.', hero: { badge: 'شراكة في المنتج', title: 'طريق أوضح إلى السوق', subtitle: 'نربط الاستراتيجية والتصميم والتنفيذ للفرق التي تبني خدمات بالعربية والإنجليزية.' } },
    services: { slug: 'services', title: 'الخدمات', type: 'ServicesPage', show_in_nav: true, seo_title: 'الخدمات · Structa Cloud', search_description: 'منتجات رقمية وتجارب ثنائية اللغة لفرق المنطقة.', hero: { title: 'من الفكرة إلى السوق', subtitle: 'خدمات رقمية مركزة وسريعة الزيارة وسهلة التشغيل لفريقك.' } },
    products: { slug: 'products', title: 'المنتجات', type: 'ProductsPage', show_in_nav: true, seo_title: 'المنتجات · Structa Cloud', search_description: 'منتجات عملية للبيع والتعلم والنشر وخدمة العملاء.', hero: { title: 'منتجات جاهزة للنمو', subtitle: 'أدوات ومنصات تساعد فريقك على البيع والتعلم والنشر وخدمة العملاء.' } },
    features: { slug: 'features', title: 'الميزات', type: 'FeaturesPage', show_in_nav: true, seo_title: 'الميزات · Structa Cloud', search_description: 'أساس هادئ للمنتج مع محتوى واضح وزيارة أولى سريعة.', hero: { title: 'سريع من أول زيارة', subtitle: 'نظام محتوى وتجربة مصمم للأداء والوضوح والعمل بالعربية والإنجليزية.' } },
    blog: { slug: 'blog', title: 'المدونة', type: 'BlogPage', show_in_nav: true, seo_title: 'المدونة · Structa Cloud', search_description: 'ملاحظات عملية عن المنتجات والأداء والمحتوى لفرق المنطقة.', hero: { title: 'أفكار من إطلاقات حقيقية', subtitle: 'ملاحظات عملية عن الخدمات الرقمية والزيارات السريعة وفرق المحتوى.' } },
    pricing: { slug: 'pricing', title: 'الأسعار', type: 'PricingPage', show_in_nav: true, seo_title: 'الأسعار · Structa Cloud', search_description: 'اختر المنتج ثم الإصدار المناسب.', hero: { title: 'اختر المنتج ثم الإصدار', subtitle: 'ابدأ مجاناً وتوسع مع نمو مشروعك.' } },
    contact: { slug: 'contact', title: 'تواصل معنا', type: 'ContactPage', show_in_nav: true, seo_title: 'تواصل معنا · Structa Cloud', search_description: 'أخبرنا بما تبنيه.', hero: { title: 'لنتحدث', subtitle: 'أرسل رسالة وسنعود إليك قريباً.' } },
    faq: { slug: 'faq', title: 'الأسئلة الشائعة', type: 'FaqPage', show_in_nav: false, seo_title: 'الأسئلة الشائعة · Structa Cloud', search_description: 'إجابات واضحة حول المكدس والمنتجات.', hero: { title: 'الأسئلة الشائعة', subtitle: 'إجابات واضحة حول المكدس والمنتجات والإصدارات.' } },
    privacy: { slug: 'privacy', title: 'الخصوصية', type: 'PrivacyPage', show_in_nav: false, seo_title: 'الخصوصية · Structa Cloud', search_description: 'كيف تتعامل Structa Cloud مع المعلومات.', hero: { title: 'سياسة الخصوصية', subtitle: 'نحافظ على جمع البيانات بالحد الأدنى.' } },
    brand: { slug: 'brand', title: 'الهوية', type: 'BrandPage', show_in_nav: false, seo_title: 'الهوية · Structa Cloud', search_description: 'نظام الهوية لمنتجات Structa Cloud.', hero: { title: 'عائلة واحدة، علامات متعددة', subtitle: 'نظام الهوية البصري لمنتجات Structa Cloud.' } },
  },
};

export function staticPageData(slug: string, language: LangCode = 'en'): PageData | null {
  const locale: 'en' | 'ar' = language === 'ar' ? 'ar' : 'en';
  const value = CONTENT[locale][slug];
  return value ? ({ id: 0, ...value } as PageData) : null;
}
