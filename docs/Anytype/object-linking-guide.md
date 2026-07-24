---
# yaml-language-server: $schema=schemas/page.schema.json
Object type:
    - Page
Creation date: "2026-07-24T19:54:39Z"
Created by:
    - mammhoud
id: bafyreicp6hpjenivis7zoctnjz3nykjj2geihjiozkofwqpxcjgcwgr5q4
---
# Object Linking Guide   
> Import Instruction: Use these Relations in AnyType to link related documentation objects.   
> Apply the "Object" property type with the specified relation name.   

 --- 
## Relation Definitions   
|                   Name   <br> |                    Type   <br> |        Source → Target   <br> |                                 Description   <br> |
|:------------------------------|:-------------------------------|:------------------------------|:---------------------------------------------------|
| `Related Architecture`   <br> |   Object → Architecture   <br> |     Any → Architecture   <br> | Links features/guides to architectural docs   <br> |
|      `Related Feature`   <br> |        Object → Feature   <br> |          Any → Feature   <br> |  Links architectures/guides to feature docs   <br> |
|        `Related Guide`   <br> |          Object → Guide   <br> |            Any → Guide   <br> |      Links features/architectures to guides   <br> |
|    `Related Reference`   <br> |      Object → Reference   <br> |        Any → Reference   <br> |   Links features/guides to API/command refs   <br> |
|           `Depends On`   <br> |   Object → Task/Feature   <br> |    Task → Task/Feature   <br> |         Dependency chain for implementation   <br> |
|           `Implements`   <br> |   Object → Architecture   <br> |   Guide → Architecture   <br> |     A guide that implements an architecture   <br> |
|             `See Also`   <br> |            Object → Any   <br> |              Any → Any   <br> |                     General cross-reference   <br> |

 --- 
## Graph View Connections   
```
                    Architecture
                   /     |      \
                  ▼      ▼       ▼
             Features  Guides  References
                  \      |      /
                   ▼     ▼     ▼
                   Relations Hub
                   (Backlinks)

```
 --- 
## Usage in Files   
Each markdown file ends with a `Related Docs` section using → arrows:   
```
## Related Docs
- → `architecture/editions-overview.md` — Edition comparison
- → `features/pos-mini.md` — pos-mini features
- → `guides/setup.md` — Setup guide

```
In AnyType, convert these → links to Object Relations by:   
1. Opening the target document   
2. Adding a "Related Architecture" or "Related Feature" property   
3. Linking it back to the source document   
[Object Linking Guide](object-linking-guide.md)    
