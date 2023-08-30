from enum import Enum


class EnumPlus(str, Enum):
    def __str__(self) -> str:
        return self.value

    def __eq__(self, other) -> bool:
        if isinstance(other, str):
            return self.value == other
        elif isinstance(other, EnumPlus):
            return self.value == other.value
        elif isinstance(other, tuple):
            return self.value == other[0]
        else:
            raise TypeError(f"Cannot compare {self} and {other}")

    def __hash__(self) -> int:
        return hash(self.value)

    @classmethod
    def from_str(cls, s: str) -> "EnumPlus":
        return cls(s)


class Tag(EnumPlus):
    id = "id"
    form = "form"
    lemma = "lemma"
    pos = "pos"
    xpos = "xpos"
    feats = "feats"
    head = "head"
    deprel = "deprel"
    deps = "deps"
    misc = "misc"
    whitespace = "whitespace"
    text = "text"


class OutputType(EnumPlus):
    csv = "csv"
    json = "json"
    txt = "txt"
    xml = "xml"
    zip = "zip"


class Output(EnumPlus):
    pivot = "pivot"
    json = "json"
    txm = "txm"
    iramuteq = "iramuteq"
    gephi = "gephi"
    cluster_tool = "cluster_tool"
    csv = "csv"
    stats = "stats"
    processed_stats = "processed_stats"
    plots = "plots"
    conllu = "conllu"
    hyperbase = "hyperbase"


class OutToType(EnumPlus):
    pivot = OutputType.json
    json = OutputType.json
    txm = OutputType.xml
    iramuteq = OutputType.txt
    gephi = OutputType.csv
    cluster_tool = OutputType.csv
    csv = OutputType.csv
    stats = OutputType.json
    processed_stats = OutputType.zip
    plots = OutputType.zip
    conllu = OutputType.txt
    hyperbase = OutputType.txt


class MimeType(EnumPlus):
    json = "application/json"
    txt = "text/plain"
    xml = "text/xml"
    csv = "text/csv"
    zip = "application/zip"
    conllu = "text/conllu"
    hyperbase = "text/hyperbase"


def get_mimetype(output_type: OutputType) -> MimeType:
    return MimeType[output_type.value]


def get_output_type(output: Output) -> OutputType:
    return OutToType[output.value].value
