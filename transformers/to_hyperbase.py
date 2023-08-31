from io import StringIO
from typing import List

import re
import spacy

from transformers.enums import Tag
from transformers.default import DefaultTransformer


def remove_par(s: str) -> str:
    if not s:
        return s

    s = (
        s.strip().replace(" ", " ").replace("", " ").replace(" ", " ")
    )  # Pas les mêmes espaces (unicode)
    s = "\n".join([e.strip() for e in s.split("\n") if e.strip()])
    s = re.sub(r"(\t| ){2,}", " ", s)
    s = re.sub(r"\n{2,}", "\n", s)
    s = re.sub(r"\s\n", "\n", s)
    s = re.sub(r"\n{2,}", "\n", s)
    s = re.sub(r"^\s", "", s)

    return s


def to_meta(s: str) -> str:
    return re.sub(r"\s", "-", s)


class HyperbaseTransformer(DefaultTransformer):
    supTags = ('@id', '@xpos', '@feats', '@head', '@deprel', '@deps', '@misc', '@whitespace')

    def __init__(
        self,
        tags: List[List[Tag]] | List[Tag] = None,
        pivot_tags: List[List[Tag]] | List[Tag] = None,
        nlp: spacy.language.Language = None,
    ):
        super().__init__(tags, pivot_tags, nlp)

        self.sent_id = 0
        self.metaline = None
        self.srtio = StringIO()

    def transform(self, pivot: dict) -> str:
        if self.srtio:
            self.srtio.close()
            self.srtio = StringIO()

        pivot = self.epurer(pivot)

        meta = pivot.pop("TEI-EXTRACTED-METADATA")
        print(meta)

        self.metaline = StringIO()
        self.metaline.write("**** ")

        for k, v in meta.items():
            if isinstance(v, str):
                self.metaline.write(f"*{k.lower()}_{v} ")

            if k == "Personnages":
                for i, p in enumerate(v):
                    self.metaline.write(f"*personnage-{i}_{p['Id']} ")

            if k == "Responsables":
                for r in v:
                    self.metaline.write(f"*responsable-{r['Role']}_{r['Name']} ")

        # self.srtio.write(f"{metaline.getvalue().strip()}")

        self.iterateonpivot(pivot)

        self.srtio.seek(0)
        return self.srtio.getvalue()

    def w_process(self, v):
        if not v:
            return
        if not isinstance(v, list):
            v = [v]

        if "@pos" not in v[0] or "@lemma" not in v[0]:
            sent = self.sentWMaxSpacing(v)
            par = remove_par(sent).strip()

            if par:
                self.idsent()
                self.srtio.write(f"{par}\n\n")

        else:
            self.idsent()
            for w in v:

                if "@form" not in w:
                    w["@form"] = w["#text"]

                try:
                    self.srtio.write(f"{w['@form']}\t{w['@pos']}")
                    for key in self.supTags:
                        if key in w:
                            value = w[key] if w[key] else "_"
                            self.srtio.write(f":{value}")
                    self.srtio.write(f"\t{w['@lemma']}\n")
                except KeyError:
                    print(w)
                    raise
            self.srtio.write("\n\n")

    def idsent(self, sentid: int | str | None = None) -> None:
        self.srtio.write(self.metaline.getvalue() + f"*sent_{super().idsent(sentid)}\n")
