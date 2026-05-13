import socket

orig_getaddrinfo = socket.getaddrinfo


# use only IPv4
def patched_getaddrinfo(*args, **kwargs):
    responses = orig_getaddrinfo(*args, **kwargs)
    return [res for res in responses if res[0] == socket.AF_INET]


socket.getaddrinfo = patched_getaddrinfo


import argparse
import json
import os
import tempfile
import zipfile
from pathlib import Path

import kagglehub
import pathspec


class KaggleDatasetUploader:
    def __init__(self, dataset_path=".", auto_confirm=False):
        self.dataset_path = Path(dataset_path).resolve()
        self.auto_confirm = auto_confirm
        self.spec = self._load_spec()
        self.dataset_id = self._load_dataset_id()

    def _load_spec(self):
        ignore_file = self.dataset_path / ".kaggleignore"
        if not ignore_file.exists():
            raise FileNotFoundError(f"{ignore_file} not found")
        return pathspec.PathSpec.from_lines(
            "gitwildmatch", ignore_file.read_text().splitlines()
        )

    def _load_dataset_id(self):
        metadata_path = self.dataset_path / "dataset-metadata.json"
        if not metadata_path.exists():
            raise FileNotFoundError(f"{metadata_path} not found")
        metadata = json.loads(metadata_path.read_text())
        return metadata["id"]

    @staticmethod
    def _format_bytes(size):
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"

    def _collect_files(self):
        """Collect files respecting .kaggleignore patterns."""
        result = []
        for root, dirs, files in os.walk(self.dataset_path):
            # Filter directories in-place to skip ignored dirs
            dirs[:] = [
                d
                for d in dirs
                if not self.spec.match_file(
                    os.path.relpath(os.path.join(root, d), self.dataset_path)
                )
            ]
            for f in files:
                rel = os.path.relpath(os.path.join(root, f), self.dataset_path)
                if not self.spec.match_file(rel):
                    result.append((os.path.join(root, f), rel))
        return result

    def upload(self):
        print(f"Dataset: {self.dataset_id}")
        print(f"Ignore patterns: {self.spec.patterns}")

        files = self._collect_files()
        total_size = sum(os.path.getsize(p) for p, _ in files)
        print(f"Total size: {self._format_bytes(total_size)}")

        if not self.auto_confirm:
            if input("Proceed with upload? (y/n): ").strip().lower() not in (
                "y",
                "yes",
            ):
                print("Upload cancelled.")
                return False

        with tempfile.TemporaryDirectory() as tmp:
            zip_path = Path(tmp) / "dataset.zip"
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for abs_path, rel_path in files:
                    zf.write(abs_path, rel_path)

            print(
                f"Created: {zip_path} ({self._format_bytes(zip_path.stat().st_size)})"
            )

            kagglehub.dataset_upload(
                handle=self.dataset_id,
                local_dataset_dir=str(zip_path.parent),
                version_notes="Automated update",
            )

        print("Upload successful!")
        return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kaggle dataset uploader")
    parser.add_argument(
        "dataset_path", nargs="?", default=".", help="Path to dataset folder"
    )
    parser.add_argument("-y", "--yes", action="store_true", help="Auto-confirm upload")
    args = parser.parse_args()

    uploader = KaggleDatasetUploader(args.dataset_path, args.yes)
    if uploader.upload():
        print("Process completed successfully")
