from pathlib import Path
from bs4 import BeautifulSoup
import re
import xmltodict


def getReplique(p):
    if p.find("p"):
        texte = p.find("p").text
    elif p.find("l"):
        texte = p.find("l").text
    else:
        texte = p.text

    return re.sub(r"(\s)\1+", r"\g<1>", texte).strip()


original_folder = Path("textes Codif")
output_folder = Path("forTXM")
output_folder.mkdir(exist_ok=True)

for piece in original_folder.glob("*.xml"):
    with piece.open("r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "xml")

    TEI = soup.find("TEI")
    teiHeader = TEI.find("teiHeader")
    text = TEI.find("text")

    meta = {
        "Titre": teiHeader.find("title").text,
        "Edition": teiHeader.find("edition").text if teiHeader.find("edition") else "N/A",
        "Publication": teiHeader.find("publicationStmt").find("publisher").text if teiHeader.find(
            "publicationStmt").find("publisher") else "N/A",
        "Date": teiHeader.find("publicationStmt").find("date").attrs["when"] if teiHeader.find("publicationStmt").find(
            "date") and "when" in teiHeader.find("publicationStmt").find("date").attrs else "N/A",
        "Source": teiHeader.find("sourceDesc").text,
    }
    meta = {k: v.strip() for k, v in meta.items()}

    personnages = text.find("castList").findAll("castItem")
    personnages = [
        {"Id": p.attrs["xml:id"], "Display": p.text} if "xml:id" in p.attrs else {"Id": "N/A", "Display": p.text} for p
        in personnages]
    meta["Personnages"] = personnages

    responsables = teiHeader.findAll("respStmt")
    responsables = [{"Name": r.find("name").text, "Role": r.find("resp").text} for r in responsables]
    meta["Responsables"] = responsables

    text = text.find("body")

    actes = [
        {
            "Numéro": a.attrs["n"],
            "Titre": a.find("head").text,
            "Stage": a.find("stage").text,
            "Scènes": [
                {
                    "Numéro": s.attrs["n"],
                    "Titre": s.find("head").text,
                    "Scène": s.find("stage").text if s.find("stage") else "N/A",
                    "Paroles": [
                        {
                            "Personnage": {
                                "Id": p.attrs["who"] if "who" in p.attrs else "N/A",
                                "Display": p.find("speaker").text if p.find("speaker") else "N/A",
                            },
                            "Réplique": getReplique(p),
                        }
                        for p in s.findAll("sp")
                    ],
                }
                for s in a.findAll("div", {"type": "scene"})
            ],
        }
        for a in text.findAll("div", {"type": "acte"})
    ]

    finalxml = xmltodict.unparse(
        {
            "TEI": {
                "@xmlns": "http://www.tei-c.org/ns/1.0",
                "teiHeader": {
                    "fileDesc": {
                        "titleStmt": {
                            "title": meta["Titre"],

                        },
                        "editionStmt": {
                            "respStmt": [
                                {
                                    "resp": e["Role"],
                                    "name": e["Name"],
                                }
                                for e in meta["Responsables"]
                            ],
                        },
                        "publicationStmt": {
                            "publisher": meta["Publication"],
                            "date": meta["Date"],
                        },
                        "sourceDesc": {"p": meta["Source"]},
                    }
                },
                "text": {
                    "body": {
                        "div": [
                            {
                                "@type": "acte",
                                "@n": a["Numéro"],
                                "head": a["Titre"],
                                "stage": a["Stage"],
                                "div": [
                                    {
                                        "@type": "scene",
                                        "@n": s["Numéro"],
                                        "head": s["Titre"],
                                        "stage": s["Scène"],
                                        "sp": [
                                            {
                                                "@who": p["Personnage"]["Id"],
                                                "speaker": p["Personnage"]["Display"],
                                                "p": p["Réplique"],
                                            }
                                            for p in s["Paroles"]
                                        ],
                                    }
                                    for s in a["Scènes"]
                                ],
                            }
                            for a in actes
                        ]
                    }
                },
            }
        },
        pretty=True,
    )

    with open(output_folder / piece.name, "w", encoding="utf-8") as f:
        f.write(finalxml)
