import json
from pathlib import Path
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


def replace_text(e):
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
            # print(v)
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

def str_to_xml(text: str) -> dict:
    # text = re.sub(r"(\s)\1+", r"\g<1>", text).strip()
    text = re.sub(r"(\s)+", " ", text)
    doc = nlp(text)
    # new_text = []
    # for token in doc:
    #     new_token = soup.new_tag("w", pos=token.pos_, dep=token.dep_, lemma=token.lemma_, entity=token.ent_type_)
    #     new_token.string = token.text
    #     new_text.append(xmltodict.parse(new_token))
    # return new_text
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

    return {
            "w": [
                {
                    "@pos": token.pos_,
                    "@dep": token.dep_,
                    "@lemma": token.lemma_,
                    "@entity": token.ent_type_,
                    "#text": token.text
                }
                for token in doc
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
