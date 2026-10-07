from pathlib import Path


class GodotProjectTool:

    def __init__(self, project_root: str | Path) -> None:
        self.project_root = Path(project_root).resolve()

        project_file = self.project_root / "project.godot"

        if not project_file.exists():
            raise ValueError(
                f"Not a Godot project: {self.project_root}"
            )

    def list_files(self) -> list[str]:
        files: list[str] = []

        for path in self.project_root.rglob("*"):
            if path.is_file():
                files.append(
                    str(path.relative_to(self.project_root))
                )

        return sorted(files)

    def read_file(self, relative_path: str) -> str:
        path = (self.project_root / relative_path).resolve()

        if not path.is_relative_to(self.project_root):
            raise ValueError(
                f"Path is outside the Godot project: {relative_path}"
            )

        if not path.is_file():
            raise FileNotFoundError(
                f"Project file not found: {relative_path}"
            )

        return path.read_text(encoding="utf-8")

    def search_files(
            self,
            query: str,
            extensions: tuple[str, ...] = (
                ".gd",
                ".tscn",
                ".godot",
            ),
    ) -> list[str]:
        matches: list[str] = []

        query_lower = query.lower()

        for relative_path in self.list_files():
            path = Path(relative_path)

            if path.suffix not in extensions:
                continue

            try:
                content = self.read_file(relative_path)
            except (UnicodeDecodeError, OSError):
                continue

            if query_lower in content.lower():
                matches.append(relative_path)

        return matches