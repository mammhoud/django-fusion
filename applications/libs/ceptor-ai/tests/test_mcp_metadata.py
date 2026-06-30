from ceptor_ai.mcp_server import MCP_FEATURES, MCP_FILE_STRUCTURE, latest_features


def test_latest_features_exposes_required_mcp_endpoints() -> None:
    paths = {feature["path"] for feature in MCP_FEATURES}

    assert {"/health", "/info", "/features", "/file-structure"}.issubset(paths)


def test_latest_features_exposes_documentation_file_structure() -> None:
    metadata = latest_features()

    assert metadata["package"] == "ceptor-ai"
    assert "docs/ai/latest_features.md" in metadata["file_structure"]["docs"]
    assert "applications/libs/ceptor-ai/src/ceptor_ai/mcp_server.py" in (
        metadata["file_structure"]["package"]
    )
    assert ".kilo/config.json" in MCP_FILE_STRUCTURE["kilo"]
