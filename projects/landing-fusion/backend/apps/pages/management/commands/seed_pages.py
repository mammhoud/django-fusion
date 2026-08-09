"""
Seed the landing Wagtail page tree with default content.

Creates the site record plus Home / About / Company / Services / Products /
Features / Projects / Contact / FAQ / Privacy pages mirroring the Astro
frontend content (see src/lib/site.ts and the pages in frontend/src/pages/).

Idempotent: pages already present under the site root are left untouched;
empty content fields added by later migrations are backfilled.

Usage:
    python manage.py seed_pages
"""
import json
import logging
import os

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from wagtail.models import Locale, Page, Site

logger = logging.getLogger(__name__)

from apps.pages.models import (
    AboutPage,
    BlogPage,
    BlogPostPage,
    BrandPage,
    ContactPage,
    FaqPage,
    FeaturesPage,
    FounderPage,
    HomePage,
    PricingPage,
    PrivacyPage,
    ProductPage,
    ProductsPage,
    ServicesPage,
    StartupPage,
    PhasePage,
    PromptPage,
    TeamPage,
)
from apps.content.models.translations import PageTranslation

# Bilingual overlays are deliberately partial: untranslated fields continue to
# use the canonical Wagtail content through the API fallback contract.
DEFAULT_PAGE_TRANSLATIONS = {
    "home": {
        "ar": {
            "title": "الرئيسية",
            "search_description": "منتجات رقمية هادئة وسريعة للفرق التي تخدم أسواق الخليج والمشرق وشمال أفريقيا.",
            "content": {
                "hero": {"badge": "structa.cloud · شريك المنتجات الرقمية", "title": "منتجات رقمية تنمو مع", "accent": "السوق", "subtitle": "نساعد الفرق على إطلاق تجارب عربية وإنجليزية واضحة، سريعة، وقابلة للتوسع.", "primary_cta": {"label": "استكشف المنتجات"}, "secondary_cta": {"label": "اعمل معنا"}, "trusted_by": "جاهز للعربية · جاهز للإنجليزية · مبني لفرق حقيقية"},
                "cta": {"title": "ابدأ من احتياج حقيقي", "subtitle": "نحوّل الفكرة أو النظام الحالي إلى تجربة عملية يمكن لفريقك امتلاكها.", "primary_cta": {"label": "عرض على GitHub"}, "secondary_cta": {"label": "اقرأ التوثيق"}},
            },
        },
        "sv": {"title": "Hem", "content": {"hero": {"badge": "structa.cloud · digital produktpartner", "title": "Digitala produkter, levererade som", "accent": "dokument", "subtitle": "Vi hjälper team som betjänar Gulfen, Levanten och Nordafrika att lansera tydliga, tvåspråkiga tjänster som känns snabba och är lätta att driva.", "primary_cta": {"label": "Utforska produkter"}, "secondary_cta": {"label": "Samarbeta med oss"}, "trusted_by": "Redo för arabiska · Redo för engelska · byggt för riktiga team"}, "cta": {"title": "En användbar första release slår en bullrig färdplan", "subtitle": "Vi börjar med kundresan, lanserar en fokuserad del och lämnar ditt team med innehåll och verktyg för att fortsätta förbättra.", "primary_cta": {"label": "Visa på GitHub"}, "secondary_cta": {"label": "Läs dokumentationen"}}}},
        "fr": {"title": "Accueil", "content": {"hero": {"badge": "structa.cloud · partenaire produit numérique", "title": "Des produits numériques, livrés comme", "accent": "documents", "subtitle": "Nous aidons les équipes qui servent le Golfe, le Levant et l'Afrique du Nord à lancer des services bilingues clairs, rapides et faciles à exploiter.", "primary_cta": {"label": "Explorer les produits"}, "secondary_cta": {"label": "Travaillez avec nous"}, "trusted_by": "Prêt pour l'arabe · Prêt pour l'anglais · conçu pour de vraies équipes"}, "cta": {"title": "Une première version utile vaut mieux qu'une feuille de route bruyante", "subtitle": "Nous partons du parcours client, lançons une première version ciblée et laissons à votre équipe le contenu et les outils pour continuer à l'améliorer.", "primary_cta": {"label": "Voir sur GitHub"}, "secondary_cta": {"label": "Lire la documentation"}}}},
        "de": {"title": "Startseite", "content": {"hero": {"badge": "structa.cloud · digitaler Produktpartner", "title": "Digitale Produkte, geliefert als", "accent": "Dokumente", "subtitle": "Wir helfen Teams, die den Golf, die Levante und Nordafrika bedienen, klare zweisprachige Dienste zu starten, die sich schnell anfühlen und leicht zu betreiben sind.", "primary_cta": {"label": "Produkte entdecken"}, "secondary_cta": {"label": "Arbeiten Sie mit uns"}, "trusted_by": "Bereit für Arabisch · Bereit für Englisch · gebaut für echte Teams"}, "cta": {"title": "Ein nützlicher erster Release schlägt eine laute Roadmap", "subtitle": "Wir starten mit der Customer Journey, bringen einen fokussierten ersten Wurf heraus und überlassen Ihrem Team die Inhalte und Werkzeuge, um weiter zu verbessern.", "primary_cta": {"label": "Auf GitHub ansehen"}, "secondary_cta": {"label": "Dokumentation lesen"}}}},
        "es": {"title": "Inicio", "content": {"hero": {"badge": "structa.cloud · socio de productos digitales", "title": "Productos digitales, entregados como", "accent": "documentos", "subtitle": "Ayudamos a los equipos que atienden el Golfo, el Levante y el norte de África a lanzar servicios bilingües claros, rápidos y fáciles de operar.", "primary_cta": {"label": "Explorar productos"}, "secondary_cta": {"label": "Trabaja con nosotros"}, "trusted_by": "Listo para árabe · Listo para inglés · hecho para equipos reales"}, "cta": {"title": "Un primer lanzamiento útil gana a una hoja de ruta ruidosa", "subtitle": "Empezamos por el recorrido del cliente, lanzamos una primera versión enfocada y dejamos a tu equipo el contenido y las herramientas para seguir mejorando.", "primary_cta": {"label": "Ver en GitHub"}, "secondary_cta": {"label": "Leer la documentación"}}}},
        "pt": {"title": "Início", "content": {"hero": {"badge": "structa.cloud · parceiro de produtos digitais", "title": "Produtos digitais, entregues como", "accent": "documentos", "subtitle": "Ajudamos equipas que servem o Golfo, o Levante e o norte de África a lançar serviços bilingues claros, rápidos e fáceis de operar.", "primary_cta": {"label": "Explorar produtos"}, "secondary_cta": {"label": "Trabalhe connosco"}, "trusted_by": "Pronto para árabe · Pronto para inglês · feito para equipas reais"}, "cta": {"title": "Um primeiro lançamento útil vence um roadmap ruidoso", "subtitle": "Começamos pela jornada do cliente, lançamos uma primeira versão focada e deixamos à sua equipa o conteúdo e as ferramentas para continuar a melhorar.", "primary_cta": {"label": "Ver no GitHub"}, "secondary_cta": {"label": "Ler a documentação"}}}},
    },
    "about": {
        "ar": {
            "title": "من نحن",
            "search_description": "شريك منتج للفرق التي تبني خدمات رقمية في أسواق الخليج والمشرق وشمال أفريقيا.",
            "body": "<p>Structa Cloud استوديو منتجات يساعد الفرق على تحويل الأفكار والأنظمة القديمة إلى خدمات رقمية واضحة وقابلة للاستخدام.</p><p>نصمم تجارب عربية وإنجليزية، ونبدأ من رحلة العميل قبل اختيار التقنية. النتيجة منصة سريعة يستطيع فريقك إدارتها بعد الإطلاق.</p>",
            "content": {"hero": {"title": "شريكك في المنتج الرقمي", "subtitle": "نربط الاستراتيجية والتصميم والهندسة في مسار واحد من الفكرة إلى السوق.", "primary_cta": {"label": "شاهد كيف نعمل"}, "secondary_cta": {"label": "ابدأ محادثة"}}, "cta": {"title": "لنصمم الخطوة التالية", "subtitle": "أخبرنا عن السوق والعميل والقيود، وسنقترح مساراً عملياً.", "primary_cta": {"label": "عرض على GitHub"}, "secondary_cta": {"label": "تواصل معنا"}}},
        },
        "sv": {"title": "Om oss", "content": {"hero": {"title": "En tydligare väg till marknaden", "subtitle": "Vi kopplar samman strategi, design och leverans för team som bygger tjänster på arabiska och engelska.", "primary_cta": {"label": "Se hur vi arbetar"}, "secondary_cta": {"label": "Inled en konversation"}}, "cta": {"title": "Byggt i öppenhet, levererat som HTML", "subtitle": "Vissa produkter och kärnbiblioteken är offentliga på GitHub. Utgåvor och licenser varierar mellan produkter; Precis LMS erbjuds som Solo och Business.", "primary_cta": {"label": "Visa på GitHub"}, "secondary_cta": {"label": "Ta kontakt"}}}},
        "fr": {"title": "À propos", "content": {"hero": {"title": "Un chemin plus clair vers le marché", "subtitle": "Nous relions stratégie, design et livraison pour les équipes qui construisent des services en arabe et en anglais.", "primary_cta": {"label": "Découvrez comment nous travaillons"}, "secondary_cta": {"label": "Engagez la conversation"}}, "cta": {"title": "Construit en toute transparence, livré en HTML", "subtitle": "Certains produits et les bibliothèques de base sont publics sur GitHub. La disponibilité des éditions et les licences varient selon le produit ; Precis LMS est proposé en Solo et Business.", "primary_cta": {"label": "Voir sur GitHub"}, "secondary_cta": {"label": "Contactez-nous"}}}},
        "de": {"title": "Über uns", "content": {"hero": {"title": "Ein klarerer Weg zum Markt", "subtitle": "Wir verbinden Strategie, Design und Auslieferung für Teams, die Dienste auf Arabisch und Englisch aufbauen.", "primary_cta": {"label": "So arbeiten wir"}, "secondary_cta": {"label": "Gespräch starten"}}, "cta": {"title": "In Offenheit gebaut, als HTML ausgeliefert", "subtitle": "Einige Produkte und die Kernbibliotheken sind auf GitHub öffentlich. Editionen und Lizenzen variieren je nach Produkt; Precis LMS ist als Solo und Business erhältlich.", "primary_cta": {"label": "Auf GitHub ansehen"}, "secondary_cta": {"label": "Kontakt aufnehmen"}}}},
        "es": {"title": "Acerca de", "content": {"hero": {"title": "Un camino más claro hacia el mercado", "subtitle": "Conectamos estrategia, diseño y entrega para equipos que construyen servicios en árabe e inglés.", "primary_cta": {"label": "Mira cómo trabajamos"}, "secondary_cta": {"label": "Inicia una conversación"}}, "cta": {"title": "Construido en abierto, entregado como HTML", "subtitle": "Algunos productos y las bibliotecas principales son públicos en GitHub. La disponibilidad de ediciones y las licencias varían según el producto; Precis LMS se ofrece en Solo y Business.", "primary_cta": {"label": "Ver en GitHub"}, "secondary_cta": {"label": "Ponte en contacto"}}}},
        "pt": {"title": "Sobre nós", "content": {"hero": {"title": "Um caminho mais claro para o mercado", "subtitle": "Ligamos estratégia, design e entrega para equipas que constroem serviços em árabe e inglês.", "primary_cta": {"label": "Veja como trabalhamos"}, "secondary_cta": {"label": "Inicie uma conversa"}}, "cta": {"title": "Construído em aberto, entregue como HTML", "subtitle": "Alguns produtos e as bibliotecas principais são públicos no GitHub. A disponibilidade de edições e as licenças variam por produto; o Precis LMS é oferecido em Solo e Business.", "primary_cta": {"label": "Ver no GitHub"}, "secondary_cta": {"label": "Entre em contacto"}}}},
    },
    # About subpages — these overlays use the same partial contract as the
    # top-level pages, so missing fields continue to fall back to Wagtail.
    "team": {
        "ar": {
            "title": "الفريق",
            "search_description": "الأشخاص الذين يبنون منتجات Structa Cloud الرقمية.",
            "body": "<p>فريق صغير يملك القرار من الفكرة إلى الإطلاق، ويحوّل الخبرة اليومية إلى أدوات يمكن للفرق استخدامها بثقة.</p>",
            "content": {
                "hero": {"title": "الأشخاص الذين يقفون خلف المنتجات", "subtitle": "خبرة عملية في التصميم والهندسة والمحتوى، من شخص واحد إلى فرق متعاونة."},
                "cta": {"title": "لنبنِ شيئاً مفيداً", "subtitle": "أخبرنا عن فريقك والعميل والنتيجة التي تريد الوصول إليها."},
            },
        },
        "sv": {"title": "Team", "content": {"hero": {"title": "Personerna bakom structa.cloud", "subtitle": "En ingenjör, tre produktledare och de öppna källkodsbidragarna som får monorepot att leverera.", "primary_cta": {"label": "Träffa grundaren"}, "secondary_cta": {"label": "Ta kontakt"}}, "cta": {"title": "Byggt i öppenhet", "subtitle": "Varje rad av structa.cloud är offentlig på GitHub. Kom och bygg med oss.", "primary_cta": {"label": "Visa på GitHub"}, "secondary_cta": {"label": "Tillbaka till Om oss"}}}},
        "fr": {"title": "Équipe", "content": {"hero": {"title": "Les personnes derrière structa.cloud", "subtitle": "Un ingénieur, trois responsables produit et les contributeurs open source qui font avancer le monorepo.", "primary_cta": {"label": "Rencontrer le fondateur"}, "secondary_cta": {"label": "Contactez-nous"}}, "cta": {"title": "Construit en toute transparence", "subtitle": "Chaque ligne de structa.cloud est publique sur GitHub. Venez construire avec nous.", "primary_cta": {"label": "Voir sur GitHub"}, "secondary_cta": {"label": "Retour à À propos"}}}},
        "de": {"title": "Team", "content": {"hero": {"title": "Die Menschen hinter structa.cloud", "subtitle": "Ein Engineer, drei Produktverantwortliche und die Open-Source-Beitragenden, die das Monorepo zum Laufen bringen.", "primary_cta": {"label": "Den Gründer kennenlernen"}, "secondary_cta": {"label": "Kontakt aufnehmen"}}, "cta": {"title": "In Offenheit gebaut", "subtitle": "Jede Zeile von structa.cloud ist öffentlich auf GitHub. Bauen Sie mit uns.", "primary_cta": {"label": "Auf GitHub ansehen"}, "secondary_cta": {"label": "Zurück zu Über uns"}}}},
        "es": {"title": "Equipo", "content": {"hero": {"title": "Las personas detrás de structa.cloud", "subtitle": "Un ingeniero, tres responsables de producto y los contribuidores de código abierto que hacen avanzar el monorepo.", "primary_cta": {"label": "Conoce al fundador"}, "secondary_cta": {"label": "Ponte en contacto"}}, "cta": {"title": "Construido en abierto", "subtitle": "Cada línea de structa.cloud es pública en GitHub. Ven a construir con nosotros.", "primary_cta": {"label": "Ver en GitHub"}, "secondary_cta": {"label": "Volver a Acerca de"}}}},
        "pt": {"title": "Equipa", "content": {"hero": {"title": "As pessoas por detrás da structa.cloud", "subtitle": "Um engenheiro, três responsáveis de produto e os contribuidores de código aberto que fazem o monorepo avançar.", "primary_cta": {"label": "Conheça o fundador"}, "secondary_cta": {"label": "Entre em contacto"}}, "cta": {"title": "Construído em aberto", "subtitle": "Cada linha da structa.cloud é pública no GitHub. Venha construir connosco.", "primary_cta": {"label": "Ver no GitHub"}, "secondary_cta": {"label": "Voltar a Sobre"}}}},
    },
    "founder": {
        "ar": {
            "title": "المؤسس",
            "search_description": "المهندس الذي يبني Structa Cloud ومنتجاتها ومكتباتها المفتوحة.",
            "body": "<p>أبني المنتجات من طبقة البيانات إلى الواجهة، مع اهتمام خاص بسرعة الوصول ووضوح المحتوى وسهولة امتلاك الفريق للنظام بعد الإطلاق.</p>",
            "content": {
                "hero": {"title": "مهندس يبني من الفكرة إلى الإطلاق", "subtitle": "هندسة عملية تجمع Django وWagtail وRust وواجهات الويب في مسار واحد."},
                "tech": {"title": "المكدس التقني"},
                "cta": {"title": "هل لديك منتج يحتاج إلى مسار أوضح؟", "subtitle": "لنحوّل الفكرة إلى أول إصدار يمكن استخدامه وقياسه."},
            },
        },
        "sv": {"title": "Grundare", "content": {"hero": {"title": "Mahmoud Ezzat Moustafa", "subtitle": "Fullstackutvecklare, bidragsgivare till öppen källkod och ingenjören bakom structa.cloud. Django, Wagtail och AI-drivna system.", "primary_cta": {"label": "Träffa teamet"}, "secondary_cta": {"label": "Visa på GitHub"}, "trusted_by": "Python · Django · Wagtail · AI tooling"}, "cta": {"title": "Byggt i öppenhet", "subtitle": "Hela monorepot är offentligt på GitHub. Community-utgåvorna är gratis, Pro-utgåvorna är kommersiella.", "primary_cta": {"label": "Visa på GitHub"}, "secondary_cta": {"label": "Kontakt"}}}},
        "fr": {"title": "Fondateur", "content": {"hero": {"title": "Mahmoud Ezzat Moustafa", "subtitle": "Développeur full-stack, contributeur open source et l'ingénieur derrière structa.cloud. Django, Wagtail et des systèmes pilotés par l'IA.", "primary_cta": {"label": "Rencontrer l'équipe"}, "secondary_cta": {"label": "Voir sur GitHub"}, "trusted_by": "Python · Django · Wagtail · AI tooling"}, "cta": {"title": "Construit en toute transparence", "subtitle": "L'ensemble du monorepo est public sur GitHub. Les éditions Communauté sont gratuites, les éditions Pro sont commerciales.", "primary_cta": {"label": "Voir sur GitHub"}, "secondary_cta": {"label": "Contact"}}}},
        "de": {"title": "Gründer", "content": {"hero": {"title": "Mahmoud Ezzat Moustafa", "subtitle": "Full-Stack-Entwickler, Open-Source-Mitwirkender und der Engineer hinter structa.cloud. Django, Wagtail und KI-gestützte Systeme.", "primary_cta": {"label": "Das Team kennenlernen"}, "secondary_cta": {"label": "Auf GitHub ansehen"}, "trusted_by": "Python · Django · Wagtail · AI tooling"}, "cta": {"title": "In Offenheit gebaut", "subtitle": "Das gesamte Monorepo ist öffentlich auf GitHub. Community-Editionen sind kostenlos, Pro-Editionen kommerziell.", "primary_cta": {"label": "Auf GitHub ansehen"}, "secondary_cta": {"label": "Kontakt"}}}},
        "es": {"title": "Fundador", "content": {"hero": {"title": "Mahmoud Ezzat Moustafa", "subtitle": "Desarrollador full-stack, contribuidor de código abierto y el ingeniero detrás de structa.cloud. Django, Wagtail y sistemas impulsados por IA.", "primary_cta": {"label": "Conoce al equipo"}, "secondary_cta": {"label": "Ver en GitHub"}, "trusted_by": "Python · Django · Wagtail · AI tooling"}, "cta": {"title": "Construido en abierto", "subtitle": "Todo el monorepo es público en GitHub. Las ediciones Community son gratuitas, las Pro son comerciales.", "primary_cta": {"label": "Ver en GitHub"}, "secondary_cta": {"label": "Contacto"}}}},
        "pt": {"title": "Fundador", "content": {"hero": {"title": "Mahmoud Ezzat Moustafa", "subtitle": "Programador full-stack, contribuidor de código aberto e o engenheiro por detrás da structa.cloud. Django, Wagtail e sistemas baseados em IA.", "primary_cta": {"label": "Conheça a equipa"}, "secondary_cta": {"label": "Ver no GitHub"}, "trusted_by": "Python · Django · Wagtail · AI tooling"}, "cta": {"title": "Construído em aberto", "subtitle": "Todo o monorepo é público no GitHub. As edições Community são gratuitas, as Pro são comerciais.", "primary_cta": {"label": "Ver no GitHub"}, "secondary_cta": {"label": "Contacto"}}}},
    },
    "startup": {
        "ar": {
            "title": "قصة الشركة الناشئة",
            "search_description": "كيف نمت Structa Cloud من مشاريع مستقلة إلى عائلة من المنتجات والمكتبات.",
            "body": "<p>بدأت الرحلة من مشاريع صغيرة، ثم تحولت الأدوات المتكررة إلى مكتبات ومنتجات مستقلة تشترك في بنية واحدة.</p>",
            "content": {
                "hero": {"title": "من مشروع صغير إلى نظام منتجات", "subtitle": "قصة نمو تدريجي مبني على إعادة الاستخدام والإطلاق المستمر."},
                "process": {"title": "المحطات الرئيسية"},
                "stats": {"title": "القصة بالأرقام"},
                "cta": {"title": "ابدأ من خطوتك الأولى", "subtitle": "الإصدار الأول المفيد أفضل من خارطة طريق لا تنتهي."},
            },
        },
        "sv": {"title": "Startup", "content": {"hero": {"title": "Startup", "subtitle": "Hur structa.cloud växte från frilans-Django-projekt till ett monorepo av öppen källkodsprodukter, AI-verktyg och en stationär POS-applikation.", "primary_cta": {"label": "Se produkterna"}, "secondary_cta": {"label": "Träffa grundaren"}, "trusted_by": "2019 · frilans → 2026 · fem produkter"}, "cta": {"title": "Byggt i öppenhet, levererat som HTML", "subtitle": "Community-utgåvorna och kärnbiblioteken är offentliga på GitHub. Betalda utgåvor är kommersiella.", "primary_cta": {"label": "Visa på GitHub"}, "secondary_cta": {"label": "Läs Om oss-sidan"}}}},
        "fr": {"title": "Start-up", "content": {"hero": {"title": "La start-up", "subtitle": "Comment structa.cloud est passé de projets Django indépendants à un monorepo de produits open source, d'outils d'IA et d'une application de caisse de bureau.", "primary_cta": {"label": "Voir les produits"}, "secondary_cta": {"label": "Rencontrer le fondateur"}, "trusted_by": "2019 · freelance → 2026 · cinq produits"}, "cta": {"title": "Construit en toute transparence, livré en HTML", "subtitle": "Les éditions Communauté et les bibliothèques de base sont publiques sur GitHub. Les éditions payantes sont commerciales.", "primary_cta": {"label": "Voir sur GitHub"}, "secondary_cta": {"label": "Lire la page À propos"}}}},
        "de": {"title": "Startup", "content": {"hero": {"title": "Das Startup", "subtitle": "Wie structa.cloud von freiberuflichen Django-Projekten zu einem Monorepo aus Open-Source-Produkten, KI-Tools und einer Desktop-POS-Anwendung wurde.", "primary_cta": {"label": "Produkte ansehen"}, "secondary_cta": {"label": "Den Gründer kennenlernen"}, "trusted_by": "2019 · freiberuflich → 2026 · fünf Produkte"}, "cta": {"title": "In Offenheit gebaut, als HTML ausgeliefert", "subtitle": "Community-Editionen und die Kernbibliotheken sind öffentlich auf GitHub. Kostenpflichtige Editionen sind kommerziell.", "primary_cta": {"label": "Auf GitHub ansehen"}, "secondary_cta": {"label": "Die Über-uns-Seite lesen"}}}},
        "es": {"title": "Startup", "content": {"hero": {"title": "La startup", "subtitle": "Cómo structa.cloud pasó de proyectos Django freelance a un monorepo de productos de código abierto, herramientas de IA y una aplicación de punto de venta de escritorio.", "primary_cta": {"label": "Ver los productos"}, "secondary_cta": {"label": "Conoce al fundador"}, "trusted_by": "2019 · freelance → 2026 · cinco productos"}, "cta": {"title": "Construido en abierto, entregado como HTML", "subtitle": "Las ediciones Community y las bibliotecas principales son públicas en GitHub. Las ediciones de pago son comerciales.", "primary_cta": {"label": "Ver en GitHub"}, "secondary_cta": {"label": "Leer la página Acerca de"}}}},
        "pt": {"title": "Startup", "content": {"hero": {"title": "A startup", "subtitle": "Como a structa.cloud cresceu de projetos Django freelance para um monorepo de produtos de código aberto, ferramentas de IA e uma aplicação POS de secretária.", "primary_cta": {"label": "Ver os produtos"}, "secondary_cta": {"label": "Conheça o fundador"}, "trusted_by": "2019 · freelance → 2026 · cinco produtos"}, "cta": {"title": "Construído em aberto, entregue como HTML", "subtitle": "As edições Community e as bibliotecas principais são públicas no GitHub. As edições pagas são comerciais.", "primary_cta": {"label": "Ver no GitHub"}, "secondary_cta": {"label": "Ler a página Sobre"}}}},
    },
    # Delivery phases and prompts are also Wagtail subpages. Their scalar
    # prompt fields are overridden through ``content`` by the page API.
    "discover": {
        "ar": {
            "title": "الاكتشاف",
            "search_description": "تحويل الموجز إلى نموذج محتوى ومسار إصدار أول واضح.",
            "body": "<p>نحوّل الموجز إلى نموذج مستند واضح واتجاه بصري وقرار قابل للقياس للإصدار الأول.</p>",
            "content": {"phase_label": "الاكتشاف", "outcomes": ["موجز محدد", "خريطة محتوى ومسارات", "سجل قرارات الإصدار الأول"]},
        },
        "sv": {"title": "Utforska", "content": {"phase_label": "utforskning", "outcomes": ["En avgränsad brief", "En karta över innehåll och vägar", "En beslutslogg för första releasen"]}},
        "fr": {"title": "Découvrir", "content": {"phase_label": "découverte", "outcomes": ["Un brief délimité", "Une carte des contenus et des parcours", "Un journal de décisions pour la première version"]}},
        "de": {"title": "Entdecken", "content": {"phase_label": "entdeckung", "outcomes": ["Ein abgegrenzter Brief", "Eine Karte aus Inhalten und Routen", "Ein Entscheidungsprotokoll für den ersten Release"]}},
        "es": {"title": "Descubrir", "content": {"phase_label": "descubrimiento", "outcomes": ["Un brief acotado", "Un mapa de contenido y rutas", "Un registro de decisiones para el primer lanzamiento"]}},
        "pt": {"title": "Descobrir", "content": {"phase_label": "descoberta", "outcomes": ["Um brief delimitado", "Um mapa de conteúdos e rotas", "Um registo de decisões para o primeiro lançamento"]}},
    },
    "build": {
        "ar": {
            "title": "البناء",
            "search_description": "بناء أصغر مسار مكتمل يبدأ من نموذج المحتوى وينتهي بواجهة قابلة للاستخدام.",
            "body": "<p>نبني المسار الكامل الأصغر كصفحة HTML من الخادم، ثم نضيف التحسين التدريجي حيث يخدم المستند.</p>",
            "content": {"phase_label": "البناء", "outcomes": ["نموذج محتوى يعمل", "مسار مستجيب", "اختبارات للتحسين التدريجي"]},
        },
        "sv": {"title": "Bygg", "content": {"phase_label": "bygg", "outcomes": ["En fungerande innehållsmodell", "En responsiv dokumentrutt", "Kontroller av progressiv förbättring"]}},
        "fr": {"title": "Construire", "content": {"phase_label": "construction", "outcomes": ["Un modèle de contenu fonctionnel", "Un parcours documentaire responsive", "Des contrôles d'amélioration progressive"]}},
        "de": {"title": "Bauen", "content": {"phase_label": "bau", "outcomes": ["Ein funktionierendes Content-Modell", "Eine responsive Dokument-Route", "Checks für progressive Enhancement"]}},
        "es": {"title": "Construir", "content": {"phase_label": "construcción", "outcomes": ["Un modelo de contenido funcional", "Una ruta documental responsive", "Controles de mejora progresiva"]}},
        "pt": {"title": "Construir", "content": {"phase_label": "construção", "outcomes": ["Um modelo de conteúdo funcional", "Uma rota documental responsive", "Verificações de melhoramento progressivo"]}},
    },
    "launch": {
        "ar": {
            "title": "الإطلاق",
            "search_description": "إطلاق يمكن الاعتماد عليه مع تكافؤ المحتوى وتسليم واضح للفريق.",
            "body": "<p>نشحن إصداراً يمكن الاعتماد عليه مع تكافؤ المحتوى والمراقبة وتسليم يستطيع الفريق امتلاكه.</p>",
            "content": {"phase_label": "الإطلاق", "outcomes": ["فحوص SEO وإتاحة", "دليل نشر وتشغيل", "تسليم للمحررين"]},
        },
        "sv": {"title": "Lansera", "content": {"phase_label": "lansering", "outcomes": ["SEO- och tillgänglighetskontroller", "Driftsättningsrunbook", "Överlämning till redaktörer"]}},
        "fr": {"title": "Lancer", "content": {"phase_label": "lancement", "outcomes": ["Contrôles SEO et accessibilité", "Runbook de déploiement", "Remise aux éditeurs"]}},
        "de": {"title": "Starten", "content": {"phase_label": "start", "outcomes": ["SEO- und Barrierefreiheits-Checks", "Deployment-Runbook", "Übergabe an Redakteure"]}},
        "es": {"title": "Lanzar", "content": {"phase_label": "lanzamiento", "outcomes": ["Comprobaciones de SEO y accesibilidad", "Runbook de despliegue", "Entrega a editores"]}},
        "pt": {"title": "Lançar", "content": {"phase_label": "lançamento", "outcomes": ["Verificações de SEO e acessibilidade", "Runbook de implementação", "Entrega a editores"]}},
    },
    "enhance": {
        "ar": {
            "title": "التحسين",
            "search_description": "تحسين النظام الحي عبر قياس المحتوى والأداء والتفاعلات.",
            "body": "<p>نحسّن النظام الحي عبر تغييرات مقاسة في المحتوى والأداء والتفاعل، من دون فقدان ملكية الفريق.</p>",
            "content": {"phase_label": "التحسين", "outcomes": ["قائمة تحسينات مقاسة", "أنماط محتوى قابلة لإعادة الاستخدام", "دورة تكرار آمنة"]},
        },
        "sv": {"title": "Förbättra", "content": {"phase_label": "förbättring", "outcomes": ["En mätt förbättringsbacklog", "Återanvändbara innehållsmönster", "En trygg iterationsloop"]}},
        "fr": {"title": "Améliorer", "content": {"phase_label": "amélioration", "outcomes": ["Un backlog d'amélioration mesuré", "Des motifs de contenu réutilisables", "Une boucle d'itération sûre"]}},
        "de": {"title": "Verbessern", "content": {"phase_label": "verbesserung", "outcomes": ["Ein gemessener Verbesserungs-Backlog", "Wiederverwendbare Content-Muster", "Eine sichere Iterationsschleife"]}},
        "es": {"title": "Mejorar", "content": {"phase_label": "mejora", "outcomes": ["Un backlog de mejoras medido", "Patrones de contenido reutilizables", "Un bucle de iteración seguro"]}},
        "pt": {"title": "Melhorar", "content": {"phase_label": "melhoria", "outcomes": ["Um backlog de melhorias medido", "Padrões de conteúdo reutilizáveis", "Um ciclo de iteração seguro"]}},
    },
    "shape-the-brief": {
        "ar": {
            "title": "صياغة الموجز",
            "search_description": "تحويل موجز المنتج إلى نطاق واضح للإصدار الأول.",
            "content": {"prompt": "حوّل موجز هذا المنتج إلى إصدار أول مركز، مع تحديد المستخدم والمحتوى والمسارات وقيود النجاح.", "context": "استخدم هذا قبل بدء التصميم أو التنفيذ.", "output": "نطاق مختصر مع الافتراضات والمخاطر وقائمة قبول.", "tool": "Wagtail واكتشاف المنتج"},
        },
        "sv": {"title": "Forma briefen", "content": {"prompt": "Förvandla denna produktbrief till en fokuserad första release med användar-, innehålls-, väg- och framgångskrav.", "context": "Använd detta innan design eller implementation börjar.", "output": "En kortfattad omfattning med antaganden, risker och en acceptanslista.", "tool": "Wagtail + produktutforskning"}},
        "fr": {"title": "Façonner le brief", "content": {"prompt": "Transformez ce brief produit en une première version ciblée, avec des contraintes d'utilisateur, de contenu, de parcours et de réussite.", "context": "À utiliser avant le début de la conception ou de l'implémentation.", "output": "Un périmètre concis, avec hypothèses, risques et liste de critères d'acceptation.", "tool": "Wagtail + découverte produit"}},
        "de": {"title": "Den Brief formen", "content": {"prompt": "Verwandeln Sie diesen Produktbrief in einen fokussierten ersten Release mit Nutzer-, Inhalts-, Routen- und Erfolgsanforderungen.", "context": "Verwenden Sie dies, bevor Design oder Implementierung beginnen.", "output": "Ein prägnanter Umfang mit Annahmen, Risiken und einer Abnahmeliste.", "tool": "Wagtail + Produkt-Discovery"}},
        "es": {"title": "Dar forma al brief", "content": {"prompt": "Convierte este brief de producto en un primer lanzamiento enfocado, con restricciones de usuario, contenido, ruta y éxito.", "context": "Úsalo antes de que empiecen el diseño o la implementación.", "output": "Un alcance conciso con supuestos, riesgos y una lista de aceptación.", "tool": "Wagtail + descubrimiento de producto"}},
        "pt": {"title": "Moldar o brief", "content": {"prompt": "Transforme este brief de produto num primeiro lançamento focado, com restrições de utilizador, conteúdo, rota e sucesso.", "context": "Use isto antes de começar o design ou a implementação.", "output": "Um âmbito conciso com pressupostos, riscos e uma lista de aceitação.", "tool": "Wagtail + descoberta de produto"}},
    },
    "build-the-first-vertical-slice": {
        "ar": {
            "title": "بناء المسار الرأسي الأول",
            "search_description": "تنفيذ رحلة مستخدم كاملة من نموذج Wagtail إلى HTML قابل للوصول.",
            "content": {"prompt": "نفّذ رحلة مستخدم كاملة من نموذج Wagtail إلى HTML قابل للوصول، مع تحسين تدريجي عند الحاجة فقط.", "context": "حافظ على قابلية استخدام المسار المولّد من الخادم من دون JavaScript.", "output": "مسار رأسي مختبر يضم النموذج وواجهة API والقالب وحالات المتصفح.", "tool": "Astro وHTMX وAlpine"},
        },
        "sv": {"title": "Bygg den första vertikala skivan", "content": {"prompt": "Implementera en komplett användarresa från Wagtail-modell till tillgänglig HTML, med progressiv förbättring endast där det behövs.", "context": "Håll den serverrenderade vägen användbar utan JavaScript.", "output": "En testad vertikal skiva med modell, API, mall och webbläsartillstånd.", "tool": "Astro + HTMX + Alpine"}},
        "fr": {"title": "Construire la première tranche verticale", "content": {"prompt": "Implémentez un parcours utilisateur complet, du modèle Wagtail au HTML accessible, avec une amélioration progressive uniquement là où c'est nécessaire.", "context": "Gardez le parcours rendu côté serveur utilisable sans JavaScript.", "output": "Une tranche verticale testée, avec modèle, API, gabarit et états navigateur.", "tool": "Astro + HTMX + Alpine"}},
        "de": {"title": "Den ersten vertikalen Slice bauen", "content": {"prompt": "Setzen Sie eine vollständige User Journey vom Wagtail-Modell bis zu barrierefreiem HTML um, mit progressive Enhancement nur dort, wo es nötig ist.", "context": "Halten Sie den serverseitig gerenderten Pfad auch ohne JavaScript nutzbar.", "output": "Ein getesteter vertikaler Slice mit Modell, API, Template und Browser-Zuständen.", "tool": "Astro + HTMX + Alpine"}},
        "es": {"title": "Construye la primera rebanada vertical", "content": {"prompt": "Implementa un recorrido de usuario completo, del modelo de Wagtail al HTML accesible, con mejora progresiva solo donde haga falta.", "context": "Mantén la ruta renderizada en servidor utilizable sin JavaScript.", "output": "Una rebanada vertical probada, con modelo, API, plantilla y estados de navegador.", "tool": "Astro + HTMX + Alpine"}},
        "pt": {"title": "Construir a primeira fatia vertical", "content": {"prompt": "Implemente um percurso de utilizador completo, do modelo Wagtail ao HTML acessível, com melhoramento progressivo apenas onde for necessário.", "context": "Mantenha o percurso renderizado no servidor utilizável sem JavaScript.", "output": "Uma fatia vertical testada, com modelo, API, template e estados de navegador.", "tool": "Astro + HTMX + Alpine"}},
    },
    "prepare-the-release": {
        "ar": {
            "title": "تجهيز الإصدار",
            "search_description": "مراجعة المسارات والمحتوى والإتاحة وتكافؤ الواجهات قبل النشر.",
            "content": {"prompt": "راجع هذا الإصدار بحثاً عن المسارات المكسورة والمحتوى الناقص ومشكلات الإتاحة واختلافات الواجهة قبل النشر.", "context": "طبّق قائمة الفحص نفسها على مساري Astro وDjango.", "output": "تقرير إصدار مرتب حسب الأولوية مع الإصلاحات ومعايير موافقة واضحة.", "tool": "التحقق من Django وAstro"},
        },
        "sv": {"title": "Förbered releasen", "content": {"prompt": "Granska denna release för trasiga rutter, saknat innehåll, tillgänglighetsregressioner och backend/frontend-paritet före driftsättning.", "context": "Kör samma checklista mot Astro- och Django-vägarna.", "output": "En prioriterad release-rapport med åtgärder och tydliga godkännandekriterier.", "tool": "Django + Astro-verifiering"}},
        "fr": {"title": "Préparer la version", "content": {"prompt": "Auditez cette version avant déploiement : parcours cassés, contenu manquant, régressions d'accessibilité et parité backend/frontend.", "context": "Appliquez la même liste de contrôle aux parcours Astro et Django.", "output": "Un rapport de version priorisé avec correctifs et critères d'approbation explicites.", "tool": "Vérification Django + Astro"}},
        "de": {"title": "Den Release vorbereiten", "content": {"prompt": "Prüfen Sie diesen Release vor dem Deployment auf kaputte Routen, fehlende Inhalte, Barrierefreiheits-Regressionen und Backend/Frontend-Parität.", "context": "Führen Sie dieselbe Checkliste gegen die Astro- und Django-Pfade aus.", "output": "Ein priorisierter Release-Bericht mit Fixes und expliziten Abnahmekriterien.", "tool": "Django + Astro-Verifikation"}},
        "es": {"title": "Prepara el lanzamiento", "content": {"prompt": "Audita este lanzamiento antes del despliegue: rutas rotas, contenido faltante, regresiones de accesibilidad y paridad backend/frontend.", "context": "Ejecuta la misma lista de comprobaciones en las rutas de Astro y Django.", "output": "Un informe de lanzamiento priorizado con correcciones y criterios de aprobación explícitos.", "tool": "Verificación Django + Astro"}},
        "pt": {"title": "Preparar o lançamento", "content": {"prompt": "Audite este lançamento antes da implementação: rotas quebradas, conteúdo em falta, regressões de acessibilidade e paridade backend/frontend.", "context": "Execute a mesma lista de verificação nos percursos Astro e Django.", "output": "Um relatório de lançamento priorizado com correções e critérios de aprovação explícitos.", "tool": "Verificação Django + Astro"}},
    },
    "enhance-without-drift": {
        "ar": {
            "title": "التحسين من دون انحراف",
            "search_description": "تحسين الصفحة مع الحفاظ على ملكية المحتوى وتكافؤ العرض وإمكانية الوصول.",
            "content": {"prompt": "حسّن هذه الصفحة مع الحفاظ على ملكية المحتوى وتكافؤ العرض وإمكانية الوصول ولغة التصميم الحالية.", "context": "فضّل المكونات القابلة لإعادة الاستخدام ومحتوى Wagtail على markup خاص بصفحة واحدة.", "output": "مجموعة تغييرات صغيرة مع فحوص تراجع وسبب موثق لكل تغيير.", "tool": "مكونات django-fusion"},
        },
        "sv": {"title": "Förbättra utan drift", "content": {"prompt": "Förbättra denna sida samtidigt som du bevarar innehållsägarskap, renderingsparitet, tillgänglighet och det befintliga designspråket.", "context": "Föredra återanvändbara komponenter och Wagtail-hanterat innehåll framför engångsmarkup.", "output": "En liten ändringsuppsättning med regressionskontroller och en dokumenterad anledning för varje ändring.", "tool": "django-fusion-komponenter"}},
        "fr": {"title": "Améliorer sans dérive", "content": {"prompt": "Améliorez cette page en préservant la propriété du contenu, la parité de rendu, l'accessibilité et le langage de conception existant.", "context": "Privilégiez les composants réutilisables et les contenus gérés par Wagtail plutôt qu'un balisage de page ponctuel.", "output": "Un petit ensemble de modifications avec contrôles de régression et une raison documentée pour chaque changement.", "tool": "composants django-fusion"}},
        "de": {"title": "Verbessern ohne Drift", "content": {"prompt": "Verbessern Sie diese Seite und bewahren Sie dabei Content-Ownership, Render-Parität, Barrierefreiheit und die bestehende Designsprache.", "context": "Bevorzugen Sie wiederverwendbare Komponenten und Wagtail-verwaltete Inhalte gegenüber einmaligem Seiten-Markup.", "output": "Ein kleiner Änderungssatz mit Regressions-Checks und einer dokumentierten Begründung für jede Änderung.", "tool": "django-fusion-Komponenten"}},
        "es": {"title": "Mejorar sin desviación", "content": {"prompt": "Mejora esta página preservando la propiedad del contenido, la paridad de renderizado, la accesibilidad y el lenguaje de diseño existente.", "context": "Prefiere componentes reutilizables y contenido gestionado por Wagtail sobre el marcado de página puntual.", "output": "Un conjunto de cambios pequeño con comprobaciones de regresión y una razón documentada para cada cambio.", "tool": "componentes django-fusion"}},
        "pt": {"title": "Melhorar sem deriva", "content": {"prompt": "Melhore esta página preservando a propriedade do conteúdo, a paridade de renderização, a acessibilidade e a linguagem de design existente.", "context": "Prefira componentes reutilizáveis e conteúdo gerido pelo Wagtail em vez de markup de página avulso.", "output": "Um conjunto de alterações pequeno com verificações de regressão e uma razão documentada para cada alteração.", "tool": "componentes django-fusion"}},
    },
    # Blog post children.
    "why-landing-pages-as-documents": {
        "ar": {
            "title": "الزيارة الأولى السريعة قرار منتج",
            "search_description": "لماذا تعد سرعة الصفحة الأولى جزءاً من الثقة بالمنتج.",
            "content": {"hero": {"title": "الزيارة الأولى السريعة قرار منتج", "subtitle": "الأداء جزء من الثقة، والصفحة الواضحة التي تصل بسرعة تمنح العميل يقيناً أكبر."}},
        },
        "sv": {"title": "Ett snabbt första besök är ett produktbeslut", "content": {"hero": {"title": "Ett snabbt första besök är ett produktbeslut", "subtitle": "Prestanda är en del av förtroendet. En tydlig sida som levereras snabbt ger kunderna mer förtroende före det första samtalet."}}},
        "fr": {"title": "Une première visite rapide est une décision produit", "content": {"hero": {"title": "Une première visite rapide est une décision produit", "subtitle": "La performance fait partie de la confiance. Une page claire qui arrive vite rassure les clients avant la première conversation."}}},
        "de": {"title": "Ein schneller erster Besuch ist eine Produktentscheidung", "content": {"hero": {"title": "Ein schneller erster Besuch ist eine Produktentscheidung", "subtitle": "Performance ist Teil von Vertrauen. Eine klare Seite, die schnell ankommt, gibt Kunden mehr Zuversicht vor dem ersten Gespräch."}}},
        "es": {"title": "Una primera visita rápida es una decisión de producto", "content": {"hero": {"title": "Una primera visita rápida es una decisión de producto", "subtitle": "El rendimiento forma parte de la confianza. Una página clara que llega rápido da a los clientes más seguridad antes de la primera conversación."}}},
        "pt": {"title": "Uma primeira visita rápida é uma decisão de produto", "content": {"hero": {"title": "Uma primeira visita rápida é uma decisão de produto", "subtitle": "O desempenho faz parte da confiança. Uma página clara que chega depressa dá aos clientes mais confiança antes da primeira conversa."}}},
    },
    "htmx-fragments-vs-json-apis": {
        "ar": {
            "title": "تصميم مسارات ثنائية اللغة بلا تكرار",
            "search_description": "طريقة عملية للحفاظ على اتساق المحتوى العربي والإنجليزي.",
            "content": {"hero": {"title": "تصميم مسارات ثنائية اللغة بلا تكرار", "subtitle": "كيف يبقى المحتوى متسقاً مع السماح لكل لغة بأن تبدو طبيعية."}},
        },
        "sv": {"title": "Designa tvåspråkiga resor utan dubbelarbete", "content": {"hero": {"title": "Designa tvåspråkiga resor utan dubbelarbete", "subtitle": "Ett praktiskt sätt att hålla arabiskt och engelskt innehåll i linje samtidigt som varje språk låter naturligt."}}},
        "fr": {"title": "Concevoir des parcours bilingues sans duplication", "content": {"hero": {"title": "Concevoir des parcours bilingues sans duplication", "subtitle": "Une façon pratique de garder les contenus arabe et anglais alignés tout en laissant chaque langue sonner naturellement."}}},
        "de": {"title": "Zweisprachige Journeys ohne Duplikate gestalten", "content": {"hero": {"title": "Zweisprachige Journeys ohne Duplikate gestalten", "subtitle": "Ein praktischer Weg, arabische und englische Inhalte in Einklang zu halten, während jede Sprache natürlich klingt."}}},
        "es": {"title": "Diseñar recorridos bilingües sin duplicación", "content": {"hero": {"title": "Diseñar recorridos bilingües sin duplicación", "subtitle": "Una forma práctica de mantener alineados los contenidos en árabe e inglés y que cada idioma suene natural."}}},
        "pt": {"title": "Conceber percursos bilingues sem duplicação", "content": {"hero": {"title": "Conceber percursos bilingues sem duplicação", "subtitle": "Uma forma prática de manter os conteúdos em árabe e inglês alinhados, deixando cada língua soar natural."}}},
    },
    "wagtail-streamfield-marketing": {
        "ar": {
            "title": "امنح فريق المحتوى غرفة تحكم مفيدة",
            "search_description": "كيف تساعد بنية التحرير فرق التسويق على التحرك بسرعة بأمان.",
            "content": {"hero": {"title": "امنح فريق المحتوى غرفة تحكم مفيدة", "subtitle": "بنية تحرير واضحة تمنح الفريق سرعة من دون تحويل كل صفحة إلى تفاوض تصميمي."}},
        },
        "sv": {"title": "Ge innehållsteamen ett användbart kontrollrum", "content": {"hero": {"title": "Ge innehållsteamen ett användbart kontrollrum", "subtitle": "Bra redaktionell struktur hjälper marknadsteam att röra sig snabbt utan att varje sida blir en designförhandling."}}},
        "fr": {"title": "Offrez aux équipes de contenu une salle de contrôle utile", "content": {"hero": {"title": "Offrez aux équipes de contenu une salle de contrôle utile", "subtitle": "Une bonne structure éditoriale aide les équipes marketing à avancer vite sans transformer chaque page en négociation de design."}}},
        "de": {"title": "Geben Sie Content-Teams einen nützlichen Kontrollraum", "content": {"hero": {"title": "Geben Sie Content-Teams einen nützlichen Kontrollraum", "subtitle": "Eine gute redaktionelle Struktur hilft Marketing-Teams, schnell voranzukommen, ohne jede Seite zu einer Design-Verhandlung zu machen."}}},
        "es": {"title": "Da a los equipos de contenido una sala de control útil", "content": {"hero": {"title": "Da a los equipos de contenido una sala de control útil", "subtitle": "Una buena estructura editorial ayuda a los equipos de marketing a moverse rápido sin convertir cada página en una negociación de diseño."}}},
        "pt": {"title": "Dê às equipas de conteúdo uma sala de controlo útil", "content": {"hero": {"title": "Dê às equipas de conteúdo uma sala de controlo útil", "subtitle": "Uma boa estrutura editorial ajuda as equipas de marketing a avançar depressa sem transformar cada página numa negociação de design."}}},
    },
    "alpine-reactivity-landing": {
        "ar": {
            "title": "تفاعلات صغيرة، تركيز أفضل",
            "search_description": "استخدم التفاعل لتوضيح القرار، لا لإضافة ضجيج إلى الصفحة.",
            "content": {"hero": {"title": "تفاعلات صغيرة، تركيز أفضل", "subtitle": "التفاعل الجيد يوضح الخطوة التالية ولا يشتت عن الهدف."}},
        },
        "sv": {"title": "Små interaktioner, bättre fokus", "content": {"hero": {"title": "Små interaktioner, bättre fokus", "subtitle": "Använd interaktion där den förtydligar ett beslut, inte där den lägger till brus på en sida som bara ska hjälpa någon framåt."}}},
        "fr": {"title": "De petites interactions, une meilleure concentration", "content": {"hero": {"title": "De petites interactions, une meilleure concentration", "subtitle": "Utilisez l'interaction là où elle clarifie une décision, pas là où elle ajoute du bruit à une page qui devrait simplement aider à avancer."}}},
        "de": {"title": "Kleine Interaktionen, besserer Fokus", "content": {"hero": {"title": "Kleine Interaktionen, besserer Fokus", "subtitle": "Setzen Sie Interaktion dort ein, wo sie eine Entscheidung klärt, nicht wo sie einer Seite Rauschen hinzufügt, die einfach beim Vorankommen helfen soll."}}},
        "es": {"title": "Interacciones pequeñas, mejor concentración", "content": {"hero": {"title": "Interacciones pequeñas, mejor concentración", "subtitle": "Usa la interacción donde aclara una decisión, no donde añade ruido a una página que simplemente debería ayudar a avanzar."}}},
        "pt": {"title": "Interações pequenas, melhor foco", "content": {"hero": {"title": "Interações pequenas, melhor foco", "subtitle": "Use a interação onde clarifica uma decisão, não onde adiciona ruído a uma página que devia simplesmente ajudar a avançar."}}},
    },
    "monorepo-six-products": {
        "ar": {
            "title": "ابنِ نظاماً يستطيع فريقك وراثته",
            "search_description": "دروس عملية لبناء منتجات متعددة من مستودع واحد يمكن للفريق توسيعه.",
            "content": {"hero": {"title": "ابنِ نظاماً يستطيع فريقك وراثته", "subtitle": "أفضل تسليم ليس نصباً تقنياً، بل قرارات مفهومة يمكن توسيعها بأمان."}},
        },
        "sv": {"title": "Bygg ett system ditt team kan ärva", "content": {"hero": {"title": "Bygg ett system ditt team kan ärva", "subtitle": "Den bästa plattformsöverlämningen är inte ett tekniskt monument. Det är en uppsättning begripliga beslut som människor säkert kan utöka."}}},
        "fr": {"title": "Construisez un système que votre équipe peut hériter", "content": {"hero": {"title": "Construisez un système que votre équipe peut hériter", "subtitle": "La meilleure remise de plateforme n'est pas un monument technique. C'est un ensemble de décisions compréhensibles que l'on peut étendre sans risque."}}},
        "de": {"title": "Bauen Sie ein System, das Ihr Team erben kann", "content": {"hero": {"title": "Bauen Sie ein System, das Ihr Team erben kann", "subtitle": "Die beste Plattform-Übergabe ist kein technisches Denkmal. Sie ist ein Satz verständlicher Entscheidungen, die Menschen sicher erweitern können."}}},
        "es": {"title": "Construye un sistema que tu equipo pueda heredar", "content": {"hero": {"title": "Construye un sistema que tu equipo pueda heredar", "subtitle": "La mejor entrega de plataforma no es un monumento técnico. Es un conjunto de decisiones comprensibles que la gente puede ampliar con seguridad."}}},
        "pt": {"title": "Construa um sistema que a sua equipa possa herdar", "content": {"hero": {"title": "Construa um sistema que a sua equipa possa herdar", "subtitle": "A melhor entrega de plataforma não é um monumento técnico. É um conjunto de decisões compreensíveis que as pessoas podem expandir com segurança."}}},
    },
    "server-time-streamed-htmx": {
        "ar": {
            "title": "ميزانية أداء عملية للإطلاق",
            "search_description": "حافظ على المسار الحرج صغيراً وقِس التجربة على الشبكات الحقيقية.",
            "content": {"hero": {"title": "ميزانية أداء عملية للإطلاق", "subtitle": "اترك مساحة للمحتوى المهم، وقِس التجربة على الشبكات الإقليمية الفعلية."}},
        },
        "sv": {"title": "En praktisk prestandabudget för lansering", "content": {"hero": {"title": "En praktisk prestandabudget för lansering", "subtitle": "Reservera plats för det innehåll som betyder något, håll den kritiska vägen liten och mät upplevelsen på riktiga regionala nätverk."}}},
        "fr": {"title": "Un budget de performance pratique pour le lancement", "content": {"hero": {"title": "Un budget de performance pratique pour le lancement", "subtitle": "Réservez de la place pour le contenu qui compte, gardez le chemin critique petit et mesurez l'expérience sur de vrais réseaux régionaux."}}},
        "de": {"title": "Ein praktisches Performance-Budget für den Launch", "content": {"hero": {"title": "Ein praktisches Performance-Budget für den Launch", "subtitle": "Reservieren Sie Platz für den Inhalt, der zählt, halten Sie den kritischen Pfad klein und messen Sie die Erfahrung in echten regionalen Netzwerken."}}},
        "es": {"title": "Un presupuesto de rendimiento práctico para el lanzamiento", "content": {"hero": {"title": "Un presupuesto de rendimiento práctico para el lanzamiento", "subtitle": "Reserva espacio para el contenido que importa, mantén pequeño el camino crítico y mide la experiencia en redes regionales reales."}}},
        "pt": {"title": "Um orçamento de desempenho prático para o lançamento", "content": {"hero": {"title": "Um orçamento de desempenho prático para o lançamento", "subtitle": "Reserve espaço para o conteúdo que importa, mantenha pequeno o percurso crítico e meça a experiência em redes regionais reais."}}},
    },
    "services": {
        "ar": {
            "title": "الخدمات",
            "body": "<p>نبني مواقع ومنتجات تساعد فرق التسويق والعمليات على خدمة العملاء في المنطقة بثقة.</p>",
            "content": {
                "hero": {"title": "من الفكرة إلى السوق", "subtitle": "نصمم ونبني ونحسن تجارب رقمية سريعة، ثنائية اللغة، ومهيأة للنمو.", "primary_cta": {"label": "استكشف المنتجات"}, "secondary_cta": {"label": "ابدأ محادثة"}, "trusted_by": "جاهز للعربية · جاهز للإنجليزية · مبني لفرق حقيقية"},
                "cta": {"title": "الإصدار الأول المفيد أفضل من خارطة طريق لا تنتهي", "subtitle": "نبدأ من رحلة العميل، ونطلق شريحة مركزة، ونترك لفريقك المحتوى والأدوات لمواصلة التحسين.", "primary_cta": {"label": "عرض على GitHub"}, "secondary_cta": {"label": "اقرأ التوثيق"}},
            },
        },
        "sv": {"title": "Tjänster", "content": {"hero": {"title": "Från idé till marknad", "subtitle": "Fokuserade digitala tjänster för team som behöver en tydlig kundresa och en pålitlig lansering.", "primary_cta": {"label": "Utforska produkter"}, "secondary_cta": {"label": "Inled en konversation"}, "trusted_by": "Redo för arabiska · Redo för engelska · byggt för riktiga team"}, "cta": {"title": "En användbar första release slår en bullrig färdplan", "subtitle": "Vi börjar med kundresan, lanserar en fokuserad del och lämnar ditt team med innehåll och verktyg för att fortsätta förbättra.", "primary_cta": {"label": "Visa på GitHub"}, "secondary_cta": {"label": "Läs dokumentationen"}}}},
        "fr": {"title": "Services", "content": {"hero": {"title": "De l'idée au marché", "subtitle": "Des services numériques ciblés pour les équipes qui ont besoin d'un parcours client clair et d'un lancement fiable.", "primary_cta": {"label": "Explorer les produits"}, "secondary_cta": {"label": "Engagez la conversation"}, "trusted_by": "Prêt pour l'arabe · Prêt pour l'anglais · conçu pour de vraies équipes"}, "cta": {"title": "Une première version utile vaut mieux qu'une feuille de route bruyante", "subtitle": "Nous partons du parcours client, lançons une première version ciblée et laissons à votre équipe le contenu et les outils pour continuer à l'améliorer.", "primary_cta": {"label": "Voir sur GitHub"}, "secondary_cta": {"label": "Lire la documentation"}}}},
        "de": {"title": "Leistungen", "content": {"hero": {"title": "Von der Idee zum Markt", "subtitle": "Fokussierte digitale Leistungen für Teams, die eine klare Customer Journey und einen zuverlässigen Launch brauchen.", "primary_cta": {"label": "Produkte entdecken"}, "secondary_cta": {"label": "Gespräch starten"}, "trusted_by": "Bereit für Arabisch · Bereit für Englisch · gebaut für echte Teams"}, "cta": {"title": "Ein nützlicher erster Release schlägt eine laute Roadmap", "subtitle": "Wir starten mit der Customer Journey, bringen einen fokussierten ersten Wurf heraus und überlassen Ihrem Team die Inhalte und Werkzeuge, um weiter zu verbessern.", "primary_cta": {"label": "Auf GitHub ansehen"}, "secondary_cta": {"label": "Dokumentation lesen"}}}},
        "es": {"title": "Servicios", "content": {"hero": {"title": "De la idea al mercado", "subtitle": "Servicios digitales enfocados para equipos que necesitan un recorrido del cliente claro y un lanzamiento fiable.", "primary_cta": {"label": "Explorar productos"}, "secondary_cta": {"label": "Inicia una conversación"}, "trusted_by": "Listo para árabe · Listo para inglés · hecho para equipos reales"}, "cta": {"title": "Un primer lanzamiento útil gana a una hoja de ruta ruidosa", "subtitle": "Empezamos por el recorrido del cliente, lanzamos una primera versión enfocada y dejamos a tu equipo el contenido y las herramientas para seguir mejorando.", "primary_cta": {"label": "Ver en GitHub"}, "secondary_cta": {"label": "Leer la documentación"}}}},
        "pt": {"title": "Serviços", "content": {"hero": {"title": "Da ideia ao mercado", "subtitle": "Serviços digitais focados para equipas que precisam de uma jornada do cliente clara e de um lançamento fiável.", "primary_cta": {"label": "Explorar produtos"}, "secondary_cta": {"label": "Inicie uma conversa"}, "trusted_by": "Pronto para árabe · Pronto para inglês · feito para equipas reais"}, "cta": {"title": "Um primeiro lançamento útil vence um roadmap ruidoso", "subtitle": "Começamos pela jornada do cliente, lançamos uma primeira versão focada e deixamos à sua equipa o conteúdo e as ferramentas para continuar a melhorar.", "primary_cta": {"label": "Ver no GitHub"}, "secondary_cta": {"label": "Ler a documentação"}}}},
    },
    "products": {
        "ar": {
            "title": "المنتجات",
            "body": "<p>منتجات عملية لنقاط البيع والتعلم والمحتوى والملفات المهنية، مصممة لتناسب إيقاع الفرق والأسواق المتنوعة.</p>",
            "content": {
                "hero": {"title": "منتجات جاهزة للنمو", "subtitle": "أدوات ومنصات تساعد فريقك على البيع والتعلم والنشر وخدمة العملاء.", "primary_cta": {"label": "شاهد الإصدارات"}, "secondary_cta": {"label": "تصفح المستودع"}},
                "cta": {"title": "مبني في العلن، يُسلَّم كصفحة HTML", "subtitle": "بعض المنتجات والمكتبات الأساسية متاحة علناً على GitHub. تختلف الإصدارات والتراخيص حسب المنتج؛ Precis LMS متاح بإصدار Solo وBusiness.", "primary_cta": {"label": "عرض على GitHub"}, "secondary_cta": {"label": "تواصل معنا"}},
            },
        },
        "sv": {"title": "Produkter", "content": {"hero": {"title": "Det mesta av det vi bygger, levererat som", "subtitle": "Hela katalogen: produkter med utgåvor och priser, plus projekten bakom dem, från ett enda monorepo.", "primary_cta": {"label": "Se utgåvorna"}, "secondary_cta": {"label": "Bläddra i arkivet"}}, "cta": {"title": "Byggt i öppenhet, levererat som HTML", "subtitle": "Vissa produkter och kärnbiblioteken är offentliga på GitHub. Utgåvor och licenser varierar mellan produkter; Precis LMS erbjuds som Solo och Business.", "primary_cta": {"label": "Visa på GitHub"}, "secondary_cta": {"label": "Ta kontakt"}}}},
        "fr": {"title": "Produits", "content": {"hero": {"title": "L'essentiel de ce que nous construisons, livré comme", "subtitle": "Le catalogue complet : produits avec éditions et tarifs, plus les projets qui les sous-tendent, issus d'un seul monorepo.", "primary_cta": {"label": "Voir les éditions"}, "secondary_cta": {"label": "Parcourir le dépôt"}}, "cta": {"title": "Construit en toute transparence, livré en HTML", "subtitle": "Certains produits et les bibliothèques de base sont publics sur GitHub. La disponibilité des éditions et les licences varient selon le produit ; Precis LMS est proposé en Solo et Business.", "primary_cta": {"label": "Voir sur GitHub"}, "secondary_cta": {"label": "Contactez-nous"}}}},
        "de": {"title": "Produkte", "content": {"hero": {"title": "Das meiste, was wir bauen, geliefert als", "subtitle": "Der vollständige Katalog: Produkte mit Editionen und Preisen, plus die Projekte dahinter, aus einem einzigen Monorepo.", "primary_cta": {"label": "Editionen ansehen"}, "secondary_cta": {"label": "Repository durchstöbern"}}, "cta": {"title": "In Offenheit gebaut, als HTML ausgeliefert", "subtitle": "Einige Produkte und die Kernbibliotheken sind auf GitHub öffentlich. Editionen und Lizenzen variieren je nach Produkt; Precis LMS ist als Solo und Business erhältlich.", "primary_cta": {"label": "Auf GitHub ansehen"}, "secondary_cta": {"label": "Kontakt aufnehmen"}}}},
        "es": {"title": "Productos", "content": {"hero": {"title": "La mayor parte de lo que construimos, entregado como", "subtitle": "El catálogo completo: productos con ediciones y precios, más los proyectos que los respaldan, desde un único monorepo.", "primary_cta": {"label": "Ver las ediciones"}, "secondary_cta": {"label": "Explorar el repositorio"}}, "cta": {"title": "Construido en abierto, entregado como HTML", "subtitle": "Algunos productos y las bibliotecas principales son públicos en GitHub. La disponibilidad de ediciones y las licencias varían según el producto; Precis LMS se ofrece en Solo y Business.", "primary_cta": {"label": "Ver en GitHub"}, "secondary_cta": {"label": "Ponte en contacto"}}}},
        "pt": {"title": "Produtos", "content": {"hero": {"title": "Grande parte do que construímos, entregue como", "subtitle": "O catálogo completo: produtos com edições e preços, mais os projetos por trás deles, a partir de um único monorepo.", "primary_cta": {"label": "Ver as edições"}, "secondary_cta": {"label": "Explorar o repositório"}}, "cta": {"title": "Construído em aberto, entregue como HTML", "subtitle": "Alguns produtos e as bibliotecas principais são públicos no GitHub. A disponibilidade de edições e as licenças variam por produto; o Precis LMS é oferecido em Solo e Business.", "primary_cta": {"label": "Ver no GitHub"}, "secondary_cta": {"label": "Entre em contacto"}}}},
    },
    "features": {
        "ar": {
            "title": "الميزات",
            "body": "<p>نوازن بين سرعة التجربة ومرونة الإدارة: صفحات خفيفة، محتوى ثنائي اللغة، وتفاعلات صغيرة لا تعيق العميل.</p>",
            "content": {
                "hero": {"title": "سريع من أول زيارة", "subtitle": "نظام محتوى وتجربة مصمم للأداء، والوضوح، والعمل عبر العربية والإنجليزية.", "primary_cta": {"label": "منتجاتنا"}, "secondary_cta": {"label": "ابدأ الآن"}},
                "cta": {"title": "مبني في العلن، يُسلَّم كصفحة HTML", "subtitle": "بعض المنتجات والمكتبات الأساسية متاحة علناً على GitHub. تختلف الإصدارات والتراخيص حسب المنتج؛ Precis LMS متاح بإصدار Solo وBusiness.", "primary_cta": {"label": "عرض على GitHub"}, "secondary_cta": {"label": "تواصل معنا"}},
            },
        },
        "sv": {"title": "Funktioner", "content": {"hero": {"title": "Byggt för att levereras som", "subtitle": "AHA-stacken, dokumenterad. Alla funktioner i Structa Cloud.", "primary_cta": {"label": "Våra produkter"}, "secondary_cta": {"label": "Kom igång"}}, "cta": {"title": "Byggt i öppenhet, levererat som HTML", "subtitle": "Vissa produkter och kärnbiblioteken är offentliga på GitHub. Utgåvor och licenser varierar mellan produkter; Precis LMS erbjuds som Solo och Business.", "primary_cta": {"label": "Visa på GitHub"}, "secondary_cta": {"label": "Ta kontakt"}}}},
        "fr": {"title": "Fonctionnalités", "content": {"hero": {"title": "Conçu pour être livré comme", "subtitle": "La stack AHA, documentée. Toutes les capacités de Structa Cloud.", "primary_cta": {"label": "Nos produits"}, "secondary_cta": {"label": "Commencer"}}, "cta": {"title": "Construit en toute transparence, livré en HTML", "subtitle": "Certains produits et les bibliothèques de base sont publics sur GitHub. La disponibilité des éditions et les licences varient selon le produit ; Precis LMS est proposé en Solo et Business.", "primary_cta": {"label": "Voir sur GitHub"}, "secondary_cta": {"label": "Contactez-nous"}}}},
        "de": {"title": "Funktionen", "content": {"hero": {"title": "Gebaut, um ausgeliefert zu werden als", "subtitle": "Der AHA-Stack, dokumentiert. Jede Funktion von Structa Cloud.", "primary_cta": {"label": "Unsere Produkte"}, "secondary_cta": {"label": "Loslegen"}}, "cta": {"title": "In Offenheit gebaut, als HTML ausgeliefert", "subtitle": "Einige Produkte und die Kernbibliotheken sind auf GitHub öffentlich. Editionen und Lizenzen variieren je nach Produkt; Precis LMS ist als Solo und Business erhältlich.", "primary_cta": {"label": "Auf GitHub ansehen"}, "secondary_cta": {"label": "Kontakt aufnehmen"}}}},
        "es": {"title": "Funciones", "content": {"hero": {"title": "Construido para entregarse como", "subtitle": "El stack AHA, documentado. Cada capacidad de Structa Cloud.", "primary_cta": {"label": "Nuestros productos"}, "secondary_cta": {"label": "Empezar"}}, "cta": {"title": "Construido en abierto, entregado como HTML", "subtitle": "Algunos productos y las bibliotecas principales son públicos en GitHub. La disponibilidad de ediciones y las licencias varían según el producto; Precis LMS se ofrece en Solo y Business.", "primary_cta": {"label": "Ver en GitHub"}, "secondary_cta": {"label": "Ponte en contacto"}}}},
        "pt": {"title": "Funcionalidades", "content": {"hero": {"title": "Construído para ser entregue como", "subtitle": "A stack AHA, documentada. Cada capacidade da Structa Cloud.", "primary_cta": {"label": "Os nossos produtos"}, "secondary_cta": {"label": "Começar"}}, "cta": {"title": "Construído em aberto, entregue como HTML", "subtitle": "Alguns produtos e as bibliotecas principais são públicos no GitHub. A disponibilidade de edições e as licenças variam por produto; o Precis LMS é oferecido em Solo e Business.", "primary_cta": {"label": "Ver no GitHub"}, "secondary_cta": {"label": "Entre em contacto"}}}},
    },
    "blog": {
        "ar": {
            "title": "المدونة",
            "content": {
                "hero": {"title": "أفكار من واقع الإطلاق", "subtitle": "ملاحظات عملية عن المنتجات الرقمية، الأداء، والمحتوى الذي يخدم أسواق المنطقة.", "primary_cta": {"label": "استكشف المنتجات"}, "secondary_cta": {"label": "ابدأ محادثة"}},
                "cta": {"title": "الإصدار الأول المفيد أفضل من خارطة طريق لا تنتهي", "subtitle": "نبدأ من رحلة العميل، ونطلق شريحة مركزة، ونترك لفريقك المحتوى والأدوات لمواصلة التحسين.", "primary_cta": {"label": "عرض على GitHub"}, "secondary_cta": {"label": "اقرأ التوثيق"}},
            },
        },
        "sv": {"title": "Blogg", "content": {"hero": {"title": "Idéer från verkliga lanseringar", "subtitle": "Praktiska anteckningar om digitala tjänster, prestanda och innehåll för team som betjänar regionen.", "primary_cta": {"label": "Utforska produkter"}, "secondary_cta": {"label": "Inled en konversation"}}, "cta": {"title": "En användbar första release slår en oändlig färdplan", "subtitle": "Vi börjar med kundresan, lanserar en fokuserad del och lämnar ditt team med innehåll och verktyg för att fortsätta förbättra.", "primary_cta": {"label": "Visa på GitHub"}, "secondary_cta": {"label": "Läs dokumentationen"}}}},
        "fr": {"title": "Blog", "content": {"hero": {"title": "Des idées issues de lancements réels", "subtitle": "Des notes pratiques sur les services numériques, la performance et le contenu, pour les équipes qui servent la région.", "primary_cta": {"label": "Explorer les produits"}, "secondary_cta": {"label": "Engagez la conversation"}}, "cta": {"title": "Une première version utile vaut mieux qu'une feuille de route sans fin", "subtitle": "Nous partons du parcours client, lançons une première version ciblée et laissons à votre équipe le contenu et les outils pour continuer à l'améliorer.", "primary_cta": {"label": "Voir sur GitHub"}, "secondary_cta": {"label": "Lire la documentation"}}}},
        "de": {"title": "Blog", "content": {"hero": {"title": "Ideen aus echten Launches", "subtitle": "Praktische Notizen zu digitalen Diensten, Performance und Inhalten für Teams, die die Region bedienen.", "primary_cta": {"label": "Produkte entdecken"}, "secondary_cta": {"label": "Gespräch starten"}}, "cta": {"title": "Ein nützlicher erster Release schlägt eine endlose Roadmap", "subtitle": "Wir starten mit der Customer Journey, bringen einen fokussierten ersten Wurf heraus und überlassen Ihrem Team die Inhalte und Werkzeuge, um weiter zu verbessern.", "primary_cta": {"label": "Auf GitHub ansehen"}, "secondary_cta": {"label": "Dokumentation lesen"}}}},
        "es": {"title": "Blog", "content": {"hero": {"title": "Ideas de lanzamientos reales", "subtitle": "Notas prácticas sobre servicios digitales, rendimiento y contenido para equipos que atienden la región.", "primary_cta": {"label": "Explorar productos"}, "secondary_cta": {"label": "Inicia una conversación"}}, "cta": {"title": "Un primer lanzamiento útil gana a una hoja de ruta interminable", "subtitle": "Empezamos por el recorrido del cliente, lanzamos una primera versión enfocada y dejamos a tu equipo el contenido y las herramientas para seguir mejorando.", "primary_cta": {"label": "Ver en GitHub"}, "secondary_cta": {"label": "Leer la documentación"}}}},
        "pt": {"title": "Blog", "content": {"hero": {"title": "Ideias de lançamentos reais", "subtitle": "Notas práticas sobre serviços digitais, desempenho e conteúdo para equipas que servem a região.", "primary_cta": {"label": "Explorar produtos"}, "secondary_cta": {"label": "Inicie uma conversa"}}, "cta": {"title": "Um primeiro lançamento útil vence um roadmap interminável", "subtitle": "Começamos pela jornada do cliente, lançamos uma primeira versão focada e deixamos à sua equipa o conteúdo e as ferramentas para continuar a melhorar.", "primary_cta": {"label": "Ver no GitHub"}, "secondary_cta": {"label": "Ler a documentação"}}}},
    },
    "pricing": {
        "ar": {
            "title": "الأسعار",
            "content": {
                "hero": {"title": "اختر المنتج، ثم الإصدار", "subtitle": "ابدأ مجاناً وتوسع عندما ينمو مشروعك.", "primary_cta": {"label": "ابدأ مجاناً"}, "secondary_cta": {"label": "تواصل مع المبيعات"}},
                "cta": {"title": "الإصدار الأول المفيد أفضل من خارطة طريق لا تنتهي", "subtitle": "نبدأ من رحلة العميل، ونطلق شريحة مركزة، ونترك لفريقك المحتوى والأدوات لمواصلة التحسين.", "primary_cta": {"label": "عرض على GitHub"}, "secondary_cta": {"label": "اقرأ التوثيق"}},
            },
        },
        "sv": {"title": "Priser", "content": {"hero": {"title": "Priser", "subtitle": "Enkel och transparent prissättning. Börja gratis och skala när du växer.", "primary_cta": {"label": "Börja gratis"}, "secondary_cta": {"label": "Kontakta sälj"}}, "cta": {"title": "En användbar första release slår en oändlig färdplan", "subtitle": "Vi börjar med kundresan, lanserar en fokuserad del och lämnar ditt team med innehåll och verktyg för att fortsätta förbättra.", "primary_cta": {"label": "Visa på GitHub"}, "secondary_cta": {"label": "Läs dokumentationen"}}}},
        "fr": {"title": "Tarifs", "content": {"hero": {"title": "Tarifs", "subtitle": "Des tarifs simples et transparents. Commencez gratuitement et évoluez à votre rythme.", "primary_cta": {"label": "Commencer gratuitement"}, "secondary_cta": {"label": "Contacter les ventes"}}, "cta": {"title": "Une première version utile vaut mieux qu'une feuille de route sans fin", "subtitle": "Nous partons du parcours client, lançons une première version ciblée et laissons à votre équipe le contenu et les outils pour continuer à l'améliorer.", "primary_cta": {"label": "Voir sur GitHub"}, "secondary_cta": {"label": "Lire la documentation"}}}},
        "de": {"title": "Preise", "content": {"hero": {"title": "Preise", "subtitle": "Einfache, transparente Preise. Kostenlos starten und mitwachsen.", "primary_cta": {"label": "Kostenlos starten"}, "secondary_cta": {"label": "Vertrieb kontaktieren"}}, "cta": {"title": "Ein nützlicher erster Release schlägt eine endlose Roadmap", "subtitle": "Wir starten mit der Customer Journey, bringen einen fokussierten ersten Wurf heraus und überlassen Ihrem Team die Inhalte und Werkzeuge, um weiter zu verbessern.", "primary_cta": {"label": "Auf GitHub ansehen"}, "secondary_cta": {"label": "Dokumentation lesen"}}}},
        "es": {"title": "Precios", "content": {"hero": {"title": "Precios", "subtitle": "Precios sencillos y transparentes. Empieza gratis y escala a medida que creces.", "primary_cta": {"label": "Empezar gratis"}, "secondary_cta": {"label": "Contactar con ventas"}}, "cta": {"title": "Un primer lanzamiento útil gana a una hoja de ruta interminable", "subtitle": "Empezamos por el recorrido del cliente, lanzamos una primera versión enfocada y dejamos a tu equipo el contenido y las herramientas para seguir mejorando.", "primary_cta": {"label": "Ver en GitHub"}, "secondary_cta": {"label": "Leer la documentación"}}}},
        "pt": {"title": "Preços", "content": {"hero": {"title": "Preços", "subtitle": "Preços simples e transparentes. Comece grátis e escale à medida que cresce.", "primary_cta": {"label": "Começar grátis"}, "secondary_cta": {"label": "Contactar vendas"}}, "cta": {"title": "Um primeiro lançamento útil vence um roadmap interminável", "subtitle": "Começamos pela jornada do cliente, lançamos uma primeira versão focada e deixamos à sua equipa o conteúdo e as ferramentas para continuar a melhorar.", "primary_cta": {"label": "Ver no GitHub"}, "secondary_cta": {"label": "Ler a documentação"}}}},
    },
    "contact": {
        "ar": {"title": "تواصل معنا", "content": {"hero": {"title": "لنتحدث", "subtitle": "أرسل رسالتك وسنعود إليك قريباً."}}},
        "sv": {"title": "Kontakt", "content": {"hero": {"title": "Hör av dig", "subtitle": "Vi vill gärna höra från dig. Kontakta oss när som helst."}}},
        "fr": {"title": "Contact", "content": {"hero": {"title": "Prenez contact", "subtitle": "Nous serions ravis de vous entendre. Contactez-nous à tout moment."}}},
        "de": {"title": "Kontakt", "content": {"hero": {"title": "Kommen Sie in Kontakt", "subtitle": "Wir freuen uns auf Ihre Nachricht. Melden Sie sich jederzeit."}}},
        "es": {"title": "Contacto", "content": {"hero": {"title": "Ponte en contacto", "subtitle": "Nos encantará saber de ti. Escríbenos cuando quieras."}}},
        "pt": {"title": "Contacto", "content": {"hero": {"title": "Entre em contacto", "subtitle": "Gostaríamos muito de ouvir de si. Contacte-nos a qualquer momento."}}},
    },
    "faq": {
        "ar": {"title": "الأسئلة الشائعة", "content": {"hero": {"title": "الأسئلة الشائعة", "subtitle": "إجابات واضحة حول المكدس والمنتجات والإصدارات."}}},
        "sv": {"title": "Vanliga frågor", "content": {"hero": {"title": "Vanliga frågor", "subtitle": "De ärliga svaren på frågorna tekniska köpare ställer."}}},
        "fr": {"title": "Questions fréquentes", "content": {"hero": {"title": "Questions fréquentes", "subtitle": "Les réponses honnêtes aux questions que se posent les acheteurs techniques."}}},
        "de": {"title": "Häufige Fragen", "content": {"hero": {"title": "Häufige Fragen", "subtitle": "Die ehrlichen Antworten auf die Fragen, die technische Käufer stellen."}}},
        "es": {"title": "Preguntas frecuentes", "content": {"hero": {"title": "Preguntas frecuentes", "subtitle": "Las respuestas honestas a las preguntas que hacen los compradores técnicos."}}},
        "pt": {"title": "Perguntas frequentes", "content": {"hero": {"title": "Perguntas frequentes", "subtitle": "As respostas honestas às perguntas que os compradores técnicos fazem."}}},
    },
    "privacy": {
        "ar": {"title": "الخصوصية", "content": {"hero": {"title": "سياسة الخصوصية", "subtitle": "نحافظ على جمع البيانات بالحد الأدنى."}}},
        "sv": {"title": "Integritetspolicy", "content": {"hero": {"title": "Integritetspolicy", "subtitle": "Vi håller datainsamlingen till ett minimum."}}},
        "fr": {"title": "Politique de confidentialité", "content": {"hero": {"title": "Politique de confidentialité", "subtitle": "Nous limitons la collecte de données au minimum."}}},
        "de": {"title": "Datenschutzerklärung", "content": {"hero": {"title": "Datenschutzerklärung", "subtitle": "Wir halten die Datenerfassung so gering wie möglich."}}},
        "es": {"title": "Política de privacidad", "content": {"hero": {"title": "Política de privacidad", "subtitle": "Mantenemos la recopilación de datos al mínimo."}}},
        "pt": {"title": "Política de privacidade", "content": {"hero": {"title": "Política de privacidade", "subtitle": "Mantemos a recolha de dados ao mínimo."}}},
    },
    "brand": {
        "ar": {"title": "الهوية", "content": {"hero": {"title": "عائلة واحدة، علامات متعددة", "subtitle": "نظام الهوية البصري لمنتجات Structa Cloud."}}},
        "sv": {"title": "Varumärke", "content": {"hero": {"title": "En familj, fem märken", "subtitle": "Varje produkt bär sin egen konstruerade symbol — byggd utifrån vad den gör, inte en generisk ikon. Samma system, fem distinkta identiteter."}}},
        "fr": {"title": "Marque", "content": {"hero": {"title": "Une famille, cinq marques", "subtitle": "Chaque produit porte sa propre marque construite — un symbole bâti sur ce qu'il fait, pas un glyphe générique. Un même système, cinq identités distinctes."}}},
        "de": {"title": "Marke", "content": {"hero": {"title": "Eine Familie, fünf Marken", "subtitle": "Jedes Produkt trägt sein eigenes konstruiertes Zeichen — ein Symbol, das aus dem gebaut ist, was es tut, kein generisches Piktogramm. Gleiches System, fünf eigenständige Identitäten."}}},
        "es": {"title": "Marca", "content": {"hero": {"title": "Una familia, cinco marcas", "subtitle": "Cada producto lleva su propia marca construida — un símbolo creado a partir de lo que hace, no un glifo genérico. Mismo sistema, cinco identidades distintas."}}},
        "pt": {"title": "Marca", "content": {"hero": {"title": "Uma família, cinco marcas", "subtitle": "Cada produto tem a sua própria marca construída — um símbolo criado a partir do que faz, não um glifo genérico. Mesmo sistema, cinco identidades distintas."}}},
    },
}

# Seeded language catalog — mirrors the Astro ``LANG_META`` table in
# frontend/src/lib/translations.ts. Each row becomes a ``SiteLanguage``
# Wagtail snippet (admin-editable), and ``GET /apis/content/languages/``
# serves the active rows to the frontend switcher. Keep this list in sync
# with ``LANG_META`` and Django's ``LANGUAGES`` setting.
DEFAULT_SITE_LANGUAGES = [
    {"code": "en", "name": "English", "native_name": "English", "direction": "ltr", "flag": "🇬🇧", "is_active": True, "sort_order": 0},
    {"code": "ar", "name": "Arabic", "native_name": "العربية", "direction": "rtl", "flag": "🇸🇦", "is_active": True, "sort_order": 10},
    {"code": "sv", "name": "Swedish", "native_name": "Svenska", "direction": "ltr", "flag": "🇸🇪", "is_active": True, "sort_order": 20},
    {"code": "fr", "name": "French", "native_name": "Français", "direction": "ltr", "flag": "🇫🇷", "is_active": True, "sort_order": 30},
    {"code": "de", "name": "German", "native_name": "Deutsch", "direction": "ltr", "flag": "🇩🇪", "is_active": True, "sort_order": 40},
    {"code": "es", "name": "Spanish", "native_name": "Español", "direction": "ltr", "flag": "🇪🇸", "is_active": True, "sort_order": 50},
    {"code": "pt", "name": "Portuguese", "native_name": "Português", "direction": "ltr", "flag": "🇧🇷", "is_active": True, "sort_order": 60},
]

# Services the project offers — the “feature” grid on the Services page.
# Three service lines: website building, product & project development, and
# enhancements — mirrors the frontend services page (cards + deliverables).
DEFAULT_SERVICES_SECTIONS = {
    "services": [
        (
            "services",
            {
                "title": "Build for the market you serve",
                "description": (
                    "A focused path from customer need to a dependable digital service. "
                    "We help teams across the Gulf, Levant, and North Africa launch "
                    "clear, bilingual experiences without unnecessary complexity."
                ),
                "services": [
                    {
                        "icon": "M4 5h16v14H4z M4 12h16",
                        "title": "Market-ready websites",
                        "description": "Clear Arabic and English journeys for campaigns, services, and products. Editors can update content without waiting for a release.",
                        "deliverables": ["Bilingual page structure", "Editorial sections your team can own", "Fast first visits on mobile networks", "Hosting, domains + HTTPS setup"],
                        "cta_label": "See the stack",
                        "cta_href": "/features/",
                    },
                    {
                        "icon": "M13 10V3L4 14h7v7l9-11h-7z",
                        "title": "Digital product delivery",
                        "description": "Customer portals, learning services, commerce tools, and internal workflows shaped around how your team actually operates.",
                        "deliverables": ["Journey mapping and product direction", "Web or desktop delivery", "Arabic and English-ready interfaces", "Cloud deployment and handover"],
                        "cta_label": "See our products",
                        "cta_href": "/products/",
                    },
                    {
                        "icon": "M3 3v18h18M7 15l4-4 3 3 5-6",
                        "title": "Improve what already works",
                        "description": "Make an existing service easier to use and faster to operate, without forcing a risky rewrite.",
                        "deliverables": ["Conversion and content review", "Performance budget and Core Web Vitals", "Safe content migration", "Team training and ongoing support"],
                        "cta_label": "Contact us",
                        "cta_href": "/contact/",
                    },
                ],
            },
        )
    ],
    "process": [
        (
            "process",
            {
                "title": "A measured path to launch",
                "description": (
                    "We keep the work visible and incremental. Each phase leaves your team "
                    "with a clearer decision, a working slice, or a useful handoff."
                ),
                "steps": [
                    {
                        "title": "Discover",
                        "description": "We map the customer, the offer, the languages, and the moments that need to work first.",
                        "deliverable": "Customer and route map",
                    },
                    {
                        "title": "Design",
                        "description": "We turn the direction into a calm interface with clear content hierarchy and a flexible visual system.",
                        "deliverable": "Approved experience direction",
                    },
                    {
                        "title": "Build",
                        "description": "We build the first useful slice, connect content, and test the critical path on real devices.",
                        "deliverable": "Working product slice",
                    },
                    {
                        "title": "Ship & grow",
                        "description": "We launch with a performance budget, an editor handoff, and a simple plan for the next market.",
                        "deliverable": "Live service + growth plan",
                    },
                ],
            },
        )
    ],
}


# Blog posts — the “Insights” grid on the Blog page (mirrors the repo's 18-post
# count loosely; the grid is editor-driven so more posts can be added anytime).
# Each post ALSO becomes a BlogPostPage child (see handle()) so grid cards link
# to live /blog/<slug>/ detail pages — slugs here must match those pages.
DEFAULT_BLOG_POSTS = [
    {
        "title": "A fast first visit is a product decision",
        "slug": "why-landing-pages-as-documents",
        "category": "Product",
        "date": "2026-07-28",
        "read_time": "6 min read",
        "excerpt": "Performance is part of trust. A clear page that arrives quickly gives customers more confidence before the first conversation.",
    },
    {
        "title": "Designing bilingual journeys without duplication",
        "slug": "htmx-fragments-vs-json-apis",
        "category": "Content",
        "date": "2026-07-14",
        "read_time": "5 min read",
        "excerpt": "A practical way to keep Arabic and English content aligned while letting each language sound natural.",
    },
    {
        "title": "Give content teams a useful control room",
        "slug": "wagtail-streamfield-marketing",
        "category": "Operations",
        "date": "2026-06-30",
        "read_time": "8 min read",
        "excerpt": "Good editorial structure helps marketing teams move quickly without turning every page into a design negotiation.",
    },
    {
        "title": "Small interactions, better focus",
        "slug": "alpine-reactivity-landing",
        "category": "Experience",
        "date": "2026-06-12",
        "read_time": "4 min read",
        "excerpt": "Use interaction where it clarifies a decision, not where it adds noise to a page that should simply help someone move forward.",
    },
    {
        "title": "Build a system your team can inherit",
        "slug": "monorepo-six-products",
        "category": "Delivery",
        "date": "2026-05-20",
        "read_time": "7 min read",
        "excerpt": "The best platform handoff is not a technical monument. It is a set of understandable decisions that people can safely extend.",
    },
    {
        "title": "A practical performance budget for launch",
        "slug": "server-time-streamed-htmx",
        "category": "Performance",
        "date": "2026-05-04",
        "read_time": "3 min read",
        "excerpt": "Reserve space for the content that matters, keep the critical path small, and measure the experience on real regional networks.",
    },
    # Deep dives — the code sections moved off the product pages. Each post
    # hosts one product's reference code (DEFAULT_BLOG_POST_SNIPPETS) and the
    # product page links its snippet cards here via SnippetBlock.related_post.
    {
        "title": "The Formints data model",
        "slug": "formint-pos-data-model",
        "category": "Engineering",
        "date": "2026-07-06",
        "read_time": "9 min read",
        "excerpt": "The SQLite schema, Rust models and Tauri commands behind Formints — moved here from the product page so each code section lives with its story.",
    },
    {
        "title": "The Precis LMS content model",
        "slug": "precis-lms-content-model",
        "category": "Engineering",
        "date": "2026-06-22",
        "read_time": "7 min read",
        "excerpt": "How Precis LMS models courses and enrollments in Wagtail + django-fusion — the content-driven pattern the Loop site builder generalizes.",
    },
    {
        "title": "The Loop block library",
        "slug": "loop-block-library",
        "category": "Engineering",
        "date": "2026-06-08",
        "read_time": "6 min read",
        "excerpt": "The StreamField blocks and server-rendered fragments that make a site content-driven — the code behind every structa.cloud page.",
    },
]


DEFAULT_BLOG_SECTION = {
    "blog": [
        (
            "blog",
            {
                "title": "Ideas for the next release",
                "description": (
                    "Practical notes on launching digital services, keeping first visits fast, "
                    "and giving content teams control after handover."
                ),
                "posts": DEFAULT_BLOG_POSTS,
            },
        )
    ],
}


# Full body content for each seeded post — rendered on the /blog/<slug>/
# detail pages (BlogPostPage children of the Blog index). Keys match the
# ``slug`` values in DEFAULT_BLOG_SECTION so grid cards link to live pages.
DEFAULT_BLOG_POST_BODIES = {
    "why-landing-pages-as-documents": (
        "<p>When we rebuilt the structa.cloud landing pages, the first "
        "decision was the rendering model. The old stack shipped a heavy "
        "React SPA: a shell, a hydration step, and a JSON API feeding it. "
        "The browser waited through all three before a user saw text.</p>"
        "<h2>The document model</h2>"
        "<p>We switched to the AHA stack — Astro, HTMX, Alpine. Every page is "
        "finished HTML in one response. The server composes the document from "
        "Wagtail StreamField blocks; the browser just paints it.</p>"
        "<p>The difference is measurable: first paint dropped from seconds to "
        "tens of milliseconds, and SEO tools stopped complaining about empty "
        "shells. A page is a document again, not an application bootstrap.</p>"
        "<h2>What we kept</h2>"
        "<ul><li>HTMX fragments for the rare dynamic region</li>"
        "<li>Alpine.js for micro-interactions — accordions, toggles, counters</li>"
        "<li>Wagtail as the single source of content truth</li></ul>"
        "<p>No SPA shell, no hydration waterfall — just the web as it should "
        "be.</p>"
    ),
    "htmx-fragments-vs-json-apis": (
        "<p>Every interactive region on a marketing site is a trade: fetch "
        "JSON and render it client-side, or fetch HTML and let the server do "
        "the rendering. HTMX picks the second, and it is the right default "
        "for content sites.</p>"
        "<h2>The API contract tax</h2>"
        "<p>JSON APIs force you to maintain a schema, a serializer, and a "
        "client-side renderer that all agree. Add a field and you touch three "
        "files. Streaming HTML removes the decoder entirely — the response is "
        "the UI.</p>"
        "<h2>Where it shines</h2>"
        "<p>Our contact form, newsletter subscribe, and server-time demo all "
        "swap small HTML fragments into place. The Django view returns a "
        "finished fragment; HTMX does the swap. There is no frontend state to "
        "desync.</p>"
        "<p>Half the frontend state we used to maintain simply no longer "
        "exists.</p>"
    ),
    "wagtail-streamfield-marketing": (
        "<p>Marketing sites live and die by iteration speed. A page builder "
        "gives editors speed but fights developers; hand-rolled templates give "
        "developers control but bottleneck editors. StreamField sits in the "
        "middle.</p>"
        "<h2>Sections, not pages</h2>"
        "<p>Each section of a landing page is a StructBlock with its own "
        "Django template. Editors compose and reorder sections; developers own "
        "the templates. Nobody needs a drag-drop page builder.</p>"
        "<p>The result is composition superpowers without the complexity: "
        "hero, stats, features, testimonials, pricing, FAQ — each a block, "
        "each rendered server-side, each editable in the Wagtail admin.</p>"
        "<h2>Why it scales</h2>"
        "<p>Blocks are plain Python classes with plain Django templates. New "
        "sections ship in a day, and the API serializer and server renderer "
        "pick them up automatically from the same field list.</p>"
        "<h2>Real StreamField blocks from Loop</h2>"
        "<p>A Hero block — the simplest section that starts every page document:</p>"
        "<pre><code>from wagtail import blocks\n\nclass HeroBlock(blocks.StructBlock):\n    badge = blocks.CharBlock(max_length=80, required=False)\n    title = blocks.CharBlock(max_length=200)\n    accent = blocks.CharBlock(max_length=60, required=False)\n    subtitle = blocks.TextBlock(required=False)\n    primary_cta = ButtonBlock(required=False)\n    secondary_cta = ButtonBlock(required=False)\n\n    class Meta:\n        template = 'content/blocks/hero.html'\n        label = 'Hero'\n</code></pre>"
        "<p>A course page — content-driven with a curriculum StreamField:</p>"
        "<pre><code>class CoursePage(Page):\n    title = models.CharField(max_length=255)\n    description = RichTextField(blank=True)\n    price_cents = models.IntegerField(default=0)\n    curriculum = StreamField([\n        ('lesson', LessonBlock()),\n        ('quiz', QuizBlock()),\n    ], use_json_field=True)\n\n    content_panels = Page.content_panels + [\n        FieldPanel('description'),\n        FieldPanel('price_cents'),\n        FieldPanel('curriculum'),\n    ]\n</code></pre>"
        "<p>These blocks ship from one codebase and render on both Django and Astro — the API auto-exposes every field from the same block list.</p>"
    ),
    "alpine-reactivity-landing": (
        "<p>Landing pages need a little reactivity — an accordion, a theme "
        "toggle, a count-up on scroll. They do not need a framework's "
        "reconciliation engine.</p>"
        "<h2>A few x-data attributes</h2>"
        "<p>Alpine.js adds declarative behavior with plain HTML attributes. "
        "Our FAQ accordion is an <code>x-data</code> directive and a couple "
        "of <code>x-show</code> toggles. The contact modal is the same shape. "
        "There is no component tree to mount.</p>"
        "<h2>The AHA promise</h2>"
        "<p>Astro renders the document, HTMX swaps fragments, Alpine hydrates "
        "micro-interactions. Each tool does one job and stays out of the "
        "critical path. Accordions, toggles, counters — a few x-data "
        "attributes instead of a framework.</p>"
    ),
    "monorepo-six-products": (
        "<p>Six projects, one repository, one CI pipeline. The structa.cloud "
        "monorepo holds Django sites, an Astro frontend, a desktop POS, and "
        "the libraries that bind them.</p>"
        "<h2>Shared everything</h2>"
        "<p>Configs, assets, and component templates live once under "
        "<code>projects/</code>. Sites pick from them instead of copying. A "
        "fix in django-fusion propagates to every site in one commit.</p>"
        "<h2>The cost</h2>"
        "<p>Monorepos trade isolation for consistency. We pay it down with a "
        "strict Makefile dispatcher and per-site tests, so a change to shared "
        "code is validated against every consumer before it lands.</p>"
        "<p>For a small team shipping products that share a stack, the "
        "trade is worth it.</p>"
        "<h2>Formints: the SQLite schema shared across editions</h2>"
        "<p>Every Formints edition starts from the same local schema. Community "
        "uses it directly, Standard adds a sync layer, and Pro turns it into "
        "a cloud master. Here is the core of it:</p>"
        "<pre><code>CREATE TABLE sales (\n  id INTEGER PRIMARY KEY AUTOINCREMENT,\n  terminal_id TEXT NOT NULL,\n  total_cents INTEGER NOT NULL,\n  payment_method TEXT NOT NULL,\n  created_at TEXT NOT NULL DEFAULT (datetime('now'))\n);\n\nCREATE TABLE sale_items (\n  id INTEGER PRIMARY KEY AUTOINCREMENT,\n  sale_id INTEGER NOT NULL REFERENCES sales(id),\n  product_id TEXT NOT NULL,\n  quantity INTEGER NOT NULL,\n  unit_cents INTEGER NOT NULL\n);\n</code></pre>"
        "<p>The Rust model that maps to this schema via Diesel ORM:</p>"
        "<pre><code>#[derive(Queryable, Insertable, Serialize)]\n#[diesel(table_name = crate::db::schema::sales)]\npub struct Sale {\n    pub id: i32,\n    pub terminal_id: String,\n    pub total_cents: i32,\n    pub payment_method: String,\n    pub created_at: String,\n}\n</code></pre>"
        "<p>The Tauri command that generates an invoice — reusable across Standard and Pro:</p>"
        "<pre><code>#[tauri::command]\npub fn generate_invoice(sale_id: i32, state: State<AppState>) -> Result<String, String> {\n    let conn = &mut state.pool.get().map_err(|e| e.to_string())?;\n    let sale: Sale = sales::table.find(sale_id).first(conn).map_err(|e| e.to_string())?;\n    let items: Vec<SaleItem> = sale_items::table\n        .filter(sale_items::sale_id.eq(sale_id)).load(conn).map_err(|e| e.to_string())?;\n    render_invoice_pdf(&sale, &items)\n}\n</code></pre>"
        "<p>One codebase, four editions — the schema and commands stay the same, "
        "and each edition gates features on top of them.</p>"
    ),
    "server-time-streamed-htmx": (
        "<p>The smallest useful fragment endpoint proves the whole pipeline: "
        "a button, an HTMX attribute, and a Django view that returns the "
        "server time as an HTML fragment.</p>"
        "<h2>The endpoint</h2>"
        "<p><code>/fragment/ping/</code> renders the current timestamp into a "
        "small <code>div</code>. A request with the <code>HX-Request</code> "
        "header swaps it into the page — no JSON, no re-render of the "
        "document, no client state.</p>"
        "<pre><code>from django.http import HttpResponse\nfrom django.utils import timezone\n\ndef server_time(request):\n    now = timezone.now().isoformat()\n    if request.headers.get('HX-Request'):\n        return HttpResponse(f'<div id=\"server-time\">{now}</div>')\n    return HttpResponse(f'<p>Server time: {now}</p>')\n</code></pre>"
        "<h2>Why it matters</h2>"
        "<p>If a five-line fragment endpoint works end to end, the heavier "
        "regions — contact forms, newsletter signup, product filters — ride "
        "the same rails. The demo is trivial; the architecture it proves is "
        "not.</p>"
    ),
    "formint-pos-data-model": (
        "<p>Formints keeps its point-of-sale core deliberately small: one "
        "SQLite database, a handful of Rust models, and Tauri commands that "
        "read and write them. This post is the code that used to sit on the "
        "product page — moved here so it can be read, discussed and copied "
        "with the story attached.</p>"
        "<h2>The schema</h2>"
        "<p>Everything starts from two tables: a sale and its line items. "
        "Money is stored in cents (never floats), the terminal id scopes the "
        "row, and the timestamp is generated by SQLite itself.</p>"
        "<h2>The model</h2>"
        "<p>The Rust side is a Diesel <code>Queryable</code> mirror of the "
        "schema — one field per column, typed, serializable for the frontend. "
        "The invoice command shows the pattern end to end: borrow a connection "
        "from the pool, load the sale and its items, render the PDF.</p>"
        "<p>The full code is below. Copy the patterns — not the database — "
        "into your own project.</p>"
    ),
    "precis-lms-content-model": (
        "<p>The learning platform models content the way the CMS does: "
        "Wagtail pages plus StreamField blocks. A course is a page with a "
        "curriculum; an enrollment is a fusion viewset over that content.</p>"
        "<h2>Why pages, not tables</h2>"
        "<p>Courses are content — editors should compose lessons and quizzes "
        "without a migration. StreamField gives them exactly that, and the "
        "frontend consumes the same structure the CMS does.</p>"
        "<h2>The viewset</h2>"
        "<p>Reads ride django-fusion's <code>ModelViewset</code>: a class, a "
        "model and a field list. The enrollment row tracks progress and the "
        "completion date; everything else is derived from it.</p>"
    ),
    "loop-block-library": (
        "<p>Every structa.cloud page is composed from the blocks in this post. "
        "A section is a StructBlock with a Django template; the page is a "
        "StreamField of those sections; the server renders finished HTML.</p>"
        "<h2>The hero block</h2>"
        "<p>One block, one template. The editor picks a badge, a title, a "
        "subtitle and optional CTAs — no design system negotiation, no custom "
        "page builder.</p>"
        "<h2>The fragment</h2>"
        "<p>The template is deliberately plain: a section, a heading, a "
        "paragraph. It is what HTMX swaps when a fragment request comes in — "
        "the same road as the full page, so the two can never drift.</p>"
    ),
}


# Code sections moved off the product pages into their deep-dive posts. The
# product page keeps a reference card per snippet (SnippetBlock.related_post)
# that links here; the code itself lives with its story and its comment
# thread. Keys match the deep-dive slugs in DEFAULT_BLOG_POSTS.
DEFAULT_BLOG_POST_SNIPPETS = {
    "formint-pos-data-model": [
        (
            "snippets",
            {
                "title": "The code, end to end",
                "description": "The core schema and entrypoint — the patterns LMS and other projects borrow.",
                "snippets": [
                    {
                        "title": "SQLite schema (Diesel up.sql)",
                        "language": "sql",
                        "code": "CREATE TABLE sales (\n  id INTEGER PRIMARY KEY AUTOINCREMENT,\n  terminal_id TEXT NOT NULL,\n  total_cents INTEGER NOT NULL,\n  payment_method TEXT NOT NULL,\n  created_at TEXT NOT NULL DEFAULT (datetime('now'))\n);\n\nCREATE TABLE sale_items (\n  id INTEGER PRIMARY KEY AUTOINCREMENT,\n  sale_id INTEGER NOT NULL REFERENCES sales(id),\n  product_id TEXT NOT NULL,\n  quantity INTEGER NOT NULL,\n  unit_cents INTEGER NOT NULL\n);",
                    },
                    {
                        "title": "Rust model (src-tauri/src/db/models.rs)",
                        "language": "rust",
                        "code": "#[derive(Queryable, Insertable, Serialize)]\n#[diesel(table_name = crate::db::schema::sales)]\npub struct Sale {\n    pub id: i32,\n    pub terminal_id: String,\n    pub total_cents: i32,\n    pub payment_method: String,\n    pub created_at: String,\n}",
                    },
                    {
                        "title": "Diesel migration (up.sql)",
                        "language": "sql",
                        "code": "-- Loyalty + refunds land on top of the core schema.\nALTER TABLE sales ADD COLUMN loyalty_points INTEGER NOT NULL DEFAULT 0;\n\nCREATE TABLE refunds (\n  id INTEGER PRIMARY KEY AUTOINCREMENT,\n  sale_id INTEGER NOT NULL REFERENCES sales(id),\n  amount_cents INTEGER NOT NULL,\n  reason TEXT NOT NULL,\n  created_at TEXT NOT NULL DEFAULT (datetime('now'))\n);",
                    },
                    {
                        "title": "Tauri command (invoice PDF)",
                        "language": "rust",
                        "code": "#[tauri::command]\npub fn generate_invoice(sale_id: i32, state: State<AppState>) -> Result<String, String> {\n    let conn = &mut state.pool.get().map_err(|e| e.to_string())?;\n    let sale: Sale = sales::table\n        .find(sale_id)\n        .first(conn)\n        .map_err(|e| e.to_string())?;\n    let items: Vec<SaleItem> = sale_items::table\n        .filter(sale_items::sale_id.eq(sale_id))\n        .load(conn)\n        .map_err(|e| e.to_string())?;\n    render_invoice_pdf(&sale, &items)\n}",
                    },
                ],
            },
        )
    ],
    "precis-lms-content-model": [
        (
            "snippets",
            {
                "title": "The content model",
                "description": "How the LMS models content — the pattern the CMS site builder generalizes.",
                "snippets": [
                    {
                        "title": "Wagtail course page",
                        "language": "python",
                        "code": "class CoursePage(Page):\n    title = models.CharField(max_length=255)\n    description = RichTextField(blank=True)\n    price_cents = models.IntegerField(default=0)\n    curriculum = StreamField([\n        ('lesson', LessonBlock()),\n        ('quiz', QuizBlock()),\n    ], use_json_field=True)\n\n    content_panels = Page.content_panels + [\n        FieldPanel('description'),\n        FieldPanel('price_cents'),\n        FieldPanel('curriculum'),\n    ]",
                    },
                    {
                        "title": "Enrollment (django-fusion)",
                        "language": "python",
                        "code": "from django_fusion.routes import ModelViewset\n\nclass EnrollmentViewset(ModelViewset):\n    model = Enrollment\n    fields = ['id', 'course', 'user', 'progress', 'completed_at']",
                    },
                ],
            },
        )
    ],
    "loop-block-library": [
        (
            "snippets",
            {
                "title": "The building blocks",
                "description": "The pieces that make a site content-driven — copy them into any Fusion project.",
                "snippets": [
                    {
                        "title": "A StreamField section block",
                        "language": "python",
                        "code": "class HeroBlock(blocks.StructBlock):\n    badge = blocks.CharBlock(max_length=80, required=False)\n    title = blocks.CharBlock(max_length=200)\n    subtitle = blocks.TextBlock(required=False)\n    primary_cta = ButtonBlock(required=False)\n\n    class Meta:\n        template = 'content/blocks/hero.html'\n        label = 'Hero'\n",
                    },
                    {
                        "title": "Server-rendered fragment",
                        "language": "html",
                        "code": "<section class=\"container-fusion py-20 text-center\">\n  <h1 class=\"text-4xl font-bold sm:text-6xl\">{{ value.title }}</h1>\n  {% if value.subtitle %}<p class=\"mx-auto mt-6 max-w-2xl text-lg text-fu-muted\">{{ value.subtitle }}</p>{% endif %}\n</section>",
                    },
                ],
            },
        )
    ],
}


# Screenshot variants for the deep-dive posts — a name, an optional image URL
# (empty here so the stylized screen frame renders), a caption and a
# hyperlink per variant. Editors can drop real screenshot URLs in the admin.
DEFAULT_BLOG_POST_VARIANTS = {
    "formint-pos-data-model": [
        (
            "variant",
            {
                "name": "Community terminal",
                "caption": "The free, offline-first single-terminal edition.",
                "link_label": "Preview Community",
                "link_href": "/products/formint-pos/preview/community/",
            },
        ),
        (
            "variant",
            {
                "name": "Cloud dashboard",
                "caption": "The hosted multi-terminal master, managed for you.",
                "link_label": "Preview Cloud",
                "link_href": "/products/formint-pos/preview/cloud/",
            },
        ),
    ],
    "precis-lms-content-model": [
        (
            "variant",
            {
                "name": "Course page",
                "caption": "A lesson + quiz curriculum composed in a Wagtail StreamField.",
                "link_label": "See Precis LMS",
                "link_href": "/products/lms/",
            },
        ),
    ],
    "loop-block-library": [
        (
            "variant",
            {
                "name": "Block library",
                "caption": "The StreamField blocks this very site is composed from.",
                "link_label": "See Loop",
                "link_href": "/products/cms/",
            },
        ),
    ],
}


# ── Product pages ───────────────────────────────────────────────────
# One ProductPage per product, created as children of the Products page so
# /products/ lists them (get_product_cards) and each gets /products/<slug>/.
# Each page is a reference document: overview + tech stack + editions with
# per-edition pricing + reference snippets/models other projects can copy
# (e.g. LMS reusing Formints patterns).

DEFAULT_PRODUCT_PAGES = {
    "formint-pos": {
        "title": "Formints",
        "version": "beta 0.2",
        "logo_style": "crest",
        "category": "application",
        "tagline": "Desktop point-of-sale in four editions: Community, Standard, Pro, Cloud.",
        "hero": [
            (
                "hero",
                {
                    "title": "Formints",
                    "subtitle": "A desktop point-of-sale application with a Tauri 2 + Rust core, React/Vite shell, and SQLite storage.",
                    "primary_cta": {"label": "See the editions", "href": "/products/formint-pos/#editions", "style": "secondary"},
                    "secondary_cta": {"label": "View the repo", "href": "https://github.com/mammhoud/formint-community", "style": "white"},
                    "trusted_by": "Community · Standard · Pro · Cloud",
                },
            )
        ],
        "body": (
            "<p>Formints is a desktop point-of-sale application built on "
            "Tauri 2 + Rust with a React/Vite frontend and SQLite storage.</p>"
            "<p>It ships in four editions that share one codebase: Community "
            "(free, offline-first single terminal), Standard (standalone with "
            "an embedded Python sidecar + cloud sync), Pro (multi-terminal "
            "with a cloud master), and Cloud (fully hosted multi-terminal "
            "with managed cloud CRM).</p>"
        ),
        "tech": [
            ("tech", {"title": "Built on", "items": ["Rust", "Tauri 2", "React", "TypeScript", "SQLite", "Diesel"]}),
        ],
        "editions": [
            (
                "editions",
                {
                    "eyebrow": "Editions & pricing",
                    "title": "Four editions, one codebase",
                    "description": "Every edition shares the Tauri + Rust core. Upgrade as your terminal grows.",
                    "editions": [
                        {
                            "name": "Community",
                            "tagline": "Free and open source. The offline-first POS for a single terminal.",
                            "price": "$0",
                            "period": "/open source",
                            "features": ["Tauri 2 + Rust core (Diesel ORM)", "SQLite storage", "Sales, receipting + inventory", "Payment types: cash, card, split", "Offline-first mode", "Refunds & returns", "i18n: en, fr, ar"],
                            "cta_label": "Download",
                            "cta_href": "https://github.com/mammhoud/formint-community",
                            "featured": False,
                            "tier": "outline",
                        },
                        {
                            "name": "Standard",
                            "tagline": "Standalone terminal for growing businesses: high-end design, food & beverage tools, and integrations.",
                            "price": "$119",
                            "period": "/one-time license",
                            "features": ["Everything in Community", "High-end interface design", "Inventory adjustments + stock control", "Food & beverage (F&B) menu support", "Kitchen display + payroll", "REST API for integrations", "Inventory + sales analytics", "Invoice PDF generation", "Loyalty & rewards program", "Multi-currency & tax profiles", "Custom roles & permissions", "Data export (CSV/JSON)", "Deployment & support quoted per site"],
                            "preview_images": [
                                {"url": "/static/related/formints/standard-checkout.jpg", "kind": "image", "label": "Front of house", "alt": "Formints Standard point-of-sale checkout screen"},
                                {"url": "/static/related/formints/standard-operations.jpg", "kind": "image", "label": "Data and operations", "alt": "Formints Standard data and operations screen"},
                                {"url": "/static/related/formints/standard-walkthrough.gif", "kind": "gif", "label": "Standard walkthrough", "alt": "Animated walkthrough of the Formints Standard point-of-sale interface"},
                                {"url": "/static/related/formints/standard-sale-complete.png", "kind": "image", "label": "Sale complete", "alt": "Formints Standard completed sale receipt with PDF, print, and new sale actions"},
                            ],
                            "cta_label": "Buy Standard",
                            "cta_href": "/contact/",
                            "featured": False,
                            "tier": "default",
                        },
                        {        "name": "Pro",
        "tagline": "Multi-terminal with a cloud master, WebSocket streaming, and a high-throughput Rust API.",
        "price": "$79",
        "period": "/per year",
        "offer_label": "50% off · launch",
        "offer_old_price": "$158",
                            "features": ["Everything in Standard", "Multi-terminal sync (cloud master)", "High-throughput Rust API (60k+ RPS)", "WebSocket real-time streaming", "Product sync engine (master)", "Employee scheduling + KPIs", "Change signals + approvals", "Deployment & support fees apply"],
                            "preview_images": [
                                {"url": "/static/related/formints/pro-admin-dashboard.jpg", "label": "Admin dashboard", "alt": "Formints Pro admin dashboard"},
                                {"url": "/static/related/formints/pro-admin-products.jpg", "label": "Product administration", "alt": "Formints Pro product administration screen"},
                            ],
                            "cta_label": "Contact Sales",
                            "cta_href": "/contact/",
                            "featured": True,
                            "tier": "featured",
                        },
                        {
                            "name": "Cloud",
                            "tagline": "Fully hosted multi-terminal. The Pro cloud master, managed for you.",
                            "price": "Custom",
                            "period": "/per month",
                            "features": ["Everything in Pro", "Hosted cloud CRM master", "Unlimited terminals", "Cross-device data sync", "Automatic cloud backups + monitoring", "Dedicated onboarding + support", "Contact us for a managed-cloud quote"],
                            "cta_label": "Talk to Sales",
                            "cta_href": "/contact/",
                            "featured": False,
                            "tier": "managed",
                        },
                    ],
                },
            )
        ],
        "gallery": [
            (
                "gallery",
                {
                    "eyebrow": "Inside Standard",
                    "title": "A real checkout, in two views",
                    "description": "See the counter experience and the full checkout flow before you choose an edition.",
                    "display": "grid",
                    "items": [
                        {
                            "url": "/static/related/formints/standard-checkout.jpg",
                            "kind": "image",
                            "label": "Checkout screenshot",
                            "alt": "Formints Standard point-of-sale checkout screenshot",
                        },
                        {
                            "url": "/static/related/formints/standard-walkthrough.gif",
                            "kind": "gif",
                            "label": "Standard screencast",
                            "alt": "Formints Standard point-of-sale screencast",
                        },
                    ],
                },
            )
        ],
        "comparison": [
            (
                "comparison",
                {
                    "eyebrow": "Compare editions",
                    "title": "Community vs Standard vs Pro vs Cloud",
                    "description": "Every edition shares the Tauri + Rust core. Rows below show exactly what moves you up the ladder.",
                    "columns": ["Community", "Standard", "Pro", "Cloud"],
                    "rows": [
                        {"feature": "React 19 + TypeScript frontend", "cells": ["Yes", "Yes", "Yes", "Yes"]},
                        {"feature": "Tauri 2 + Rust backend", "cells": ["Yes", "Yes", "Yes", "Yes"]},
                        {"feature": "SQLite database", "cells": ["Yes", "Yes", "Yes", "Yes"]},
                        {"feature": "i18n (en/fr/ar)", "cells": ["Yes", "Yes", "Yes", "Yes"]},
                        {"feature": "POS terminal + inventory + analytics", "cells": ["Yes", "Yes", "Yes", "Yes"]},
                        {"feature": "Payment types (cash, card, split)", "cells": ["Yes", "Yes", "Yes", "Yes"]},
                        {"feature": "Employees, payroll, scheduling", "cells": ["Yes", "Yes", "Yes", "Yes"]},
                        {"feature": "High-end interface design", "cells": ["No", "Yes", "Yes", "Yes"]},
                        {"feature": "Inventory adjustments + stock control", "cells": ["No", "Yes", "Yes", "Yes"]},
                        {"feature": "Food & beverage (F&B) menu support", "cells": ["No", "Yes", "Yes", "Yes"]},
                        {"feature": "Kitchen display system", "cells": ["No", "Yes", "Yes", "Yes"]},
                        {"feature": "POS-KO Gaming Center", "cells": ["Yes", "Yes", "Yes", "Yes"]},
                        {"feature": "Django Portal (admin UI)", "cells": ["Yes", "Yes", "Yes", "Yes"]},
                        {"feature": "REST API (35+ endpoints)", "cells": ["No", "Yes", "Yes", "Yes"]},
                        {"feature": "Invoice PDF generation", "cells": ["No", "Yes", "Yes", "Yes"]},
                        {"feature": "Chat support widget", "cells": ["No", "Yes", "Yes", "Yes"]},
                        {"feature": "WebSocket real-time streaming", "cells": ["No", "/ws/config", "/ws/config + /ws/nodes", "/ws/config + /ws/nodes"]},
                        {"feature": "Django Signals (config_changed, etc.)", "cells": ["No", "Yes", "Yes", "Yes"]},
                        {"feature": "Moderated Approvals (SyncApproval)", "cells": ["No", "Yes", "Yes", "Yes"]},
                        {"feature": "Product Sync Engine", "cells": ["No", "child", "master", "master"]},
                        {"feature": "Cross-device data sync", "cells": ["No", "push to master", "cloud master", "cloud master"]},
                        {"feature": "Cloud CRM (shared-portal)", "cells": ["No", "sync client", "sync master", "sync master"]},
                        {"feature": "JSON seed fixtures", "cells": ["No", "No", "Yes", "Yes"]},
                        {"feature": "Change signals (broadcast)", "cells": ["No", "No", "Yes", "Yes"]},
                        {"feature": "High-throughput Rust API (60k+ RPS)", "cells": ["No", "No", "Yes", "Yes"]},
                        {"feature": "Hosted deployment + managed backups", "cells": ["No", "No", "No", "Yes"]},
                        {"feature": "Offline-first mode", "cells": ["Yes", "Yes", "Yes", "Yes"]},
                        {"feature": "Refunds & returns", "cells": ["Yes", "Yes", "Yes", "Yes"]},
                        {"feature": "Loyalty & rewards program", "cells": ["No", "Yes", "Yes", "Yes"]},
                        {"feature": "Multi-currency & tax profiles", "cells": ["No", "Yes", "Yes", "Yes"]},
                        {"feature": "Custom roles & permissions", "cells": ["No", "Yes", "Yes", "Yes"]},
                        {"feature": "Data export (CSV/JSON)", "cells": ["No", "Yes", "Yes", "Yes"]},
                        {"feature": "Automatic cloud backups", "cells": ["No", "No", "No", "Yes"]},
                    ],
                },
            )
        ],
        "snippets": [
            (
                "snippets",
                {
                    "title": "Models & snippets you can reuse",
                    "description": "The core schema and entrypoint. The same patterns LMS and other projects borrow.",
                    "snippets": [
                        {
                            "title": "SQLite schema (Diesel up.sql)",
                            "language": "sql",
                            "code": "CREATE TABLE sales (\n  id INTEGER PRIMARY KEY AUTOINCREMENT,\n  terminal_id TEXT NOT NULL,\n  total_cents INTEGER NOT NULL,\n  payment_method TEXT NOT NULL,\n  created_at TEXT NOT NULL DEFAULT (datetime('now'))\n);\n\nCREATE TABLE sale_items (\n  id INTEGER PRIMARY KEY AUTOINCREMENT,\n  sale_id INTEGER NOT NULL REFERENCES sales(id),\n  product_id TEXT NOT NULL,\n  quantity INTEGER NOT NULL,\n  unit_cents INTEGER NOT NULL\n);",
                        },
                        {
                            "title": "Rust model (src-tauri/src/db/models.rs)",
                            "language": "rust",
                            "code": "#[derive(Queryable, Insertable, Serialize)]\n#[diesel(table_name = crate::db::schema::sales)]\npub struct Sale {\n    pub id: i32,\n    pub terminal_id: String,\n    pub total_cents: i32,\n    pub payment_method: String,\n    pub created_at: String,\n}",
                        },
                        {
                            "title": "Diesel migration (up.sql)",
                            "language": "sql",
                            "code": "-- Loyalty + refunds land on top of the core schema.\nALTER TABLE sales ADD COLUMN loyalty_points INTEGER NOT NULL DEFAULT 0;\n\nCREATE TABLE refunds (\n  id INTEGER PRIMARY KEY AUTOINCREMENT,\n  sale_id INTEGER NOT NULL REFERENCES sales(id),\n  amount_cents INTEGER NOT NULL,\n  reason TEXT NOT NULL,\n  created_at TEXT NOT NULL DEFAULT (datetime('now'))\n);",
                        },
                        {
                            "title": "Tauri command (invoice PDF)",
                            "language": "rust",
                            "code": "#[tauri::command]\npub fn generate_invoice(sale_id: i32, state: State<AppState>) -> Result<String, String> {\n    let conn = &mut state.pool.get().map_err(|e| e.to_string())?;\n    let sale: Sale = sales::table\n        .find(sale_id)\n        .first(conn)\n        .map_err(|e| e.to_string())?;\n    let items: Vec<SaleItem> = sale_items::table\n        .filter(sale_items::sale_id.eq(sale_id))\n        .load(conn)\n        .map_err(|e| e.to_string())?;\n    render_invoice_pdf(&sale, &items)\n}",
                        },
                    ],
                },
            )
        ],
        "features": [
            (
                "features",
                {
                    "title": "What Formints POS ships",
                    "description": "The features that move a terminal from a cash register to a business tool.",
                    "features": [
                        {"icon": "M4 7v10c0 2.2 1.8 4 4 4h8c2.2 0 4-1.8 4-4V7M4 7h16M4 7l2-3h12l2 3", "title": "Fast, native checkout", "description": "A Rust core keeps every keystroke instant, with no web latency on the counter."},
                        {"icon": "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.6a2 2 0 011.4.6l4.4 4.4a2 2 0 01.6 1.4V19a2 2 0 01-2 2z", "title": "SQLite by default", "description": "Zero-config local storage that scales up to a synced multi-terminal setup in Pro."},
                        {"icon": "M13 10V3L4 14h7v7l9-11h-7z", "title": "Four editions, one codebase", "description": "Community, Standard, Pro, Cloud, feature-gated from a single Tauri + Rust core."},
                    ],
                },
            ),
            (
                "features",
                {
                    "title": "Product roadmap",
                    "description": "What ships next across the four editions — the loyalty engine, multi-currency, and managed backups are already in the comparison above.",
                    "features": [
                        {"icon": "M12 2l8 4v6c0 5-3.5 8-8 10-4.5-2-8-5-8-10V6l8-4z", "title": "Loyalty & rewards engine", "description": "Points, tiers and voucher redemption built into the sale flow — Standard and up."},
                        {"icon": "M3 3v18h18M7 15l4-4 3 3 5-6", "title": "Multi-currency & tax profiles", "description": "Per-terminal currency and tax profiles for border regions — Standard and up."},
                        {"icon": "M17 21v-2a4 4 0 00-4-4H7a4 4 0 00-4 4v2M9 11a4 4 0 100-8 4 4 0 000 8zM21 21v-2a4 4 0 00-3-3.87", "title": "Automatic cloud backups", "description": "Scheduled encrypted backups of the cloud master with point-in-time restore — Cloud."},
                    ],
                },
            )
        ],
        "faq": [
            (
                "faq",
                {
                    "title": "Formints POS questions",
                    "items": [
                        {"question": "Which edition should I start with?", "answer": "Community is open source and perfect for a single terminal. Upgrade to Standard for the sidecar API + cloud sync, to Pro for a multi-terminal cloud master, or to Cloud for the fully hosted setup."},
                        {"question": "Can I reuse the schema in another project?", "answer": "Yes. The SQLite schema and Rust models are public reference material under the repo's license."},
                    ],
                },
            )
        ],
        "cta": [
            (
                "cta",
                {
                    "title": "Run a terminal in minutes",
                    "subtitle": "Clone the repo, run the Community edition, and upgrade editions as you grow.",
                    "primary_cta": {"label": "View on GitHub", "href": "https://github.com/mammhoud/formint-community", "style": "white"},
                    "secondary_cta": {"label": "Get in Touch", "href": "/contact/", "style": "outline"},
                },
            )
        ],
    },
    "lms": {
        "title": "Precis LMS",
        "logo_style": "ribbon",
        "category": "platform",
        "tagline": "The learning platform behind structa.cloud: courses, enrollments, payments.",
        "hero": [
            (
                "hero",
                {
                    "title": "Precis LMS",
                    "subtitle": "A content-driven learning platform built on Django + django-fusion with a Next.js frontend.",
                    "primary_cta": {"label": "See the editions", "href": "/products/lms/#editions", "style": "secondary"},
                    "secondary_cta": {"label": "Learn more", "href": "/about/", "style": "white"},
                },
            )
        ],
        "body": (
            "<p>Precis LMS powers the Structa Cloud learning platform: courses, "
            "enrollments, payments (Stripe), and progress tracking, all served "
            "by Django/Wagtail with django-fusion's component pipeline.</p>"
            "<p>Its frontend is a Next.js app consuming django-fusion APIs and "
            "server-rendered fragments, the same content-driven pattern the "
            "landing CMS uses.</p>"
        ),
        "tech": [
            ("tech", {"title": "Built on", "items": ["Django", "Wagtail", "django-fusion", "Next.js", "React", "Stripe"]}),
        ],
        "editions": [
            (
                "editions",
                {
                    "eyebrow": "Editions & pricing",
                    "title": "Scale from one course to a cohort",
                    "editions": [
                        {
                            "name": "Solo",
                            "tagline": "For active creators and small academies who want a polished learning experience.",
                            "price": "$29",
                            "period": "/per month",
                            "features": ["Unlimited courses", "Priority support", "Advanced analytics", "Offline downloads", "Certificates", "SSO & role management", "Dedicated success manager", "High-end learning experience design"],
                            "cta_label": "Go Solo",
                            "cta_href": "/contact/",
                            "featured": True,
                            "tier": "featured",
                        },
                        {
                            "name": "Business",
                            "tagline": "For organizations with cohorts, staff, and connected systems.",
                            "price": "$99",
                            "period": "/per month",
                            "features": ["Everything in Solo", "Custom branding", "API access"],
                            "cta_label": "Contact Sales",
                            "cta_href": "/contact/",
                            "featured": False,
                            "tier": "default",
                        },
                    ],
                },
            )
        ],
        "snippets": [
            (
                "snippets",
                {
                    "title": "Content-driven models & snippets",
                    "description": "How the LMS models content. The pattern the CMS site builder generalizes.",
                    "snippets": [
                        {
                            "title": "Wagtail course page",
                            "language": "python",
                            "code": "class CoursePage(Page):\n    title = models.CharField(max_length=255)\n    description = RichTextField(blank=True)\n    price_cents = models.IntegerField(default=0)\n    curriculum = StreamField([\n        ('lesson', LessonBlock()),\n        ('quiz', QuizBlock()),\n    ], use_json_field=True)\n\n    content_panels = Page.content_panels + [\n        FieldPanel('description'),\n        FieldPanel('price_cents'),\n        FieldPanel('curriculum'),\n    ]",
                        },
                        {
                            "title": "Enrollment (django-fusion)",
                            "language": "python",
                            "code": "from django_fusion.routes import ModelViewset\n\nclass EnrollmentViewset(ModelViewset):\n    model = Enrollment\n    fields = ['id', 'course', 'user', 'progress', 'completed_at']",
                        },
                    ],
                },
            )
        ],
        "features": [
            (
                "features",
                {
                    "title": "What Precis LMS ships",
                    "features": [
                        {"icon": "M12 2l8 4v6c0 5-3.5 8-8 10-4.5-2-8-5-8-10V6l8-4z", "title": "Content-driven courses", "description": "Lessons, quizzes and certificates composed in Wagtail StreamFields."},
                        {"icon": "M3 3v18h18M7 15l4-4 3 3 5-6", "title": "Payments built in", "description": "Stripe checkout for courses, enrollments, and subscriptions."},
                        {"icon": "M13 10V3L4 14h7v7l9-11h-7z", "title": "Fragment-rendered UI", "description": "django-fusion HTMX fragments keep the app server-rendered and fast."},
                    ],
                },
            )
        ],
        "faq": [
            (
                "faq",
                {
                    "title": "Precis LMS questions",
                    "items": [
                        {"question": "How does this relate to the landing CMS?", "answer": "LMS and CMS share django-fusion. The CMS is the content-driven website builder; LMS is its highest-value use case."},
                        {"question": "Can I embed LMS on my own site?", "answer": "Yes. Courses and progress are served as server-rendered fragments that any Fusion site can embed."},
                    ],
                },
            )
        ],
        "cta": [
            (
                "cta",
                {
                    "title": "Teach on the AHA stack",
                    "subtitle": "From one course to a full academy: content-driven, payment-enabled, server-rendered.",
                    "primary_cta": {"label": "See pricing", "href": "/products/lms/#editions", "style": "white"},
                    "secondary_cta": {"label": "Contact Us", "href": "/contact/", "style": "outline"},
                },
            )
        ],
    },
    "cms": {
        "title": "Loop",
        "version": "v2.7",
        "logo_style": "isometric",
        "category": "platform",
        "tagline": "Build content-driven websites from Wagtail blocks. This very site is built with it.",
        "hero": [
            (
                "hero",
                {
                    "title": "Loop",
                    "subtitle": "A content-driven website builder. Wagtail StreamFields composed into server-rendered pages by django-fusion.",
                    "primary_cta": {"label": "See the editions", "href": "/products/cms/#editions", "style": "secondary"},
                    "secondary_cta": {"label": "Explore the stack", "href": "/features/", "style": "white"},
                },
            )
        ],
        "body": (
            "<p>Loop is the content-driven website builder behind every "
            "structa.cloud landing page. Editors compose Wagtail StreamField "
            "blocks; django-fusion renders them as finished server-side HTML.</p>"
            "<p>It powers both render roads: Django's fusion-render HTML and the "
            "Astro frontend's data APIs, from one source of content.</p>"
        ),
        "tech": [
            ("tech", {"title": "Built on", "items": ["Wagtail", "Django", "django-fusion", "HTMX", "Alpine.js", "Astro"]}),
        ],
        "applications": [
            (
                "applications",
                {
                    "eyebrow": "Built with Loop",
                    "title": "Sites and apps running on Loop",
                    "description": (
                        "Real usage, not mockups: every structa.cloud property is a "
                        "Loop build — composed from the same Wagtail blocks you see "
                        "on this page and rendered server-side."
                    ),
                    "applications": [
                        {
                            "name": "vResume",
                            "edition": "Community",
                            "url": "/products/vresume/preview/community/",
                            "description": "The cloud resume platform — modern templates, PDF export, and Syntara-powered AI summaries, served from the same content pipeline.",
                        },
                        {
                            "name": "structa.cloud",
                            "edition": "Community",
                            "url": "/",
                            "description": "This site. Every landing page you are reading is composed from StreamField blocks and rendered as finished HTML.",
                        },
                        {
                            "name": "Precis LMS",
                            "edition": "Business",
                            "url": "/products/lms/",
                            "description": "The learning platform — courses, enrollments and payments built on the same django-fusion component system.",
                        },
                    ],
                },
            )
        ],
        "editions": [
            (
                "editions",
                {
                    "eyebrow": "Editions & pricing",
                    "title": "From one page to a whole site",
                    "editions": [
                        {
                            "name": "Community",
                            "tagline": "A single landing page with the core section blocks.",
                            "price": "$0",
                            "period": "/open source",
                            "features": ["Wagtail StreamField blocks", "django-fusion rendering", "HTMX fragments", "MIT license"],
                            "cta_label": "Self-host",
                            "cta_href": "https://github.com/mammhoud/django-fusion",
                            "featured": False,
                            "tier": "outline",
                        },
                        {
                            "name": "Business",
                            "tagline": "A full marketing site with custom blocks + analytics. Multi-site, multi-editor, fully managed.",
                            "price": "Custom",
                            "period": "/project",
                            "features": ["Everything in Community", "Custom StreamField blocks", "Blog + FAQ sections", "Analytics + SEO", "HTMX forms", "Multi-site + roles", "Dedicated support"],
                            "cta_label": "Contact Sales",
                            "cta_href": "/contact/",
                            "featured": True,
                            "tier": "featured",
                        },
                    ],
                },
            )
        ],
        "snippets": [
            (
                "snippets",
                {
                    "title": "Blocks & snippets you can reuse",
                    "description": "The building blocks that make a site content-driven. Copy them into any Fusion project.",
                    "snippets": [
                        {
                            "title": "A StreamField section block",
                            "language": "python",
                            "code": "class HeroBlock(blocks.StructBlock):\n    badge = blocks.CharBlock(max_length=80, required=False)\n    title = blocks.CharBlock(max_length=200)\n    subtitle = blocks.TextBlock(required=False)\n    primary_cta = ButtonBlock(required=False)\n\n    class Meta:\n        template = 'content/blocks/hero.html'\n        label = 'Hero'\n",
                        },
                        {
                            "title": "Server-rendered fragment",
                            "language": "html",
                            "code": "<section class=\"container-fusion py-20 text-center\">\n  <h1 class=\"text-4xl font-bold sm:text-6xl\">{{ value.title }}</h1>\n  {% if value.subtitle %}<p class=\"mx-auto mt-6 max-w-2xl text-lg text-fu-muted\">{{ value.subtitle }}</p>{% endif %}\n</section>",
                        },
                    ],
                },
            )
        ],
        "features": [
            (
                "features",
                {
                    "title": "What Loop ships",
                    "features": [
                        {"icon": "M12 2l8 4v6c0 5-3.5 8-8 10-4.5-2-8-5-8-10V6l8-4z", "title": "Block-based editing", "description": "Editors compose sections; developers own the templates."},
                        {"icon": "M13 10V3L4 14h7v7l9-11h-7z", "title": "Two render roads", "description": "Fusion-render HTML and data APIs from one Wagtail source of truth."},
                        {"icon": "M12 2a10 10 0 100 20 10 10 0 000-20zM2 12h20", "title": "Open source", "description": "django-fusion is public on GitHub under a permissive license."},
                    ],
                },
            )
        ],
        "faq": [
            (
                "faq",
                {
                    "title": "Loop questions",
                    "items": [
                        {"question": "Is this the same CMS that runs this site?", "answer": "Yes. Every page you're reading is composed from these StreamField blocks and rendered by django-fusion."},
                        {"question": "Can I add my own blocks?", "answer": "Absolutely. Blocks are plain Wagtail StructBlocks with Django templates, no framework lock-in."},
                    ],
                },
            )
        ],
        "cta": [
            (
                "cta",
                {
                    "title": "Ships as HTML, edits as blocks",
                    "subtitle": "The CMS is open source. Clone it, add your blocks, ship your site.",
                    "primary_cta": {"label": "View on GitHub", "href": "https://github.com/mammhoud/django-fusion", "style": "white"},
                    "secondary_cta": {"label": "Read the Docs", "href": "/about/", "style": "outline"},
                },
            )
        ],
    },
    "cypercloud": {
        "title": "Syntara",
        "logo_style": "orbit",
        "status": "development",
        "category": "platform",
        "tagline": "AI chat customizer. Embed Syntara-powered chat into any site.",
        "hero": [
            (
                "hero",
                {
                    "title": "Syntara",
                    "subtitle": "An AI chat customizer platform. Ceptor-ai powered chat embedded into customer sites, fully branded.",
                    "primary_cta": {"label": "See the editions", "href": "/products/cypercloud/#editions", "style": "secondary"},
                    "secondary_cta": {"label": "View ceptor-ai on GitHub", "href": "https://github.com/mammhoud/ceptor-ai", "style": "white"},
                },
            )
        ],
        "body": (
            "<p>Syntara lets you embed intelligent chat into customer sites with "
            "full customization: branding, behavior, and model selection.</p>"
            "<p>It is powered by ceptor-ai (the MCP server + chat client library) "
            "and ships as an embeddable widget.</p>"
            "<p><strong>Status: under development.</strong> Syntara is an early "
            "preview — its APIs, editions and pricing may change before the 1.0 "
            "release. Treat everything below as a roadmap, not a contract.</p>"
        ),
        "tech": [("tech", {"title": "Built on", "items": ["Python", "Django", "ceptor-ai", "MCP"]})],
        "editions": [
            (
                "editions",
                {
                    "eyebrow": "Editions & pricing",
                    "title": "Free to embed, paid to customize",
                    "editions": [
                        {"name": "Community", "tagline": "The open-source chat client, self-hosted.", "price": "$0", "period": "/open source", "features": ["ceptor-ai chat client", "MCP server", "Multi-model support"], "cta_label": "Self-host", "cta_href": "https://github.com/mammhoud/ceptor-ai", "featured": False, "tier": "outline"},
                        {"name": "Business", "tagline": "Managed chat with full branding.", "price": "$39", "period": "/per month", "features": ["Everything in Community", "Branded widget", "Behavior rules", "Analytics"], "cta_label": "Get Started", "cta_href": "/contact/", "featured": True, "tier": "featured"},
                    ],
                },
            )
        ],
        "cta": [("cta", {"title": "Chat that looks like your brand", "subtitle": "Embed Syntara-powered chat in an afternoon.", "primary_cta": {"label": "Get Started", "href": "/contact/", "style": "white"}, "secondary_cta": {"label": "View ceptor-ai on GitHub", "href": "https://github.com/mammhoud/ceptor-ai", "style": "outline"}})],
    },
    "vresume": {
        "title": "vResume",
        "logo_style": "ascent",
        "category": "platform",
        # Subproduct — stays catalog-only (visible on /products/ + pricing
        # tabs) but is excluded from the homepage preview cards.
        "show_on_home": False,
        "tagline": "Cloud resume platform. Create, update, publish professional resumes — with Syntara-powered AI summaries.",
        "hero": [
            (
                "hero",
                {
                    "title": "vResume",
                    "subtitle": "A cloud-hosted resume builder with modern templates, custom domains, CI/CD deployments, and Syntara-powered AI profile summaries.",
                    "primary_cta": {"label": "Launch vResume", "href": "https://vresume.structa.cloud", "style": "secondary"},
                    "secondary_cta": {"label": "See the editions", "href": "/products/vresume/#editions", "style": "white"},
                },
            )
        ],
        "body": (
            "<p>vResume lets you create, update, and publish professional resumes "
            "with modern templates, cloud-hosted at vresume.structa.cloud.</p>"
            "<p>Custom domains and a CI/CD pipeline make it a production showcase "
            "of the monorepo's deploy tooling.</p>"
            "<p>It pairs with Syntara, the AI chat customizer, for AI-assisted "
            "resume summaries and a chat-ready profile on every page.</p>"
        ),
        "tech": [("tech", {"title": "Built on", "items": ["Django", "Wagtail", "Next.js", "Syntara", "CI/CD"]})],
        "editions": [
            (
                "editions",
                {
                    "eyebrow": "Editions & pricing",
                    "title": "From one resume to a hosted portfolio",
                    "editions": [
                        {"name": "Community", "tagline": "One resume with the default template.", "price": "$0", "period": "/forever", "features": ["Modern resume templates", "Live preview", "PDF export"], "cta_label": "View on GitHub", "cta_href": "https://github.com/mammhoud", "featured": False, "tier": "outline"},
                        {"name": "Business", "tagline": "Custom domain + multiple resumes.", "price": "$9", "period": "/per month", "features": ["Everything in Community", "Custom domain", "Multiple resumes", "Syntara AI summaries", "Analytics"], "cta_label": "Upgrade", "cta_href": "/contact/", "featured": True, "tier": "featured"},
                    ],
                },
            )
        ],
        "cta": [("cta", {"title": "Your career, published", "subtitle": "Build a resume that ships like a product.", "primary_cta": {"label": "Launch vResume", "href": "https://vresume.structa.cloud", "style": "white"}, "secondary_cta": {"label": "Contact Us", "href": "/contact/", "style": "outline"}})],
    },
    "ceptor-ai": {
        "title": "ceptor-ai",
        "logo_style": "orbit",
        "category": "library",
        # Internal library — keep it out of the homepage, catalog, pricing,
        # and product dropdown even if its hidden state is changed later.
        "show_on_home": False,
        "hidden": True,
        "tagline": "AI chat client + MCP server. Agent communication and generation.",
        "hero": [
            (
                "hero",
                {
                    "title": "ceptor-ai",
                    "subtitle": "An AI chat client with a Model Context Protocol (MCP) server. Powers Syntara and agent tooling.",
                    "primary_cta": {"label": "View on GitHub", "href": "https://github.com/mammhoud/ceptor-ai", "style": "secondary"},
                    "secondary_cta": {"label": "See the editions", "href": "/products/ceptor-ai/#editions", "style": "white"},
                },
            )
        ],
        "body": (
            "<p>ceptor-ai is the AI layer of the monorepo: an MCP server for agent "
            "communication, a chat client with multi-model support, and a BEM "
            "converter for prompt-to-component generation.</p>"
        ),
        "tech": [("tech", {"title": "Built on", "items": ["Python", "MCP", "AI/ML", "Node.js"]})],
        "editions": [
            (
                "editions",
                {
                    "eyebrow": "Editions & pricing",
                    "title": "One library, one license",
                    "editions": [
                        {"name": "Open Source", "tagline": "The full MCP server + chat client.", "price": "$0", "period": "/MIT", "features": ["MCP server", "Chat client", "BEM converter", "Agent generation"], "cta_label": "View on GitHub", "cta_href": "https://github.com/mammhoud/ceptor-ai", "featured": True},
                    ],
                },
            )
        ],
        "cta": [("cta", {"title": "Agents that talk to your tools", "subtitle": "ceptor-ai connects LLMs to anything via MCP.", "primary_cta": {"label": "View on GitHub", "href": "https://github.com/mammhoud/ceptor-ai", "style": "white"}, "secondary_cta": {"label": "See Syntara", "href": "/products/cypercloud/", "style": "outline"}})],
    },
}


DEFAULT_HOME_CONTENT = {
    "hero": [
        (
            "hero",
            {
                "badge": "structa.cloud · digital product partner",
                # NB: the Hero renders ``title`` + ``accent`` separately (both
                # roads — Astro Hero.astro and content/blocks/hero.html), so
                # the accent word is NOT part of the stored title. Keep titles
                # free of the accent phrase.
                "title": "Digital products, shipped as",
                "accent": "documents",
                "subtitle": (
                    "We help teams serving the Gulf, Levant, and North Africa launch clear, "
                    "bilingual services that feel fast and stay easy to operate."
                ),
                "primary_cta": {"label": "Explore products", "href": "/products/", "style": "secondary"},
                "secondary_cta": {"label": "Work with us", "href": "/contact/", "style": "white"},
                "trusted_by": "Arabic-ready · English-ready · built for real teams",
            },
        )
    ],
    "cta": [
        (
            "cta",
            {
                "title": "A useful first release beats a noisy roadmap",
                "subtitle": "We start with the customer journey, launch a focused slice, and leave your team with the content and tools to keep improving it.",
                "primary_cta": {"label": "View on GitHub", "href": "https://github.com/mammhoud", "style": "white"},
                "secondary_cta": {"label": "Read the Docs", "href": "/about/", "style": "outline"},
            },
        )
    ],
}


# The full document lives on the About page (mirrors the Astro frontend where
# /about carries hero + mission + stats + features + pricing + testimonials +
# faq + cta and / is a slim hero + cta entry point).
DEFAULT_ABOUT_SECTIONS = {
    "stats": [
        (
            "stats",
            {
                "title": "Built for steady growth",
                "stats": [
                    {"value": "15", "suffix": "+", "label": "Open-source repos"},
                    {"value": "18", "suffix": "", "label": "Blog posts"},
                    {"value": "4", "suffix": "+", "label": "Production sites"},
                    {"value": "5", "suffix": "+", "label": "Years building"},
                ],
            },
        )
    ],
    "features": [
        (
            "features",
            {
                "title": "Built by one engineer, for real teams",
                "description": (
                    "Structa Cloud is a one-person studio with an open-source backbone: "
                    "the founder designs, builds, and ships every product, and the "
                    "libraries that make them possible are public on GitHub."
                ),
                "features": [
                    {
                        "icon": "M12 2l8 4v6c0 5-3.5 8-8 10-4.5-2-8-5-8-10V6l8-4z",
                        "title": "A founder who ships",
                        "description": "One engineer owns the full stack — Django, Wagtail, Rust, React — and ships every product as finished, server-rendered documents.",
                    },
                    {
                        "icon": "M13 10V3L4 14h7v7l9-11h-7z",
                        "title": "Your team owns the content",
                        "description": "Structured content lets marketing and operations teams update Arabic and English pages without waiting for engineering.",
                    },
                    {
                        "icon": "M4 5h16v14H4z M4 12h16",
                        "title": "Arabic and English by design",
                        "description": "Language direction, navigation, content fallbacks, and editorial fields are considered from the first page, not added at the end.",
                    },
                    {
                        "icon": "M17 21v-2a4 4 0 00-4-4H7a4 4 0 00-4 4v2M9 11a4 4 0 100-8 4 4 0 000 8zM21 21v-2a4 4 0 00-3-3.87",
                        "title": "A system that can be handed over",
                        "description": "Reusable blocks, clear controls, and practical documentation keep the service maintainable after launch.",
                    },
                    {
                        "icon": "M3 3v18h18M7 15l4-4 3 3 5-6",
                        "title": "Automation with a human check",
                        "description": "AI can accelerate research, support, and content workflows while your team keeps the final say.",
                    },
                    {
                        "icon": "M12 2a10 10 0 100 20 10 10 0 000-20zM2 12h20",
                        "title": "A performance budget, not a promise",
                        "description": "We reserve room for content, images, and future features, then check Core Web Vitals on the devices and networks your customers use.",
                    },
                ],
            },
        )
    ],
    "testimonials": [
        (
            "testimonials",
            {
                "title": "Designed around the people using it",
                "description": "The strongest product decisions come from clear journeys, useful content, and teams who can keep the experience moving.",
                "testimonials": [
                    {
                        "quote": "The switch from a heavy React SPA to HTMX fragments cut our page load time in half. django-fusion's component system made the migration straightforward.",
                        "author": "Sarah Mitchell",
                        "role": "CTO, EduStart",
                        "avatar_initials": "SM",
                    },
                    {
                        "quote": "Alpine.js replaced all our custom UI state code. The FAQ accordion and modals took an afternoon instead of a week.",
                        "author": "David Chen",
                        "role": "Lead Developer, LearnLoop",
                        "avatar_initials": "DC",
                    },
                    {
                        "quote": "Server-rendered HTML means perfect SEO without any extra work. Our blog traffic doubled within a month.",
                        "author": "Amira Hassan",
                        "role": "Marketing Director, SkillBridge",
                        "avatar_initials": "AH",
                    },
                ],
            },
        )
    ],
    "pricing": [
        (
            "pricing",
            {
                "title": "Simple, transparent pricing",
                "description": "A clear starting point for the products we ship. Edition names, availability, and pricing are product-specific — Precis LMS, for example, is offered as Solo and Business rather than a Community tier.",
                "tiers": [
                    {
                        "name": "Open source",
                        "description": "For exploring the public libraries and products that offer a self-hosted edition.",
                        "price": "$0",
                        "period": "/where available",
                        "features": [
                            "Public source code",
                            "Self-hosted documentation",
                            "Core product capabilities",
                            "Product-specific licensing",
                        ],
                        "cta_label": "Explore products",
                        "cta_href": "/products/",
                        "featured": False,
                    },
                    {
                        "name": "Pro",
                        "description": "For teams that need production workflows and room to grow.",
                        "price": "From $29",
                        "period": "/per month",
                        "features": [
                            "Production-ready capabilities",
                            "Priority support options",
                            "Advanced analytics where included",
                            "Deployment guidance",
                            "Product-specific feature set",
                        ],
                        "cta_label": "Compare products",
                        "cta_href": "/pricing/",
                        "featured": True,
                    },
                    {
                        "name": "Business",
                        "description": "For organizations that need governance, integrations, or managed delivery.",
                        "price": "Custom",
                        "period": "/per deployment",
                        "features": [
                            "Organization workflows",
                            "Roles and permissions where included",
                            "Custom branding options",
                            "API and integration support",
                            "Deployment and success support",
                        ],
                        "cta_label": "Contact Sales",
                        "cta_href": "/contact/",
                        "featured": False,
                    },
                ],
            },
        )
    ],
    "cta": [
        (
            "cta",
            {
                "title": "Built in the open, shipped as HTML",
                "subtitle": "Some products and the core libraries are public on GitHub. Edition availability and licensing vary by product; Precis LMS is offered as Solo and Business.",
                "primary_cta": {"label": "View on GitHub", "href": "https://github.com/mammhoud", "style": "white"},
                "secondary_cta": {"label": "Get in Touch", "href": "/contact/", "style": "outline"},
            },
        )
    ],
}


# The dedicated FAQ page — the single home for general questions. Unlike the
# section stacks on About/Products/Features (which no longer carry a generic
# FAQ), this list is the one place with the platform-wide answers, expanded
# across the domain: the stack, the products, editions, licensing, auth,
# privacy/cookies and support. Product pages keep their own short
# product-specific FAQ (e.g. "Formints POS questions").
DEFAULT_FAQ_SECTIONS = {
    "faq": [
        (
            "faq",
            {
                "title": "Frequently Asked Questions",
                "description": "The honest answers to the questions technical buyers ask — the stack, the products, the editions, and the fine print.",
                "items": [
                    {
                        "question": "What is structa.cloud?",
                        "answer": "Structa Cloud is the portfolio and product hub for Mahmoud Ezzat Moustafa: a full-stack developer building Django/Wagtail platforms, AI tools, and open-source libraries.",
                    },
                    {
                        "question": "What is the AHA stack?",
                        "answer": "AHA stands for Astro + HTMX + Alpine.js: a server-first rendering stack that ships minimal client-side JavaScript. Astro renders the document, HTMX swaps server-rendered fragments, and Alpine hydrates micro-interactions.",
                    },
                    {
                        "question": "Which products are available and in what editions?",
                        "answer": "Formints POS (Community, Standard, Pro, Cloud), Precis LMS (Solo, Business), Loop CMS (Community, Business), Syntara AI chat (Community, Business) and vResume (Community, Business). Product editions are priced by capability; paid tiers add richer learning operations, integrations, cloud sync, multi-terminal and hosted features.",
                    },
                    {
                        "question": "Are the libraries free to use?",
                        "answer": "Yes. django-fusion, ceptor-ai, and the Formints POS core are all open-source on GitHub under permissive licenses. You can use them in commercial and client projects.",
                    },
                    {
                        "question": "Can I use this for a client project?",
                        "answer": "Absolutely. The libraries are production-tested across vResume, Syntara, and the landing pages. The monorepo even documents the licensing terms for reuse.",
                    },
                    {
                        "question": "How do I get started?",
                        "answer": "Clone the monorepo from github.com/mammhoud, run 'make dev' in projects/landing-fusion, and explore the Wagtail admin at /admin/. Each product page ships reference snippets and models you can copy.",
                    },
                    {
                        "question": "How do I deploy a Fusion site?",
                        "answer": "The monorepo includes Docker Compose orchestration with Traefik + Nginx + Postgres. One 'make deploy' provisions the full stack with HTTPS, and the docs cover DNS-01 Let's Encrypt via Cloudflare.",
                    },
                    {
                        "question": "What is django-fusion?",
                        "answer": "django-fusion is the component system + routing framework used across every structa.cloud product: StreamField blocks rendered server-side, HTMX fragments, and a dual-mode API pipeline.",
                    },
                    {
                        "question": "What is ceptor-ai?",
                        "answer": "ceptor-ai is the AI layer of the monorepo: an MCP server for agent communication, a chat client with multi-model support, and a BEM converter for prompt-to-component generation. It powers Syntara.",
                    },
                    {
                        "question": "Is there an account or login system?",
                        "answer": "Yes — sign-in is powered by django-allauth (headless API + social providers like GitHub and Google). The Log In button in the header opens a modal; after sign-in your session is stored server-side.",
                    },
                    {
                        "question": "What data does the site collect, and what about cookies?",
                        "answer": "We only use essential cookies (theme preference + HTMX navigation state) and never sell data. The privacy policy lists exactly what is collected and how you can request deletion. Non-essential analytics are opt-in via the cookie banner.",
                    },
                    {
                        "question": "Which editions need a license vs. deployment fees?",
                        "answer": "Community editions are open source. Standard/Pro list a per-month license; deployment and support are quoted per site. Cloud is fully hosted and quoted on contact. Pricing pages always state the exact model.",
                    },
                    {
                        "question": "How do the POS editions differ?",
                        "answer": "Community is a free offline single-terminal POS. Standard adds an embedded Python sidecar + cloud sync client. Pro is multi-terminal with a cloud master and high-throughput Rust API. Cloud is the Pro master, hosted and managed for you.",
                    },
                    {
                        "question": "How is this different from a React or Vue site?",
                        "answer": "A React site sends a shell plus a bundle, then builds the page in the browser. Fusion sends the finished HTML in one response. Less to download, less to run, and search engines read exactly what visitors see.",
                    },
                    {
                        "question": "Can I still build dynamic dashboards?",
                        "answer": "Yes. HTMX streams HTML fragments from Django over plain HTTP — the same technology as the landing page. Dynamic regions stay server-rendered, so there is never a second, parallel API to maintain.",
                    },
                    {
                        "question": "How do I get support?",
                        "answer": "Open an issue on GitHub for open-source questions, or use the contact form on the Contact page for deployment, licensing and Cloud quoting. Business and Cloud editions include dedicated support.",
                    },
                ],
            },
        )
    ],
}


# About → Team subpage (child of About, served at /about/team/).
# The people behind structa.cloud: the founder + product leads, each with
# their social links. Links use the mammhoud handles (GitHub / LinkedIn /
# Facebook) so the team page and the rest of the site stay consistent.
DEFAULT_TEAM_SECTIONS = {
    "hero": [
        (
            "hero",
            {
                "title": "The people behind structa.cloud",
                "subtitle": "One engineer, three product leads, and the open-source contributors who make the monorepo ship.",
                "primary_cta": {"label": "Meet the founder", "href": "/about/", "style": "secondary"},
                "secondary_cta": {"label": "Get in touch", "href": "/contact/", "style": "white"},
            },
        )
    ],
    "body": (
        "<p>structa.cloud is built in the open. The founder runs the "
        "architecture; each product has a named lead; the libraries are "
        "public on GitHub for anyone to contribute to.</p>"
    ),
    "team": [
        (
            "team",
            {
                "eyebrow": "the team",
                "title": "Who builds what",
                "description": "Every product is a project in the monorepo, and every project has an owner.",
                "members": [
                    {
                        "name": "Mahmoud Ezzat Moustafa",
                        "role": "Founder · full-stack engineer",
                        "bio": "Architect of the monorepo: Django/Wagtail platforms, the AHA landing stack, and the AI libraries. Ships everything as server-rendered documents.",
                        "initials": "ME",
                        "links": [
                            {"platform": "GitHub", "url": "https://github.com/mammhoud"},
                            {"platform": "LinkedIn", "url": "https://linkedin.com/in/mammhoud"},
                            {"platform": "Facebook", "url": "https://facebook.com/mammhoud"},
                            {"platform": "Portfolio", "url": "https://mammhoud.github.io"},
                        ],
                    },
                    {
                        "name": "Formints",
                        "role": "Product lead · point-of-sale",
                        "bio": "The Tauri 2 + Rust desktop POS: SQLite, four editions, one codebase. Community is open source on GitHub.",
                        "initials": "FP",
                        "links": [{"platform": "GitHub", "url": "https://github.com/mammhoud/formint-community"}],
                    },
                    {
                        "name": "Precis LMS",
                        "role": "Product lead · learning platform",
                        "bio": "Courses, enrollments and Stripe payments on django-fusion. The highest-value use case of the CMS.",
                        "initials": "PL",
                        "links": [{"platform": "GitHub", "url": "https://github.com/mammhoud"}],
                    },
                    {
                        "name": "Loop CMS",
                        "role": "Product lead · website builder",
                        "bio": "Wagtail StreamField blocks rendered by django-fusion. This very site is built with it.",
                        "initials": "LC",
                        "links": [{"platform": "GitHub", "url": "https://github.com/mammhoud/django-fusion"}],
                    },
                    {
                        "name": "Syntara",
                        "role": "Product lead · AI chat",
                        "bio": "Ceptor-ai powered chat embedded into any site. Under development — a preview of what's next.",
                        "initials": "SY",
                        "links": [{"platform": "GitHub", "url": "https://github.com/mammhoud/ceptor-ai"}],
                    },
                    {
                        "name": "vResume",
                        "role": "Product lead · cloud resume",
                        "bio": "Create, update and publish professional resumes with custom domains and CI/CD deployments.",
                        "initials": "VR",
                        "links": [{"platform": "GitHub", "url": "https://github.com/mammhoud"}],
                    },
                ],
            },
        )
    ],
    "cta": [
        (
            "cta",
            {
                "title": "Built in the open",
                "subtitle": "Every line of structa.cloud is public on GitHub. Come build with us.",
                "primary_cta": {"label": "View on GitHub", "href": "https://github.com/mammhoud", "style": "white"},
                "secondary_cta": {"label": "Back to About", "href": "/about/", "style": "outline"},
            },
        )
    ],
}


# About → Founder subpage (child of About, served at /about/founder/).
# The engineer behind structa.cloud — mirrors the Astro founder page: hero,
# story body, tech-stack band (TechStackSectionBlock) and a skills grid
# (FeaturesSectionBlock).
DEFAULT_FOUNDER_SECTIONS = {
    "hero": [
        (
            "hero",
            {
                "title": "Mahmoud Ezzat Moustafa",
                "subtitle": "Full-stack developer, open-source contributor, and the engineer behind structa.cloud. Django, Wagtail, and AI-powered systems.",
                "primary_cta": {"label": "Meet the team", "href": "/about/team/", "style": "secondary"},
                "secondary_cta": {"label": "View on GitHub", "href": "https://github.com/mammhoud", "style": "white"},
                "trusted_by": "Python · Django · Wagtail · AI tooling",
            },
        )
    ],
    "body": (
        "<p>Mahmoud Ezzat Moustafa is a full-stack developer specializing in "
        "Python/Django, Wagtail CMS, and AI tooling. He builds server-rendered "
        "platforms that ship as documents — no heavy SPAs, no framework "
        "overhead. Every project in the structa.cloud monorepo carries his "
        "signature: finished HTML in one response.</p>"
        "<p>He works in the open: the libraries, the products, and the "
        "documentation that explains them are all public on GitHub.</p>"
    ),
    "tech": [
        (
            "tech",
            {
                "eyebrow": "the stack",
                "title": "Built on",
                "description": "The tools that ship every product in the monorepo.",
                "items": ["Python", "Django", "Wagtail", "django-fusion", "ceptor-ai", "Astro", "HTMX", "Alpine.js", "Tauri 2", "Rust", "React", "PostgreSQL", "Redis", "Docker", "Traefik", "GitHub Actions"],
            },
        )
    ],
    "features": [
        (
            "features",
            {
                "eyebrow": "skills & values",
                "title": "How the work gets done",
                "description": "The capabilities and principles that show up in every project.",
                "features": [
                    {
                        "icon": "M13 10V3L4 14h7v7l9-11h-7z",
                        "title": "Ships as documents",
                        "description": "Server-rendered HTML in one response — no hydration waterfalls, no 500 KB bundles.",
                    },
                    {
                        "icon": "M12 2l8 4v6c0 5-3.5 8-8 10-4.5-2-8-5-8-10V6l8-4z",
                        "title": "Reusable systems",
                        "description": "django-fusion and ceptor-ai extracted from real projects, so every site inherits the patterns.",
                    },
                    {
                        "icon": "M4 5h16v14H4z M4 12h16",
                        "title": "Bilingual by default",
                        "description": "Arabic and English considered from the first page — direction, content fallbacks, editorial fields.",
                    },
                    {
                        "icon": "M3 3v18h18M7 15l4-4 3 3 5-6",
                        "title": "Performance as trust",
                        "description": "A fast first visit gives customers confidence before the first conversation.",
                    },
                ],
            },
        )
    ],
    "cta": [
        (
            "cta",
            {
                "title": "Built in the open",
                "subtitle": "The full monorepo is public on GitHub. Community editions are free, Pro editions are commercial.",
                "primary_cta": {"label": "View on GitHub", "href": "https://github.com/mammhoud", "style": "white"},
                "secondary_cta": {"label": "Contact", "href": "/contact/", "style": "outline"},
            },
        )
    ],
}


# About → Startup subpage (child of About, served at /about/startup/).
# The origin story — mirrors the Astro startup page: hero, story body, a
# numbered timeline (ProcessSectionBlock, one step per era) and a stats band.
DEFAULT_STARTUP_SECTIONS = {
    "hero": [
        (
            "hero",
            {
                "title": "The Startup",
                "subtitle": "How structa.cloud grew from freelance Django projects into a monorepo of open-source products, AI tools, and a desktop POS application.",
                "primary_cta": {"label": "See the products", "href": "/products/", "style": "secondary"},
                "secondary_cta": {"label": "Meet the founder", "href": "/about/founder/", "style": "white"},
                "trusted_by": "2019 · freelance → 2026 · five products",
            },
        )
    ],
    "body": (
        "<p>Structa Cloud started as one developer shipping Wagtail sites. "
        "Each project repeated the same auth patterns, the same blocks, the "
        "same table layouts — until the reusable parts became a library, and "
        "the library became a monorepo of products.</p>"
    ),
    "process": [
        (
            "process",
            {
                "eyebrow": "the timeline",
                "title": "From freelance to five products",
                "description": "A measured path: learn the pattern, extract it, open it, productize it.",
                "steps": [
                    {
                        "title": "2019–2021 · Freelance foundations",
                        "description": "Solo Django developer shipping Wagtail sites. WordPress had the market share; Django had the performance. Auth, CMS, payments, analytics — hand-rolled every time.",
                        "deliverable": "Five client projects",
                    },
                    {
                        "title": "2022 · The reusable library",
                        "description": "After five projects with the same auth, blocks, and tables, django-fusion was extracted — a component system and routing framework every project could share.",
                        "deliverable": "django-fusion v1",
                    },
                    {
                        "title": "2023 · Open source and AI",
                        "description": "Published django-fusion on GitHub, built ceptor-ai (AI chat customizer + MCP server), and started Formints, a desktop POS in Tauri 2 + Rust + React.",
                        "deliverable": "ceptor-ai · Formints",
                    },
                    {
                        "title": "2024 · The AHA stack",
                        "description": "Migrated from heavy React SPAs to Astro + HTMX + Alpine.js — server-rendered HTML with minimal client JS. This landing page is the framework itself.",
                        "deliverable": "Astro + HTMX + Alpine",
                    },
                    {
                        "title": "2025–2026 · Products and scale",
                        "description": "Five products shipping from one monorepo: Formints POS, Precis LMS, Loop CMS, Syntara AI, vResume. Community editions open source, paid editions commercial.",
                        "deliverable": "Five products, one repo",
                    },
                ],
            },
        )
    ],
    "stats": [
        (
            "stats",
            {
                "title": "The story in numbers",
                "stats": [
                    {"value": "5", "suffix": "+", "label": "Years building"},
                    {"value": "5", "suffix": "", "label": "Products shipping"},
                    {"value": "15", "suffix": "+", "label": "Open-source repos"},
                    {"value": "1", "suffix": "", "label": "Monorepo"},
                ],
            },
        )
    ],
    "cta": [
        (
            "cta",
            {
                "title": "Built in the open, shipped as HTML",
                "subtitle": "Community editions and the core libraries are public on GitHub. Paid editions are commercial.",
                "primary_cta": {"label": "View on GitHub", "href": "https://github.com/mammhoud", "style": "white"},
                "secondary_cta": {"label": "Read the About page", "href": "/about/", "style": "outline"},
            },
        )
    ],
}


class Command(BaseCommand):
    help = "Seed the landing Wagtail page tree with default content."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help=(
                "Overwrite existing content fields with seed values "
                "(default: only backfill empty fields, preserving edits)."
            ),
        )
        parser.add_argument(
            "--refresh-product",
            metavar="SLUG",
            help=(
                "Refresh and publish one seeded ProductPage only (for example "
                "formint-pos), preserving unrelated editor-managed pages."
            ),
        )

    def handle(self, *args, **options):
        self.force = options.get("force", False)
        refresh_product = options.get("refresh_product")
        if refresh_product:
            self._refresh_product(refresh_product)
            return
        self.stdout.write("Seeding landing pages…")

        root = Page.objects.filter(depth=1).first()
        if root is None:
            self.stdout.write(self.style.ERROR("No root page — run migrations first."))
            return

        landing_models = {
            HomePage,
            AboutPage,
            ServicesPage,
            PhasePage,
            PromptPage,
            ProductsPage,
            FeaturesPage,
            BlogPage,
            BrandPage,
            PricingPage,
            ContactPage,
            FaqPage,
            PrivacyPage,
        }

        # Repoint-or-drop any Site that does not point at one of our landing
        # pages (Wagtail's migrations create a default site rooted on the
        # "Welcome" page, which we remove below).
        for site in Site.objects.all():
            try:
                rooted_in_landing = site.root_page.specific_class in landing_models
            except Page.DoesNotExist:  # pragma: no cover — orphaned pointer
                rooted_in_landing = False
            if not rooted_in_landing:
                self.stdout.write(f"Removing default site: {site.hostname}")
                site.delete()

        # ── Home page (root child) ──────────────────────────────────────
        # Create the owned page before deleting Wagtail's migration-time
        # "Welcome" sibling. Older treebeard versions calculate a new
        # sibling path from the current last child and can return None when
        # the root has just been emptied in a fresh TestCase database.
        home, created = self._get_or_create_child(
            root, HomePage, title="Home", slug="home", **DEFAULT_HOME_CONTENT
        )
        self._created(created, "home")

        # Remove Wagtail's default "Welcome" page and any other non-landing
        # root child now that the root has a valid landing sibling. This keeps
        # the command idempotent while making fresh test databases reliable.
        for child in root.get_children():
            if child.pk != home.pk and child.specific_class not in landing_models:
                self.stdout.write(f"Removing default page: {child.title} (slug={child.slug})")
                child.delete()

        site, _ = Site.objects.get_or_create(
            hostname="localhost",
            defaults={"port": 8074, "is_default_site": True, "root_page": home},
        )
        site.root_page = home
        site.save()
        self.stdout.write(f"Site root set to {home.title} (http://localhost:{site.port}/)")

        # ── Social auth apps ──────────────────────────────────────────
        self.stdout.write("Seeding social auth apps (GitHub + Google)…")
        from allauth.socialaccount.models import SocialApp

        for provider_id, name, client_id_key, secret_key in (
            ("github", "GitHub", "GITHUB_CLIENT_ID", "GITHUB_CLIENT_SECRET"),
            ("google", "Google", "GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET"),
        ):
            client_id = os.environ.get(client_id_key, "")
            secret = os.environ.get(secret_key, "")
            if client_id and secret:
                app, created = SocialApp.objects.get_or_create(
                    provider=provider_id,
                    defaults={"name": name, "client_id": client_id, "secret": secret},
                )
                if created:
                    app.sites.add(site)
                    self.stdout.write(f"  ✓ {name} SocialApp created")
                else:
                    app.sites.add(site)
                    self.stdout.write(f"  → {name} SocialApp already exists, site added")
            else:
                self.stdout.write(
                    f"  ⚠ {name} skipped — set {client_id_key}/{secret_key} env vars"
                )

        # ── About (the full document) ────────────────────────────────
        about, created = self._get_or_create_child(
            home,
            AboutPage,
        title="About Us",
        slug="about",
        hero=[
            (
                "hero",
                {
                    "title": "A clearer path to market",
                    "subtitle": "We connect strategy, design, and delivery for teams building services in Arabic and English.",
                    "primary_cta": {"label": "See how we work", "href": "/services/", "style": "secondary"},
                    "secondary_cta": {"label": "Start a conversation", "href": "/contact/", "style": "white"},
                },
            )
        ],
        body=(
            "<p>Structa Cloud helps teams across the Gulf, Levant, and North Africa turn important ideas into useful digital services.</p>"
            "<p>We start with the customer journey, the content, and the operating reality of your team. Then we choose the simplest technology that can carry the experience well.</p>"
            "<p>Arabic and English content, quick first visits, and clear editorial controls are part of the product brief from the beginning.</p>"
            "<p>The handover matters as much as the launch. Your team gets a system it can understand, update, and improve without a permanent dependency on a development queue.</p>"
        ),
            # About tells the full story — stats, features, testimonials AND
            # the simple transparent pricing stack. The dedicated /pricing/
            # page carries the per-product price sheets on top.
            **DEFAULT_ABOUT_SECTIONS,
        )
        self._created(created, "about")

        # ── About → Team (subpage, /about/team/) ────────────────────────
        team, created = self._get_or_create_child(
            about,
            TeamPage,
            title="Team",
            slug="team",
            hero=DEFAULT_TEAM_SECTIONS["hero"],
            body=DEFAULT_TEAM_SECTIONS["body"],
            team=DEFAULT_TEAM_SECTIONS["team"],
            cta=DEFAULT_TEAM_SECTIONS["cta"],
        )
        self._created(created, "about:team")

        # ── About → Founder (subpage, /about/founder/) ───────────────────
        founder, created = self._get_or_create_child(
            about,
            FounderPage,
            title="Founder",
            slug="founder",
            hero=DEFAULT_FOUNDER_SECTIONS["hero"],
            body=DEFAULT_FOUNDER_SECTIONS["body"],
            tech=DEFAULT_FOUNDER_SECTIONS["tech"],
            features=DEFAULT_FOUNDER_SECTIONS["features"],
            cta=DEFAULT_FOUNDER_SECTIONS["cta"],
        )
        self._created(created, "about:founder")

        # ── About → Startup (subpage, /about/startup/) ───────────────────
        startup, created = self._get_or_create_child(
            about,
            StartupPage,
            title="Startup",
            slug="startup",
            hero=DEFAULT_STARTUP_SECTIONS["hero"],
            body=DEFAULT_STARTUP_SECTIONS["body"],
            process=DEFAULT_STARTUP_SECTIONS["process"],
            stats=DEFAULT_STARTUP_SECTIONS["stats"],
            cta=DEFAULT_STARTUP_SECTIONS["cta"],
        )
        self._created(created, "about:startup")

        # ── Services ────────────────────────────────────────────────────
        services, created = self._get_or_create_child(
            home,
            ServicesPage,
            title="Services",
            slug="services",
            hero=[
                (
                    "hero",
                    {
                "title": "From idea to market",
                "subtitle": "Focused digital services for teams that need a clear customer journey and a dependable launch.",
                "primary_cta": {"label": "Explore products", "href": "/products/", "style": "secondary"},
                "secondary_cta": {"label": "Start a conversation", "href": "/contact/", "style": "white"},
                "trusted_by": "Arabic-ready · English-ready · built for real teams",
                    },
                )
            ],
    body=(
        "<p>We shape three kinds of work: market-ready websites, digital products, and focused improvements to services that already have customers.</p>"
        "<p>Every engagement balances brand, content, accessibility, and the realities of mobile networks across the region.</p>"
        "<p>We leave teams with a performance budget, bilingual content controls, and a practical handover instead of a black box.</p>"
    ),
            **DEFAULT_SERVICES_SECTIONS,
            cta=DEFAULT_HOME_CONTENT["cta"],
        )
        self._created(created, "services")

        # ── Services → delivery phases + reusable implementation prompts ──
        phase_seed = [
            {
                "title": "Discover", "slug": "discover", "phase_number": 1,
                "phase_label": "discovery",
                "body": "<p>Turn the brief into a clear document model, visual direction, and measurable first release.</p>",
                "outcomes": "A bounded brief\nA content and route map\nA first-release decision log",
                "prompts": [{
                    "title": "Shape the brief", "slug": "shape-the-brief",
                    "prompt": "Turn this product brief into a focused first release with user, content, route, and success constraints.",
                    "context": "Use this before design or implementation begins.",
                    "output": "A concise scope, assumptions, risks, and acceptance checklist.",
                    "tool": "Wagtail + product discovery",
                }],
            },
            {
                "title": "Build", "slug": "build", "phase_number": 2,
                "phase_label": "build",
                "body": "<p>Build the smallest complete path as server-rendered HTML, then add HTMX and Alpine where they improve the document.</p>",
                "outcomes": "A working content model\nA responsive document route\nProgressive enhancement checks",
                "prompts": [{
                    "title": "Build the first vertical slice", "slug": "build-the-first-vertical-slice",
                    "prompt": "Implement one complete user journey from Wagtail model to accessible HTML, with progressive enhancement only where needed.",
                    "context": "Keep the server-rendered path usable without JavaScript.",
                    "output": "A tested vertical slice with model, API, template, and browser states.",
                    "tool": "Astro + HTMX + Alpine",
                }],
            },
            {
                "title": "Launch", "slug": "launch", "phase_number": 3,
                "phase_label": "launch",
                "body": "<p>Ship a dependable release with content parity, observability, and a handoff the team can own.</p>",
                "outcomes": "SEO and accessibility checks\nDeployment runbook\nEditor handoff",
                "prompts": [{
                    "title": "Prepare the release", "slug": "prepare-the-release",
                    "prompt": "Audit this release for broken routes, missing content, accessibility regressions, and backend/frontend parity before deployment.",
                    "context": "Run the same checklist against the Astro and Django roads.",
                    "output": "A prioritized release report with fixes and explicit sign-off criteria.",
                    "tool": "Django + Astro verification",
                }],
            },
            {
                "title": "Enhance", "slug": "enhance", "phase_number": 4,
                "phase_label": "enhance",
                "body": "<p>Improve the living system through measured content, performance, and interaction enhancements.</p>",
                "outcomes": "A measured improvement backlog\nReusable content patterns\nA safe iteration loop",
                "prompts": [{
                    "title": "Enhance without drift", "slug": "enhance-without-drift",
                    "prompt": "Improve this page while preserving content ownership, render parity, accessibility, and the existing design language.",
                    "context": "Prefer reusable components and Wagtail-managed content over one-off page markup.",
                    "output": "A small change set with regression checks and a documented reason for each change.",
                    "tool": "django-fusion components",
                }],
            },
        ]
        for phase_data in phase_seed:
            prompts = phase_data.pop("prompts")
            phase, phase_created = self._get_or_create_child(services, PhasePage, **phase_data)
            self._created(phase_created, f"services:phase:{phase.slug}")
            for prompt_data in prompts:
                prompt, prompt_created = self._get_or_create_child(phase, PromptPage, **prompt_data)
                self._created(prompt_created, f"services:phase:{phase.slug}:prompt:{prompt.slug}")

        # ── Products (full document, like About) ───────────────────────
        products, created = self._get_or_create_child(
            home,
            ProductsPage,
            title="Products",
            slug="products",
            hero=[
                (
                    "hero",
                    {
                        # + Astro accent "open source"
                        "title": "Most of what we build, shipped as",
                        "subtitle": "The full catalog: products with editions and pricing, plus the projects behind them, from one monorepo.",
                        "primary_cta": {"label": "See the editions", "href": "/products/formint-pos/#editions", "style": "secondary"},
                        "secondary_cta": {"label": "Browse the repo", "href": "https://github.com/mammhoud", "style": "white"},
                    },
                )
            ],
            body=(
                "<p>Every project in the structa.cloud monorepo, one card "
                "each: desktop applications, hosted platforms, and open-source "
                "libraries. Every card links to a reference page with editions "
                "&amp; pricing, tech stack, and snippets/models you can reuse.</p>"
                "<p>The product cards and the repo project grid were merged "
                "into one list — each product IS a project in this repo.</p>"
            ),
            projects=[],
            **DEFAULT_ABOUT_SECTIONS,
        )
        self._created(created, "products")

        # ── Product pages (children of Products) ─────────────────────────
        # Rename cleanup — the POS product moved from slug ``forge-pos`` to
        # ``formint-pos`` (Formints). Rename in place BEFORE the creation loop
        # so an older page keeps its tree position (the flagship leads the
        # catalog); only delete when the new slug was already created.
        stale_forge = ProductPage.objects.filter(slug="forge-pos").first()
        if stale_forge is not None:
            if ProductPage.objects.filter(slug="formint-pos").exists():
                stale_forge.delete()
                self.stdout.write("Removed stale product page: forge-pos")
            else:
                stale_forge.slug = "formint-pos"
                stale_forge.save()
                self.stdout.write("Renamed product page: forge-pos → formint-pos")

        # Each is a reference document with editions & pricing + snippets.
        for slug, product in DEFAULT_PRODUCT_PAGES.items():
            product_page, created = self._get_or_create_child(
                products,
                ProductPage,
                slug=slug,
                title=product["title"],
                category=product.get("category", "application"),
                tagline=product.get("tagline", ""),
                version=product.get("version", ""),
                logo_style=product.get("logo_style", "crest"),
                status=product.get("status", "live"),
                hidden=product.get("hidden", False),
                show_on_home=product.get("show_on_home", True),
                hero=product.get("hero", []),
                body=product.get("body", ""),
                tech=product.get("tech", []),
                editions=product.get("editions", []),
                comparison=product.get("comparison", []),
                applications=product.get("applications", []),
                gallery=product.get("gallery", []),
                snippets=product.get("snippets", []),
                features=product.get("features", []),
                faq=product.get("faq", []),
                cta=product.get("cta", []),
            )
            self._created(created, f"product:{slug}")

        # Catalog flags follow the seed spec on every run. This keeps public
        # subproducts (vResume) out of the curated home/dropdown surfaces and
        # keeps internal libraries (ceptor-ai) explicitly ineligible even if a
        # stale database row predates these flags.
        for slug, product in DEFAULT_PRODUCT_PAGES.items():
            # Scope the backfill to this landing catalog. A shared Wagtail
            # database may contain another site's ProductPage with the same
            # slug; never mutate that page while refreshing landing content.
            page = products.get_children().filter(slug=slug).first()
            if page is None:
                continue
            page = page.specific
            if not isinstance(page, ProductPage):
                continue
            wanted_show_on_home = product.get("show_on_home", True)
            wanted_hidden = product.get("hidden", False)
            updates = []
            if page.show_on_home != wanted_show_on_home:
                page.show_on_home = wanted_show_on_home
                updates.append("show_on_home")
            if page.hidden != wanted_hidden:
                page.hidden = wanted_hidden
                updates.append("hidden")
            if updates:
                page.save(update_fields=updates)
                self.stdout.write(
                    f"Updated product flags: {slug} "
                    f"show_on_home={wanted_show_on_home} hidden={wanted_hidden}"
                )

        # Catalog order — product children follow DEFAULT_PRODUCT_PAGES so the
        # flagship (Formints) leads the tree on fresh DBs and after renames.
        desired_order = [slug for slug in DEFAULT_PRODUCT_PAGES]
        current_order = [
            c.slug
            for c in products.get_children().live()
            if isinstance(c.specific, ProductPage)
        ]
        if current_order != desired_order:
            placed = None
            for slug in desired_order:
                node = products.get_children().live().filter(slug=slug).first()
                if node is None:
                    continue
                if placed is None:
                    node.move(products, pos="first-child")
                else:
                    node.move(placed, pos="right")
                placed = node

        # Removed-product cleanup — django-bolt was dropped from the catalog
        # (its capability lives on inside Formints' Pro tier). Any page seeded
        # by an older revision is removed so the tree mirrors the catalog.
        stale_bolt = ProductPage.objects.filter(slug="django-bolt").first()
        if stale_bolt is not None:
            stale_bolt.delete()
            self.stdout.write("Removed removed-product page: django-bolt")

        # ── Blog (index grid, mirror of the frontend /blog) ───────────────
        blog, created = self._get_or_create_child(
            home,
            BlogPage,
            title="Blog",
            slug="blog",
            hero=[
                (
                    "hero",
                    {
                "title": "Ideas from real launches",
                "subtitle": "Practical notes on digital services, performance, and content for teams serving the region.",
                "primary_cta": {"label": "Explore products", "href": "/products/", "style": "secondary"},
                "secondary_cta": {"label": "Start a conversation", "href": "/contact/", "style": "white"},
                    },
                )
            ],
            **DEFAULT_BLOG_SECTION,
            cta=DEFAULT_HOME_CONTENT["cta"],
        )
        self._created(created, "blog")

        # ── Blog post pages (children of Blog — each has /blog/<slug>/) ────
        # One BlogPostPage per seeded post: same slug as the grid card so the
        # links resolve, plus real body content for the detail page.
        for post in DEFAULT_BLOG_POSTS:
            slug = post.get("slug")
            if not slug:
                continue
            post_page, post_created = self._get_or_create_child(
                blog,
                BlogPostPage,
                slug=slug,
                title=post.get("title", ""),
                category=post.get("category", ""),
                post_date=post.get("date") or None,
                read_time=post.get("read_time", ""),
                excerpt=post.get("excerpt", ""),
                hero_screenshot_url=post.get("hero_screenshot_url", ""),
                body=DEFAULT_BLOG_POST_BODIES.get(slug, ""),
                variants=DEFAULT_BLOG_POST_VARIANTS.get(slug, []),
                snippets=DEFAULT_BLOG_POST_SNIPPETS.get(slug, []),
                hero=[
                    (
                        "hero",
                        {
                            "title": post.get("title", ""),
                            "subtitle": post.get("excerpt", ""),
                            "primary_cta": {"label": "Back to Blog", "href": "/blog/", "style": "secondary"},
                            "secondary_cta": {"label": "Contact Us", "href": "/contact/", "style": "white"},
                        },
                    )
                ],
                cta=DEFAULT_HOME_CONTENT["cta"],
            )
            self._created(post_created, f"blog-post:{slug}")

        # ── Wire product snippet cards to their deep-dive posts ─────────
        # The code for each product's reference snippets now lives in a blog
        # deep dive; the product page keeps a reference card that links out
        # (SnippetBlock.related_post). Runs AFTER the posts are created so
        # the PageChooser resolves on both fresh and re-seeded databases, and
        # touches existing pages too (idempotent — only sets missing links).
        DEEP_DIVE_POST_SLUGS = {
            "formint-pos": "formint-pos-data-model",
            "lms": "precis-lms-content-model",
            "cms": "loop-block-library",
        }
        for product_slug, post_slug in DEEP_DIVE_POST_SLUGS.items():
            product_page = ProductPage.objects.filter(slug=product_slug).first()
            deep_dive = BlogPostPage.objects.filter(slug=post_slug).first()
            if product_page is None or deep_dive is None:
                continue
            self._wire_snippet_deep_dives(product_page, deep_dive)

        # ── Pricing (dedicated page with its own tiers + faq) ─────────────
        pricing, created = self._get_or_create_child(
            home,
            PricingPage,
            title="Pricing",
            slug="pricing",
            hero=[
                (
                    "hero",
                    {
                        "title": "Pricing",
                        "subtitle": "Simple, transparent pricing. Start free and scale as you grow.",
                        "primary_cta": {"label": "Start Free", "href": "/contact/", "style": "secondary"},
                        "secondary_cta": {"label": "Contact Sales", "href": "/contact/", "style": "white"},
                    },
                )
            ],
            # The tabbed per-product pricing (get_product_pricing) supersedes
            # the old generic tier stack — no tiers seeded here. The generic
            # FAQ moved to the dedicated /faq/ page — no FAQ seeded here.
            pricing=[],
            cta=DEFAULT_HOME_CONTENT["cta"],
        )
        self._created(created, "pricing")

        # ── Features (full document, like About) ────────────────────────
        features, created = self._get_or_create_child(
            home,
            FeaturesPage,
            title="Features",
            slug="features",
            hero=[
                (
                    "hero",
                    {
                        # + Astro accent "documents"
                        "title": "Built to ship as",
                        "subtitle": "The AHA stack, documented. Every capability of Structa Cloud.",
                        "primary_cta": {"label": "Our Products", "href": "/products/", "style": "secondary"},
                        "secondary_cta": {"label": "Get Started", "href": "/contact/", "style": "white"},
                    },
                )
            ],
            body=(
                "<p>The AHA stack is Astro + HTMX + Alpine.js: a server-first "
                "rendering stack that ships finished HTML in one response.</p>"
                "<p>Every capability below exists to keep the page a document: "
                "fast by default, secure by default, editable by editors.</p>"
            ),
            **DEFAULT_ABOUT_SECTIONS,
        )
        self._created(created, "features")

        # ── Brand (identity system, page + product-tooltip modal) ─────────
        # A real Wagtail page (BrandPage) so editors can toggle display_mode
        # (page / modal / both) in the admin. The identity boards themselves
        # are derived from the catalog + BRAND_SPEC — they can never drift.
        brand, created = self._get_or_create_child(
            home,
            BrandPage,
            title="Brand",
            slug="brand",
            display_mode="both",
            hero=[
                (
                    "hero",
                    {
                        # + Astro accent "five marks"
                        "title": "One family, five marks",
                        "subtitle": "Every product carries its own constructed mark — a symbol built from what it does, not a generic glyph. Same system, five distinct identities.",
                        "primary_cta": {"label": "See the products", "href": "/products/", "style": "secondary"},
                        "secondary_cta": {"label": "Pricing", "href": "/pricing/", "style": "white"},
                    },
                )
            ],
            cta=DEFAULT_HOME_CONTENT["cta"],
        )
        self._created(created, "brand")

        # ── Projects merged into Products ─────────────────────────────
        # The Projects page was folded into the Products catalog: the product
        # cards ARE the repo project grid (the separate project grid seed was
        # removed) and the legacy /projects/ URL permanently redirects
        # (apps/handlers/urls.py). The ProjectsPage model was removed by
        # migration 0012 so there is nothing to clean up here.

        # ── Contact ─────────────────────────────────────────────────────
        contact, created = self._get_or_create_child(
            home,
            ContactPage,
            title="Contact",
            slug="contact",
            hero=[
                (
                    "hero",
                    {
                        "title": "Get in Touch",
                        "subtitle": "We'd love to hear from you. Reach out any time.",
                    },
                )
            ],
            contact=[
                (
                    "contact",
                    {
                        "title": "We'd love to hear from you",
                        "description": "Send us a message and we'll respond within 24 hours.",
                        "methods": [
                            {
                                "method_type": "email",
                                "label": "Email",
                                "value": "structa.cloud@gmail.com",
                                "href": "mailto:structa.cloud@gmail.com",
                            },
                            {
                                "method_type": "phone",
                                "label": "Phone",
                                "value": "+1 (555) 010-2030",
                                "href": "tel:+15550102030",
                            },
                            {
                                "method_type": "address",
                                "label": "Address",
                                "value": "123 Fusion Lane, Suite 400",
                            },
                            {
                                "method_type": "hours",
                                "label": "Working Hours",
                                "value": "Mon – Fri, 9:00 – 18:00",
                            },
                        ],
                        "form_title": "Send us a message",
                        "form_description": "Fill out the form and our team will get back to you.",
                        "topics": [
                            "General inquiry",
                            "Formints POS",
                            "Precis LMS",
                            "Loop CMS",
                            "Syntara",
                            "vResume",
                            "Website building",
                            "Product development",
                            "Enhancements & extensions",
                            "Partnership",
                        ],
                    },
                )
            ],
            cta=[
                (
                    "cta",
                    {
                        "title": "Prefer email?",
                        "subtitle": "Write to structa.cloud@gmail.com and we'll reply within a day.",
                        "primary_cta": {"label": "Send an Email", "href": "mailto:structa.cloud@gmail.com", "style": "white"},
                    },
                )
            ],
        )
        self._created(created, "contact")

        # ── FAQ ─────────────────────────────────────────────────────────
        faq, created = self._get_or_create_child(
            home,
            FaqPage,
            title="FAQ",
            slug="faq",
            hero=[
                (
                    "hero",
                    {
                        "title": "Frequently Asked Questions",
                        "subtitle": "The honest answers to the questions technical buyers ask.",
                    },
                )
            ],
            faq=DEFAULT_FAQ_SECTIONS["faq"],
            cta=DEFAULT_HOME_CONTENT["cta"],
        )
        self._created(created, "faq")

        # ── Privacy ─────────────────────────────────────────────────────
        privacy, created = self._get_or_create_child(
            home,
            PrivacyPage,
            title="Privacy Policy",
            slug="privacy",
            body=(
                "<p>This privacy policy explains how Structa Cloud collects, uses, "
                "and protects your information. We keep data collection minimal "
                "by design: this site is a static-first document, not a data "
                "platform.</p>"
                "<h3>What we collect</h3>"
                "<p>Contact form submissions (name, email, message), account "
                "details for authenticated features, and anonymous usage "
                "patterns. We never sell your personal information to third "
                "parties.</p>"
                "<h3>How we use it</h3>"
                "<p>To respond to inquiries, deliver requested services, "
                "personalize your experience, and improve the platform.</p>"
                "<h3>Cookies and consent</h3>"
                "<p>We only use <strong>essential cookies</strong>: a theme "
                "preference and HTMX navigation state. No tracking, no ads, "
                "no third-party cookies. The cookie banner on first visit asks "
                "for consent; your choice (Accept or Deny) is stored locally in "
                "your browser, and no non-essential cookie is ever set without "
                "it.</p>"
                "<p>When you accept, no additional data is collected — consent "
                "only permits the same essential cookies. When you deny, the "
                "site works identically, minus the persisted theme "
                "preference.</p>"
                "<h3>Your rights</h3>"
                "<p>You can request a copy or deletion of your data at any time "
                "by contacting us, and you can withdraw cookie consent at any "
                "time by clearing your browser storage.</p>"
            ),
        )
        self._created(created, "privacy")

        # ── Social links (Wagtail snippets) ─────────────────────────────
        # Seeded idempotently: existing links are left untouched unless the
        # URL differs from the seed (then the seed wins — the mammhoud handles
        # are the canonical identity).
        try:
            from apps.content.models.settings import SocialLink

            default_links = [
                {"platform": "github", "label": "GitHub", "url": "https://github.com/mammhoud"},
                {"platform": "linkedin", "label": "LinkedIn", "url": "https://linkedin.com/in/mammhoud"},
                {"platform": "facebook", "label": "Facebook", "url": "https://facebook.com/mammhoud"},
                {"platform": "twitter", "label": "X / Twitter", "url": "https://x.com/mammhoud", "is_active": False},
            ]
            for i, link in enumerate(default_links):
                obj, _ = SocialLink.objects.get_or_create(
                    platform=link["platform"],
                    defaults={**link, "sort_order": i},
                )
                if obj.url != link["url"]:
                    obj.url = link["url"]
                    obj.sort_order = i
                    obj.save()
        except Exception as exc:
            logger.exception("Social links seed failed")
            raise CommandError("Unable to seed social links") from exc

        self._seed_wagtail_locales()
        self._seed_site_languages()
        self._seed_page_translations()
        self.stdout.write(self.style.SUCCESS("✅ Landing pages seeded."))

    def _seed_wagtail_locales(self):
        """Ensure every configured content language has a Wagtail Locale row.

        Landing Fusion keeps one canonical page tree plus partial editorial
        overlays, but Wagtail still needs native Locale records for the admin
        language picker, translation workflows, and future page translations.
        This is additive and idempotent: it never changes existing locale rows.
        """
        from django.conf import settings

        language_codes = [code for code, _label in settings.LANGUAGES]
        with transaction.atomic():
            for code in language_codes:
                locale, created = Locale.objects.get_or_create(language_code=code)
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Seeded Wagtail locale {code}."))

    def _seed_site_languages(self):
        """Create/update the seeded ``SiteLanguage`` catalog idempotently.

        Existing rows keep their editor changes unless ``--force`` is passed
        (then active/order are refreshed). New languages added to
        ``DEFAULT_SITE_LANGUAGES`` are created; languages removed from the
        default list are left untouched (editors may re-enable them later).
        """
        from apps.content.models.languages import SiteLanguage

        try:
            for entry in DEFAULT_SITE_LANGUAGES:
                code = entry["code"]
                language, created = SiteLanguage.objects.get_or_create(
                    code=code,
                    defaults=entry,
                )
                if not created and self.force:
                    changed = False
                    for field in ("name", "native_name", "direction", "flag"):
                        if getattr(language, field) != entry[field]:
                            setattr(language, field, entry[field])
                            changed = True
                    if language.is_active != entry["is_active"] or language.sort_order != entry["sort_order"]:
                        language.is_active = entry["is_active"]
                        language.sort_order = entry["sort_order"]
                        changed = True
                    if changed:
                        language.save(update_fields=["name", "native_name", "direction", "flag", "is_active", "sort_order"])
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Seeded language {code} ({entry['name']})."))
        except Exception as exc:
            logger.exception("Site language seed failed")
            raise CommandError("Unable to seed site languages") from exc

    def _seed_page_translations(self):
        """Create/update the seeded editorial overlays for every language.

        The map is keyed by page slug then language code; each payload is a
        partial overlay, so untranslated fields keep falling back to the
        canonical Wagtail content through the page-API merge.
        """
        for slug, values in DEFAULT_PAGE_TRANSLATIONS.items():
            landing_root = HomePage.objects.first()
            page = (
                landing_root.get_descendants(inclusive=True).live().filter(slug=slug).first()
                if landing_root is not None
                else Page.objects.live().filter(slug=slug).first()
            )
            if page is None:
                continue
            for language, payload in values.items():
                if not payload:
                    continue
                translation, created = PageTranslation.objects.get_or_create(
                    page=page,
                    language=language,
                    defaults=payload,
                )
                if not created:
                    changed = False
                    for field in ("title", "search_description", "body", "content"):
                        seeded = payload.get(field, {} if field == "content" else "")
                        if self.force or not getattr(translation, field):
                            setattr(translation, field, seeded)
                            changed = True
                    if changed:
                        translation.save(update_fields=["title", "search_description", "body", "content", "updated_at"])

    # ── Helpers ─────────────────────────────────────────────────────
    def _get_or_create_child(self, parent, model, **fields):
        """Idempotently create a treebeard page under ``parent``.

        Treebeard nodes cannot be created with ``Model.objects.get_or_create``
        (``save()`` runs ``full_clean`` before ``path``/``depth`` are set), so
        we look up by slug first and otherwise use ``parent.add_child``.

        If the page already exists, only *empty* content fields are backfilled
        from the seed values — editor changes to non-empty fields are never
        clobbered. This also refreshes pages whose fields were added by a
        later migration (e.g. Products upgraded to a full document).
        """
        slug = fields["slug"]
        # Scope the lookup to this exact parent. A depth-only lookup can find
        # an identically-slugged page elsewhere in a fresh test tree, then
        # still attempt to add a duplicate child under the current parent.
        existing_node = parent.get_children().filter(slug=slug).first()
        if existing_node is not None:
            existing = existing_node.specific
            if not isinstance(existing, model):
                # Wagtail's migration fixture can leave a generic Page at the
                # exact slug we now own. Keep it temporarily as a Treebeard
                # sibling while allocating the concrete landing node; deleting
                # the only child first makes older Treebeard releases call
                # _inc_path() on None. The cleanup below removes this renamed
                # placeholder after the concrete page exists.
                placeholder_slug = f"{slug}-placeholder"
                existing_node.slug = placeholder_slug
                existing_node.save(update_fields=["slug"])
            else:
                self._backfill_empty_fields(existing, fields)
                return existing, False
        page = model(**fields)
        parent.add_child(instance=page)
        # If a generic placeholder occupied this exact parent/slug, remove it
        # after the concrete sibling has been allocated safely.
        if existing_node is not None and not isinstance(existing_node.specific, model):
            existing_node.delete()
        return page, True

    def _refresh_product(self, slug):
        """Refresh only a product's release metadata and preview gallery.

        Gallery captures are deployment metadata, but the rest of a product
        page is editor-owned content. This deliberately avoids ``--force`` so
        a media refresh cannot overwrite a curated hero, body, pricing, FAQ,
        or CTA. The resulting revision is published for the live API.
        """
        product = DEFAULT_PRODUCT_PAGES.get(slug)
        if product is None:
            raise CommandError(f"Unknown seeded product: {slug}")

        products_page = ProductsPage.objects.first()
        existing = (
            products_page.get_children().filter(slug=slug).first()
            if products_page is not None
            else None
        )
        if existing is None or not isinstance(existing.specific, ProductPage):
            raise CommandError(
                f"ProductPage with slug '{slug}' does not exist; run seed_pages first."
            )
        existing = existing.specific

        field = ProductPage._meta.get_field("editions")
        raw_editions = json.loads(field.value_to_string(existing))
        gallery_field = ProductPage._meta.get_field("gallery")
        raw_gallery = json.loads(gallery_field.value_to_string(existing))
        seeded_gallery = product.get("gallery", [])

        def normalize_gallery(value):
            """Compare seed tuple syntax with Wagtail's persisted block JSON."""
            normalized = []
            for block in value:
                if isinstance(block, (list, tuple)):
                    block_type, block_value = block
                else:
                    block_type = block.get("type")
                    block_value = block.get("value", {})
                block_value = dict(block_value or {})
                items = []
                for item in block_value.get("items", []):
                    if isinstance(item, dict) and item.get("type") == "item":
                        item = item.get("value", {})
                    items.append(item)
                block_value["items"] = items
                normalized.append({"type": block_type, "value": block_value})
            return normalized

        seeded_editions = {
            str(edition.get("name", "")).casefold(): edition
            for block_type, section in product.get("editions", [])
            if block_type == "editions"
            for edition in section.get("editions", [])
        }
        changed = existing.version != product.get("version", "")
        existing.version = product.get("version", "")
        if normalize_gallery(raw_gallery) != normalize_gallery(seeded_gallery):
            raw_gallery = seeded_gallery
            changed = True

        for block in raw_editions:
            if block.get("type") != "editions":
                continue
            for wrapped in block.get("value", {}).get("editions", []):
                value = wrapped.get("value", {})
                seeded = seeded_editions.get(str(value.get("name", "")).casefold())
                if seeded is None:
                    continue
                preview_images = seeded.get("preview_images", [])
                if value.get("preview_images", []) != preview_images:
                    value["preview_images"] = preview_images
                    changed = True

        if changed:
            existing.editions = raw_editions
            existing.gallery = raw_gallery
            existing.save()
            existing.save_revision().publish()
            self.stdout.write(self.style.SUCCESS(f"Refreshed and published product: {slug}"))
        else:
            self.stdout.write(f"Product already current: {slug}")

    def _backfill_empty_fields(self, existing, fields):
        """Apply seed values to an existing page's content fields.

        Without ``--force`` only *empty* fields are set (editor changes to
        non-empty fields are preserved and content added by later migrations
        is backfilled). With ``--force`` every content field is overwritten,
        refreshing pages that hold content from an older seed revision.
        """
        changed = False
        for name, value in fields.items():
            if name == "slug":
                continue  # slugs anchor the tree; never rewritten
            # Titles are only rewritten for ProductPage (the catalog rename
            # path); every other page keeps its title even under --force so
            # editor-customized About/Blog titles are never clobbered.
            if name == "title" and not isinstance(existing, ProductPage):
                continue
            current = getattr(existing, name, None)
            # StreamFields/RichTextFields are falsy when empty.
            if self.force or (not current and value):
                setattr(existing, name, value)
                changed = True
        if changed:
            existing.save()
        return changed

    def _wire_snippet_deep_dives(self, product_page, deep_dive):
        """Set SnippetBlock.related_post on every snippet of a product page.

        The code for each product's reference snippets lives in a blog deep
        dive; the product page keeps a reference card that links out to it.
        Runs after the posts are created so the PageChooser resolves on fresh
        databases, and is idempotent — existing pages are only touched when a
        snippet is missing its deep-dive link (editor content is preserved).
        """
        if not product_page.snippets:
            return
        blocks = []
        changed = False
        for block in product_page.snippets:
            if block.block_type != "snippets":
                blocks.append(block)
                continue
            value = dict(block.value)
            snippets = []
            for snip in value.get("snippets", []):
                snip_dict = dict(snip)
                if not snip_dict.get("related_post"):
                    snip_dict["related_post"] = deep_dive
                    changed = True
                snippets.append(snip_dict)
            value["snippets"] = snippets
            blocks.append(("snippets", value))
        if changed:
            product_page.snippets = blocks
            product_page.save()

    def _created(self, created, label):
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created {label} page."))
        else:
            self.stdout.write(f"{label} page already exists.")
