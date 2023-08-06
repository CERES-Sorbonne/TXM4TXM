from typing import List, Union, Dict, Optional, Tuple
from pathlib import Path

import spacy

from transformers.enums import Output, MimeType, Tag
from transformers.to_pivot import PivotTransformer
from transformers.to_xml import XMLTransformer
from transformers.utils import File

nlp = spacy.load("fr_core_news_sm")
nlp.max_length = 50000


def pipeline(
    files: List[File],
    output: List[Output] = None,
    tags: List[List[Tag] | Tag] = None,
) -> List[List[str], List[str | bytes], List[MimeType]]:
    pivots: List[dict] = []

    if output is None:
        output = [Output.json]

    if tags is None:
        tags = [[Tag.id, Tag.form, Tag.lemma, Tag.pos, Tag.text] for _ in files]

    if isinstance(tags[0], Tag):
        tags = [tags for _ in files]

    if len(tags) != len(files):
        raise ValueError("tags must be the same length as files")

    pivot_tags = [t for i, t in enumerate(tags) if output[i] == Output.json]

    outputs = {"name": [], "output": [], "mime": []}

    for file in files:
        file_name = [file.name] * len(output)
        file_output = []
        file_mime = []

        if file.mime_type == MimeType.xml:
            pivot = PivotTransformer(
                tags=pivot_tags, pivot_tags=pivot_tags, nlp=nlp
            ).transform(file.file)
        elif file.mime_type == MimeType.json:
            pivot = file.file
        else:
            raise ValueError("Only xml and pre-pivoted json are supported")

        if Output.json in output:
            file_output.append(pivot)
            file_mime.append(MimeType.json)

        if Output.txm in output:
            tags = [t for i, t in enumerate(tags) if output[i] == Output.txm]

            xml = XMLTransformer(tags=tags, pivot_tags=pivot_tags, nlp=nlp).transform(
                pivot
            )
            file_output.append(xml)
            file_mime.append(MimeType.xml)

        outputs["name"].extend(file_name)
        outputs["output"].extend(file_output)
        outputs["mime"].extend(file_mime)

    return outputs
