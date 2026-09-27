"""Regression tests for the site-level auth mixins.

Both tests here pin bugs that the suite could not see before, because neither
one is reachable through the happy path.
"""

from __future__ import annotations


def test_process_registration_does_not_shadow_the_gettext_alias():
    """`_` must stay the module-level gettext alias inside the method.

    ``AuthProcessorMixin.process_registration`` reports validation failures with
    ``_("Registration failed")``. The module imports ``gettext_lazy as _``, so
    any local assignment to ``_`` anywhere in the method makes ``_`` a *local*
    for the whole body -- and the earlier call then raises ``UnboundLocalError``
    on every invalid submission, which is the path users hit most often.

    The original offender was ``group, _ = Group.objects.get_or_create(...)``.
    This asserts on the compiled code object rather than driving a request,
    because the bug is a scoping mistake, not a behavior of the success path.
    """
    from django_fusion.site.auth.mixins import AuthProcessorMixin

    code = AuthProcessorMixin.process_registration.__code__
    assert "_" not in code.co_varnames, (
        "`process_registration` declares a local named `_`, which shadows the "
        "module-level `gettext_lazy as _` alias and breaks the validation-error "
        "path with UnboundLocalError. Use a named throwaway (e.g. `_created`)."
    )


def test_enhancement_plan_exposes_project_guidance():
    """The enhancement plan resolves guidance and must return it.

    ``designer_webapp_enhancement_plan`` called ``_project_guidance(project)``
    and then discarded the result, so callers could not read the project's audit
    guidance from the plan even though ``designer_website_audit`` returned it.
    """
    from django_fusion.plugins.designer.website import designer_webapp_enhancement_plan

    result = designer_webapp_enhancement_plan(
        project="example",
        surface="webapp",
        sections=[{"name": "Hero", "is_multi_column": False}],
    )

    assert "guidance" in result
    assert result["guidance"]["surface"]
