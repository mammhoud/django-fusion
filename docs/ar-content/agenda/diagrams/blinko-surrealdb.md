---
title: 🗒️ Blinko — طوبولوجيا SurrealDB وتدفّق البيانات
description: خدمة ملاحظات Blinko المستضافة ذاتياً — الطوبولوجيا، طبقة تخزين SurrealDB، وتدفّق المصادقة والمحتوى والاستعلامات.
navigation:
  title: Blinko SurrealDB
  icon: i-lucide-notebook
---

# 🗒️ Blinko — طوبولوجيا SurrealDB وتدفّق البيانات

> **الغرض:** توثيق خدمة ملاحظات Blinko بالذكاء الاصطناعي المستضافة ذاتياً
> (`application/tools/blinko/`) — طوبولوجيا الخدمة، وطبقة تخزين SurrealDB،
> وكيف تتدفّق المصادقة والمحتوى والاستعلامات عبرها.
> **الحالة:** نشط · **المالك:** البنية التحتية

---

## 1. طوبولوجيا الخدمة

```mermaid
graph LR
    subgraph "Public"
        P["tools.structa.cloud/notes/"]
    end
    subgraph "Proxy"
        TP["tools-proxy Nginx"]
    end
    subgraph "Docker: application/tools/blinko"
        B["blinko:1111<br/>NextAuth + App (Next.js)"]
        S["surrealdb:v1.5.6<br/>:8000 file:/data/blinko.db"]
        V["blinko-data/surreal<br/>(persistent volume)"]
    end

    P --> TP
    TP --> B
    B -->|"SurrealDB client (surrealdb.js ^1.0.0)"| S
    S --> V
```
![Rendered diagram](/agenda/diagrams/diagrams-blinko-surrealdb-1.svg)

## 2. تدفّق البيانات — المصادقة، مخطط المحتوى، الاستعلامات

```mermaid
sequenceDiagram
    autonumber
    participant U as User (browser)
    participant B as Blinko app (:1111)
    participant S as SurrealDB (:8000)
    participant V as blinko-data/surreal

    U->>B: login (NextAuth)
    B->>S: auth lookup (surreal record)
    S->>V: read blinko.db
    V-->>S: record
    S-->>B: session token
    B-->>U: authenticated session

    U->>B: create note
    B->>S: INSERT content node (graph)
    S->>V: write record
    V-->>S: ok
    S-->>B: record id
    B-->>U: note saved

    U->>B: query / search notes
    B->>S: graph query (relations)
    S->>V: read
    V-->>S: results
    S-->>B: rows
    B-->>U: rendered results
```
![Rendered diagram](/agenda/diagrams/diagrams-blinko-surrealdb-2.svg)

## 3. ترحيل SurrealDB (M1–M4)

وفق ترويسة Compose، انتقل Blinko من Prisma + PostgreSQL إلى SurrealDB:

| الترحيل | ما تغيّر |
|-----------|--------------|
| **M1** | انتقلت المصادقة إلى سجلات SurrealDB |
| **M2** | انتقل مخطط المحتوى (ملاحظات، روابط، وسوم) إلى SurrealDB |
| **M3** | انتقل محرّك الاستعلامات إلى SurrealDB |
| **M4** | لم تعد PostgreSQL مطلوبة وقت التشغيل |

**قيود يجب مراعاتها:**
- **ثبّت SurrealDB على خط الإصدار 1.x** — إذ يثبّت الخادم المضمَّن
  `surrealdb.js@^1.0.0`، وهو يرفض محرّكات v2/v3
  (`UnsupportedVersion`).
- يستخدم `server/lib/scheduler.ts` دلالات upsert المتوافقة مع v1
  (`UPDATE ... MERGE` على معرّف سجل صريح).
- صورة `surrealdb` بلا صدفة (scratch) — لذا تعتمد الجاهزية على فحص
  `/surreal isready` المدمج في الملف التنفيذي، لا على `wget`/`curl`.
- تأتي بيانات الاعتماد من `.env` (`SURREALDB_PASS`، `BLINKO_NEXTAUTH_SECRET`، …).

## 4. ذو صلة

- Compose وMakefile: `application/tools/blinko/`
- سجل قواعد البيانات: `application/databases/README.md` (صف قاعدة `blinko`)
- البدء السريع في الوثائق: `docs/guides/01-quickstart.md` (خدمة Blinko Notes)

<!-- AI-generated: review needed -->
