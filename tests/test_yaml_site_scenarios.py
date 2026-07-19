"""Validate YAML site scenario definitions used by workspace smoke runners."""
from __future__ import annotations

from pathlib import Path

TESTS_ROOT = Path(__file__).resolve().parent
ROOT = TESTS_ROOT.parent
SCENARIOS = sorted(TESTS_ROOT.glob("*-tests.yaml"))


def parse_scalar(value: str):
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        return [item.strip() for item in inner.split(",") if item.strip()]
    if value.isdigit():
        return int(value)
    return value


def load_yaml_subset(path: Path) -> dict:
    data: dict = {}
    current_key: str | None = None
    current_item: dict | None = None
    for raw_line in path.read_text().splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()
        if indent == 0 and ":" in line:
            key, value = line.split(":", 1)
            current_key = key
            current_item = None
            if value.strip():
                data[key] = parse_scalar(value)
            else:
                data[key] = [] if key == "routes" else {}
        elif current_key == "routes" and line.startswith("- "):
            current_item = {}
            data[current_key].append(current_item)
            key, value = line[2:].split(":", 1)
            current_item[key] = parse_scalar(value)
        elif current_key == "routes" and current_item is not None and ":" in line:
            key, value = line.split(":", 1)
            current_item[key] = parse_scalar(value)
        elif isinstance(data.get(current_key), dict) and ":" in line:
            key, value = line.split(":", 1)
            data[current_key][key] = parse_scalar(value)
    return data


def test_yaml_scenario_files_exist_for_all_sites():
    assert {path.name for path in SCENARIOS} == {
        "ctc-website-tests.yaml",
        "lms-tests.yaml",
        "vresume-tests.yaml",
    }


def test_yaml_scenarios_have_unique_ports_and_commands():
    seen_ports = set()
    for path in SCENARIOS:
        scenario = load_yaml_subset(path)
        assert scenario["site"]
        assert scenario["base_url"].startswith("http://")
        assert scenario["port"] not in seen_ports
        seen_ports.add(scenario["port"])
        assert "check" in scenario["commands"]
        assert "build" in scenario["commands"]
        assert scenario["routes"]
