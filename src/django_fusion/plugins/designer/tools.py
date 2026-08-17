"""MCP tool metadata for the django-fusion designer.

The shape follows MCP ``tools/list`` conventions while remaining independent
of a particular MCP SDK. Projects can adapt this mapping to FastMCP, an MCP
SDK server, or the included Django JSON-RPC view.
"""

from __future__ import annotations

MCP_DESIGNER_TOOLS = {
    "designer.website_audit": {
        "title": "Audit a website surface",
        "description": "Score structured website or webapp metadata against accessibility, responsive, content, interaction, asset, and anti-template-slop guidance without fetching URLs or changing files.",
        "inputSchema": {
            "type": "object",
            "required": ["project", "sections"],
            "properties": {
                "project": {"type": "string", "minLength": 1, "description": "Project identifier (e.g. precis-landing, precis, formint, or any project name). Must be a non-empty string."},
                "surface": {"type": "string", "enum": ["website", "webapp", "landing", "catalog", "dashboard"], "default": "website"},
                "audience": {"type": "string"},
                "vibe": {"type": "string"},
                "sections": {"type": "array", "minItems": 1, "maxItems": 50, "items": {"type": "object", "required": ["name"], "properties": {"name": {"type": "string"}, "kind": {"type": "string"}, "layout": {"type": "string"}, "has_visual": {"type": "boolean"}, "has_cta": {"type": "boolean"}, "has_eyebrow": {"type": "boolean"}, "is_multi_column": {"type": "boolean"}, "mobile_strategy": {"type": "string"}, "interactive_states": {"type": "array", "items": {"type": "string"}}, "text_words": {"type": "integer", "minimum": 0}}}},
                "design_variance": {"type": "integer", "minimum": 1, "maximum": 10, "default": 7},
                "motion_intensity": {"type": "integer", "minimum": 1, "maximum": 10, "default": 4},
                "visual_density": {"type": "integer", "minimum": 1, "maximum": 10, "default": 4},
                "dark_mode": {"type": "boolean", "default": True},
                "accessibility_reviewed": {"type": "boolean", "default": False},
                "real_assets_available": {"type": "boolean", "default": False},
                "cta_intents": {"type": "array", "maxItems": 50, "items": {"type": "string"}},
                "required_features": {"type": "array", "maxItems": 50, "items": {"type": "string"}},
            },
        },
        "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
    },
    "designer.webapp_enhancement_plan": {
        "title": "Plan website enhancements",
        "description": "Convert a structured website audit into an ordered, project-aware enhancement plan; it never edits or deploys code.",
        "inputSchema": {"type": "object", "required": ["project", "sections"], "properties": {"project": {"type": "string", "minLength": 1, "description": "Project identifier (e.g. precis-landing, precis, formint, or any project name). Must be a non-empty string."}, "surface": {"type": "string", "enum": ["website", "webapp", "landing", "catalog", "dashboard"]}, "sections": {"type": "array", "minItems": 1, "maxItems": 50, "items": {"type": "object", "required": ["name"], "properties": {"name": {"type": "string"}, "kind": {"type": "string"}, "layout": {"type": "string"}, "has_visual": {"type": "boolean"}, "has_cta": {"type": "boolean"}, "has_eyebrow": {"type": "boolean"}, "is_multi_column": {"type": "boolean"}, "mobile_strategy": {"type": "string"}, "interactive_states": {"type": "array", "items": {"type": "string"}}, "text_words": {"type": "integer", "minimum": 0}}}}, "audience": {"type": "string"}, "vibe": {"type": "string"}, "design_variance": {"type": "integer", "minimum": 1, "maximum": 10, "default": 7}, "motion_intensity": {"type": "integer", "minimum": 1, "maximum": 10, "default": 4}, "visual_density": {"type": "integer", "minimum": 1, "maximum": 10, "default": 4}, "dark_mode": {"type": "boolean", "default": True}, "accessibility_reviewed": {"type": "boolean", "default": False}, "real_assets_available": {"type": "boolean", "default": False}, "cta_intents": {"type": "array", "maxItems": 50, "items": {"type": "string"}}, "required_features": {"type": "array", "maxItems": 50, "items": {"type": "string"}}}},
        "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
    },
    "designer.component_catalog": {
        "title": "Browse fusion components",
        "description": "Search the registered django-fusion component catalog without changing project files.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Optional component name/path filter."},
                "limit": {"type": "integer", "minimum": 1, "maximum": 50, "default": 50},
            },
        },
        "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
    },
    "designer.wagtail_field": {
        "title": "Suggest a Wagtail field",
        "description": "Create a review-only schema for an approved Django or Wagtail field/block; it does not modify models.",
        "inputSchema": {
            "type": "object",
            "required": ["field_type", "name"],
            "properties": {
                "field_type": {"type": "string", "enum": ["char", "text", "rich_text", "image", "choice", "struct", "stream"]},
                "name": {"type": "string", "pattern": "^[A-Za-z_][A-Za-z0-9_]*$"},
                "label": {"type": "string"},
                "required": {"type": "boolean", "default": False},
                "help_text": {"type": "string"},
                "choices": {"type": "array", "maxItems": 50},
            },
        },
        "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
    },
    "designer.form_scaffold": {
        "title": "Draft a Django form",
        "description": "Generate a review-only Django form scaffold using django-fusion styling conventions.",
        "inputSchema": {
            "type": "object",
            "required": ["class_name", "fields"],
            "properties": {
                "class_name": {"type": "string", "pattern": "^[A-Za-z_][A-Za-z0-9_]*$"},
                "fields": {"type": "array", "maxItems": 50, "items": {"type": "object", "required": ["name"], "properties": {"name": {"type": "string", "pattern": "^[A-Za-z_][A-Za-z0-9_]*$"}, "type": {"type": "string", "enum": ["char", "email", "text", "integer", "boolean", "url"]}, "label": {"type": "string"}, "required": {"type": "boolean"}, "help_text": {"type": "string"}}}},
                "base": {"type": "string", "default": "BaseStyledForm"},
                "style_framework": {"type": "string", "enum": ["bootstrap", "tailwind"], "default": "bootstrap"},
            },
        },
        "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
    },
    "designer.table_scaffold": {
        "title": "Draft a data table",
        "description": "Generate a review-only django-tables2 table scaffold with project-owned authorization left to the caller.",
        "inputSchema": {
            "type": "object",
            "required": ["class_name", "columns"],
            "properties": {
                "class_name": {"type": "string", "pattern": "^[A-Za-z_][A-Za-z0-9_]*$"},
                "columns": {"type": "array", "maxItems": 50, "items": {"type": "object", "required": ["name"], "properties": {"name": {"type": "string", "pattern": "^[A-Za-z_][A-Za-z0-9_]*$"}, "label": {"type": "string"}, "orderable": {"type": "boolean"}}}},
                "base": {"type": "string", "default": "BaseTable"},
            },
        },
        "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
    },
    "designer.validate": {
        "title": "Validate a design draft",
        "description": "Validate a form, table, or Wagtail field draft and return a non-applied result.",
        "inputSchema": {"type": "object", "required": ["draft"], "properties": {"draft": {"type": "object", "required": ["kind"], "properties": {"kind": {"type": "string", "enum": ["django_form", "django_table", "wagtail_field"]}, "class_name": {"type": "string"}, "fields": {"type": "array"}, "columns": {"type": "array"}, "field_type": {"type": "string"}, "name": {"type": "string"}}}}},
        "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
    },
    "designer.preview": {
        "title": "Preview a registered component",
        "description": "Safely preview a registered component with JSON props; raw template source and file writes are forbidden.",
        "inputSchema": {
            "type": "object",
            "required": ["name"],
            "properties": {
                "name": {"type": "string", "description": "Exact registered component name or unambiguous path."},
                "props": {"type": "object", "default": {}},
                "max_chars": {"type": "integer", "minimum": 100, "maximum": 50000, "default": 20000},
            },
        },
        "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
    },
}
