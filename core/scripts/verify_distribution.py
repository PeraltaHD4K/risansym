"""Validate Risansym wheel and source-distribution release artifacts."""

from __future__ import annotations

import argparse
import tarfile
import zipfile
from email.parser import Parser
from pathlib import Path, PurePosixPath


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("dist_dir", type=Path)
    return parser.parse_args()


def _assert_safe_path(name: str) -> None:
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"unsafe archive member: {name}")


def _single_match(dist_dir: Path, pattern: str) -> Path:
    matches = sorted(dist_dir.glob(pattern))
    if len(matches) != 1:
        raise ValueError(f"expected one {pattern} artifact, found {len(matches)}")
    return matches[0]


def _verify_wheel(wheel_path: Path) -> tuple[str, str]:
    with zipfile.ZipFile(wheel_path) as archive:
        names = archive.namelist()
        for name in names:
            _assert_safe_path(name)

        if "risansym/py.typed" not in names:
            raise ValueError("wheel does not contain risansym/py.typed")

        metadata_names = [name for name in names if name.endswith(".dist-info/METADATA")]
        if len(metadata_names) != 1:
            raise ValueError("wheel must contain exactly one METADATA file")
        metadata = Parser().parsestr(archive.read(metadata_names[0]).decode())

        forbidden = ("tests/", "benchmarks/", "scripts/", "__pycache__/")
        leaked = [name for name in names if name.startswith(forbidden)]
        if leaked:
            raise ValueError(f"wheel contains development files: {leaked}")

    name = metadata["Name"]
    version = metadata["Version"]
    if name != "risansym" or not version:
        raise ValueError(f"unexpected package identity: {name} {version}")
    if metadata["Requires-Python"] != ">=3.10":
        raise ValueError("unexpected Requires-Python metadata")
    if not any(value.startswith("pydantic") for value in metadata.get_all("Requires-Dist", [])):
        raise ValueError("pydantic runtime dependency is missing")
    return name, version


def _verify_sdist(sdist_path: Path, version: str) -> None:
    expected_root = f"risansym-{version}"
    with tarfile.open(sdist_path, "r:gz") as archive:
        names = [member.name for member in archive.getmembers()]
        for name in names:
            _assert_safe_path(name)
            if PurePosixPath(name).parts[0] != expected_root:
                raise ValueError(f"unexpected sdist root: {name}")

        required = {
            f"{expected_root}/PKG-INFO",
            f"{expected_root}/README.md",
            f"{expected_root}/pyproject.toml",
            f"{expected_root}/src/risansym/__init__.py",
            f"{expected_root}/src/risansym/py.typed",
        }
        missing = required.difference(names)
        if missing:
            raise ValueError(f"sdist is missing required files: {sorted(missing)}")

        forbidden_parts = {"tests", "benchmarks", "scripts", "__pycache__"}
        leaked = [
            name
            for name in names
            if forbidden_parts.intersection(PurePosixPath(name).parts)
            or name.endswith((".pyc", ".pyo"))
        ]
        if leaked:
            raise ValueError(f"sdist contains development files: {leaked}")


def main() -> None:
    dist_dir = _parse_args().dist_dir.resolve()
    wheel = _single_match(dist_dir, "risansym-*.whl")
    sdist = _single_match(dist_dir, "risansym-*.tar.gz")
    name, version = _verify_wheel(wheel)
    _verify_sdist(sdist, version)
    print(f"verified {name} {version}: {wheel.name}, {sdist.name}")


if __name__ == "__main__":
    main()
