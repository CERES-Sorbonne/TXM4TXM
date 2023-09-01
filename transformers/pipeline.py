import json
from pathlib import Path
from typing import List
from copy import deepcopy  # To copy the pivot dict

import spacy
from tqdm.auto import tqdm

from transformers.enums import Output, MimeType, Tag

from transformers.to_pivot import PivotTransformer
from transformers.to_xml import XMLTransformer
from transformers.to_conllu import CONLLUTransformer
from transformers.to_hyperbase import HyperbaseTransformer

from transformers.utils import File
from transformers.epurer import epurer

nlp = spacy.load("fr_core_news_sm")
nlp.max_length = 50000


def pipeline(
    files: List[File],
    output: List[Output] = None,
    tags: List[List[Tag] | Tag] = None,
) -> List[File]:
    """Pipeline de transformation des fichiers
    prend une liste de fichiers en entrée et retourne une liste de ces fichiers transformés
    dans les différents formats demandés (xml, json), avec les tags demandés
    (id, form, lemma, pos, text, etc.)
    """

    if output is None:
        output = [Output.json]

    if tags is None:
        tags = [[Tag.id, Tag.form, Tag.lemma, Tag.pos, Tag.text] for _ in output]

    if isinstance(tags[0], Tag):
        tags = [tags for _ in output]

    if len(tags) != len(output):
        if len(tags) == 1:
            tags = [tags[0] for _ in output]

        else:
            raise ValueError("tags must be the same length as files or a single list")

    pivot_tags = list(set([tag for tag_list in tags for tag in tag_list]))

    outputs = []

    pbar = tqdm(files, desc="Processing files", unit="file")

    for file in pbar:
        if not isinstance(file, (File, Path, str)):
            raise ValueError(f"file must be a Path, a File or a str ({type(file) = })")

        name = file.name if "name" in file.__dict__ else file[:10] + "..." + file[-10:]
        pbar.set_postfix_str(name)

        if file.mime_type == MimeType.xml:
            pivot = PivotTransformer(tags=pivot_tags, pivot_tags=pivot_tags, nlp=nlp).transform(file)
        elif file.mime_type == MimeType.json:
            pivot = file.content
        else:
            raise ValueError("Only xml and pre-pivoted json are supported")

        if Output.pivot in output:
            outputs.append(
                File(name=file.with_suffix(".pivot.json"), file=json.dumps(pivot, ensure_ascii=False, indent=4)))

        if Output.json in output:
            pivot_copy = deepcopy(pivot)
            pivot_copy.pop("TEI-EXTRACTED-METADATA")
            json_str = json.dumps(epurer(pivot_copy, tags[output.index(Output.json)]), ensure_ascii=False, indent=4)
            outputs.append(File(name=file.with_suffix(".json"), file=json_str))

        if Output.txm in output:
            pivot_copy = deepcopy(pivot)
            tag = tags[output.index(Output.txm)] if Output.txm in output else []

            xml = XMLTransformer(tags=tag, pivot_tags=pivot_tags, nlp=nlp).transform(pivot_copy)

            outputs.append(File(name=file.with_suffix(".xml"), file=xml))

        if Output.conllu in output:
            pivot_copy = deepcopy(pivot)
            tag = tags[output.index(Output.conllu)] if Output.conllu in output else []

            conllu = CONLLUTransformer(tags=tag, pivot_tags=pivot_tags, nlp=nlp).transform(pivot_copy)

            outputs.append(File(name=file.with_suffix(".conllu"), file=conllu))

        if Output.hyperbase in output:
            pivot_copy = deepcopy(pivot)
            tag = tags[output.index(Output.hyperbase)] if Output.hyperbase in output else []

            hyperbase = HyperbaseTransformer(tags=tag, pivot_tags=pivot_tags, nlp=nlp).transform(pivot_copy)

            outputs.append(File(name=file.with_suffix(".hyperbase.txt"), file=hyperbase))

    return outputs
