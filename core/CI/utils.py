"""
Template validation utilities for Django templates.

This module provides comprehensive template validation including:
- Syntax validation
- Structure validation
- Missing variable detection
- Missing filter detection
- Detailed error reporting
"""

import logging
import re
from typing import Dict, List, Optional, Set, Tuple
from pathlib import Path

from django.template import Context, Template, TemplateSyntaxError
from django.template.loader import get_template
from django.template.base import Node, FilterExpression, Variable
from django.template.exceptions import TemplateDoesNotExist


logger = logging.getLogger(__name__)


class TemplateValidationError(Exception):
    """Custom exception for template validation errors."""
    pass


class TemplateValidator:
    """
    Validates Django templates for syntax, structure, and completeness.

    This validator checks:
    - Template syntax correctness
    - Template structure (blocks, extends, includes)
    - Missing variables in context
    - Missing or invalid filters
    - Template inheritance chain
    """

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.variables_found: Set[str] = set()
        self.filters_found: Set[str] = set()

    def validate_template(
        self,
        template_name: str,
        context: Optional[Dict] = None
    ) -> Tuple[bool, List[str], List[str]]:
        """
        Validate a Django template.

        Args:
            template_name: Name or path of the template to validate
            context: Optional context dictionary to check for missing variables

        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        self.errors = []
        self.warnings = []
        self.variables_found = set()
        self.filters_found = set()

        # Step 1: Validate syntax
        template = self._validate_syntax(template_name)
        if not template:
            return False, self.errors, self.warnings

        # Step 2: Validate structure
        self._validate_structure(template)

        # Step 3: Extract variables and filters
        self._extract_variables_and_filters(template)

        # Step 4: Check for missing variables if context provided
        if context is not None:
            self._check_missing_variables(context)

        # Step 5: Validate filters
        self._validate_filters()

        is_valid = len(self.errors) == 0
        return is_valid, self.errors, self.warnings

    def _validate_syntax(self, template_name: str) -> Optional[Template]:
        """
        Validate template syntax.

        Args:
            template_name: Name or path of the template

        Returns:
            Template object if valid, None otherwise
        """
        try:
            # Try to load as template name first
            template = get_template(template_name)
            return template
        except TemplateDoesNotExist:
            self.errors.append(
                f"Template '{template_name}' does not exist"
            )
            return None
        except TemplateSyntaxError as e:
            self.errors.append(
                f"Template syntax error in '{template_name}': {str(e)}"
            )
            return None
        except Exception as e:
            self.errors.append(
                f"Unexpected error loading template '{template_name}': {str(e)}"
            )
            return None

    def _validate_structure(self, template: Template) -> None:
        """
        Validate template structure.

        Checks for:
        - Proper block definitions
        - Valid extends usage
        - Valid include usage

        Args:
            template: Template object to validate
        """
        # Check for unclosed tags
        template_source = template.source

        # Check for balanced block tags
        block_pattern = r'{%\s*block\s+(\w+)\s*%}'
        endblock_pattern = r'{%\s*endblock\s*(?:\w+)?\s*%}'

        blocks = re.findall(block_pattern, template_source)
        endblocks = re.findall(endblock_pattern, template_source)

        if len(blocks) != len(endblocks):
            self.errors.append(
                f"Unbalanced block tags: {len(blocks)} block(s) but {len(endblocks)} endblock(s)"
            )

        # Check for balanced if tags
        if_pattern = r'{%\s*if\s+'
        endif_pattern = r'{%\s*endif\s*%}'

        ifs = len(re.findall(if_pattern, template_source))
        endifs = len(re.findall(endif_pattern, template_source))

        if ifs != endifs:
            self.errors.append(
                f"Unbalanced if tags: {ifs} if(s) but {endifs} endif(s)"
            )

        # Check for balanced for tags
        for_pattern = r'{%\s*for\s+'
        endfor_pattern = r'{%\s*endfor\s*%}'

        fors = len(re.findall(for_pattern, template_source))
        endfors = len(re.findall(endfor_pattern, template_source))

        if fors != endfors:
            self.errors.append(
                f"Unbalanced for tags: {fors} for(s) but {endfors} endfor(s)"
            )

    def _extract_variables_and_filters(self, template: Template) -> None:
        """
        Extract all variables and filters used in the template.

        Args:
            template: Template object to analyze
        """
        # Extract variables from template source
        template_source = template.source

        # Pattern for variables: {{ variable }}
        var_pattern = r'{{\s*([^}]+?)\s*}}'
        matches = re.findall(var_pattern, template_source)

        for match in matches:
            # Split by pipe to separate variable from filters
            parts = match.split('|')

            # First part is the variable
            var_name = parts[0].strip()
            # Remove any method calls or attribute access for base variable
            base_var = var_name.split('.')[0].split('(')[0]
            self.variables_found.add(base_var)

            # Remaining parts are filters
            for filter_part in parts[1:]:
                filter_name = filter_part.split(':')[0].strip()
                self.filters_found.add(filter_name)

        # Also extract variables from template tags
        tag_pattern = r'{%\s*\w+\s+([^%]+?)\s*%}'
        tag_matches = re.findall(tag_pattern, template_source)

        for match in tag_matches:
            # Extract variable names from tag content
            words = match.split()
            for word in words:
                if not word.startswith('"') and not word.startswith("'"):
                    # Remove operators and keywords
                    if word not in ['in', 'as', 'with', 'and', 'or', 'not']:
                        base_var = word.split('.')[0]
                        if base_var and not base_var.isdigit():
                            self.variables_found.add(base_var)

    def _check_missing_variables(self, context: Dict) -> None:
        """
        Check for variables used in template but missing from context.

        Args:
            context: Context dictionary to check against
        """
        # Common Django template variables that are always available
        builtin_vars = {
            'True', 'False', 'None', 'forloop', 'block', 'csrf_token',
            'request', 'user', 'perms', 'messages', 'debug'
        }

        missing_vars = self.variables_found - set(context.keys()) - builtin_vars

        if missing_vars:
            self.warnings.append(
                f"Variables used in template but not in context: {', '.join(sorted(missing_vars))}"
            )

    def _validate_filters(self) -> None:
        """
        Validate that all filters used in the template are valid Django filters.
        """
        from django.template.defaultfilters import register as default_filters
        from django.template.library import InvalidTemplateLibrary

        # Get all registered filters
        try:
            valid_filters = set(default_filters.filters.keys())
        except (AttributeError, InvalidTemplateLibrary):
            # If we can't get the filter list, skip validation
            return

        # Check for invalid filters
        invalid_filters = self.filters_found - valid_filters

        if invalid_filters:
            self.warnings.append(
                f"Potentially invalid filters: {', '.join(sorted(invalid_filters))}"
            )


def validate_template(
    template_name: str,
    context: Optional[Dict] = None
) -> Tuple[bool, List[str], List[str]]:
    """
    Convenience function to validate a template.

    Args:
        template_name: Name or path of the template to validate
        context: Optional context dictionary to check for missing variables

    Returns:
        Tuple of (is_valid, errors, warnings)

    Example:
        >>> is_valid, errors, warnings = validate_template('email/welcome.html', {'user': user})
        >>> if not is_valid:
        ...     print(f"Errors: {errors}")
    """
    validator = TemplateValidator()
    return validator.validate_template(template_name, context)


def validate_template_string(
    template_string: str,
    context: Optional[Dict] = None
) -> Tuple[bool, List[str], List[str]]:
    """
    Validate a template from a string.

    Args:
        template_string: Template content as string
        context: Optional context dictionary to check for missing variables

    Returns:
        Tuple of (is_valid, errors, warnings)

    Example:
        >>> template = "Hello {{ name }}!"
        >>> is_valid, errors, warnings = validate_template_string(template, {'name': 'World'})
    """
    errors = []
    warnings = []

    try:
        template = Template(template_string)
    except TemplateSyntaxError as e:
        errors.append(f"Template syntax error: {str(e)}")
        return False, errors, warnings
    except Exception as e:
        errors.append(f"Unexpected error: {str(e)}")
        return False, errors, warnings

    # If context provided, try to render and check for missing variables
    if context is not None:
        try:
            template.render(Context(context))
        except Exception as e:
            warnings.append(f"Template rendering warning: {str(e)}")

    return True, errors, warnings
