from enum import Enum


class Tag(Enum):
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

    def __str__(self):
        return self.value

    def __eq__(self, other):
        if isinstance(other, str):
            return self.value == other
        elif isinstance(other, Tag):
            return self.value == other.value
        else:
            raise TypeError

    def __hash__(self):
        return hash(self.value)

    @classmethod
    def from_str(cls, s: str):
        return cls(s)
