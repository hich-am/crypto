"""Locker launcher package.

This package centralizes the module catalog and the independent launcher
layer used by the CLI and desktop GUI.
"""

from .catalog import (
    COURSE_ALIASES,
    MODULE_CATALOG,
    THEME_LABELS,
    THEME_SEQUENCE,
    iter_modules_for_theme,
    resolve_target,
)
