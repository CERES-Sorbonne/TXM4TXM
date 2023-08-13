import json
from typing import List, Union, Dict, Optional, Tuple
from pathlib import Path

import spacy

from transformers.enums import Output, MimeType, Tag
from transformers.to_pivot import PivotTransformer
from transformers.to_xml import XMLTransformer
from transformers.utils import File
from transformers.epurer import epurer

nlp = spacy.load("fr_core_news_sm")
nlp.max_length = 50000


def pipeline(
    files: List[File],
    output: List[Output] = None,
    tags: List[List[Tag] | Tag] = None,
) -> List[File]:
    pivots: List[dict] = []

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

    # outputs = {"name": [], "output": [], "mime": []}
    outputs = []

    for file in files:
        file_name = []
        file_output = []
        file_mime = []

        if file.mime_type == MimeType.xml:
            pivot = PivotTransformer(
                tags=pivot_tags, pivot_tags=pivot_tags, nlp=nlp
            ).transform(file)
        elif file.mime_type == MimeType.json:
            pivot = file.content
        else:
            raise ValueError("Only xml and pre-pivoted json are supported")

        if Output.pivot in output:
            outputs.append(
                File(
                    name=file.with_suffix(".pivot.json"),
                    file=json.dumps(pivot, ensure_ascii=False, indent=4),
                    # mime_type = MimeType.json
                )
            )
            #
            #
            # file_name.append(file.with_suffix(".pivot.json"))
            # file_output.append(json.dumps(pivot, ensure_ascii=False, indent=4))
            # file_mime.append(MimeType.json)

        if Output.json in output:
            # file_name.append(file.with_suffix(".json"))
            # file_output.append(
            #     json.dumps(
            #         epurer(
            #             pivot,
            #             tags[output.index(Output.json)],
            #         ),
            #         ensure_ascii=False,
            #         indent=4,
            #     )
            # )
            # file_mime.append(MimeType.json)
            json_str = json.dumps(
                epurer(pivot, tags[output.index(Output.json)]),
                ensure_ascii=False,
                indent=4,
            )
            outputs.append(
                File(
                    name=file.with_suffix(".json"),
                    file=json_str,
                    # mime_type = MimeType.json
                )
            )

        if Output.txm in output:
            tag = tags[output.index(Output.txm)] if Output.txm in output else []

            xml = XMLTransformer(tags=tag, pivot_tags=pivot_tags, nlp=nlp).transform(
                pivot
            )
            # file_name.append(file.with_suffix(".xml"))
            # file_output.append(xml)
            # file_mime.append(MimeType.xml)

            outputs.append(
                File(
                    name=file.with_suffix(".xml"),
                    file=xml,
                    # mime_type = MimeType.xml
                )
            )

        # outputs["name"].extend(file_name)
        # outputs["output"].extend(file_output)
        # outputs["mime"].extend(file_mime)
        #

        print()

    return outputs
