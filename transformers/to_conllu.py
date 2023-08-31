from io import StringIO
from pathlib import Path
from typing import List

import spacy

from transformers.enums import Tag
from transformers.default import DefaultTransformer

allfields = "ID FORM LEMMA UPOS XPOS FEATS HEAD DEPREL DEPS MISC"


class CONLLUTransformer(DefaultTransformer):
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
        self.srtio.write(f"# sent_id = {super().idsent(sentid)}\n")

    def w_process(self, v: list) -> None:
        self.idsent()

        self.srtio.write(f"# text = {self.sentWMaxSpacing(v)}\n")

        for w in v:
            if "@form" not in w:
                w["@form"] = w["#text"]

            self.srtio.write(
                "\t".join(
                    [
                        str(w[field]) if field in w and w[field] else "_"
                        for field in self.tupfields
                    ]
                )
            )
            self.srtio.write("\n")

        self.srtio.write("\n")

    def transform(self, pivot: Path | str | dict) -> str:
        if self.srtio:
            self.srtio.close()
            self.srtio = StringIO()

        pivot.pop("TEI-EXTRACTED-METADATA")
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
