---
# yaml-language-server: $schema=schemas/page.schema.json
Object type:
    - Page
Creation date: "2026-07-24T19:54:39Z"
Created by:
    - mammhoud
id: bafyreieogldmfz2mwu5aqplkgs4k4dxfw2w455emywcrzaaqqenh23g5uu
---
# Reference — Tauri Commands   
**Type:** Reference 📚
T**ags: **#`pos-mini `#`pos-solo `#`pos-full `#`tauri `#`backend
`S**tatus: **Published
C**ategory: **CLI   
 --- 
## Command Categories   
```
┌──────────────────────────────────────────────────┐
│                 Tauri Commands                    │
├───────────┬──────────┬───────────┬───────────────┤
│ Products  │  Sales   │ Inventory │  System       │
├───────────┼──────────┼───────────┼───────────────┤
│ get       │ add_sale │ get       │ get_settings  │
│ add       │ invoice  │ record    │ save_settings │
│ update    │ PDF/Print│ adjust    │ export_db     │
│ delete    │          │           │ import_db     │
│ categories│          │           │ change_pwd    │
└───────────┴──────────┴───────────┴───────────────┘

```
 --- 
## Products   
|           Command   <br> |      Returns   <br> |                                 Params   <br> |
|:-------------------------|:--------------------|:----------------------------------------------|
|   `get\_products`   <br> |  `Product[]`   <br> |                                      —   <br> |
|    `add\_product`   <br> | `id: number`   <br> | `{ name, price, unit, category\_id? }`   <br> |
| `update\_product`   <br> |       `void`   <br> |                    `{ id, ...fields }`   <br> |
| `delete\_product`   <br> |       `void`   <br> |                               `{ id }`   <br> |
| `get\_categories`   <br> | `Category[]`   <br> |                                      —   <br> |

## Sales   
|                  Command   <br> |         Returns   <br> |                                            Params   <br> |
|:--------------------------------|:-----------------------|:---------------------------------------------------------|
|              `add\_sale`   <br> |       `Receipt`   <br> | `{ sale: NewSaleData, items: NewSaleItemData[] }`   <br> |
|          `get\_receipts`   <br> |     `Receipt[]`   <br> |                             `{ limit?, offset? }`   <br> |
| `download\_invoice\_pdf`   <br> | `string` (path)   <br> |                 `{ invoice\_type, items[], ... }`   <br> |

## Employees   
|                Command   <br> |      Returns   <br> |                                     Params   <br> |
|:------------------------------|:--------------------|:--------------------------------------------------|
|       `get\_employees`   <br> | `Employee[]`   <br> |                   `{ include\_inactive? }`   <br> |
|        `add\_employee`   <br> |         `id`   <br> | `{ name, phone, email, type\_id, salary }`   <br> |
|     `update\_employee`   <br> |       `void`   <br> |                        `{ id, ...fields }`   <br> |
| `deactivate\_employee`   <br> |       `void`   <br> |                                   `{ id }`   <br> |

## Inventory   
|               Command   <br> |        Returns   <br> |                                        Params   <br> |
|:-----------------------------|:----------------------|:-----------------------------------------------------|
|    `get\_ingredients`   <br> | `Ingredient[]`   <br> |                                             —   <br> |
|     `add\_ingredient`   <br> |           `id`   <br> | `{ name, unit, stock, reorder\_level, cost }`   <br> |
| `record\_transaction`   <br> |           `id`   <br> |  `{ ingredient\_id, quantity\_change, note }`   <br> |

## System   
|                 Command   <br> |           Returns   <br> |                                    Params   <br> |
|:-------------------------------|:-------------------------|:-------------------------------------------------|
|         `get\_settings`   <br> |        `Settings`   <br> |                                         —   <br> |
|        `save\_settings`   <br> |            `void`   <br> |                         `{ ...settings }`   <br> |
| `export\_database\_cmd`   <br> | `string` (base64)   <br> |                                         —   <br> |
| `import\_database\_cmd`   <br> |            `void`   <br> |                        `{ data: base64 }`   <br> |
| `change\_password\_cmd`   <br> |            `void`   <br> | `{ email, old\_password, new\_password }`   <br> |

 --- 
## Related Docs   
- → `features/pos-mini.md` — pos-mini feature details   
- → `guides/setup.md` — Running the app   
- → `references/database-schema.md` — Underlying DB schema   
[Reference — Tauri Commands](reference-tauri-commands.md)    
