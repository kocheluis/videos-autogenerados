"""Los tools WAT importan y exponen `main` sin requerir GPU ni modelos pesados."""

from __future__ import annotations

import importlib

import pytest

TOOL_MODULES = [
    "tools._common",
    "tools.new_project",
    "tools.generate_script",
    "tools.build_bible",
    "tools.generate_keyframes",
    "tools.animate_clips",
    "tools.upscale_clips",
    "tools.synthesize_voice",
    "tools.align_captions",
    "tools.render_video",
    "tools.publish",
    "tools.project_status",
    "tools.approve_gate",
    "tools.run_batch",
]


@pytest.mark.parametrize("mod_name", TOOL_MODULES)
def test_tool_imports(mod_name: str):
    mod = importlib.import_module(mod_name)
    if mod_name != "tools._common":
        assert callable(getattr(mod, "main")), f"{mod_name} sin main()"


def test_common_exit_codes():
    from tools import _common

    assert (_common.EXIT_OK, _common.EXIT_ERROR, _common.EXIT_NOT_WIRED, _common.EXIT_BLOCKED) == (0, 1, 2, 3)
