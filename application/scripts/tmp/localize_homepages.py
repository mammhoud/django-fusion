#!/usr/bin/env python3
"""Localize the Precis homepage hero/vision StreamField content per locale.

Fixes the P0 locale-audit gap: the pages.homepage ``head`` (slider) and
``summary`` (about) StreamFields are English-only for every locale. This
script rewrites the visible strings on the non-English homepage records while
preserving block ids, image references, and HTML structure.

Usage: python3 localize_homepages.py [--write]
"""
import json
import sys
from pathlib import Path

FIXTURE = Path("projects/precis/precis-lms/backend/assets/fixtures/dump-data.json")

# Locale code -> homepage page PK (mirrors wagtailcore.page locales in the dump)
LOCALE_PK = {"ar": 8, "de": 13, "es": 18, "fr": 23, "pt-br": 28}

TRANSLATIONS = {
    "ar": {
        "slide1_title": "تمكين الجيل القادم من قادة الرعاية الصحية",
        "slide1_subtitle": "المركز العالمي للذكاء الاصطناعي الطبي والابتكار الصحي",
        "slide2_title": "الترابط بين المناخ والصحة",
        "slide2_subtitle": "نمذجة بالذكاء الاصطناعي لتأثير البيئة على صحة المجتمع",
        "main_title": "مركز سي تي سي",
        "welcome_text": "مرحباً بكم في مركز الأبحاث",
        "description": "نحن مركز تميز عالمي معترف به يعزز الصحة والرفاهية من خلال الابتكار متعدد التخصصات والأبحاث عالية التأثير. ومن خلال ريادتنا للتقنيات والأنظمة الذكية، نمكّن المجتمع ونقوّي نتائج الرعاية الصحية ونساهم بنشاط في أهداف التنمية المستدامة للأمم المتحدة.",
        "items": [
            ("ركيزة الإتقان", "تعميق الخبرة في الذكاء الاصطناعي الطبي والصحة الرقمية"),
            ("ركيزة القدرات", "تزويد المتعلمين بكفاءات عملية مواكبة للمستقبل"),
            ("ركيزة الأثر", "تحسين نتائج الرعاية الصحية عالمياً عبر المعرفة والابتكار"),
        ],
        "vision_title": "رؤيتنا",
        "vision_subtitle": "ما نقوم به",
        "vision_description": "أن نصبح المنصة الرائدة عالمياً في تعليم وأبحاث الذكاء الاصطناعي الطبي — معترفاً بها للتميز والابتكار والأثر القابل للقياس على أنظمة الرعاية الصحية العالمية.",
        "vision_methods": ["البحث متعدد التخصصات في الذكاء الاصطناعي", "تحليلات البيانات الطبية", "نُجري أبحاثاً رائدة"],
    },
    "fr": {
        "slide1_title": "Former la prochaine génération de leaders de la santé",
        "slide1_subtitle": "Centre mondial pour l'IA médicale et l'innovation en santé",
        "slide2_title": "Nexus climat-santé",
        "slide2_subtitle": "Modélisation par IA de l'impact de l'environnement sur la santé des communautés",
        "main_title": "CTC Hub",
        "welcome_text": "Bienvenue au Hub de recherche",
        "description": "Nous sommes un centre d'excellence mondialement reconnu qui fait progresser la santé et le bien-être grâce à l'innovation interdisciplinaire et à la recherche à fort impact. En pionnier des technologies et des systèmes intelligents, nous renforçons la société, améliorons les résultats de soins et contribuons activement aux Objectifs de développement durable des Nations Unies.",
        "items": [
            ("Le pilier de la maîtrise", "Développer l'expertise en IA médicale et en santé numérique"),
            ("Le pilier des capacités", "Doter les apprenants de compétences pratiques et pérennes"),
            ("Le pilier de l'impact", "Améliorer les résultats de santé mondiaux par la connaissance et l'innovation"),
        ],
        "vision_title": "Notre vision",
        "vision_subtitle": "Ce que nous faisons",
        "vision_description": "Devenir la plateforme mondiale de référence pour l'éducation et la recherche en IA médicale — reconnue pour l'excellence, l'innovation et un impact mesurable sur les systèmes de santé mondiaux.",
        "vision_methods": ["la recherche interdisciplinaire en IA", "l'analyse de données médicales", "Nous menons des recherches de pointe"],
    },
    "de": {
        "slide1_title": "Die nächste Generation von Führungskräften im Gesundheitswesen stärken",
        "slide1_subtitle": "Globales Zentrum für medizinische KI und Gesundheitsinnovation",
        "slide2_title": "Klima-Gesundheit-Nexus",
        "slide2_subtitle": "KI-Modellierung der Auswirkungen der Umwelt auf die Gesundheit von Gemeinschaften",
        "main_title": "CTC Hub",
        "welcome_text": "Willkommen im Research Hub",
        "description": "Wir sind ein weltweit anerkanntes Exzellenzzentrum, das Gesundheit und Wohlbefinden durch interdisziplinäre Innovation und wirkungsvolle Forschung voranbringt. Mit intelligenten Technologien und Systemen stärken wir die Gesellschaft, verbessern Ergebnisse im Gesundheitswesen und tragen aktiv zu den Zielen für nachhaltige Entwicklung der Vereinten Nationen bei.",
        "items": [
            ("Die Meisterschaftssäule", "Fachwissen in medizinischer KI und digitaler Gesundheit ausbauen"),
            ("Die Fähigkeitssäule", "Lernende mit praktischen, zukunftsfähigen Kompetenzen ausstatten"),
            ("Die Wirkungssäule", "Globale Gesundheitsergebnisse durch Wissen und Innovation verbessern"),
        ],
        "vision_title": "Unsere Vision",
        "vision_subtitle": "Was wir tun",
        "vision_description": "Zur weltweit führenden Plattform für medizinische KI-Ausbildung und -Forschung zu werden — anerkannt für Exzellenz, Innovation und messbare Auswirkungen auf globale Gesundheitssysteme.",
        "vision_methods": ["interdisziplinäre KI-Forschung", "medizinische Datenanalyse", "Wir betreiben Spitzenforschung"],
    },
    "es": {
        "slide1_title": "Potenciando la próxima generación de líderes sanitarios",
        "slide1_subtitle": "Centro Global de IA Médica e Innovación en Salud",
        "slide2_title": "Nexo clima-salud",
        "slide2_subtitle": "Modelado con IA del impacto del medio ambiente en la salud comunitaria",
        "main_title": "CTC Hub",
        "welcome_text": "Bienvenido al Centro de Investigación",
        "description": "Somos un centro de excelencia reconocido mundialmente que impulsa la salud y el bienestar a través de la innovación interdisciplinaria y la investigación de alto impacto. Al liderar tecnologías y sistemas inteligentes, empoderamos a la sociedad, fortalecemos los resultados sanitarios y contribuimos activamente a los Objetivos de Desarrollo Sostenible de las Naciones Unidas.",
        "items": [
            ("El pilar del dominio", "Avanzar la experiencia en IA médica y salud digital"),
            ("El pilar de las capacidades", "Dotar a los estudiantes de competencias prácticas y preparadas para el futuro"),
            ("El pilar del impacto", "Mejorar los resultados sanitarios mundiales a través del conocimiento y la innovación"),
        ],
        "vision_title": "Nuestra visión",
        "vision_subtitle": "Lo que hacemos",
        "vision_description": "Convertirnos en la plataforma líder mundial en educación e investigación de IA médica — reconocida por la excelencia, la innovación y un impacto medible en los sistemas de salud globales.",
        "vision_methods": ["investigación interdisciplinaria en IA", "análisis de datos médicos", "Realizamos investigación de vanguardia"],
    },
    "pt-br": {
        "slide1_title": "Capacitando a próxima geração de líderes da saúde",
        "slide1_subtitle": "Centro Global de IA Médica e Inovação em Saúde",
        "slide2_title": "Nexo clima-saúde",
        "slide2_subtitle": "Modelagem por IA do impacto do ambiente na saúde comunitária",
        "main_title": "CTC Hub",
        "welcome_text": "Bem-vindo ao Centro de Pesquisa",
        "description": "Somos um centro de excelência reconhecido mundialmente que promove saúde e bem-estar por meio de inovação interdisciplinar e pesquisa de alto impacto. Ao liderar tecnologias e sistemas inteligentes, empoderamos a sociedade, fortalecemos os resultados de saúde e contribuímos ativamente para os Objetivos de Desenvolvimento Sustentável das Nações Unidas.",
        "items": [
            ("O pilar do domínio", "Avançar a especialização em IA médica e saúde digital"),
            ("O pilar das capacidades", "Equipar alunos com competências práticas e preparadas para o futuro"),
            ("O pilar do impacto", "Melhorar os resultados globais de saúde por meio do conhecimento e da inovação"),
        ],
        "vision_title": "Nossa visão",
        "vision_subtitle": "O que fazemos",
        "vision_description": "Tornar-se a plataforma líder mundial em educação e pesquisa de IA médica — reconhecida pela excelência, inovação e impacto mensurável nos sistemas globais de saúde.",
        "vision_methods": ["pesquisa interdisciplinar em IA", "análise de dados médicos", "Conduzimos pesquisa de ponta"],
    },
}


def localize_head(value, tr):
    """Translate slider slides inside the ``head`` StreamField value."""
    for block in value:
        if not isinstance(block, dict) or block.get("type") != "slider":
            continue
        titles = [tr["slide1_title"], tr["slide2_title"]]
        subtitles = [tr["slide1_subtitle"], tr["slide2_subtitle"]]
        for slide in block.get("value", []):
            if not isinstance(slide, dict):
                continue
            v = slide.get("value")
            if not isinstance(v, dict):
                continue
            if "title" in v and v.get("title") and titles:
                v["title"] = titles.pop(0)
            if "subtitle" in v and v.get("subtitle") and subtitles:
                v["subtitle"] = subtitles.pop(0)


def localize_summary(value, tr):
    """Translate the about block inside the ``summary`` StreamField value."""
    for block in value:
        if not isinstance(block, dict) or block.get("type") != "about":
            continue
        v = block.get("value")
        if not isinstance(v, dict):
            continue
        v["main_title"] = tr["main_title"]
        v["welcome_text"] = tr["welcome_text"]
        desc = v.get("description", "")
        if isinstance(desc, str) and desc.startswith("<p"):
            v["description"] = f"<p>{tr['description']}</p>"
        else:
            v["description"] = tr["description"]
        for i, item in enumerate(v.get("service_items", [])):
            if not isinstance(item, dict):
                continue
            item_v = item.get("value")
            if not isinstance(item_v, dict):
                continue
            title, description = tr["items"][i % len(tr["items"])]
            item_v["title"] = title
            item_v["description"] = description


def localize_cta(value, tr):
    """Translate the why_choose_section block inside the ``CTA`` StreamField."""
    for block in value:
        if not isinstance(block, dict) or block.get("type") != "why_choose_section":
            continue
        v = block.get("value")
        if not isinstance(v, dict):
            continue
        v["title"] = tr["vision_title"]
        v["subtitle"] = tr["vision_subtitle"]
        v["description"] = tr["vision_description"]
        for i, method in enumerate(v.get("methods", [])):
            if not isinstance(method, dict):
                continue
            method_v = method.get("value")
            if isinstance(method_v, str):
                method["value"] = tr["vision_methods"][i % len(tr["vision_methods"])]


def main():
    write = "--write" in sys.argv
    with open(FIXTURE) as f:
        data = json.load(f)

    changed = 0
    for entry in data:
        if entry.get("model") != "pages.homepage":
            continue
        pk = entry.get("pk")
        locale = next((code for code, p in LOCALE_PK.items() if p == pk), None)
        if locale is None:
            continue
        tr = TRANSLATIONS[locale]
        fields = entry.setdefault("fields", {})
        for field_name, localizer in (("head", localize_head), ("summary", localize_summary), ("CTA", localize_cta)):
            raw = fields.get(field_name)
            if not raw:
                continue
            value = json.loads(raw)
            localizer(value, tr)
            fields[field_name] = json.dumps(value, ensure_ascii=False)
        changed += 1

    if not write:
        print(f"Dry run: {changed} homepage record(s) would be localized.")
        for code, pk in LOCALE_PK.items():
            print(f"  - {code} (pk {pk})")
        return

    with open(FIXTURE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Wrote {changed} localized homepage record(s) to {FIXTURE}")


if __name__ == "__main__":
    main()
