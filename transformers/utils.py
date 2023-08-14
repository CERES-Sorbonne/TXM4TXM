import zipfile
from typing import List
from pathlib import Path
from io import BytesIO

from starlette.datastructures import UploadFile

from transformers.enums import MimeType


class File:
    def __init__(self, name, file):
        self.__pathver = None
        self.name = name
        if isinstance(file, bytes):
            file = file.decode("utf-8")
        elif isinstance(file, UploadFile):
            file = file.file.read().decode("utf-8")
        self.content = file

    def __repr__(self):
        return f"File(name={self.name}, file={self.content})"

    def __hash__(self):
        return hash((self.name, self.content))

    def __eq__(self, other):
        if isinstance(other, str):
            return self.name == other
        elif isinstance(other, File):
            return self.name == other.name and self.content == other.content

        raise TypeError(f"Cannot compare {self} and {other}")

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        if isinstance(other, str):
            return self.name < other
        elif isinstance(other, File):
            return self.name < other.name

        raise TypeError(f"Cannot compare {self} and {other}")

    @property
    def mime_type(self):
        return MimeType[self.suffix[1:]]

    @property
    def is_text(self):
        if self.mime_type is None:
            return False
        elif self.mime_type.startswith("text"):
            return True
        elif self.mime_type.startswith("application"):
            if self.mime_type.endswith("xml") or self.mime_type.endswith("json"):
                return True
        else:
            return False

    @property
    def is_binary(self):
        return not self.is_text

    @property
    def is_xml(self):
        return self.mime_type in ("application/xml", "text/xml")

    @property
    def is_json(self):
        return self.mime_type == "application/json"

    @property
    def is_zip(self):
        return self.mime_type == "application/zip"

    @classmethod
    def from_starlette_upload_file(cls, upload_file: UploadFile):
        return cls(upload_file.filename, upload_file.file.read().decode("utf-8"))

    @classmethod
    def from_path(cls, path: Path):
        return cls(path.name, path.read_text(encoding="utf-8"))

    @classmethod
    def from_str(cls, name: str, text: str):
        return cls(name, text)

    @classmethod
    def from_dict(cls, d: dict):
        return cls(d["name"], d["file"])

    @classmethod
    def auto_from(cls, obj: Path | UploadFile | dict):
        if isinstance(obj, Path):
            return cls.from_path(obj)
        elif isinstance(obj, UploadFile):
            return cls.from_starlette_upload_file(obj)
        elif isinstance(obj, dict):
            return cls.from_dict(obj)
        else:
            raise TypeError(f"Cannot convert {obj} to File")

    def to_dict(self):
        return {"name": self.name, "file": self.content}

    def to_upload_file(self):
        if self.is_binary:
            return UploadFile(
                filename=self.name, file=BytesIO(self.content.encode("utf-8"))
            )
        else:
            return UploadFile(filename=self.name, file=self.content)


    def to_path(self, path: Path):
        path.write_text(self.content, encoding="utf-8")
        return path

    def __str__(self):
        return self.name, self.content

    @property
    def pathver(self):
        if self.__pathver is None:
            self.__pathver = Path(self.name)
        return self.__pathver

    @property
    def stem(self):
        return self.pathver.stem

    @property
    def suffix(self):
        return self.pathver.suffix

    def with_suffix(self, suffix):
        return self.pathver.with_suffix(suffix).name


# def ZipCreator(list_of_files: List[File], mode: str = "types"):
#     if mode not in ("types", "names"):
#         raise ValueError(f"Invalid mode {mode}, must be types or names")
#
#     zip_io = BytesIO()
#     with zipfile.ZipFile(zip_io, mode="w", compression=zipfile.ZIP_DEFLATED) as temp_zip:
#         for f in list_of_files:
#             if mode == "types":
#                 if f.stem.endswith(".pivot"):
#                     type = "pivot"
#                 else:
#                     type = f.suffix[1:]
#                 temp_zip.writestr(f"{type}/{f.name}", f.content)
#             elif mode == "names":
#                 temp_zip.writestr(f.name, f.content)
#
#
#
#     zip_io.seek(0)
#     return zip_io


class ZipCreator(File):
    def __init__(self, name, mode: str = "types"):
        if mode not in ("types", "names"):
            raise ValueError(f"Invalid mode {mode}, must be types or names")

        self.mode = mode

        super().__init__(name, BytesIO())

    def __repr__(self):
        return f"ZipCreator(name={self.name}, file={self.content})"

    def is_binary(self):
        return True

    def fill_zip(self, files: List[File], ):

        with zipfile.ZipFile(self.content, mode="w", compression=zipfile.ZIP_DEFLATED) as temp_zip:
            for f in files:
                if self.mode == "types":
                    type_ = f.suffix[1:]
                    temp_zip.writestr(f"{_}/{f.name}", f.content)
                elif self.mode == "files":
                    stem = f.stem
                    temp_zip.writestr(f"{stem}/{f.name}", f.content)

        self.content.seek(0)

        return self.content



    #
