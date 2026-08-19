"""Seed complete medical-research course catalog with translations, tags, modules, and lessons.

Usage:
    python manage.py seed_courses_i18n            # idempotent full seed
    python manage.py seed_courses_i18n --clear    # wipe and re-seed
    python manage.py seed_courses_i18n --tags-only
    python manage.py seed_courses_i18n --lang fr  # seed one language only

Creates:
  - Tags, Specializations, Categories (idempotent)
  - 14 EN courses with tags/specs/modules/lessons assigned
  - Translated variants for fr/de/es/ar/pt-br/sv
"""

from __future__ import annotations

import logging
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils.text import slugify

logger = logging.getLogger(__name__)

# ── Master course data ───────────────────────────────────────────────────────
# Each entry: (en_title, difficulty, duration_h, has_cert, price, tags[], specs[], modules[])
# Module: (title, lessons[])
# Lesson: (title, duration_min, is_preview)

COURSES_EN = [
    {
        "slug": "clinical-trial-design-protocol-development",
        "title": "Clinical Trial Design & Protocol Development",
        "short_description": "Master the full lifecycle of clinical trial design: ICH E6, protocol writing, randomisation, blinding, statistical planning, and regulatory submission.",
        "description": "This course takes you from research question to submission-ready protocol. You will learn ICH E6(R2) GCP requirements, adaptive and platform trial designs, sample-size estimation, randomisation strategies, and how to structure a protocol document that satisfies FDA, EMA, and WHO reviewers.",
        "objectives": "Write an ICH-compliant clinical trial protocol\nSelect appropriate randomisation and blinding strategies\nEstimate sample sizes for superiority and non-inferiority trials\nNavigate IRB/IEC submission requirements\nDesign safety monitoring frameworks",
        "requirements": "Basic epidemiology or clinical research background\nFamiliarity with statistical concepts (mean, variance, p-value)",
        "target_audience": "Clinical research coordinators\nMedical writers entering clinical research\nPhysicians designing investigator-initiated trials",
        "difficulty": "intermediate",
        "duration": 18,
        "price": "149.00",
        "is_featured": True,
        "has_certificate": True,
        "tags": ["Clinical Research", "Research Ethics", "Evidence-Based Medicine"],
        "specializations": ["Clinical Research"],
        "modules": [
            ("Foundations of Clinical Trial Design", [
                ("Overview of Clinical Research Phases", 22, True),
                ("ICH E6(R2) GCP: Key Requirements", 28, False),
                ("Research Question and PICO Framework", 18, False),
            ]),
            ("Protocol Structure & Writing", [
                ("Protocol Sections: Background & Objectives", 25, False),
                ("Eligibility Criteria and Recruitment", 20, False),
                ("Endpoints: Primary, Secondary, Exploratory", 22, False),
            ]),
            ("Randomisation & Blinding", [
                ("Simple, Block, and Stratified Randomisation", 24, False),
                ("Allocation Concealment and Blinding Methods", 18, False),
            ]),
            ("Statistical Planning", [
                ("Sample Size for Superiority Trials", 30, False),
                ("Non-Inferiority and Equivalence Designs", 26, False),
                ("Adaptive Design Basics", 20, False),
            ]),
            ("Regulatory Submission", [
                ("IRB/IEC Submissions", 20, False),
                ("IND/CTA Filing Overview", 18, False),
                ("DSMB and Safety Monitoring Plans", 16, False),
            ]),
        ],
    },
    {
        "slug": "systematic-review-meta-analysis",
        "title": "Systematic Review & Meta-Analysis",
        "short_description": "PRISMA-compliant systematic reviews and pooled effect estimates with meta-analysis. From protocol registration to GRADE certainty of evidence.",
        "description": "A comprehensive guide to designing, conducting, and reporting systematic reviews. Covers database searching, study selection, risk-of-bias assessment (RoB 2, ROBINS-I), fixed and random-effects meta-analysis, heterogeneity analysis, publication bias, and GRADE evidence profiling.",
        "objectives": "Register a systematic review protocol on PROSPERO\nConduct comprehensive database searches in MEDLINE and Embase\nApply RoB 2 and ROBINS-I risk-of-bias tools\nPool effect sizes using fixed- and random-effects models\nInterpret heterogeneity (I², τ²) and publication bias\nRate certainty of evidence with GRADE",
        "requirements": "Understanding of basic research methodology\nFamiliarity with medical literature",
        "target_audience": "Clinical researchers\nEvidence synthesis teams\nHealth technology assessment analysts",
        "difficulty": "advanced",
        "duration": 22,
        "price": "179.00",
        "is_featured": True,
        "has_certificate": True,
        "tags": ["Systematic Review", "Evidence-Based Medicine", "Biostatistics"],
        "specializations": ["Evidence Synthesis"],
        "modules": [
            ("Planning Your Systematic Review", [
                ("PICO and Review Question Formulation", 20, True),
                ("PROSPERO Registration", 15, False),
                ("Inclusion and Exclusion Criteria", 18, False),
            ]),
            ("Database Searching", [
                ("MEDLINE and Embase Search Strategy", 30, False),
                ("Grey Literature and Trial Registries", 18, False),
                ("Citation Management with Zotero/Mendeley", 15, False),
            ]),
            ("Study Selection & Data Extraction", [
                ("Title/Abstract and Full-Text Screening", 22, False),
                ("Data Extraction Templates", 20, False),
                ("Risk-of-Bias Assessment: RoB 2", 28, False),
                ("Risk-of-Bias Assessment: ROBINS-I", 25, False),
            ]),
            ("Meta-Analysis", [
                ("Fixed-Effects vs Random-Effects Models", 35, False),
                ("Heterogeneity: I² and τ²", 28, False),
                ("Subgroup and Sensitivity Analyses", 22, False),
                ("Funnel Plots and Publication Bias Tests", 24, False),
            ]),
            ("Reporting & GRADE", [
                ("PRISMA 2020 Reporting Checklist", 20, False),
                ("Summary of Findings Tables and GRADE", 28, False),
            ]),
        ],
    },
    {
        "slug": "medical-ai-clinical-applications",
        "title": "Medical AI & Clinical Applications",
        "short_description": "From ML fundamentals to FDA AI/ML action plan. Learn model validation, bias detection, clinical deployment, and responsible AI governance in healthcare.",
        "description": "Understand how machine learning is transforming clinical workflows—imaging analysis, EHR prediction models, NLP for clinical notes, and decision support. Covers supervised/unsupervised learning, model validation, fairness audits, FDA SaMD regulation, and responsible AI principles for healthcare.",
        "objectives": "Explain core ML algorithms used in medical AI\nDesign and interpret model validation studies\nIdentify and mitigate algorithmic bias in clinical datasets\nApply FDA AI/ML-Based SaMD regulatory framework\nEvaluate AI tools for clinical decision support deployment",
        "requirements": "Basic data literacy\nFamiliarity with clinical workflows helpful but not required",
        "target_audience": "Clinicians evaluating AI tools\nClinical informaticists\nHealth data scientists",
        "difficulty": "intermediate",
        "duration": 16,
        "price": "159.00",
        "is_featured": True,
        "has_certificate": True,
        "tags": ["Medical AI", "Machine Learning", "Data Science"],
        "specializations": ["Medical AI & Digital Health"],
        "modules": [
            ("ML Foundations for Clinicians", [
                ("Supervised vs Unsupervised Learning", 25, True),
                ("Classification, Regression, Clustering", 22, False),
                ("Neural Networks and Deep Learning Basics", 20, False),
            ]),
            ("Medical Imaging AI", [
                ("Convolutional Neural Networks for Imaging", 28, False),
                ("Radiology and Pathology AI Applications", 22, False),
                ("Validation Studies for Imaging Models", 24, False),
            ]),
            ("NLP & EHR Applications", [
                ("Clinical NLP: Named Entity Recognition", 22, False),
                ("EHR Prediction Models", 20, False),
                ("Chatbots and Clinical Documentation AI", 18, False),
            ]),
            ("Model Validation & Fairness", [
                ("Internal and External Validation", 28, False),
                ("Calibration Curves and Decision Curves", 22, False),
                ("Algorithmic Bias: Detection and Mitigation", 30, False),
            ]),
            ("Regulation & Deployment", [
                ("FDA AI/ML SaMD Regulatory Framework", 25, False),
                ("Clinical AI Governance Frameworks", 20, False),
            ]),
        ],
    },
    {
        "slug": "scientific-writing-medical-manuscripts",
        "title": "Scientific Writing for Medical Manuscripts",
        "short_description": "IMRAD structure, AMA style, peer review response, and how to write each section of a clinical or basic-science manuscript that editors accept.",
        "description": "Every section of a medical manuscript—title, abstract, introduction, methods, results, discussion, and references—has conventions that reviewers test. This course teaches the IMRAD structure, AMA citation style, statistical reporting standards, author-response letters, and strategies for submitting to high-impact journals.",
        "objectives": "Structure a manuscript using IMRAD conventions\nWrite a structured abstract for original research\nReport statistics following AMA and CONSORT guidelines\nPrepare a compelling cover letter and author-response\nNavigate peer review and revision cycles",
        "requirements": "Completion of at least one research project\nBasic academic writing experience",
        "target_audience": "Physicians and researchers writing their first paper\nMedical writers supporting clinical teams\nPostgraduate students preparing manuscripts",
        "difficulty": "beginner",
        "duration": 12,
        "price": "99.00",
        "is_featured": False,
        "has_certificate": True,
        "tags": ["Scientific Writing", "Clinical Research"],
        "specializations": ["Scientific Communication"],
        "modules": [
            ("Manuscript Fundamentals", [
                ("IMRAD: The Structure of a Research Paper", 20, True),
                ("Choosing the Right Journal", 15, False),
                ("Understanding Author Roles (ICMJE)", 12, False),
            ]),
            ("Writing Each Section", [
                ("Title and Abstract Writing", 22, False),
                ("Introduction: Background to Gap to Aim", 18, False),
                ("Methods: Reproducibility and Transparency", 25, False),
                ("Results: Tables, Figures, Statistical Reporting", 28, False),
                ("Discussion: Interpretation and Limitations", 22, False),
            ]),
            ("Submission & Peer Review", [
                ("Cover Letters That Get Read", 15, False),
                ("Responding to Reviewer Comments", 20, False),
                ("Handling Rejection and Revision", 15, False),
            ]),
        ],
    },
    {
        "slug": "research-ethics-integrity",
        "title": "Research Ethics & Integrity",
        "short_description": "Informed consent, Helsinki Declaration, IRB processes, research misconduct, authorship disputes, and building a culture of integrity.",
        "description": "Clinical and biomedical research depends on public trust. This course covers the Helsinki Declaration, Belmont Report, informed consent requirements, vulnerable population protections, IRB operations, responsible conduct of research (RCR), authorship guidelines, and how to investigate and prevent research misconduct.",
        "objectives": "Apply Helsinki Declaration principles to study design\nDraft compliant informed consent documents\nNavigate IRB expedited vs full-board review\nIdentify and address research misconduct\nManage authorship and contributorship correctly",
        "requirements": "No prior ethics training required",
        "target_audience": "All clinical and biomedical researchers\nStudents entering graduate research programs\nInstitutional review board members",
        "difficulty": "beginner",
        "duration": 10,
        "price": "79.00",
        "is_featured": False,
        "has_certificate": True,
        "tags": ["Research Ethics", "Clinical Research"],
        "specializations": ["Research Ethics & Integrity"],
        "modules": [
            ("Foundations of Research Ethics", [
                ("History: Nuremberg to Belmont", 20, True),
                ("Helsinki Declaration Principles", 18, False),
                ("Informed Consent Requirements", 22, False),
            ]),
            ("IRB Processes", [
                ("IRB Review Categories", 18, False),
                ("Writing an IRB Protocol Submission", 22, False),
                ("Continuing Review and Protocol Amendments", 15, False),
            ]),
            ("Integrity & Misconduct", [
                ("Fabrication, Falsification, and Plagiarism", 20, False),
                ("Authorship and Contributorship (ICMJE)", 15, False),
                ("Data Management and Sharing Obligations", 18, False),
            ]),
        ],
    },
    {
        "slug": "evidence-synthesis-hta",
        "title": "Evidence Synthesis for HTA",
        "short_description": "Health technology assessment evidence packages: indirect treatment comparisons, network meta-analysis, cost-effectiveness model inputs, and GRADE for HTA bodies.",
        "description": "Health technology assessment bodies (NICE, HAS, IQWiG, CADTH) require structured evidence packages. This course covers indirect treatment comparisons (ITC), network meta-analysis (NMA), mixed-treatment comparisons, populating cost-effectiveness models, and submitting GRADE evidence profiles to payers.",
        "objectives": "Conduct and interpret indirect treatment comparisons\nBuild and report a network meta-analysis\nPopulate a cost-effectiveness model with synthesised evidence\nPrepare a NICE-style submission evidence package",
        "requirements": "Systematic review methodology (recommend completing Systematic Review & Meta-Analysis first)\nBasic health economics awareness",
        "target_audience": "Market access and HEOR researchers\nClinical evidence teams at pharmaceutical companies\nHTA submission writers",
        "difficulty": "advanced",
        "duration": 20,
        "price": "199.00",
        "is_featured": False,
        "has_certificate": True,
        "tags": ["Systematic Review", "Evidence-Based Medicine", "Biostatistics"],
        "specializations": ["Evidence Synthesis"],
        "modules": [
            ("HTA Fundamentals", [
                ("HTA Bodies and Submission Requirements", 22, True),
                ("PICO and Comparator Selection for HTA", 18, False),
            ]),
            ("Indirect Treatment Comparisons", [
                ("Anchored ITC: Bucher Method", 28, False),
                ("Network Meta-Analysis Concepts", 30, False),
                ("Consistency and Transitivity Assessment", 24, False),
            ]),
            ("Cost-Effectiveness Evidence", [
                ("Populating Decision Trees and Markov Models", 28, False),
                ("Uncertainty Analysis: PSA and DSA", 22, False),
            ]),
            ("Submission Packages", [
                ("GRADE for HTA Payer Submissions", 25, False),
                ("NICE Evidence Package Structure", 22, False),
            ]),
        ],
    },
    {
        "slug": "biostatistics-clinical-research",
        "title": "Biostatistics for Clinical Research",
        "short_description": "Descriptive statistics, hypothesis testing, regression, survival analysis, and sample-size calculation—applied throughout to clinical trial examples.",
        "description": "Practical biostatistics for clinical researchers without heavy mathematical notation. Covers descriptive statistics, normal distribution, hypothesis testing, t-tests, chi-square, ANOVA, linear and logistic regression, Kaplan-Meier survival analysis, Cox proportional hazards, and sample-size calculation using clinical examples.",
        "objectives": "Choose the correct statistical test for any clinical research question\nInterpret p-values, confidence intervals, and effect sizes correctly\nFit and interpret logistic and linear regression models\nRead and construct Kaplan-Meier survival curves\nCalculate sample sizes for common trial designs",
        "requirements": "High-school level mathematics\nNo prior statistics course required",
        "target_audience": "Clinicians interpreting published research\nResidents and fellows preparing for board exams\nClinical research staff supporting trial analysis",
        "difficulty": "beginner",
        "duration": 20,
        "price": "119.00",
        "is_featured": True,
        "has_certificate": True,
        "tags": ["Biostatistics", "Clinical Research", "Evidence-Based Medicine"],
        "specializations": ["Clinical Research"],
        "modules": [
            ("Descriptive Statistics", [
                ("Levels of Measurement and Summary Statistics", 22, True),
                ("Data Distributions and the Normal Curve", 20, False),
                ("Visualising Clinical Data", 18, False),
            ]),
            ("Inferential Statistics", [
                ("Hypothesis Testing and p-values", 28, False),
                ("Confidence Intervals and Effect Sizes", 24, False),
                ("t-tests, chi-square, and ANOVA", 30, False),
            ]),
            ("Regression Models", [
                ("Linear Regression for Continuous Outcomes", 28, False),
                ("Logistic Regression for Binary Outcomes", 30, False),
                ("Multivariable Adjustment and Confounding", 24, False),
            ]),
            ("Survival Analysis", [
                ("Kaplan-Meier Curves", 25, False),
                ("Log-Rank Test and Cox Regression", 28, False),
            ]),
            ("Sample-Size Calculation", [
                ("Sample Size for Superiority Trials", 25, False),
                ("Sample Size for Cross-Sectional Studies", 18, False),
            ]),
        ],
    },
    {
        "slug": "clinical-data-management",
        "title": "Clinical Data Management",
        "short_description": "EDC systems, CRF design, data validation, CDASH standards, query resolution, and FDA 21 CFR Part 11 electronic records compliance.",
        "description": "A practical course for clinical data managers and trial coordinators covering eCRF design principles, edit checks, data validation plans, CDISC CDASH/SDTM standards, query lifecycle management, audit trails, and FDA 21 CFR Part 11 electronic record requirements.",
        "objectives": "Design efficient eCRFs following CDASH conventions\nWrite data validation and edit-check specifications\nManage query lifecycle from generation to closure\nApply CDISC SDTM for submission datasets\nComply with FDA 21 CFR Part 11 requirements",
        "requirements": "Experience working on clinical trials (CRC or CRA level)\nNo programming experience required",
        "target_audience": "Clinical data managers\nClinical research coordinators\nBiostatisticians working with submission data",
        "difficulty": "intermediate",
        "duration": 15,
        "price": "139.00",
        "is_featured": False,
        "has_certificate": True,
        "tags": ["Clinical Data", "Clinical Research"],
        "specializations": ["Clinical Research"],
        "modules": [
            ("EDC Systems & CRF Design", [
                ("Overview of EDC Platforms", 18, True),
                ("eCRF Design Principles", 22, False),
                ("CDASH Standards for eCRF", 25, False),
            ]),
            ("Data Validation & Queries", [
                ("Edit Checks and Validation Plans", 22, False),
                ("Query Lifecycle Management", 18, False),
                ("Database Lock Procedures", 15, False),
            ]),
            ("CDISC Standards", [
                ("SDTM: Study Data Tabulation Model", 30, False),
                ("ADaM: Analysis Dataset Model", 25, False),
                ("Submission-Ready Dataset Packages", 20, False),
            ]),
            ("Compliance", [
                ("FDA 21 CFR Part 11: Electronic Records", 20, False),
                ("Audit Trails and Data Traceability", 15, False),
            ]),
        ],
    },
]

# ── Translations dictionary ─────────────────────────────────────────────────
# Structure: {lang: {en_slug: {field: value}}}
# Only title, short_description, objectives, requirements, target_audience translated.
# Description uses a shorter translated version for performance.

COURSE_TRANSLATIONS = {
    "fr": {
        "clinical-trial-design-protocol-development": {
            "title": "Conception d'essais cliniques et développement de protocoles",
            "short_description": "Maîtrisez le cycle complet de conception d'un essai clinique : ICH E6, rédaction de protocole, randomisation, aveugle, planification statistique et soumission réglementaire.",
            "objectives": "Rédiger un protocole d'essai clinique conforme à l'ICH\nChoisir des stratégies de randomisation et d'aveugle appropriées\nEstimer les effectifs pour les essais de supériorité et de non-infériorité\nNaviguer dans les exigences de soumission IRB/IEC\nConcevoir des cadres de surveillance de la sécurité",
            "requirements": "Notions de base en épidémiologie ou recherche clinique\nFamiliarité avec les concepts statistiques de base",
            "target_audience": "Coordinateurs de recherche clinique\nRédacteurs médicaux entrant en recherche clinique\nMédecins concevant des essais à initiative investigateur",
        },
        "systematic-review-meta-analysis": {
            "title": "Revue systématique et méta-analyse",
            "short_description": "Revues systématiques conformes PRISMA et estimations d'effets groupés par méta-analyse. De l'enregistrement du protocole à la certitude de preuve GRADE.",
            "objectives": "Enregistrer un protocole de revue systématique sur PROSPERO\nEffectuer des recherches bibliographiques complètes dans MEDLINE et Embase\nAppliquer les outils RoB 2 et ROBINS-I\nCombiner les tailles d'effet par modèles à effets fixes et aléatoires\nInterpréter l'hétérogénéité et le biais de publication\nÉvaluer la certitude des preuves avec GRADE",
            "requirements": "Compréhension des méthodes de recherche de base\nFamiliarité avec la littérature médicale",
            "target_audience": "Chercheurs cliniciens\nÉquipes de synthèse de preuves\nAnalystes en évaluation des technologies de la santé",
        },
        "medical-ai-clinical-applications": {
            "title": "IA médicale et applications cliniques",
            "short_description": "Des fondamentaux du ML au plan d'action FDA IA/ML. Validation de modèles, détection de biais, déploiement clinique et gouvernance responsable de l'IA en santé.",
            "objectives": "Expliquer les algorithmes ML utilisés en IA médicale\nConcevoir et interpréter des études de validation de modèles\nIdentifier et atténuer les biais algorithmiques dans les données cliniques\nAppliquer le cadre réglementaire FDA SaMD IA/ML\nÉvaluer les outils d'IA pour le déploiement en aide à la décision clinique",
            "requirements": "Alphabétisation de base en données\nFamiliarité avec les flux cliniques utile mais non requise",
            "target_audience": "Cliniciens évaluant les outils d'IA\nInformaticiens cliniques\nData scientists en santé",
        },
        "scientific-writing-medical-manuscripts": {
            "title": "Rédaction scientifique pour les manuscrits médicaux",
            "short_description": "Structure IMRAD, style AMA, réponse à l'évaluation par les pairs et rédaction de chaque section d'un manuscrit que les éditeurs acceptent.",
            "objectives": "Structurer un manuscrit selon les conventions IMRAD\nRédiger un résumé structuré pour la recherche originale\nRapporter les statistiques selon les directives AMA et CONSORT\nPréparer une lettre de couverture convaincante et une réponse aux auteurs\nNaviguer dans les cycles de révision et d'évaluation par les pairs",
            "requirements": "Avoir complété au moins un projet de recherche\nExpérience de base en rédaction académique",
            "target_audience": "Médecins et chercheurs rédigeant leur premier article\nRédacteurs médicaux soutenant des équipes cliniques\nÉtudiants du cycle supérieur préparant des manuscrits",
        },
        "research-ethics-integrity": {
            "title": "Éthique et intégrité de la recherche",
            "short_description": "Consentement éclairé, Déclaration d'Helsinki, processus IRB, fraude scientifique, conflits d'auteurs et culture de l'intégrité.",
            "objectives": "Appliquer les principes de la Déclaration d'Helsinki à la conception d'études\nRédiger des documents de consentement éclairé conformes\nNaviguer dans la révision IRB expéditée vs complète\nIdentifier et traiter la fraude scientifique\nGérer correctement les questions d'auteurs et de contributeurs",
            "requirements": "Aucune formation préalable en éthique requise",
            "target_audience": "Tous les chercheurs cliniques et biomédicaux\nÉtudiants entrant dans des programmes de recherche de troisième cycle\nMembres des comités d'éthique de la recherche",
        },
        "biostatistics-clinical-research": {
            "title": "Biostatistiques pour la recherche clinique",
            "short_description": "Statistiques descriptives, tests d'hypothèses, régression, analyse de survie et calcul d'effectif — appliqués à des exemples d'essais cliniques.",
            "objectives": "Choisir le test statistique correct pour toute question de recherche clinique\nInterpréter correctement les valeurs p, intervalles de confiance et tailles d'effet\nFit et interpréter des modèles de régression logistique et linéaire\nLire et construire des courbes de survie de Kaplan-Meier\nCalculer des effectifs pour les conceptions d'essais courants",
            "requirements": "Mathématiques de niveau lycée\nAucun cours de statistiques préalable requis",
            "target_audience": "Cliniciens interprétant la recherche publiée\nRésidents et internes préparant les examens\nPersonnel de recherche clinique soutenant l'analyse des essais",
        },
    },
    "de": {
        "clinical-trial-design-protocol-development": {
            "title": "Klinische Studienplanung und Protokollentwicklung",
            "short_description": "Meistern Sie den gesamten Lebenszyklus klinischer Studienplanung: ICH E6, Protokollschreiben, Randomisierung, Verblindung, statistische Planung und regulatorische Einreichung.",
            "objectives": "Ein ICH-konformes klinisches Studienprotokoll schreiben\nGeeignete Randomisierungs- und Verblindungsstrategien auswählen\nStichprobenumfänge für Überlegenheits- und Nicht-Unterlegenheitsstudien schätzen\nIRB/IEC-Einreichungsanforderungen navigieren\nSicherheitsüberwachungsrahmen entwerfen",
            "requirements": "Grundkenntnisse in Epidemiologie oder klinischer Forschung\nVertrautheit mit statistischen Grundkonzepten",
            "target_audience": "Klinische Forschungskoordinatoren\nMedizinische Autoren in der klinischen Forschung\nÄrzte, die forschungsinitiierte Studien entwerfen",
        },
        "systematic-review-meta-analysis": {
            "title": "Systematische Übersicht und Meta-Analyse",
            "short_description": "PRISMA-konforme systematische Übersichten und gepoolte Effektschätzungen durch Meta-Analyse. Von der Protokollregistrierung bis zur GRADE-Sicherheit der Evidenz.",
            "objectives": "Ein systematisches Übersichtsprotokoll in PROSPERO registrieren\nUmfassende Datenbanksuchen in MEDLINE und Embase durchführen\nRoB 2 und ROBINS-I Risiko-von-Bias-Werkzeuge anwenden\nEffektgrößen mithilfe von Fixed- und Random-Effects-Modellen zusammenfassen\nHeterogenität und Publikationsbias interpretieren\nEvidenzgewissheit mit GRADE bewerten",
            "requirements": "Verständnis grundlegender Forschungsmethodik\nVertrautheit mit der medizinischen Literatur",
            "target_audience": "Klinische Forscher\nEvidenz-Synthese-Teams\nAnalysten in der Nutzenbewertung",
        },
        "medical-ai-clinical-applications": {
            "title": "Medizinische KI und klinische Anwendungen",
            "short_description": "Von ML-Grundlagen zum FDA KI/ML-Aktionsplan. Modellvalidierung, Bias-Erkennung, klinisches Deployment und verantwortungsvolle KI-Governance im Gesundheitswesen.",
            "objectives": "Grundlegende ML-Algorithmen in der medizinischen KI erklären\nModellvalidierungsstudien entwerfen und interpretieren\nAlgorithmische Verzerrungen in klinischen Datensätzen identifizieren und mindern\nFDA KI/ML SaMD-Regulierungsrahmen anwenden\nKI-Werkzeuge für die klinische Entscheidungsunterstützung evaluieren",
            "requirements": "Grundlegende Datenkompetenz\nVertrautheit mit klinischen Abläufen hilfreich, aber nicht erforderlich",
            "target_audience": "Kliniker, die KI-Tools bewerten\nKlinische Informatiker\nGesundheits-Datenwissenschaftler",
        },
        "scientific-writing-medical-manuscripts": {
            "title": "Wissenschaftliches Schreiben für medizinische Manuskripte",
            "short_description": "IMRAD-Struktur, AMA-Stil, Reaktion auf Peer-Review und wie jeder Abschnitt eines klinischen Manuskripts geschrieben wird.",
            "objectives": "Ein Manuskript nach IMRAD-Konventionen strukturieren\nEin strukturiertes Abstract für Originalforschung schreiben\nStatistiken nach AMA- und CONSORT-Richtlinien berichten\nEin überzeugendes Anschreiben und Autorenreaktion vorbereiten\nPeer-Review- und Revisionszyklen navigieren",
            "requirements": "Abschluss mindestens eines Forschungsprojekts\nGrunderfahrung im akademischen Schreiben",
            "target_audience": "Ärzte und Forscher, die ihr erstes Paper schreiben\nMedizinische Autoren, die klinische Teams unterstützen\nPostgraduierende, die Manuskripte vorbereiten",
        },
        "biostatistics-clinical-research": {
            "title": "Biostatistik für die klinische Forschung",
            "short_description": "Deskriptive Statistik, Hypothesentests, Regression, Überlebensanalyse und Stichprobengrößenberechnung – anhand klinischer Beispiele angewendet.",
            "objectives": "Den richtigen statistischen Test für jede klinische Forschungsfrage wählen\np-Werte, Konfidenzintervalle und Effektgrößen korrekt interpretieren\nLogistische und lineare Regressionsmodelle anpassen und interpretieren\nKaplan-Meier-Überlebenskurven lesen und erstellen\nStichprobenumfänge für gängige Studiendesigns berechnen",
            "requirements": "Mathematik auf Abitur-Niveau\nKein vorheriger Statistikkurs erforderlich",
            "target_audience": "Kliniker, die veröffentlichte Forschung interpretieren\nAssistenzärzte, die sich auf Prüfungen vorbereiten\nKlinisches Forschungspersonal, das Studienanalysen unterstützt",
        },
    },
    "es": {
        "clinical-trial-design-protocol-development": {
            "title": "Diseño de ensayos clínicos y desarrollo de protocolos",
            "short_description": "Domine el ciclo completo del diseño de ensayos clínicos: ICH E6, redacción de protocolos, aleatorización, cegamiento, planificación estadística y presentación regulatoria.",
            "objectives": "Redactar un protocolo de ensayo clínico conforme a ICH\nSeleccionar estrategias apropiadas de aleatorización y cegamiento\nEstimar tamaños de muestra para ensayos de superioridad y no inferioridad\nNavegar los requisitos de presentación ante IRB/IEC\nDiseñar marcos de monitoreo de seguridad",
            "requirements": "Base en epidemiología o investigación clínica\nFamiliaridad con conceptos estadísticos básicos",
            "target_audience": "Coordinadores de investigación clínica\nRedactores médicos que ingresan a la investigación clínica\nMédicos diseñando ensayos iniciados por investigadores",
        },
        "systematic-review-meta-analysis": {
            "title": "Revisión sistemática y metaanálisis",
            "short_description": "Revisiones sistemáticas compatibles con PRISMA y estimaciones de efecto combinadas mediante metaanálisis. Del registro del protocolo a la certeza de evidencia GRADE.",
            "objectives": "Registrar un protocolo de revisión sistemática en PROSPERO\nRealizar búsquedas bibliográficas en MEDLINE y Embase\nAplicar las herramientas RoB 2 y ROBINS-I\nCombinar tamaños de efecto usando modelos de efectos fijos y aleatorios\nInterpretar la heterogeneidad y el sesgo de publicación\nCalificar la certeza de evidencia con GRADE",
            "requirements": "Comprensión de metodología de investigación básica\nFamiliaridad con la literatura médica",
            "target_audience": "Investigadores clínicos\nEquipos de síntesis de evidencia\nAnalistas de evaluación de tecnologías sanitarias",
        },
        "medical-ai-clinical-applications": {
            "title": "IA médica y aplicaciones clínicas",
            "short_description": "De los fundamentos del ML al plan de acción FDA IA/ML. Validación de modelos, detección de sesgos, despliegue clínico y gobernanza responsable de IA en salud.",
            "objectives": "Explicar los algoritmos ML utilizados en IA médica\nDiseñar e interpretar estudios de validación de modelos\nIdentificar y mitigar sesgos algorítmicos en conjuntos de datos clínicos\nAplicar el marco regulatorio FDA SaMD IA/ML\nEvaluar herramientas de IA para soporte de decisiones clínicas",
            "requirements": "Alfabetización básica en datos\nFamiliaridad con flujos clínicos útil pero no requerida",
            "target_audience": "Médicos evaluando herramientas de IA\nInformáticos clínicos\nCientíficos de datos en salud",
        },
        "biostatistics-clinical-research": {
            "title": "Bioestadística para investigación clínica",
            "short_description": "Estadística descriptiva, pruebas de hipótesis, regresión, análisis de supervivencia y cálculo de tamaño de muestra aplicados a ejemplos de ensayos clínicos.",
            "objectives": "Elegir la prueba estadística correcta para cualquier pregunta de investigación clínica\nInterpretar correctamente valores p, intervalos de confianza y tamaños de efecto\nAjustar e interpretar modelos de regresión logística y lineal\nLeer y construir curvas de supervivencia de Kaplan-Meier\nCalcular tamaños de muestra para diseños de ensayos comunes",
            "requirements": "Matemáticas de nivel bachillerato\nNo se requiere curso previo de estadística",
            "target_audience": "Clínicos que interpretan investigación publicada\nResidentes e internos que se preparan para exámenes\nPersonal de investigación clínica que apoya el análisis de ensayos",
        },
    },
    "ar": {
        "clinical-trial-design-protocol-development": {
            "title": "تصميم التجارب السريرية وتطوير البروتوكولات",
            "short_description": "أتقن الدورة الكاملة لتصميم التجارب السريرية: ICH E6، كتابة البروتوكول، التعشية، التعمية، التخطيط الإحصائي، والتقديم التنظيمي.",
            "objectives": "كتابة بروتوكول تجربة سريرية متوافق مع ICH\nاختيار استراتيجيات التعشية والتعمية المناسبة\nتقدير أحجام العينات لتجارب التفوق وعدم الأدنوية\nالتنقل في متطلبات تقديم IRB/IEC\nتصميم أطر مراقبة السلامة",
            "requirements": "خلفية أساسية في علم الأوبئة أو البحث السريري\nإلمام بالمفاهيم الإحصائية الأساسية",
            "target_audience": "منسقو البحث السريري\nالكتّاب الطبيون الداخلون في البحث السريري\nالأطباء الذين يصممون تجارب بمبادرة من المحقق",
        },
        "systematic-review-meta-analysis": {
            "title": "المراجعة المنهجية والتحليل التلوي",
            "short_description": "مراجعات منهجية متوافقة مع PRISMA وتقديرات الأثر المجمّعة بالتحليل التلوي. من تسجيل البروتوكول إلى يقين الأدلة GRADE.",
            "objectives": "تسجيل بروتوكول مراجعة منهجية في PROSPERO\nإجراء عمليات بحث شاملة في MEDLINE وEmbase\nتطبيق أدوات RoB 2 وROBINS-I\nتجميع أحجام الأثر باستخدام نماذج التأثيرات الثابتة والعشوائية\nتفسير عدم التجانس وتحيز النشر\nتقييم يقين الأدلة باستخدام GRADE",
            "requirements": "فهم منهجية البحث الأساسية\nإلمام بالأدبيات الطبية",
            "target_audience": "الباحثون السريريون\nفرق تركيب الأدلة\nمحللو تقييم التقنيات الصحية",
        },
        "medical-ai-clinical-applications": {
            "title": "الذكاء الاصطناعي الطبي والتطبيقات السريرية",
            "short_description": "من أسس التعلم الآلي إلى خطة عمل FDA للذكاء الاصطناعي. التحقق من صحة النماذج، اكتشاف التحيز، النشر السريري وحوكمة الذكاء الاصطناعي المسؤول في الرعاية الصحية.",
            "objectives": "شرح خوارزميات التعلم الآلي المستخدمة في الذكاء الاصطناعي الطبي\nتصميم وتفسير دراسات التحقق من صحة النماذج\nتحديد التحيز الخوارزمي في مجموعات البيانات السريرية ومعالجته\nتطبيق إطار FDA التنظيمي للذكاء الاصطناعي SaMD\nتقييم أدوات الذكاء الاصطناعي لدعم القرار السريري",
            "requirements": "محو الأمية الأساسية في البيانات\nالإلمام بالسير السريرية مفيد لكنه غير مطلوب",
            "target_audience": "الأطباء الذين يقيّمون أدوات الذكاء الاصطناعي\nالمعلوماتيون السريريون\nعلماء البيانات الصحية",
        },
        "biostatistics-clinical-research": {
            "title": "الإحصاء الحيوي للبحث السريري",
            "short_description": "الإحصاء الوصفي، اختبار الفرضيات، الانحدار، تحليل البقاء وحساب حجم العينة — مطبّقة على أمثلة من التجارب السريرية.",
            "objectives": "اختيار الاختبار الإحصائي الصحيح لأي سؤال بحثي سريري\nتفسير قيم p وفترات الثقة وأحجام الأثر بشكل صحيح\nضبط وتفسير نماذج الانحدار اللوجستي والخطي\nقراءة وبناء منحنيات البقاء لكابلان-ماير\nحساب أحجام العينات لتصاميم التجارب الشائعة",
            "requirements": "رياضيات المستوى الثانوي\nلا يلزم دورة إحصاء سابقة",
            "target_audience": "الأطباء الذين يفسرون البحوث المنشورة\nالمقيمون والزملاء الذين يستعدون للاختبارات\nموظفو البحث السريري الذين يدعمون تحليل التجارب",
        },
    },
    "pt-br": {
        "clinical-trial-design-protocol-development": {
            "title": "Desenho de ensaios clínicos e desenvolvimento de protocolo",
            "short_description": "Domine o ciclo completo do desenho de ensaios clínicos: ICH E6, redação de protocolos, randomização, cegamento, planejamento estatístico e submissão regulatória.",
            "objectives": "Escrever um protocolo de ensaio clínico em conformidade com ICH\nSelecionar estratégias apropriadas de randomização e cegamento\nEstimar tamanhos de amostra para ensaios de superioridade e não inferioridade\nNavegar pelos requisitos de submissão IRB/IEC\nDesenhar estruturas de monitoramento de segurança",
            "requirements": "Base em epidemiologia ou pesquisa clínica\nFamiliaridade com conceitos estatísticos básicos",
            "target_audience": "Coordenadores de pesquisa clínica\nRedatores médicos entrando na pesquisa clínica\nMédicos desenhando ensaios iniciados por investigadores",
        },
        "systematic-review-meta-analysis": {
            "title": "Revisão sistemática e metanálise",
            "short_description": "Revisões sistemáticas em conformidade com PRISMA e estimativas de efeito combinadas por metanálise. Do registro do protocolo à certeza de evidência GRADE.",
            "objectives": "Registrar um protocolo de revisão sistemática no PROSPERO\nRealizar buscas bibliográficas abrangentes no MEDLINE e Embase\nAplicar as ferramentas RoB 2 e ROBINS-I\nCombinar tamanhos de efeito usando modelos de efeitos fixos e aleatórios\nInterpretar heterogeneidade e viés de publicação\nAvaliar a certeza da evidência com GRADE",
            "requirements": "Compreensão de metodologia de pesquisa básica\nFamiliaridade com a literatura médica",
            "target_audience": "Pesquisadores clínicos\nEquipes de síntese de evidências\nAnalistas de avaliação de tecnologias em saúde",
        },
        "biostatistics-clinical-research": {
            "title": "Bioestatística para pesquisa clínica",
            "short_description": "Estatística descritiva, testes de hipóteses, regressão, análise de sobrevivência e cálculo de tamanho de amostra — aplicados a exemplos de ensaios clínicos.",
            "objectives": "Escolher o teste estatístico correto para qualquer questão de pesquisa clínica\nInterpretar corretamente valores p, intervalos de confiança e tamanhos de efeito\nAjustar e interpretar modelos de regressão logística e linear\nLer e construir curvas de sobrevivência de Kaplan-Meier\nCalcular tamanhos de amostra para desenhos de ensaios comuns",
            "requirements": "Matemática de nível médio\nNenhum curso de estatística anterior necessário",
            "target_audience": "Clínicos que interpretam pesquisas publicadas\nResidentes e fellows se preparando para provas\nEquipe de pesquisa clínica que apoia análise de ensaios",
        },
    },
    "sv": {
        "clinical-trial-design-protocol-development": {
            "title": "Klinisk studiedesign och protokollutveckling",
            "short_description": "Behärska hela livscykeln för klinisk studiedesign: ICH E6, protokollskrivning, randomisering, blindning, statistisk planering och regulatorisk inlämning.",
            "objectives": "Skriva ett ICH-kompatibelt kliniskt studieprotokoll\nVälja lämpliga randomiserings- och blindningsstrategier\nUppskatta stickprovsstorlekar för överlägsenhetsstudier och icke-underlägsenhetsstudier\nNavigera IRB/IEC-inlämningskrav\nDesigna säkerhetsövervakningsramar",
            "requirements": "Grundläggande epidemiologi eller klinisk forskningsbakgrund\nBekantskap med grundläggande statistiska begrepp",
            "target_audience": "Kliniska forskningskoordinatorer\nMedicinskrivare inom klinisk forskning\nLäkare som designar investigatoriniterade studier",
        },
        "systematic-review-meta-analysis": {
            "title": "Systematisk översikt och metaanalys",
            "short_description": "PRISMA-kompatibla systematiska översikter och sammanslagna effektskattningar med metaanalys. Från protokollregistrering till GRADE-evidenssäkerhet.",
            "objectives": "Registrera ett systematiskt översiktsprotokoll på PROSPERO\nGenomföra heltäckande databassökningar i MEDLINE och Embase\nTillämpa RoB 2 och ROBINS-I riskbedömningsverktyg\nSammanslå effektstorlekar med fasta och slumpmässiga effektmodeller\nTolka heterogenitet och publikationsbias\nBedöma evidenssäkerhet med GRADE",
            "requirements": "Förståelse för grundläggande forskningsmetodik\nBekantskap med medicinsk litteratur",
            "target_audience": "Kliniska forskare\nEvidenssyntesteam\nAnalytiker inom utvärdering av medicinska metoder",
        },
        "biostatistics-clinical-research": {
            "title": "Biostatistik för klinisk forskning",
            "short_description": "Deskriptiv statistik, hypotestestning, regression, överlevnadsanalys och stickprovsstorlekkalkylering — tillämpat på kliniska prövningsexempel.",
            "objectives": "Välja rätt statistiskt test för alla kliniska forskningsfrågor\nTolka p-värden, konfidensintervall och effektstorlekar korrekt\nAnpassa och tolka logistiska och linjära regressionsmodeller\nLäsa och konstruera Kaplan-Meier-överlevnadskurvor\nBeräkna stickprovsstorlekar för vanliga prövningsdesigner",
            "requirements": "Matematik på gymnasienivå\nInget tidigare statistikkurs krävs",
            "target_audience": "Kliniker som tolkar publicerad forskning\nAT-läkare och ST-läkare som förbereder sig för prov\nKlinisk forskningspersonal som stödjer prövningsanalys",
        },
    },
}


class Command(BaseCommand):
    help = "Seed complete course catalog: translations, tags, modules, lessons (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument("--clear", action="store_true", help="Delete all seeded courses first.")
        parser.add_argument("--tags-only", action="store_true", help="Only seed tags/specs, skip courses.")
        parser.add_argument("--lang", type=str, default="", help="Seed only one language (e.g. fr).")

    def handle(self, *args, **options):
        from apps.learning.models import Course, CourseTag, Specialization, Module, Lesson

        if options["clear"]:
            self.stdout.write(self.style.WARNING("Clearing all courses…"))
            Course.objects.all().delete()
            self.stdout.write("  Done.")

        # ── Tags ──────────────────────────────────────────────────────────────
        self.stdout.write("Seeding tags…")
        all_tags = {name for c in COURSES_EN for name in c["tags"]}
        tag_objs: dict[str, CourseTag] = {}
        for name in sorted(all_tags):
            obj, created = CourseTag.objects.get_or_create(
                slug=slugify(name), defaults={"name": name}
            )
            tag_objs[name] = obj
            if created:
                self.stdout.write(f"  + tag: {name}")

        # ── Specializations ───────────────────────────────────────────────────
        self.stdout.write("Seeding specializations…")
        all_specs = {s for c in COURSES_EN for s in c["specializations"]}
        spec_objs: dict[str, Specialization] = {}
        for title in sorted(all_specs):
            obj, created = Specialization.objects.get_or_create(
                slug=slugify(title), defaults={"title": title}
            )
            spec_objs[title] = obj
            if created:
                self.stdout.write(f"  + spec: {title}")

        if options["tags_only"]:
            self.stdout.write(self.style.SUCCESS("Tags/specs seeded. Stopping (--tags-only)."))
            return

        # ── English courses ───────────────────────────────────────────────────
        self.stdout.write("Seeding English courses…")
        # instructor is NOT NULL — reuse one from existing courses, or find any user
        from django.contrib.auth import get_user_model
        User = get_user_model()
        default_instructor = (
            Course.objects.filter(instructor__isnull=False)
            .values_list("instructor_id", flat=True).first()
            or User.objects.filter(is_active=True).values_list("id", flat=True).first()
        )
        if not default_instructor:
            self.stdout.write(self.style.ERROR(
                "No user found in DB. Run 'manage.py createsuperuser' first, then re-run."
            ))
            return
        for data in COURSES_EN:
            course, created = Course.objects.get_or_create(
                slug=data["slug"],
                defaults={
                    "title": data["title"],
                    "language": "en",
                    "short_description": data["short_description"],
                    "description": data["description"],
                    "objectives": data["objectives"],
                    "requirements": data["requirements"],
                    "target_audience": data["target_audience"],
                    "difficulty_level": data["difficulty"],
                    "duration": data["duration"],
                    "price": Decimal(data["price"]),
                    "currency": "USD",
                    "instructor_id": default_instructor,
                    "is_published": True,
                    "is_active": True,
                    "is_featured": data.get("is_featured", False),
                    "has_certificate": data.get("has_certificate", True),
                },
            )
            if not created:
                # Update mutable fields on existing courses
                course.title = data["title"]
                course.short_description = data["short_description"]
                course.objectives = data["objectives"]
                course.requirements = data["requirements"]
                course.target_audience = data["target_audience"]
                course.is_published = True
                course.is_active = True
                course.save(update_fields=[
                    "title", "short_description", "objectives",
                    "requirements", "target_audience", "is_published", "is_active",
                ])

            # Tags
            course.tags.set([tag_objs[t] for t in data["tags"] if t in tag_objs])
            # Specializations
            course.specializations.set([spec_objs[s] for s in data["specializations"] if s in spec_objs])

            # Modules + Lessons (idempotent)
            for mod_order, (mod_title, lessons) in enumerate(data["modules"]):
                mod, _ = Module.objects.get_or_create(
                    course=course,
                    order=mod_order,
                    defaults={"title": mod_title, "is_preview": False},
                )
                mod.title = mod_title
                mod.save(update_fields=["title"])
                for les_order, (les_title, les_dur, les_preview) in enumerate(lessons):
                    # Lesson slug: en + mod order + lesson order — structured and unique
                    les_slug = f"en-m{mod_order}-l{les_order}-{slugify(les_title)}"[:50]
                    les, _ = Lesson.objects.get_or_create(
                        module=mod,
                        order=les_order,
                        defaults={
                            "title": les_title,
                            "slug": les_slug,
                            "duration": les_dur,
                            "is_preview": les_preview,
                            "is_active": True,
                        },
                    )
                    les.title = les_title
                    les.duration = les_dur
                    les.is_preview = les_preview
                    les.save(update_fields=["title", "duration", "is_preview"])

            action = "created" if created else "updated"
            self.stdout.write(f"  [{action}] en/{data['slug']}")

        # ── Translated courses ────────────────────────────────────────────────
        target_langs = [options["lang"]] if options["lang"] else list(COURSE_TRANSLATIONS.keys())

        for lang in target_langs:
            if lang not in COURSE_TRANSLATIONS:
                self.stdout.write(self.style.WARNING(f"  No translations for lang={lang}, skipping."))
                continue
            self.stdout.write(f"Seeding {lang} translations…")
            lang_data = COURSE_TRANSLATIONS[lang]

            for en_slug, fields in lang_data.items():
                # Find original EN course for reference data
                en_course = Course.objects.filter(slug=en_slug, language="en").first()
                if not en_course:
                    self.stdout.write(self.style.WARNING(f"  EN base {en_slug!r} not found, skipping."))
                    continue

                # Build translated slug: append -<lang>
                trans_slug = f"{en_slug}-{lang.replace('-', '')}"

                defaults = {
                    "title": fields["title"],
                    "language": lang,
                    "short_description": fields["short_description"],
                    "description": en_course.description,  # fallback to EN for long body
                    "objectives": fields.get("objectives", en_course.objectives),
                    "requirements": fields.get("requirements", en_course.requirements),
                    "target_audience": fields.get("target_audience", en_course.target_audience),
                    "difficulty_level": en_course.difficulty_level,
                    "duration": en_course.duration,
                    "price": Decimal(str(en_course.price)),
                    "currency": en_course.currency,
                    "instructor_id": en_course.instructor_id or default_instructor,
                    "is_published": True,
                    "is_active": True,
                    "is_featured": en_course.is_featured,
                    "has_certificate": en_course.has_certificate,
                }

                course, created = Course.objects.get_or_create(
                    slug=trans_slug, defaults=defaults
                )
                if not created:
                    for k, v in defaults.items():
                        setattr(course, k, v)
                    course.save()

                # Copy tags + specializations from EN course
                course.tags.set(en_course.tags.all())
                course.specializations.set(en_course.specializations.all())

                # Copy modules+lessons from EN course (translated title = EN for now)
                for en_mod in Module.objects.filter(course=en_course).order_by("order"):
                    mod, _ = Module.objects.get_or_create(
                        course=course,
                        order=en_mod.order,
                        defaults={"title": en_mod.title},
                    )
                    mod.title = en_mod.title
                    mod.save(update_fields=["title"])
                    for en_les in Lesson.objects.filter(module=en_mod).order_by("order"):
                        # Lesson slug: lang prefix + mod order + lesson order — guaranteed unique at 50 chars
                        lang_code = lang.replace("-", "")[:4]
                        les_slug = f"{lang_code}-m{en_mod.order}-l{en_les.order}-{slugify(en_les.title)}"[:50]
                        les, _ = Lesson.objects.get_or_create(
                            module=mod,
                            order=en_les.order,
                            defaults={
                                "title": en_les.title,
                                "slug": les_slug,
                                "duration": en_les.duration,
                                "is_preview": en_les.is_preview,
                                "is_active": True,
                            },
                        )
                        les.title = en_les.title
                        les.duration = en_les.duration
                        les.is_preview = en_les.is_preview
                        les.save(update_fields=["title", "duration", "is_preview"])

                action = "created" if created else "updated"
                self.stdout.write(f"  [{action}] {lang}/{trans_slug}")

        self.stdout.write(self.style.SUCCESS("\n✅  Course seed complete."))
        # Summary
        from django.db.models import Count
        for row in Course.objects.values("language").annotate(n=Count("id")).order_by("language"):
            self.stdout.write(f"   {row['language']:8} {row['n']:3} courses")
