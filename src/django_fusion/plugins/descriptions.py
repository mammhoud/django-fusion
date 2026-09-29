"""The plugin-description contract — where a ``PRODUCT.md`` lives and what it may claim.

Owning plan: ``docs/plans/structa-cloud/plugins/product-description-and-attach.md``.
The plan's rule is the whole point of this module:

    a description may only state what the repository can prove.

This module is the **single authority** for that rule, because two consumers
enforce it and they must not drift:

* ``manage.py plugin {describe,doctor,check}`` — the runtime side, which reads
  the live :class:`~django_fusion.plugins.registry.PluginRegistry` for
  capabilities/signals.
* ``scripts/generate_plugin_products.py`` — the docs gate, which reads the
  catalog with :mod:`ast` so it can run in a bare CI job with no virtualenv.

**Deliberately stdlib-only and free of intra-package imports.** ``django_fusion``
itself imports nothing (an empty ``__init__``), but ``django_fusion.plugins``
imports :mod:`pluggy` via ``.manager``, so the gate cannot ``import
django_fusion.plugins.descriptions`` in a bare interpreter. The gate therefore
loads this file *by path* (``importlib.util.spec_from_file_location``) instead of
by package import — no package ``__init__`` executes, so no dependency is
required. ``tests/test_plugin_command.py`` asserts the two readers agree, so this
sharing cannot silently rot.

Rules enforced by :func:`check_product` (the plan's D1-D3):

* **D1** — ``capabilities`` / ``signals`` must equal what the ``PluginSpec``
  registers, **in both directions**. Advertising a capability the plugin does not
  provide fails, and so does a plugin capability the description silently omits.
* **D2** — every ``evidence[].path`` must exist in the tree.
* **D3** — ``limits`` is mandatory and non-empty; an honest "what it does not do"
  is what keeps a listing free of unprovable claims.

The ``summary`` ↔ ``PluginSpec.description`` comparison is a **warning**, never a
failure: the runtime one-liner is hand-maintained in ``catalog.py`` alongside
curated comments, so drift is reported for a human instead of the gate either
blocking on prose or silently rewriting source.
"""
from __future__ import annotations

from pathlib import Path

#: The description filename, inside a plugin's own package.
PRODUCT_FILENAME = "PRODUCT.md"

#: Frontmatter keys every PRODUCT.md must carry.
REQUIRED_KEYS = ("id", "title", "summary", "capabilities", "signals", "limits")

#: Values ``surface`` may take. Anything else is a typo or an unrecorded class.
VALID_SURFACES = ("first-party", "third-party")

#: ``src/django_fusion`` — the package root names are resolved against.
SPEC_PACKAGE_ROOT = Path(__file__).resolve().parents[1]

#: Keys whose empty value starts a list in the frontmatter block.
_LIST_KEYS = {"capabilities", "signals", "evidence", "limits", "requires", "provides"}

#: Words that assert a **commercial** claim rather than a capability (rule D4).
#:
#: Deliberately a short, explicit list of superlatives instead of a general
#: "marketing language" detector: a fuzzy rule would either pass the claims it is
#: meant to catch or fail engineering prose ("free function", "best-effort"), and
#: a gate that cries wolf gets disabled. Each term here is a phrase a buyer-facing
#: listing would need evidence for, so the fix is always the same — add the claim to
#: ``docs/plans/marketing-claims.md``, or drop the word.
COMMERCIAL_TERMS: tuple[str, ...] = (
    "best-in-class",
    "world-class",
    "industry-leading",
    "market-leading",
    "cutting-edge",
    "state-of-the-art",
    "revolutionary",
    "blazingly",
    "effortless",
    "effortlessly",
    "unlimited",
    "fastest",
    "cheapest",
    "most advanced",
    "number one",
    "#1",
)


def find_commercial_claims(text: str) -> list[str]:
    """Return the commercial terms a description uses (empty for engineering prose)."""
    lowered = text.lower()
    return sorted({term for term in COMMERCIAL_TERMS if term in lowered})


def uncovered_claims(terms: list[str], claims_text: str) -> list[str]:
    """Terms that no entry in ``marketing-claims.md`` backs."""
    lowered = claims_text.lower()
    return [term for term in terms if term not in lowered]


#: The evidence file a commercial claim must appear in (rule D4).
CLAIMS_FILE = Path("docs") / "plans" / "marketing-claims.md"


def load_claims(repo_root: Path) -> str:
    """Read the claims register, or ``""`` when this checkout has none.

    An empty register is the strict reading, not the permissive one: with no file
    to cite, no commercial term is backed, so any claim fails. Descriptions
    without claims are unaffected, which is why this is safe to pass always.
    """
    try:
        return (repo_root / CLAIMS_FILE).read_text(encoding="utf-8")
    except OSError:
        return ""


def default_repo_root() -> Path:
    """The repository root, derived from this file's location.

    ``src/django_fusion`` → ``src`` → ``libs/django-fusion`` → ``libs`` →
    ``<repo>/``, i.e. ``SPEC_PACKAGE_ROOT.parents[3]``. Used to resolve
    ``evidence[].path`` entries, which are written repo-relative (e.g.
    ``libs/django-fusion/src/…``) so a claim is checkable from anywhere.

    Only meaningful inside the monorepo layout. A site consuming the library
    from a wheel gets a root that does not exist, and should pass ``repo_root``
    explicitly — which is why every caller-facing function accepts it.
    """
    return SPEC_PACKAGE_ROOT.parents[3]


# ─────────────────────────────────────────────────────────────────────────────
# Where a description lives
# ─────────────────────────────────────────────────────────────────────────────
def spec_path(name: str, *, package_root: Path | None = None) -> Path:
    """Filesystem path a spec's dotted name points at (package dir or module file)."""
    root = package_root or SPEC_PACKAGE_ROOT
    relative = name[len("django_fusion.") :] if name.startswith("django_fusion.") else name
    return root / Path(*relative.split("."))


def expected_product_path(name: str, *, package_root: Path | None = None) -> Path | None:
    """Canonical PRODUCT.md location for a spec, or ``None`` if it is not shipped here.

    Two shapes exist in the catalog. A plugin shipped as a **package** keeps its
    description inside it (``plugins/htmx/PRODUCT.md``) so the file travels with
    the distribution. A plugin shipped as a **single module**
    (``django_fusion.config.staticfiles``) has no directory of its own, so its
    description sits beside it as ``staticfiles.PRODUCT.md`` — the same directory,
    still unambiguous.
    """
    path = spec_path(name, package_root=package_root)
    if path.is_dir():
        return path / PRODUCT_FILENAME
    if path.with_suffix(".py").exists():
        return path.parent / f"{path.name}.PRODUCT.md"
    return None


def product_path(model: str, name: str, *, root: Path) -> Path:
    """The description path for a **product** plugin: ``<plugins dir>/<name>/PRODUCT.md``."""
    del model  # kept for a symmetric call shape with expected_product_path
    return root / name / PRODUCT_FILENAME


# ─────────────────────────────────────────────────────────────────────────────
# Frontmatter — the small subset docs/ uses
# ─────────────────────────────────────────────────────────────────────────────
def parse_scalar(raw: str):
    """Parse one frontmatter value: inline list, bool, or bare/quoted string."""
    raw = raw.strip()
    if raw.startswith("[") and raw.endswith("]"):
        body = raw[1:-1].strip()
        if not body:
            return []
        return [item.strip().strip("'\"") for item in body.split(",") if item.strip()]
    if raw in {"true", "false"}:
        return raw == "true"
    return raw.strip("'\"")


def read_frontmatter(path: Path) -> dict:
    """Parse the leading ``---`` block. Lists of dicts (``evidence``) included.

    Kept deliberately small — enough for the PRODUCT.md contract, and it fails
    loudly (returns ``{}``) on anything it cannot read rather than guessing.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return {}
    if not text.startswith("---"):
        return {}
    lines = text.splitlines()
    try:
        end = lines.index("---", 1)
    except ValueError:
        return {}

    data: dict = {}
    current_list: str | None = None
    current_item: dict | None = None

    for line in lines[1:end]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indented = line.startswith((" ", "\t"))
        stripped = line.strip()

        if indented and current_list and stripped.startswith("- "):
            current_item = {}
            data[current_list].append(current_item)
            body = stripped[2:]
            if ":" in body:
                key, _, value = body.partition(":")
                current_item[key.strip()] = parse_scalar(value)
            continue
        if indented and current_item is not None and ":" in stripped:
            key, _, value = stripped.partition(":")
            current_item[key.strip()] = parse_scalar(value)
            continue
        if ":" not in stripped:
            continue

        key, _, value = stripped.partition(":")
        key, value = key.strip(), value.strip()
        if value == "":
            data[key] = [] if key in _LIST_KEYS else ""
            current_list = key if isinstance(data[key], list) else None
            current_item = None
        else:
            data[key] = parse_scalar(value)
            current_list = None
            current_item = None
    return data


def read_body(path: Path) -> str:
    """Return the markdown after the frontmatter block (what ``describe`` prints)."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return ""
    if not text.startswith("---"):
        return text
    lines = text.splitlines()
    try:
        end = lines.index("---", 1)
    except ValueError:
        return text
    return "\n".join(lines[end + 1 :]).strip()


# ─────────────────────────────────────────────────────────────────────────────
# The rules
# ─────────────────────────────────────────────────────────────────────────────
def check_product(
    path: Path,
    *,
    name: str,
    capabilities: set[str] | frozenset[str],
    signals: set[str] | frozenset[str],
    description: str = "",
    repo_root: Path | None = None,
    claims_text: str | None = None,
) -> tuple[list[str], list[str]]:
    """Return ``(failures, warnings)`` for one PRODUCT.md against its spec.

    Capabilities/signals/description come from the caller so the same rule serves
    both a live registry (the management command) and an ``ast``-parsed catalog
    (the gate) without either importing the other.
    """
    failures: list[str] = []
    warnings: list[str] = []
    root = repo_root or default_repo_root()
    front = read_frontmatter(path)
    if not front:
        return ([f"{path.name}: frontmatter is missing or unreadable"], warnings)

    for key in REQUIRED_KEYS:
        if key not in front:
            failures.append(f"missing required key `{key}`")

    short = name.rsplit(".", 1)[-1]
    if front.get("id") and front["id"] != f"plugin.{short}":
        failures.append(f"`id` is {front['id']!r}, expected 'plugin.{short}'")

    if front.get("surface") and front["surface"] not in VALID_SURFACES:
        failures.append(f"`surface` is {front['surface']!r}, expected one of {VALID_SURFACES}")

    # D1 — capabilities and signals must match the spec in BOTH directions.
    for key, expected in (("capabilities", set(capabilities)), ("signals", set(signals))):
        declared = set(front.get(key) or [])
        for missing in sorted(expected - declared):
            failures.append(f"[D1] {key} omits {missing!r} — the PluginSpec registers it")
        for extra in sorted(declared - expected):
            failures.append(f"[D1] {key} claims {extra!r} — no PluginSpec provides it")

    # D3 — limits are mandatory and may not be empty.
    if not front.get("limits"):
        failures.append("[D3] `limits` is empty — an honest 'what it does not do' is required")

    # D2 — every cited path must exist.
    evidence = front.get("evidence")
    if not evidence:
        failures.append("[D2] `evidence` is empty — a description must cite the files that prove it")
    else:
        for item in evidence:
            if not isinstance(item, dict) or not item.get("path"):
                failures.append("[D2] evidence entry has no `path`")
                continue
            if not (root / str(item["path"])).exists():
                failures.append(f"[D2] evidence path does not exist: {item['path']}")

    # D4 — commercial wording must be backed by a claims entry.
    if claims_text is not None:
        used = find_commercial_claims(path.read_text(encoding="utf-8"))
        for term in uncovered_claims(used, claims_text):
            failures.append(
                f"[D4] uses the commercial claim {term!r} — add it to "
                "docs/plans/marketing-claims.md or drop the word"
            )

    # Warning only — see the module docstring. Compared by word overlap rather
    # than substring: a summary may be a readable paraphrase, it just may not say
    # something unrelated to what the runtime description claims.
    summary = str(front.get("summary") or "")
    if description:
        words = {w.strip(".,;:()").lower() for w in summary.split() if len(w) > 3}
        if words:
            haystack = description.lower()
            overlap = sum(1 for word in words if word in haystack) / len(words)
            if overlap < 0.6:
                warnings.append(
                    f"`summary` shares only {overlap:.0%} of its words with "
                    "PluginSpec.description (runtime one-liner) — update catalog.py or the summary"
                )
    return failures, warnings


def check_product_for_spec(
    spec, *, repo_root: Path | None = None, claims_text: str | None = None
) -> tuple[list[str], list[str]]:
    """Convenience wrapper for a live registry ``PluginSpec``.

    Returns ``(["no PRODUCT.md — expected at …"], [])`` when the description is
    missing entirely, so callers get one uniform result shape.
    """
    path = expected_product_path(spec.name)
    if path is None:
        return ([f"{spec.name}: not shipped in this library"], [])
    if not path.exists():
        return ([f"{spec.name}: no PRODUCT.md — expected at {path}"], [])
    root = repo_root or default_repo_root()
    return check_product(
        path,
        name=spec.name,
        capabilities=spec.capabilities,
        signals=spec.signals,
        description=spec.description,
        repo_root=root,
        claims_text=claims_text if claims_text is not None else load_claims(root),
    )
