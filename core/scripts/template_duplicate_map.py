from __future__ import annotations

import hashlib
from collections import defaultdict
from pathlib import Path

ROOT = Path('applications')


def template_roots() -> list[Path]:
    return sorted(p for p in ROOT.rglob('templates') if '.venv' not in p.parts and p.is_dir())


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    by_relative: dict[Path, list[Path]] = defaultdict(list)
    for root in template_roots():
        for template in sorted(p for p in root.rglob('*') if p.is_file()):
            by_relative[template.relative_to(root)].append(template)

    print('# Template duplicate map')
    print()
    print('Generated from `Path("applications").rglob("templates")` with relative file paths under each template root.')
    print()
    for relative, files in sorted(by_relative.items(), key=lambda item: str(item[0])):
        if len(files) < 2:
            continue
        print(f'## {relative}')
        groups: dict[str, list[Path]] = defaultdict(list)
        for file in files:
            groups[sha256(file)].append(file)
        if len(groups) == 1:
            classification = 'identical shared template candidate'
        else:
            classification = 'variant/site-specific review needed'
        print(f'- classification: {classification}')
        for digest, group in sorted(groups.items(), key=lambda item: item[0]):
            print(f'- sha256: `{digest[:12]}`')
            for file in group:
                print(f'  - `{file}`')
        print()


if __name__ == '__main__':
    main()
