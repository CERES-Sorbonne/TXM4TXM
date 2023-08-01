from abc import ABC
from pathlib import Path
from typing import List

import spacy

from transformers.epurer import epurer
from transformers.tag import Tag


class DefaultTransformer(ABC):
    def __init__(self, tags: List[Tag] = None, pivot_tags: List[Tag] = None, nlp: spacy.language.Language = None):
        self.pivot_tags = set(pivot_tags) if pivot_tags is not None else set()

        if nlp is None:
            self.nlp = spacy.load("fr_core_news_sm")
            self.nlp.max_length = 50000
        else:
            self.nlp = nlp

        if tags is None:
            tags = [tag for tag in Tag]

        self.tags = set(tags)

    def epurer(self, pivot: dict) -> dict:
        if self.pivot_tags == set() or self.pivot_tags == self.tags:
            return pivot

        if self.tags.difference(self.pivot_tags) != set():
            raise ValueError("tags must be a subset of pivot_tags")

        return epurer(pivot, self.tags)

    def transform(self, pivot: Path | str | dict) -> dict:
        raise NotImplementedError
