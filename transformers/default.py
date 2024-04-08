import os
import re
from abc import ABC
from pathlib import Path
from typing import List

import spacy
from treetagger import TreeTagger

from transformers.enums import Tag, Model
from transformers.epurer import epurer

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

    @classmethod
    def path_to_treetager(self) -> str:
        # p1 = os.popen("echo $TREETAGGER_HOME").read().strip()
        # print(p1)

        tt = os.getenv("TREETAGGER_HOME", None)
        if tt is None:
            tt = os.getenv("PATH", "").split(":")
            tt = [x for x in tt if "treetagger" in x.lower()]
            if tt == []:
                print("TREETAGGER_HOME is not set")
                raise ValueError("TREETAGGER_HOME is not set")
            tt = tt[0]
        return tt

    def __init__(
            self,
            tags: List[List[Tag]] | List[Tag] = None,
            pivot_tags: List[List[Tag]] | List[Tag] = None,
            nlp: spacy.language.Language | Model | TreeTagger = None,
    ) -> None:
        print(f"{self.__class__.__name__} init...")
        print(f"model: {nlp}")

        self.sent_id_n = 0
        self.sent_id_text = None
        self.sent_id = None

        self.pivot_tags = pivot_tags

        if nlp is None:
            self.nlp = spacy.load("fr_core_news_sm")
            self.nlp.max_length = 50000
        else:
            self.nlp = nlp

        if isinstance(self.nlp, Model):
            print(f"Loading TreeTagger model {self.nlp}...")
            self.nlp = TreeTagger(
                path_to_treetagger=self.path_to_treetager(),
                language=self.nlp,
            )

        if isinstance(self.nlp, TreeTagger):
            print(f"Using already loaded TreeTagger model\n{self.nlp}")

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

    def text_id_from_title(self, meta: dict) -> None:
        self.sent_id_text = self.for_meta_field(meta["Titre"])

    @staticmethod
    def for_meta_field(s: str | int) -> str:
        if isinstance(s, int):
            return str(s)

        return re.sub(r"(\s|[(,.;:?!\[\]\\/{}*&^%$#@+=~`|])+", "-", s).replace('"', "").strip("-")
