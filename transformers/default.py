import re
from abc import ABC
from pathlib import Path
from typing import List

import spacy

from transformers.epurer import epurer
from transformers.enums import Tag

tupfields = (
    "@id",
    "@form",
    "@lemma",
    "@upos",
    "@xpos",
    "@feats",
    "@head",
    "@deprel",
    "@deps",
    "@misc",
)


class DefaultTransformer(ABC):
    @property
    def tupfields(self) -> tuple[str, ...]:
        return tupfields

    def __init__(
        self,
        tags: List[List[Tag]] | List[Tag] = None,
        pivot_tags: List[List[Tag]] | List[Tag] = None,
        nlp: spacy.language.Language = None,
    ) -> None:

        self.sent_id_n = 0
        self.sent_id_text = None
        self.sent_id = None

        self.pivot_tags = pivot_tags

        if nlp is None:
            self.nlp = spacy.load("fr_core_news_sm")
            self.nlp.max_length = 50000
        else:
            self.nlp = nlp

        if tags is None:
            self.tags = list(Tag)
        else:
            self.tags = tags

    def epurer(self, pivot: dict) -> dict:
        if self.pivot_tags == [] or self.pivot_tags == self.tags:
            return pivot

        if set(self.tags).difference(set(self.pivot_tags)) != set():
            raise ValueError("tags must be a subset of pivot_tags")

        return epurer(pivot, self.tags)

    def transform(self, pivot: Path | str | dict) -> dict:
        raise NotImplementedError

    def iterateonpivot(self, pivot: dict | list) -> None:
        if isinstance(pivot, list):
            for x in pivot:
                if isinstance(x, list | dict):
                    self.iterateonpivot(x)
            return

        if isinstance(pivot, str):
            print(pivot)
            raise ValueError("pivot is a string")

        for k, v in pivot.items():
            if not isinstance(v, list | dict):
                continue

            if k != "w":
                self.iterateonpivot(v)
                continue

            self.w_process(v)

    def w_process(self, v):
        raise NotImplementedError

    def idsent(self, sentid: int | str | None = None) -> str | int:
        if sentid:
            if isinstance(sentid, int):
                self.sent_id_n = sentid
        else:
            self.sent_id_n += 1

        self.sent_id = f"{self.sent_id_text}-{self.sent_id_n}"

        return self.sent_id

    @staticmethod
    def spaceAfter(w: dict) -> str:
        if "@misc" in w:
            return " " if w["@misc"] != "SpaceAfter=No" else ""

        if "@whitespace" in w:
            return w["@whitespace"]

        return " "

    def textWSpacing(self, w: dict) -> str:
        return w["#text"] + self.spaceAfter(w)

    def sentWSpacing(self, sent: list[dict]) -> str:
        return "".join([self.textWSpacing(w) for w in sent])

    @staticmethod
    def sentWOSpacing(sent: list[dict]) -> str:
        return " ".join([w["#text"] for w in sent])

    def sentWMaxSpacing(self, sent: list[dict]) -> str:
        return (
            self.sentWSpacing(sent) if "@misc" in sent[0] else self.sentWOSpacing(sent)
        )
