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
