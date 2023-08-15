from pathlib import Path
from typing import List

import re
import xmltodict
import spacy

from transformers.enums import Tag
from transformers.default import DefaultTransformer
from transformers.utils import File


class PivotTransformer(DefaultTransformer):
    def __init__(
            self,
            tags: List[Tag] = None,
            pivot_tags: List[Tag] = None,
            nlp: spacy.language.Language = None
    ) -> None:
        super().__init__(tags, pivot_tags, nlp)
        if self.pivot_tags == set():
            self.pivot_tags = self.tags

        if self.pivot_tags != self.tags:
            raise ValueError("pivot_tags must be equal to tags (or empty) for PivotTransformer")

    def replace_text(self, e: dict | str) -> dict | str | None:
        if isinstance(e, str):
            return self.str_to_pivot(e)

        to_update = {}
        to_remove = []

        for k, v in e.items():
            if isinstance(v, str):
                if not "@" in k:
                    to_update = self.str_to_pivot(v)
                    if k != "#text":
                        to_update = {k: to_update}
                    to_remove.append(k)

            elif isinstance(v, dict):
                e[k] = self.replace_text(v)

            elif isinstance(v, list):
                if v == []:
                    continue
                e[k] = [self.replace_text(x) for x in v if x is not None]

            elif v is None:
                continue

            else:
                raise ValueError

        for k in to_remove:
            del e[k]

        e.update(to_update)
        return e

    def str_to_pivot(self, text: str) -> dict:
        tags = set(self.pivot_tags)

        text = re.sub(r"(\s)+", " ", text)
        doc = self.nlp(text)

        temp_lst = []
        for i, token in enumerate(doc, 1):
            temp = {}
            if Tag("id") in tags:
                temp["@id"] = i
            if Tag("form") in tags:
                temp["@form"] = token.text
            if Tag("lemma") in tags:
                temp["@lemma"] = token.lemma_
            if Tag("pos") in tags:
                temp["@pos"] = token.pos_
            if Tag("xpos") in tags:
                temp["@xpos"] = token.tag_
            if Tag("feats") in tags:
                temp["@feats"] = str(token.morph)
            if Tag("head") in tags:
                temp["@head"] = token.head.i + 1 if token.dep_.lower() != "root" else 0
            if Tag("deprel") in tags:
                temp["@deprel"] = token.dep_.lower()
            if Tag("deps") in tags:
                temp["@deps"] = token.dep_
            if Tag("misc") in tags:
                temp["@misc"] = "" if token.whitespace_ else "SpaceAfter=No"
            if Tag("whitespace") in tags:
                temp["@whitespace"] = token.whitespace_ == " "
            if Tag("text") in tags:
                temp["#text"] = token.text

            temp_lst.append(temp)

        return {"w": temp_lst}

    def transform(self, file: File | Path | str) -> dict:

        if not isinstance(file, (File, Path, str)):
            raise ValueError(f"file must be a Path, a File or a str ({type(file) = })")

        name = file.name if "name" in file.__dict__ else file[:10] + "..." + file[-10:]
        print(f"Processing {name}")

        if isinstance(file, Path):
            with file.open("r", encoding="utf-8") as f:
                text = f.read()
                text = re.sub(r"(\s)\1+", r"\g<1>", text).strip()

        elif isinstance(file, str):
            text = file

        elif isinstance(file, File):
            text = file.content

        text_d = xmltodict.parse(text, attr_prefix="@")
        texte = text_d["TEI"]["text"]

        self.replace_text(texte)

        text_d["TEI"]["text"] = texte

        return text_d

