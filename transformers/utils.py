import mimetypes


class NamedDict:
    pass


class File(NamedDict):
    name: str
    file: str

    def __init__(self, name, file):
        self.name = name
        self.file = file

    def __repr__(self):
        return f"File(name={self.name}, file={self.file})"

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash((self.name, self.file))

    def __eq__(self, other):
        if isinstance(other, str):
            return self.name == other
        elif isinstance(other, File):
            return self.name == other.name and self.file == other.file

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
        return mimetypes.guess_type(self.file)[0]

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
        return self.mime_type == "application/xml"

    @property
    def is_json(self):
        return self.mime_type == "application/json"

    @property
    def is_zip(self):
        return self.mime_type == "application/zip"


