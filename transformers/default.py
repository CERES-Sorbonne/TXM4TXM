from abc import ABC
from pathlib import Path
from typing import List

import spacy

from transformers.epurer import epurer
from transformers.enums import Tag


class DefaultTransformer(ABC):
    def __init__(
            self,
            tags: List[List[Tag]] | List[Tag] = None,
            pivot_tags: List[List[Tag]] | List[Tag] = None,
            nlp: spacy.language.Language = None
    ) -> None:

        self.sent_id = 0
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
                self.iterateonpivot(x)
            return

        for k, v in pivot.items():
            if not isinstance(v, list | dict):
                continue

            if k != "w":
                self.iterateonpivot(v)
                continue

            self.w_process(v)

    def w_process(self, v):
        raise NotImplementedError

    def idsent(self, sentid: int | str | None = None) -> None:
        if sentid:
            if isinstance(sentid, int):
                self.sent_id = sentid
        else:
            self.sent_id += 1

        #self.srtio.write(f"# sent_id = {self.sent_id}\n")
