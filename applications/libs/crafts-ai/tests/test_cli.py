from crafts_ai.cli import main, package_info


def test_package_info_uses_expected_import_name() -> None:
    assert package_info()["import_package"] == "crafts_ai"


def test_health_command(capsys) -> None:
    assert main(["health"]) == 0
    assert '"status": "ok"' in capsys.readouterr().out


def test_projects_command(capsys) -> None:
    assert main(["projects"]) == 0
    out = capsys.readouterr().out
    assert '"website": "VResume"' in out
    assert '"package": "crafts-ai"' in out


def test_rseal_plan_command(tmp_path, capsys) -> None:
    sample = tmp_path / "sample.py"
    sample.write_text("from django_rseal.ai.integrations import AIIntegration\n", encoding="utf-8")
    assert main(["rseal-plan", str(tmp_path)]) == 0
    assert '"status": "move-to-crafts-ai"' in capsys.readouterr().out
