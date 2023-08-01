from pathlib import Path


import spacy


from transformers import to_pivot, to_xml, tag


if __name__ == "__main__":
    nlp = spacy.load("fr_core_news_sm")
    nlp.max_length = 50000

    tegs = [tag.Tag("id"), tag.Tag("form"), tag.Tag("lemma"), tag.Tag("pos"), tag.Tag("xpos")]

    p = to_pivot.PivotTransformer(tags=tegs, nlp=nlp)

    testfile = Path("../textes Codif/BerPet.xml")

    res = p.transform(testfile)

    print(res)

    tags_xml = [tag.Tag("id"), tag.Tag("form"), tag.Tag("lemma"), tag.Tag("pos")]

    x = to_xml.XMLTransformer(tags=tags_xml, nlp=nlp, pivot_tags=tegs)

    print(x.transform(res))






