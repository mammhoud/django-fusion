---
title: مزامنة المحطات المتعددة — دراسة حالة POS
description: بث WebSocket فوري + سحب حِزم التغييرات بين محطات نقطة البيع — البنية والقرارات والنتائج
navigation:
  title: مزامنة المحطات المتعددة
  icon: i-lucide-link
object:
  type: "case-study"
  id: "case-studies.pos-multi-terminal-sync"
attributes:
  source_path: "agenda/case-studies/pos-multi-terminal-sync.md"
  canonical_route: "/docs/ar/agenda/case-studies/pos-multi-terminal-sync"
  source_of_truth: "repository-markdown"
  owner: "formint-pos"
  status: "active"
tags:
  - structa-cloud
  - case-studies
  - pos
  - sync
  - websocket
  - realtime
  - architecture
links:
  - label: "الرئيسية"
    to: "/docs/ar/agenda/main"
    icon: "i-lucide-clipboard-list"
  - label: "تتبّع الميزات — مزامنة المحطات المتعددة"
    to: "/docs/ar/agenda/feature-tracking/formint-pos"
    icon: "i-lucide-target"
  - label: "دراسة حالة — طابور عدم الاتصال"
    to: "/docs/ar/agenda/case-studies/pos-offline-queue"
    icon: "i-lucide-arrow-right"
  - label: "دليل المكتبات"
    to: "/docs/en/libs/README"
    icon: "i-lucide-book"
---

# مزامنة المحطات المتعددة — دراسة حالة POS

> **التاريخ:** 2026-08-31 | **الحالة:** نشطة
> **النطاق:** بث WebSocket فوري + سحب حِزم التغييرات (`/sync/changes`، `/sync/ack`، `/sync/trigger`) بين محطات نقطة البيع
> **تتبّع الميزات:** [`feature-tracking/formint-pos.md`](../feature-tracking/formint-pos.md) § إدارة المحطات المتعددة
> **ذو صلة:** [`pos-offline-queue.md`](./pos-offline-queue.md)، [`pos-qr-menu.md`](./pos-qr-menu.md)

---

## 1. السياق

تحتاج نقطة بيع في مطعم إلى عدة محطات (الكاشير، المطبخ، البار، الطلبات الخارجية)
تبقى متزامنة. فعند إنشاء عملية بيع على محطة، يجب أن تراها الأخريات فوراً — تظهر
تذاكر المطبخ، ويتحدّث المخزون، وتنعكس تحويلات الفروع على كل المحطات.

**القيود:**
- قد تكون المحطات على شبكات مختلفة (شبكة محلية، واي فاي، هاتف)
- بعض المحطات تعمل دون اتصال (انظر [دراسة حالة طابور عدم الاتصال](./pos-offline-queue.md))
- الفورية مفضّلة لكنها غير إلزامية — الاتساق النهائي مقبول
- يجب التعامل مع انهيار المحطات وإعادة اتصالها بسلاسة

---

## 2. البنية

### 2.1 نظرة عامة على تدفّق المزامنة

```mermaid
graph TB
    subgraph "POS Terminal A"
        TA["Terminal A<br/>(Front Counter)"]
        TA_APP["POS App"]
        TA_DB["Local SQLite"]
    end

    subgraph "POS Terminal B"
        TB["Terminal B<br/>(Kitchen Display)"]
        TB_APP["KDS App"]
        TB_DB["Local SQLite"]
    end

    subgraph "POS Terminal C"
        TC["Terminal C<br/>(Bar)"]
        TC_APP["POS App"]
        TC_DB["Local SQLite"]
    end

    subgraph "Sync Server"
        WS["WebSocket Server<br/>Broadcast"]
        SYNC_API["Sync REST API<br/>/sync/changes, /sync/ack, /sync/trigger"]
        CLOUD_DB["Cloud Database<br/>Source of truth"]
    end

    TA_APP -->|1. Sale created| TA_DB
    TA_APP -->|2. POST /sync/changes| SYNC_API
    SYNC_API -->|3. Store in cloud| CLOUD_DB
    SYNC_API -->|4. Broadcast via WS| WS
    WS -->|5. Push to terminals| TB_APP
    WS -->|5. Push to terminals| TC_APP
    TB_APP -->|6. Apply change| TB_DB
    TC_APP -->|6. Apply change| TC_DB
    TB_APP -->|7. POST /sync/ack| SYNC_API
    TC_APP -->|7. POST /sync/ack| SYNC_API
```
![Rendered diagram](/agenda/diagrams/case-studies-pos-multi-terminal-sync-1.svg)

### 2.2 بروتوكول حِزم التغييرات

```mermaid
sequenceDiagram
    participant T1 as Terminal A
    participant API as Sync API
    participant DB as Cloud DB
    participant T2 as Terminal B
    participant T3 as Terminal C

    T1->>API: POST /sync/changes
    Note over T1,API: { changes: [...], branch_id, timestamp }

    API->>DB: Store changeset
    DB-->>API: changeset_id

    API->>T2: WebSocket broadcast
    Note over API,T2: { changeset_id, branch_id }

    API->>T3: WebSocket broadcast
    Note over API,T3: { changeset_id, branch_id }

    T2->>API: POST /sync/ack
    Note over T2,API: { changeset_id, status: applied }

    T3->>API: POST /sync/ack
    Note over T3,API: { changeset_id, status: applied }

    API->>DB: Update changeset status
```
![Rendered diagram](/agenda/diagrams/case-studies-pos-multi-terminal-sync-2.svg)

### 2.3 سحب حِزم التغييرات (بديل الاستطلاع)

```mermaid
graph LR
    T["Terminal<br/>offline or no WS"] -->|POST /sync/trigger| A["Sync API"]
    A -->|Returns| C["Changeset<br/>since last ack"]
    T -->|POST /sync/changes| A
    A -->|Store| DB["Cloud DB"]
```
![Rendered diagram](/agenda/diagrams/case-studies-pos-multi-terminal-sync-3.svg)

### 2.4 حلّ التعارضات

```mermaid
stateDiagram-v2
    [*] --> NoConflict: Single terminal changed
    NoConflict --> Applied: Ack received

    [*] --> ConflictDetected: Multiple terminals changed same record
    ConflictDetected --> ManualResolve: Show conflict UI
    ManualResolve --> Applied: User chooses winner
    ManualResolve --> AutoLastWrite: Auto-resolve (last write wins)
    AutoLastWrite --> Applied: Ack sent

    Applied --> [*]
```
![Rendered diagram](/agenda/diagrams/case-studies-pos-multi-terminal-sync-4.svg)

---

## 3. التنفيذ

### 3.1 بث WebSocket

**النقطة:** اتصال WebSocket لإشعار التغييرات الفوري.

**ما يبثّه:**
- `changeset_id` — معرّف فريد لدفعة التغييرات
- `branch_id` — الفرع الذي أتى منه التغيير
- `change_type` — بيع، مخزون، تحويل، إلخ

**سلوك إعادة الاتصال:** تُعيد المحطات الاشتراك عند إعادة الاتصال، وتسحب أي حِزم
تغييرات فاتتها منذ آخر إقرار لها.

### 3.2 واجهة سحب حِزم التغييرات

```python
# POST /sync/changes — submit changes from terminal
{
    "branch_id": "branch-1",
    "timestamp": "2026-08-31T12:00:00Z",
    "changes": [
        {"type": "sale", "sale_id": "sale-123", "data": {...}},
        {"type": "inventory", "product_id": "prod-456", "delta": -1},
    ]
}

# POST /sync/ack — acknowledge changeset applied
{
    "changeset_id": "cs-789",
    "status": "applied",  # or "conflict"
    "conflict_info": {...}  # if status is conflict
}

# POST /sync/trigger — request pending changesets
{
    "branch_id": "branch-1",
    "since": "2026-08-31T11:00:00Z"  # last ack timestamp
}
```

### 3.3 مزامنة آمنة التكرار

حِزم التغييرات آمنة التكرار — فتطبيق الحِزمة نفسها مرتين لا يكرّر البيانات. ويحمل
كل تغيير معرّفاً فريداً، وتتتبّع المحطة الحِزم التي طبّقتها بالفعل.

### 3.4 تحويلات الفروع

```mermaid
graph LR
    B1["Branch A<br/>(item leaving)"] -->|Transfer out| S["Sync Server"]
    B2["Branch B<br/>(item arriving)"] -->|Transfer in| S
    S -->|Broadcast transfer| B1
    S -->|Broadcast transfer| B2
```
![Rendered diagram](/agenda/diagrams/case-studies-pos-multi-terminal-sync-5.svg)

---

## 4. النتائج

### 4.1 ما ينجح

| النتيجة | الدليل |
|---------|----------|
| مزامنة فورية بين المحطات | يوصل بث WebSocket التغييرات في أقل من 100ms على الشبكة المحلية |
| حِزم تغييرات آمنة التكرار | إعادة تطبيق الحِزمة نفسها آمنة |
| كشف التعارض | تحرير عدة محطات للسجل نفسه يُشغّل واجهة التعارض |
| صمود دون اتصال | تُصطف المحطات التغييرات عند عدم الاتصال (انظر دراسة حالة طابور عدم الاتصال) |
| تحويلات الفروع | تنتقل الأصناف بين الفروع مع المزامنة |

### 4.2 الأداء

| المقياس | القيمة |
|--------|-------|
| زمن بث WebSocket (شبكة محلية) | أقل من 100ms |
| سحب حِزم التغييرات (بديل الاستطلاع) | عند الطلب، نحو 100-500ms |
| أقصى حجم لحِزمة تغييرات | قابل للتهيئة لكل فرع |

---

## 5. الدروس المستفادة

### 5.1 المزيج الهجين (WebSocket + استطلاع) أكثر متانة من WebSocket وحده

تفشل مزامنة WebSocket الصرفة عندما تنقطع المحطات أو تكون اتصالاتها متذبذبة. أما
المقاربة الهجينة (WebSocket للدفع، واستطلاع `/sync/trigger` كبديل) فتعني أن
المحطات تتقارب دائماً.

**الدرس:** احتفظ دائماً ببديل سحب للمزامنة الفورية. فالشبكات غير موثوقة.

### 5.2 الأمان التكراري غير قابل للتفاوض

بدون حِزم تغييرات آمنة التكرار، تؤدي إعادة المزامنة بعد خطأ شبكي إلى تكرار
المبيعات ومضاعفة احتساب المخزون. ويجب أن يحمل كل تغيير معرّفاً فريداً وأن تتتبّع
المحطة ما طبّقته.

**الدرس:** صمّم المزامنة لتكون آمنة عند إعادة المحاولة. مفاتيح أمان تكراري على كل تغيير.

### 5.3 حلّ التعارضات يحتاج واجهة، لا منطقاً فقط

عندما تعدّل محطتان السجل نفسه، يستطيع النظام كشف التعارض، لكن الحلّ قرار تجاري.
وعرض التعارض للمستخدم مع النسختين أنفع من اختيار فائز بصمت.

**الدرس:** اكشف التعارضات آلياً، وحُلّها بمشاركة المستخدم.

---

## 6. الوثائق ذات الصلة

| المستند | المسار |
|----------|------|
| تتبّع الميزات — إدارة تعدد الفروع | [`../feature-tracking/formint-pos.md`](../feature-tracking/formint-pos.md) § إدارة تعدد الفروع |
| دراسة حالة — طابور عدم الاتصال | [./pos-offline-queue.md](./pos-offline-queue.md) |
| دراسة حالة — قائمة QR | [./pos-qr-menu.md](./pos-qr-menu.md) |
| دراسة حالة — وسم مزامنة DataToken | [./data-token-sync-tagging.md](./data-token-sync-tagging.md) |
| خارطة الميزات | [`../../features/feature-roadmap.md`](../../features/feature-roadmap.md) |
| وثائق منتج نقطة البيع | [`../../projects/formints/`](../../projects/formints/) |

---

## ملاحظات وإرشادات

- مزامنة المحطات المتعددة جزء من ميزة إدارة تعدد الفروع (P0، مُشحونة)
- يستخدم بروتوكول المزامنة REST + WebSocket — بلا بروتوكول مخصّص
- المحطات مسؤولة عن تتبّع آخر طابع زمني لإقرارها
- واجهة التعارض لكل منتج — طبقة المزامنة تكشف، وطبقة المنتج تحلّ

<!-- AI-generated: review needed -->
