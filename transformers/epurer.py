from typing import Iterable, Set
from transformers.enums import Tag

all_tags = list(Tag)


def epurer(pivot: dict, tags: Iterable[Tag] | Set[Tag]) -> dict:
    """Retire les clés inutiles du pivot"""
    toremove = []
    for k, v in pivot.items():
        if k.startswith("@"):
            to_check = k[1:]
            if to_check in all_tags:
                if to_check not in tags:
                    toremove.append(k)

        if isinstance(v, dict):
            epurer(v, tags)

        elif isinstance(v, list):
            for i in v:
                epurer(i, tags)

    for k in toremove:
        del pivot[k]

    return pivot


if __name__ == "__main__":
    import json

    with open("../test/json/BerPet.json", "r", encoding="utf-8") as f:
        pivot = json.load(f)

    tags = [Tag("id"), Tag("form"), Tag("lemma"), Tag("pos"), Tag("xpos")]
    pivot = epurer(pivot, tags)

    with open("tests/BerPet_epure.json", "w", encoding="utf-8") as f:
        json.dump(pivot, f, indent=4, ensure_ascii=False)
