from crafts_ai.cli import main, package_info


def test_package_info_uses_expected_import_name() -> None:
    assert package_info()["import_package"] == "crafts_ai"


def test_health_command(capsys) -> None:
    assert main(["health"]) == 0
    assert '"status": "ok"' in capsys.readouterr().out
