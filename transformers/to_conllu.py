from io import StringIO
from pathlib import Path
from typing import List

import spacy

from transformers.enums import Tag
from transformers.default import DefaultTransformer

allfields = "ID FORM LEMMA UPOS XPOS FEATS HEAD DEPREL DEPS MISC"
tupfields = ("@id", "@form", "@lemma", "@upos", "@xpos", "@feats", "@head", "@deprel", "@deps", "@misc")


class CONLLUTransformer(DefaultTransformer):
    @property
    def tupfields(self) -> tuple[str, ...]:
        return tupfields

    @property
    def allfields(self) -> str:
        return allfields

    def __init__(
        self,
        tags: List[List[Tag]] | List[Tag] = None,
        pivot_tags: List[List[Tag]] | List[Tag] = None,
        nlp: spacy.language.Language = None,
    ):
        if tags is not None and Tag.id not in tags:
            tags.append(Tag.id)

        super().__init__(tags, pivot_tags, nlp)

        self.sent_id = 0

        self.srtio = StringIO()
        self.srtio.write(f"# global.columns = {self.allfields}\n")

    def idsent(self, sentid: int | str | None = None) -> None:
        if sentid:
            if isinstance(sentid, int):
                self.sent_id = sentid
        else:
            self.sent_id += 1

        self.srtio.write(f"# sent_id = {self.sent_id}\n")

    def w_process(self, v: list) -> None:
        self.idsent()

        sent = [w["#text"] for w in v]  #  if isinstance(w, dict) and "#text" in w]
        sent = " ".join(sent)
        self.srtio.write(f"# text = {sent}\n")

        for w in v:
            if "@form" not in w:
                w["@form"] = w["#text"]

            self.srtio.write("\t".join([str(w[field]) if field in w and w[field] else "_" for field in self.tupfields]))
            self.srtio.write("\n")

        self.srtio.write("\n")

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

    def transform(self, pivot: Path | str | dict) -> str:
        pivot = self.epurer(pivot)

        self.iterateonpivot(pivot)

        self.srtio.seek(0)
        return self.srtio.getvalue()


if __name__ == "__main__":
    import json

    file = "/home/marceau/PycharmProjects/codif/results/json/BerPet.json"

    with open(file, "r", encoding="utf-8") as f:
        fic = json.load(f)

    conllu = CONLLUTransformer()
    print(conllu.transform(fic))
