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


def feats2meta(feats: str) -> str:
    if feats == "_" or not feats:
        return ""

    feats = feats.split("|")
    feats = [e.split("=")[1] for e in feats]
    feats = [e.replace(" ", "-") for e in feats]

    return f":{':'.join(feats) if feats else '_'}"




class HyperbaseTransformer(DefaultTransformer):
    supTags = (
        '@id',
        '@xpos',
        # '@feats',
        '@head',
        '@deprel',
        '@deps'
    )

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

        self.metaline = StringIO()
        self.metaline.write("**** ")

        for k, v in meta.items():
            if isinstance(v, str):
                self.metaline.write(f"*{k.lower()}_{self.for_meta_field(v)} ")

            if k == "Personnages":
                for i, p in enumerate(v):
                    self.metaline.write(f"*personnage-{i}_{self.for_meta_field(p['Id'])} ")

            if k == "Responsables":
                for r in v:
                    self.metaline.write(f"*responsable-{self.for_meta_field(r['Role'])}_{self.for_meta_field(r['Name'])} ")

        # self.srtio.write(f"{self.metaline.getvalue().strip()}\n\n")
        self.srtio.write(f"{self.metaline.getvalue().strip()}\n")


        self.iterateonpivot(pivot)

        self.srtio.seek(0)
        return self.srtio.getvalue()

    def w_process(self, v):
        if not v:
            return
        if not isinstance(v, list):
            v = [v]



        if "@pos" not in v[0] or "@lemma" not in v[0]:
            sent = self.sentWSpacing(v)
            par = remove_par(sent).strip()

            if par:
                self.idsent()
                self.srtio.write(f"{par}\n\n")

        else:
            self.idsent()
            for i, w in enumerate(v, 1):

                if "#text" not in w:
                    try:
                        w["#text"] = w["@form"]
                    except KeyError:
                        print("Impossible de trouver le texte du mot")
                        print(w)
                        raise

                lenv = len(v)

                if i == lenv or (i > lenv-2 and w["#text"] in (".", "?", "!", "...")):
                    w["@pos"] = "SENT" if w["@pos"] == "PUNCT" else f"SENT:{w['@pos']}"

                try:
                    self.srtio.write(f"{w['#text']}\t{w['@pos']}")

                    # if w["@pos"] != "SENT":
                    for key in self.supTags:
                        if key not in w:
                            continue

                        if key == "@feats" and False:  # Maybe they should be at the end of the line
                            self.srtio.write(feats2meta(w[key]))
                        else:
                            value = w[key] if w[key] else "_"
                            self.srtio.write(f":{self.for_meta_field(value)}")

                    if "@feats" in w:
                        self.srtio.write(feats2meta(w["@feats"]))

                    self.srtio.write(f"\t{w['@lemma']}\n")
                except KeyError:
                    print(w)
                    raise
            # self.srtio.write("\n\n")

    def idsent(self, sentid: int | str | None = None) -> None:
        return  # Try to diminish the size of the file because it's too big for Hyperbase
        self.srtio.write(self.metaline.getvalue() + f"*sent_{super().idsent(sentid)}\n")
