import json
from enum import Enum
from pathlib import Path
from typing import List
from ast import literal_eval

from bs4 import BeautifulSoup
import re
import pandas as pd
import xmltodict

import spacy

nlp = spacy.load("fr_core_news_sm")
nlp.max_length = 5000000

original_folder = Path("textes Codif")
test_path = Path("test")
json_output = test_path / "json"
xml_output = test_path / "xml"

json_output.mkdir(parents=True, exist_ok=True)
xml_output.mkdir(parents=True, exist_ok=True)


class Tag(Enum):
    id = "id"
    form = "form"
    lemma = "lemma"
    pos = "pos"
    xpos = "xpos"
    feats = "feats"
    head = "head"
    deprel = "deprel"
    deps = "deps"
    misc = "misc"
    whitespace = "whitespace"
    text = "text"


def replace_text(e: dict | str) -> dict | str | None:
    if e is None:
        return

    if isinstance(e, str):
        return str_to_xml(e)

    to_update = {}
    to_remove = []

    for k, v in e.items():
        if isinstance(v, str):
            if not "@" in k:
                to_update = str_to_xml(v)
                if k != "#text":
                    to_update = {k: to_update}
                to_remove.append(k)

        elif isinstance(v, dict):
            e[k] = replace_text(v)

        elif isinstance(v, list):
            if v == []:
                continue
            e[k] = [replace_text(x) for x in v]

        elif v is None:
            continue

        else:
            raise ValueError

    for k in to_remove:
        del e[k]

    e.update(to_update)

    # for k, v in e.items():
    #     if isinstance(v, str):
    #         if k == "#text":
    #             to_update = str_to_xml(v)
    #     elif isinstance(v, dict):
    #         e[k] = replace_text(v)
    #     elif isinstance(v, list):
    #         if v == []:
    #             continue
    #         # print(v)
    #         e[k] = [replace_text(x) for x in v]
    #     elif v is None:
    #         continue
    #     else:
    #         raise ValueError
    #
    # if "#text" in e:
    #     del e["#text"]
    #
    # e.update(to_update)
    return e


def str_to_xml(text: str, tags: List[Tag] = None) -> dict:
    possible_tags = {
        Tag("id"): {"@id": "i"},
        Tag("form"): {"@form": "token.text"},
        Tag("lemma"): {"@lemma": "token.lemma_"},
        Tag("pos"): {"@pos": "token.pos_"},
        Tag("xpos"): {"@xpos": "token.tag_"},
        Tag("feats"): {"@feats": "token.morph"},
        Tag("head"): {"@head": "token.head.i + 1 if deps[i] != 'root' else 0"},
        Tag("deprel"): {"@deprel": "deps[i]"},
        Tag("deps"): {"@deps": "token.dep_"},
        Tag("misc"): {"@misc": "'' if token.whitespace_ else 'SpaceAfter=No'"},
        Tag("whitespace"): {"@whitespace": "token.whitespace_ == ' '"},
        Tag("text"): {"#text": "token.text"},

    }

    if tags is None:
        tags = [tag for tag in Tag]
    tags = set(tags)

    # tags = {k: v for enum_, d in possible_tags.items() for k, v in d.items() if enum_ in tags}



    # text = re.sub(r"(\s)\1+", r"\g<1>", text).strip()
    text = re.sub(r"(\s)+", " ", text)
    doc = nlp(text)

    # res = [
    #         {
    #             "@pos": token.pos_,
    #             # "@dep": token.dep_,
    #             "@lemma": token.lemma_,
    #             # "@entity": token.ent_type_,
    #             "#text": token.text
    #         }
    #         for token in doc
    #     ]
    # return {"w": res} if len(res) > 1 else {"w": res[0]}
    #
    # return {
    #     "w": [
    #         {
    #             "@id": i,
    #             "@pos": token.pos_,
    #             "@dep": token.dep_,
    #             "@lemma": token.lemma_,
    #             "@entity": token.ent_type_,
    #             "#text": token.text
    #         }
    #         for i, token in enumerate(doc, 1)
    #     ]
    # }
    # i = 0
    # return {
    #     "w": [
    #         {k: eval("i") for k, v in tags.items()}
    #         for i, token in enumerate(doc, 1)
    #     ]}

    # if any([t in tags for t in [Tag("head"), Tag("deprel")]]):
    #     deps = [token.dep_.lower() for token in doc]
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

    return {
        "w": temp_lst
    }

    temp = [
        {
            "@id": i if Tag("id") in tags else None,
            "@form": token.text if Tag("form") in tags else None,
            "@lemma": token.lemma_ if Tag("lemma") in tags else None,
            "@pos": token.pos_ if Tag("pos") in tags else None,
            "@xpos": token.tag_ if Tag("xpos") in tags else None,
            "@feats": str(token.morph) if Tag("feats") in tags else None,
            "@head": token.head.i + 1 if token.dep_.lower() != "root" else 0 if Tag("head") in tags else None,
            "@deprel": token.dep_.lower() if Tag("deprel") in tags else None,
            "@deps": token.dep_ if Tag("deps") in tags else None,
            "@misc": "" if token.whitespace_ else "SpaceAfter=No" if Tag("misc") in tags else None,
            "@whitespace": token.whitespace_ == " " if Tag("whitespace") in tags else None,
            "#text": token.text if Tag("text") in tags else None,
        }
        for i, token in enumerate(doc, 1)
    ]

    return {
        "w": [
            {k: v for k, v in d.items() if v is not None}
            for d in temp
        ]
    }


for file in original_folder.glob("*.xml"):
    print(f"Processing {file.name}")

    with file.open("r", encoding="utf-8") as f:
        text = f.read()
        text = re.sub(r"(\s)\1+", r"\g<1>", text).strip()

        with open("test.xml", "w", encoding="utf-8") as g:
            g.write(text)

        soup = BeautifulSoup(text, "xml")

    text_d = xmltodict.parse(text, attr_prefix="@")
    texte = text_d["TEI"]["text"]

    replace_text(texte)

    text_d["TEI"]["text"] = texte

    with open(json_output / f"{file.stem}.json", "w", encoding="utf-8") as f:
        json.dump(text_d, f, ensure_ascii=False, indent=4)

    res = xmltodict.unparse(text_d, pretty=True)

    with open(xml_output / f"{file.stem}.xml", "w", encoding="utf-8") as f:
        f.write(res)
