"""Seed the public Structa Cloud learning catalog.

Usage::

    python manage.py seed_learning

The command is intentionally idempotent: editors can continue changing the
course in Wagtail without a later seed replacing their description or lessons.
Only missing records and the stable YouTube channel metadata are backfilled.
"""
from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils.html import format_html

from apps.learning.models import (
    Course,
    CourseTag,
    Lesson,
    LessonResource,
    Module,
    Review,
    Specialization,
)

YOUTUBE_CHANNEL_URL = "https://www.youtube.com/@mammhoud"
COURSE_SLUG = "ship-django-products"
SPECIALIZATION_SLUG = "practical-web-development"


OBJECTIVES = "\n".join(
    [
        "Design content and routes around real customer decisions",
        "Build search, forms, menus, and progress with progressive enhancement",
        "Protect the critical path with backend, static, and browser checks",
        "Ship a maintainable handoff instead of a fragile demo",
    ]
)
REQUIREMENTS = "\n".join(
    [
        "Comfortable with Python and basic Django",
        "HTML/CSS basics",
        "A terminal and a code editor",
    ]
)
TARGET_AUDIENCE = "\n".join(
    [
        "Founders and product teams shipping content-driven products",
        "Django developers adding HTMX and Alpine to their stack",
        "Developers who want fast pages that remain editable and testable",
    ]
)


MODULES = [
    {
        "order": 1,
        "title": "The document-first foundation",
        "description": "Start with the customer journey, finished HTML, and an editorial model your team can own.",
        "lessons": [
            ("A page is a product surface", "Choose the smallest useful journey and turn it into a clear document.", 18, True),
            ("Model content around decisions", "Shape Wagtail fields and reusable sections around the questions customers ask.", 24, True),
            ("Build a fast first response", "Keep the critical path small, readable, and measurable on real regional networks.", 22, False),
        ],
    },
    {
        "order": 2,
        "title": "HTMX interactions without a SPA",
        "description": "Add useful interaction while keeping the server response as the source of truth.",
        "lessons": [
            ("Fragments as a UI contract", "Return the exact HTML region that changes and let the browser swap it in.", 20, False),
            ("Forms, validation, and CSRF", "Handle success and failure states with progressive enhancement and safe defaults.", 27, False),
            ("Loading, empty, and error states", "Make the slow path feel intentional instead of hiding it behind a spinner.", 19, False),
        ],
    },
    {
        "order": 3,
        "title": "Alpine for the small moments",
        "description": "Use a small amount of declarative state for menus, accordions, and learner progress.",
        "lessons": [
            ("State at the edge", "Keep Alpine state local and avoid rebuilding the page in the browser.", 21, False),
            ("Accessible accordions and menus", "Pair transitions with keyboard behavior, labels, and escape paths.", 26, False),
            ("Course progress that stays honest", "Update progress from completed lessons and keep certificates derived from evidence.", 23, False),
        ],
    },
    {
        "order": 4,
        "title": "Test, ship, and hand over",
        "description": "Finish with checks that protect the critical path and a deployment your team can understand.",
        "lessons": [
            ("Test the real route", "Verify HTML, API contracts, links, assets, and the browser console before release.", 25, False),
            ("Performance as a launch feature", "Set budgets for first paint, images, JavaScript, and server response time.", 18, False),
            ("A calm production handoff", "Document the content model, environment variables, logs, and rollback path.", 24, False),
        ],
    },
]


# ── CourseTranslation overlays (ar/sv/fr/de/es/pt) ─────────────────────────
# Partial overlays: empty fields keep falling back to the canonical English
# content through the API merge contract.  ``modules`` mirrors the MODULES
# tree above; lesson overrides are keyed by order (the API resolves by id then
# order).
COURSE_TRANSLATIONS = {
    "ar": {
        "title": "أطلق منتجات Django باستخدام HTMX وAlpine",
        "short_description": "دورة عملية تعتمد على المستند أولًا لبناء منتجات سريعة تعتمد على المحتوى يمكن لفريقك امتلاكها.",
        "description": (
            "<p>ابنِ خدمة رقمية مفيدة بمكدس AHA: Astro للمستندات، وHTMX للتفاعلات المقدَّمة من "
            "الخادم، وAlpine للحظات الحالة الصغيرة.</p>"
            "<p>هذا المسار العملي موجه للمؤسسين وفرق المنتجات والمطورين الذين يريدون صفحات سريعة "
            "تبقى قابلة للتحرير والاختبار وسهلة التسليم. ستنهي الدورة بشريحة منتج بحجم دورة عمل وقائمة إطلاق.</p>"
            "<h2>ماذا ستكون قادرًا على فعله</h2>"
            "<ul><li>تصميم المحتوى والمسارات حول قرارات العملاء الحقيقية</li>"
            "<li>بناء البحث والنماذج والقوائم والتقدم بالتحسين التدريجي</li>"
            "<li>حماية المسار الحرج بفحوصات الواجهة الخلفية والثابتة والمتصفح</li>"
            "<li>تسليم عمل قابل للصيانة بدلًا من عرض تجريبي هش</li></ul>"
        ),
        "objectives": [
            "صمم المحتوى والمسارات حول قرارات العملاء الحقيقية",
            "ابنِ البحث والنماذج والقوائم والتقدم بالتحسين التدريجي",
            "احمِ المسار الحرج بفحوصات الواجهة الخلفية والثابتة والمتصفح",
            "سلّم عملًا قابلًا للصيانة بدلًا من عرض تجريبي هش",
        ],
        "requirements": [
            "راحة مع Python وأساسيات Django",
            "أساسيات HTML/CSS",
            "طرفية ومحرر أكواد",
        ],
        "target_audience": [
            "مؤسسون وفرق منتجات تنشر منتجات تعتمد على المحتوى",
            "مطورو Django الذين يضيفون HTMX وAlpine إلى مجموعتهم",
            "مطورون يريدون صفحات سريعة تبقى قابلة للتحرير والاختبار",
        ],
        "modules": [
            {"order": 1, "title": "الأساس القائم على المستند أولًا",
             "description": "ابدأ برحلة العميل، وHTML مكتمل، ونموذج تحريري يمكن لفريقك امتلاكه.",
             "lessons": [
                 {"order": 1, "title": "الصفحة هي سطح المنتج"},
                 {"order": 2, "title": "صمم المحتوى حول القرارات"},
                 {"order": 3, "title": "ابنِ أول استجابة سريعة"},
             ]},
            {"order": 2, "title": "تفاعلات HTMX بدون تطبيق من صفحة واحدة",
             "description": "أضف تفاعلًا مفيدًا مع إبقاء استجابة الخادم مصدر الحقيقة.",
             "lessons": [
                 {"order": 1, "title": "الأجزاء (Fragments) كعقد واجهة"},
                 {"order": 2, "title": "النماذج والتحقق وCSRF"},
                 {"order": 3, "title": "حالات التحميل والفراغ والخطأ"},
             ]},
            {"order": 3, "title": "Alpine للحظات الصغيرة",
             "description": "استخدم قدرًا صغيرًا من الحالة التصريحية للقوائم والأكورديون وتقدم المتعلم.",
             "lessons": [
                 {"order": 1, "title": "الحالة عند الحافة"},
                 {"order": 2, "title": "أكورديونات وقوائم متاحة للجميع"},
                 {"order": 3, "title": "تقدم دورة يظل صادقًا"},
             ]},
            {"order": 4, "title": "اختبر وانطلق وسلّم",
             "description": "أنهِ بفحوصات تحمي المسار الحرج ونشر يمكن لفريقك فهمه.",
             "lessons": [
                 {"order": 1, "title": "اختبر المسار الحقيقي"},
                 {"order": 2, "title": "الأداء كميزة إطلاق"},
                 {"order": 3, "title": "تسليم إنتاجي هادئ"},
             ]},
        ],
    },
    "sv": {
        "title": "Skicka Django-produkter med HTMX och Alpine",
        "short_description": "En praktisk, dokument-först-kurs för att bygga snabba, innehållsdrivna produkter som team kan äga.",
        "description": (
            "<p>Bygg en användbar digital tjänst med AHA-stacken: Astro för dokument, HTMX för "
            "serverrenderade interaktioner och Alpine för små stunder av tillstånd.</p>"
            "<p>Denna praktiska väg är för grundare, produktteam och utvecklare som vill ha snabba "
            "sidor som förblir redigerbara, testbara och enkla att lämna över. Du avslutar med en "
            "fungerande kursskiva och en lanseringschecklista.</p>"
            "<h2>Vad du kommer att kunna göra</h2>"
            "<ul><li>Utforma innehåll och vägar kring riktiga kundbeslut</li>"
            "<li>Bygg sök, formulär, menyer och framsteg med progressiv förbättring</li>"
            "<li>Skydda den kritiska vägen med backend-, statiska och webbläsarkontroller</li>"
            "<li>Lämna över en underhållbar leverans istället för en skör demo</li></ul>"
        ),
        "objectives": [
            "Utforma innehåll och vägar kring riktiga kundbeslut",
            "Bygg sök, formulär, menyer och framsteg med progressiv förbättring",
            "Skydda den kritiska vägen med backend-, statiska och webbläsarkontroller",
            "Lämna över en underhållbar leverans istället för en skör demo",
        ],
        "requirements": [
            "Bekväm med Python och grundläggande Django",
            "Grundläggande HTML/CSS",
            "En terminal och en kodredigerare",
        ],
        "target_audience": [
            "Grundare och produktteam som levererar innehållsdrivna produkter",
            "Django-utvecklare som lägger till HTMX och Alpine i sin stack",
            "Utvecklare som vill ha snabba sidor som förblir redigerbara och testbara",
        ],
        "modules": [
            {"order": 1, "title": "Den dokument-första grunden",
             "description": "Börja med kundresan, färdig HTML och en redaktionell modell ditt team kan äga.",
             "lessons": [
                 {"order": 1, "title": "En sida är en produktyta"},
                 {"order": 2, "title": "Modellera innehåll kring beslut"},
                 {"order": 3, "title": "Bygg ett snabbt första svar"},
             ]},
            {"order": 2, "title": "HTMX-interaktioner utan SPA",
             "description": "Lägg till användbar interaktion medan serverresponsen förblir källan till sanning.",
             "lessons": [
                 {"order": 1, "title": "Fragment som ett UI-kontrakt"},
                 {"order": 2, "title": "Formulär, validering och CSRF"},
                 {"order": 3, "title": "Laddnings-, tomma och fel-tillstånd"},
             ]},
            {"order": 3, "title": "Alpine för de små stunderna",
             "description": "Använd en liten mängd deklarativt tillstånd för menyer, accordions och elevframsteg.",
             "lessons": [
                 {"order": 1, "title": "Tillstånd vid kanten"},
                 {"order": 2, "title": "Tillgängliga accordions och menyer"},
                 {"order": 3, "title": "Kursframsteg som förblir ärliga"},
             ]},
            {"order": 4, "title": "Testa, skicka och lämna över",
             "description": "Avsluta med kontroller som skyddar den kritiska vägen och en driftsättning ditt team kan förstå.",
             "lessons": [
                 {"order": 1, "title": "Testa den verkliga vägen"},
                 {"order": 2, "title": "Prestanda som en lanseringsfunktion"},
                 {"order": 3, "title": "En lugn produktionsöverlämning"},
             ]},
        ],
    },
    "fr": {
        "title": "Livrez des produits Django avec HTMX et Alpine",
        "short_description": "Un cours pratique, document d'abord, pour créer des produits rapides pilotés par le contenu que les équipes peuvent s'approprier.",
        "description": (
            "<p>Construisez un service numérique utile avec le stack AHA : Astro pour les documents, "
            "HTMX pour les interactions rendues côté serveur et Alpine pour les petits moments d'état.</p>"
            "<p>Ce parcours pratique s'adresse aux fondateurs, équipes produit et développeurs qui veulent "
            "des pages rapides, modifiables, testables et faciles à transmettre. Vous repartirez avec une "
            "tranche de produit fonctionnelle et une checklist de lancement.</p>"
            "<h2>Ce que vous saurez faire</h2>"
            "<ul><li>Concevoir le contenu et les parcours autour de vraies décisions client</li>"
            "<li>Construire recherche, formulaires, menus et progression avec amélioration progressive</li>"
            "<li>Protéger le chemin critique avec des vérifications backend, statiques et navigateur</li>"
            "<li>Livrer un résultat maintenable plutôt qu'une démo fragile</li></ul>"
        ),
        "objectives": [
            "Concevoir le contenu et les parcours autour de vraies décisions client",
            "Construire recherche, formulaires, menus et progression avec amélioration progressive",
            "Protéger le chemin critique avec des vérifications backend, statiques et navigateur",
            "Livrer un résultat maintenable plutôt qu'une démo fragile",
        ],
        "requirements": [
            "À l'aise avec Python et les bases de Django",
            "Notions de HTML/CSS",
            "Un terminal et un éditeur de code",
        ],
        "target_audience": [
            "Fondateurs et équipes produit qui livrent des produits pilotés par le contenu",
            "Développeurs Django ajoutant HTMX et Alpine à leur stack",
            "Développeurs qui veulent des pages rapides, restant modifiables et testables",
        ],
        "modules": [
            {"order": 1, "title": "Les fondations document d'abord",
             "description": "Commencez par le parcours client, un HTML abouti et un modèle éditorial que votre équipe peut posséder.",
             "lessons": [
                 {"order": 1, "title": "Une page est une surface produit"},
                 {"order": 2, "title": "Modéliser le contenu autour des décisions"},
                 {"order": 3, "title": "Construire une première réponse rapide"},
             ]},
            {"order": 2, "title": "Des interactions HTMX sans SPA",
             "description": "Ajoutez des interactions utiles tout en gardant la réponse serveur comme source de vérité.",
             "lessons": [
                 {"order": 1, "title": "Les fragments comme contrat d'interface"},
                 {"order": 2, "title": "Formulaires, validation et CSRF"},
                 {"order": 3, "title": "États de chargement, vides et d'erreur"},
             ]},
            {"order": 3, "title": "Alpine pour les petits moments",
             "description": "Utilisez un peu d'état déclaratif pour les menus, accordéons et la progression des apprenants.",
             "lessons": [
                 {"order": 1, "title": "L'état à la périphérie"},
                 {"order": 2, "title": "Accordéons et menus accessibles"},
                 {"order": 3, "title": "Une progression de cours honnête"},
             ]},
            {"order": 4, "title": "Tester, livrer et transmettre",
             "description": "Terminez avec des vérifications qui protègent le chemin critique et un déploiement que votre équipe comprend.",
             "lessons": [
                 {"order": 1, "title": "Tester le vrai parcours"},
                 {"order": 2, "title": "La performance comme fonctionnalité de lancement"},
                 {"order": 3, "title": "Une remise en production sereine"},
             ]},
        ],
    },
    "de": {
        "title": "Django-Produkte mit HTMX und Alpine ausliefern",
        "short_description": "Ein praktischer, dokumentenorientierter Kurs für schnelle, inhaltsgetriebene Produkte, die Teams selbst verwalten können.",
        "description": (
            "<p>Bauen Sie einen nützlichen digitalen Dienst mit dem AHA-Stack: Astro für Dokumente, HTMX "
            "für servergerenderte Interaktionen und Alpine für kleine Momente von Zustand.</p>"
            "<p>Dieser praktische Weg ist für Gründer, Produktteams und Entwickler, die schnelle Seiten "
            "wollen, die editierbar, testbar und einfach zu übergeben sind. Sie beenden den Kurs mit "
            "einem funktionierenden Produktausschnitt und einer Release-Checkliste.</p>"
            "<h2>Was Sie können werden</h2>"
            "<ul><li>Inhalte und Routen um echte Kundenentscheidungen gestalten</li>"
            "<li>Suche, Formulare, Menüs und Fortschritt mit progressiver Verbesserung bauen</li>"
            "<li>Den kritischen Pfad mit Backend-, statischen und Browser-Checks schützen</li>"
            "<li>Eine wartbare Übergabe statt einer fragilen Demo ausliefern</li></ul>"
        ),
        "objectives": [
            "Inhalte und Routen um echte Kundenentscheidungen gestalten",
            "Suche, Formulare, Menüs und Fortschritt mit progressiver Verbesserung bauen",
            "Den kritischen Pfad mit Backend-, statischen und Browser-Checks schützen",
            "Eine wartbare Übergabe statt einer fragilen Demo ausliefern",
        ],
        "requirements": [
            "Sicher mit Python und grundlegendem Django",
            "HTML/CSS-Grundlagen",
            "Ein Terminal und ein Code-Editor",
        ],
        "target_audience": [
            "Gründer und Produktteams, die inhaltsgetriebene Produkte liefern",
            "Django-Entwickler, die HTMX und Alpine in ihren Stack aufnehmen",
            "Entwickler, die schnelle Seiten wollen, die editierbar und testbar bleiben",
        ],
        "modules": [
            {"order": 1, "title": "Das dokumentenorientierte Fundament",
             "description": "Beginnen Sie mit der Customer Journey, fertigem HTML und einem redaktionellen Modell, das Ihr Team besitzen kann.",
             "lessons": [
                 {"order": 1, "title": "Eine Seite ist eine Produktoberfläche"},
                 {"order": 2, "title": "Inhalte rund um Entscheidungen modellieren"},
                 {"order": 3, "title": "Eine schnelle erste Antwort bauen"},
             ]},
            {"order": 2, "title": "HTMX-Interaktionen ohne SPA",
             "description": "Fügen Sie nützliche Interaktion hinzu und behalten die Serverantwort als Quelle der Wahrheit.",
             "lessons": [
                 {"order": 1, "title": "Fragmente als UI-Vertrag"},
                 {"order": 2, "title": "Formulare, Validierung und CSRF"},
                 {"order": 3, "title": "Lade-, Leer- und Fehlerzustände"},
             ]},
            {"order": 3, "title": "Alpine für die kleinen Momente",
             "description": "Verwenden Sie kleinen deklarativen Zustand für Menüs, Akkordeons und Lernfortschritt.",
             "lessons": [
                 {"order": 1, "title": "Zustand am Rand"},
                 {"order": 2, "title": "Barrierefreie Akkordeons und Menüs"},
                 {"order": 3, "title": "Ehrlicher Kursfortschritt"},
             ]},
            {"order": 4, "title": "Testen, ausliefern und übergeben",
             "description": "Beenden Sie mit Checks, die den kritischen Pfad schützen, und einem Deployment, das Ihr Team versteht.",
             "lessons": [
                 {"order": 1, "title": "Den echten Pfad testen"},
                 {"order": 2, "title": "Performance als Launch-Funktion"},
                 {"order": 3, "title": "Eine ruhige Produktionsübergabe"},
             ]},
        ],
    },
    "es": {
        "title": "Lanza productos Django con HTMX y Alpine",
        "short_description": "Un curso práctico, primero el documento, para construir productos rápidos basados en contenido que los equipos puedan asumir.",
        "description": (
            "<p>Construye un servicio digital útil con el stack AHA: Astro para documentos, HTMX para "
            "interacciones renderizadas en servidor y Alpine para pequeños momentos de estado.</p>"
            "<p>Este camino práctico es para fundadores, equipos de producto y desarrolladores que quieren "
            "páginas rápidas, editables, probables y fáciles de entregar. Terminarás con una porción de "
            "producto funcional y una lista de verificación de lanzamiento.</p>"
            "<h2>Lo que podrás hacer</h2>"
            "<ul><li>Diseñar contenido y rutas alrededor de decisiones reales de clientes</li>"
            "<li>Construir búsqueda, formularios, menús y progreso con mejora progresiva</li>"
            "<li>Proteger la ruta crítica con verificaciones de backend, estáticas y de navegador</li>"
            "<li>Entregar un resultado mantenible en lugar de una demo frágil</li></ul>"
        ),
        "objectives": [
            "Diseñar contenido y rutas alrededor de decisiones reales de clientes",
            "Construir búsqueda, formularios, menús y progreso con mejora progresiva",
            "Proteger la ruta crítica con verificaciones de backend, estáticas y de navegador",
            "Entregar un resultado mantenible en lugar de una demo frágil",
        ],
        "requirements": [
            "Comodidad con Python y Django básico",
            "Conceptos básicos de HTML/CSS",
            "Una terminal y un editor de código",
        ],
        "target_audience": [
            "Fundadores y equipos de producto que lanzan productos basados en contenido",
            "Desarrolladores Django que añaden HTMX y Alpine a su stack",
            "Desarrolladores que quieren páginas rápidas que sigan siendo editables y probables",
        ],
        "modules": [
            {"order": 1, "title": "La base centrada en el documento",
             "description": "Empieza con el recorrido del cliente, HTML terminado y un modelo editorial que tu equipo pueda asumir.",
             "lessons": [
                 {"order": 1, "title": "Una página es una superficie de producto"},
                 {"order": 2, "title": "Modela el contenido alrededor de decisiones"},
                 {"order": 3, "title": "Construye una primera respuesta rápida"},
             ]},
            {"order": 2, "title": "Interacciones HTMX sin SPA",
             "description": "Añade interacción útil manteniendo la respuesta del servidor como fuente de verdad.",
             "lessons": [
                 {"order": 1, "title": "Fragments como contrato de UI"},
                 {"order": 2, "title": "Formularios, validación y CSRF"},
                 {"order": 3, "title": "Estados de carga, vacíos y de error"},
             ]},
            {"order": 3, "title": "Alpine para los pequeños momentos",
             "description": "Usa poco estado declarativo para menús, acordeones y el progreso del alumno.",
             "lessons": [
                 {"order": 1, "title": "Estado en el borde"},
                 {"order": 2, "title": "Acordeones y menús accesibles"},
                 {"order": 3, "title": "Progreso del curso honesto"},
             ]},
            {"order": 4, "title": "Prueba, lanza y entrega",
             "description": "Termina con verificaciones que protejan la ruta crítica y un despliegue que tu equipo entienda.",
             "lessons": [
                 {"order": 1, "title": "Prueba la ruta real"},
                 {"order": 2, "title": "Rendimiento como función de lanzamiento"},
                 {"order": 3, "title": "Una entrega de producción tranquila"},
             ]},
        ],
    },
    "pt": {
        "title": "Envie produtos Django com HTMX e Alpine",
        "short_description": "Um curso prático, documento em primeiro lugar, para criar produtos rápidos e orientados a conteúdo que as equipes possam assumir.",
        "description": (
            "<p>Construa um serviço digital útil com a stack AHA: Astro para documentos, HTMX para "
            "interações renderizadas no servidor e Alpine para pequenos momentos de estado.</p>"
            "<p>Este caminho prático é para fundadores, equipes de produto e desenvolvedores que querem "
            "páginas rápidas, editáveis, testáveis e fáceis de entregar. Você terminará com uma fatia "
            "de produto funcional e um checklist de lançamento.</p>"
            "<h2>O que você será capaz de fazer</h2>"
            "<ul><li>Projetar conteúdo e rotas em torno de decisões reais de clientes</li>"
            "<li>Construir busca, formulários, menus e progresso com aprimoramento progressivo</li>"
            "<li>Proteger o caminho crítico com verificações de backend, estáticas e do navegador</li>"
            "<li>Entregar um resultado sustentável em vez de uma demo frágil</li></ul>"
        ),
        "objectives": [
            "Projetar conteúdo e rotas em torno de decisões reais de clientes",
            "Construir busca, formulários, menus e progresso com aprimoramento progressivo",
            "Proteger o caminho crítico com verificações de backend, estáticas e do navegador",
            "Entregar um resultado sustentável em vez de uma demo frágil",
        ],
        "requirements": [
            "Confortável com Python e Django básico",
            "Noções básicas de HTML/CSS",
            "Um terminal e um editor de código",
        ],
        "target_audience": [
            "Fundadores e equipes de produto que entregam produtos orientados a conteúdo",
            "Desenvolvedores Django adicionando HTMX e Alpine ao seu stack",
            "Desenvolvedores que querem páginas rápidas, ainda editáveis e testáveis",
        ],
        "modules": [
            {"order": 1, "title": "A base centrada no documento",
             "description": "Comece pela jornada do cliente, HTML pronto e um modelo editorial que sua equipe possa assumir.",
             "lessons": [
                 {"order": 1, "title": "Uma página é uma superfície de produto"},
                 {"order": 2, "title": "Modelar conteúdo em torno de decisões"},
                 {"order": 3, "title": "Construa uma primeira resposta rápida"},
             ]},
            {"order": 2, "title": "Interações HTMX sem SPA",
             "description": "Adicione interação útil mantendo a resposta do servidor como fonte da verdade.",
             "lessons": [
                 {"order": 1, "title": "Fragments como contrato de UI"},
                 {"order": 2, "title": "Formulários, validação e CSRF"},
                 {"order": 3, "title": "Estados de carregamento, vazio e erro"},
             ]},
            {"order": 3, "title": "Alpine para os pequenos momentos",
             "description": "Use pouco estado declarativo para menus, acordeões e progresso do aluno.",
             "lessons": [
                 {"order": 1, "title": "Estado na borda"},
                 {"order": 2, "title": "Acordeões e menus acessíveis"},
                 {"order": 3, "title": "Progresso do curso honesto"},
             ]},
            {"order": 4, "title": "Teste, envie e entregue",
             "description": "Termine com verificações que protejam o caminho crítico e uma implantação que sua equipe entenda.",
             "lessons": [
                 {"order": 1, "title": "Teste o caminho real"},
                 {"order": 2, "title": "Desempenho como recurso de lançamento"},
                 {"order": 3, "title": "Uma entrega de produção tranquila"},
             ]},
        ],
    },
}


class Command(BaseCommand):
    help = "Seed the public Structa Cloud course catalog."

    def handle(self, *args, **options):
        User = get_user_model()
        instructor, created = User.objects.get_or_create(
            username="mammhoud",
            defaults={
                "email": "mammhoud@structa.cloud",
                "first_name": "Mahmoud",
                "last_name": "Ezzat",
            },
        )
        if created:
            instructor.set_unusable_password()
            instructor.save(update_fields=["password"])

        description = format_html(
            "<p>Build a useful digital service with the AHA stack: Astro for documents, "
            "HTMX for server-rendered interactions, and Alpine for small moments of state.</p>"
            "<p>This practical path is for founders, product teams, and developers who want "
            "fast pages that remain editable, testable, and easy to hand over. You will "
            "finish with a working course-sized product slice and a release checklist.</p>"
            "<h2>What you will be able to do</h2>"
            "<ul><li>Design content and routes around real customer decisions</li>"
            "<li>Build search, forms, menus, and progress with progressive enhancement</li>"
            "<li>Protect the critical path with backend, static, and browser checks</li>"
            "<li>Ship a maintainable handoff instead of a fragile demo</li></ul>"
        )
        course, course_created = Course.objects.get_or_create(
            slug=COURSE_SLUG,
            defaults={
                "title": "Ship Django Products with HTMX and Alpine",
                "short_description": "A practical, document-first course for building fast, content-driven products that teams can own.",
                "description": description,
                "instructor": instructor,
                "language": "en",
                "difficulty": "intermediate",
                "duration_hours": "6.5",
                "price": "0.00",
                "is_published": True,
                "is_featured": True,
                "has_certificate": True,
                "youtube_channel_url": YOUTUBE_CHANNEL_URL,
                "youtube_channel_name": "Mahmoud Ezzat · @mammhoud",
            },
        )
        changed = []
        if course.instructor_id != instructor.pk:
            course.instructor = instructor
            changed.append("instructor")
        if not course.youtube_channel_url:
            course.youtube_channel_url = YOUTUBE_CHANNEL_URL
            changed.append("youtube_channel_url")
        if not course.youtube_channel_name:
            course.youtube_channel_name = "Mahmoud Ezzat · @mammhoud"
            changed.append("youtube_channel_name")
        if not course.is_published:
            course.is_published = True
            changed.append("is_published")
        if not course.is_featured:
            course.is_featured = True
            changed.append("is_featured")
        if not course.has_certificate:
            course.has_certificate = True
            changed.append("has_certificate")
        if changed:
            course.save(update_fields=[*changed, "updated_at"])

        # ── Learning metadata (Precis-aligned fields, backfilled when empty) ──
        metadata_changed = []
        if not course.objectives:
            course.objectives = OBJECTIVES
            metadata_changed.append("objectives")
        if not course.requirements:
            course.requirements = REQUIREMENTS
            metadata_changed.append("requirements")
        if not course.target_audience:
            course.target_audience = TARGET_AUDIENCE
            metadata_changed.append("target_audience")
        if metadata_changed:
            course.save(update_fields=[*metadata_changed, "updated_at"])

        specialization, _ = Specialization.objects.get_or_create(
            slug=SPECIALIZATION_SLUG,
            defaults={
                "title": "Practical Web Development",
                "description": "Document-first, server-rendered product building with the AHA stack.",
                "order": 1,
            },
        )
        course.specializations.add(specialization)
        for tag_name in ("Django", "HTMX", "Alpine.js"):
            tag, _ = CourseTag.objects.get_or_create(name=tag_name)
            course.tags.add(tag)

        for module_data in MODULES:
            module, _ = Module.objects.get_or_create(
                course=course,
                order=module_data["order"],
                defaults={
                    "title": module_data["title"],
                    "description": module_data["description"],
                },
            )
            for lesson_order, lesson_data in enumerate(module_data["lessons"], start=1):
                lesson, _ = Lesson.objects.get_or_create(
                    module=module,
                    order=lesson_order,
                    defaults={
                        "title": lesson_data[0],
                        "description": lesson_data[1],
                        "duration_minutes": lesson_data[2],
                        "is_preview": lesson_data[3],
                        "is_active": True,
                    },
                )
                if lesson_order == 1:
                    # Idempotent sample resources on the first lesson of each
                    # module so the curriculum detail exposes downloads.
                    LessonResource.objects.get_or_create(
                        lesson=lesson,
                        title=f"{module_data['title']} — slides",
                        defaults={
                            "description": "Lesson slides for offline review.",
                            "resource_type": "slides",
                            "is_free": lesson.is_preview,
                        },
                    )

        # ── CourseTranslation overlays (seeded once per language) ────────────
        from apps.learning.models import CourseTranslation

        translated = 0
        for lang_code, overlay in COURSE_TRANSLATIONS.items():
            content = {
                "modules": {
                    str(mod["order"]): {
                        "title": mod["title"],
                        "description": mod["description"],
                        "lessons": {
                            str(lesson["order"]): {"title": lesson["title"]}
                            for lesson in mod["lessons"]
                        },
                    }
                    for mod in overlay["modules"]
                }
            }
            _, created = CourseTranslation.objects.get_or_create(
                course=course,
                language=lang_code,
                defaults={
                    "title": overlay["title"],
                    "short_description": overlay["short_description"],
                    "description": overlay["description"],
                    "objectives": "\n".join(overlay["objectives"]),
                    "requirements": "\n".join(overlay["requirements"]),
                    "target_audience": "\n".join(overlay["target_audience"]),
                    "content": content,
                },
            )
            if created:
                translated += 1

        # ── Published review (reviews publishing workflow, Precis parity) ──
        Review.objects.get_or_create(
            course=course,
            user=instructor,
            defaults={
                "rating": 5,
                "body": (
                    "The document-first approach made the whole path practical — "
                    "finished HTML, real HTMX interactions, and a handoff the team "
                    "could actually own."
                ),
                "is_published": True,
            },
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"{'Created' if course_created else 'Found'} course '{course.slug}' "
                f"with {course.modules.count()} modules and channel {YOUTUBE_CHANNEL_URL}"
            )
        )
        self.stdout.write(
            self.style.SUCCESS(f"Course translations: {translated} language overlays seeded")
        )
