from tools.godot_project_tool import GodotProjectTool

import pytest


def test_list_files(tmp_path):
    (tmp_path / "project.godot").write_text(
        "[application]\nconfig/name=\"Test Game\""
    )

    scripts = tmp_path / "scripts"
    scripts.mkdir()

    (scripts / "player.gd").write_text(
        "extends CharacterBody2D"
    )

    tool = GodotProjectTool(tmp_path)

    files = tool.list_files()

    assert "project.godot" in files
    assert "scripts/player.gd" in files

def test_read_file(tmp_path):
    (tmp_path / "project.godot").write_text(
        "[application]\nconfig/name=\"Test Game\""
    )

    scripts = tmp_path / "scripts"
    scripts.mkdir()

    (scripts / "player.gd").write_text(
        "extends CharacterBody2D"
    )

    tool = GodotProjectTool(tmp_path)

    content = tool.read_file("scripts/player.gd")

    assert content == "extends CharacterBody2D"


def test_read_file_rejects_path_outside_project(tmp_path):
    (tmp_path / "project.godot").write_text(
        "[application]"
    )

    tool = GodotProjectTool(tmp_path)

    with pytest.raises(ValueError):
        tool.read_file("../../outside.txt")


def test_search_files(tmp_path):
    (tmp_path / "project.godot").write_text(
        "[application]"
    )

    scripts = tmp_path / "scripts"
    scripts.mkdir()

    (scripts / "player.gd").write_text(
        "extends CharacterBody2D\n\n"
        "func jump():\n"
        "    velocity.y = -400"
    )

    (scripts / "enemy.gd").write_text(
        "extends Node2D"
    )

    tool = GodotProjectTool(tmp_path)

    matches = tool.search_files("CharacterBody2D")

    assert matches == [
        "scripts/player.gd"
    ]

def test_search_files_is_case_insensitive(tmp_path):
    (tmp_path / "project.godot").write_text(
        "[application]"
    )

    (tmp_path / "player.gd").write_text(
        "extends CharacterBody2D"
    )

    tool = GodotProjectTool(tmp_path)

    matches = tool.search_files("characterbody2d")

    assert matches == [
        "player.gd"
    ]