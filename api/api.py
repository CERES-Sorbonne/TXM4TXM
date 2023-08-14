import io
import os
from typing import List
from pathlib import Path

from fastapi import FastAPI, UploadFile, Form, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse, HTMLResponse, FileResponse

from transformers import utils, pipeline
from transformers.enums import MimeType, Output, Tag

main_dir = Path(__file__).parent

app = FastAPI()

app.mount("/static", StaticFiles(directory=main_dir / "static"), name="static")


@app.get("/", response_class=HTMLResponse, tags=["main"])
async def read_root():
    with open(main_dir / "templates/index.html") as f:
        return f.read()


@app.post("/upload", tags=["main"], response_class=FileResponse)
async def write_upload(
    files: List[UploadFile] = File(...), output: List[str] = Form(...)
):
    files = [utils.File(f.filename, await f.read()) for f in files]

    outputs: dict[Output, list[Tag]]
    output_types: list[Output]

    results: List[File]
    result: File
    res: io.StringIO | io.BytesIO
    mime: MimeType
    name: str

    outputs = {Output(o): [Tag("text")] for o in output if not "-" in o}
    for o in output:
        o = o.split("-")
        if len(o) == 2:
            outputs[Output(o[0])].append(Tag(o[1]))

    output_types = [k for k in outputs]
    output_tags = [outputs[k] for k in outputs]

    results = pipeline.pipeline(files, output_types, output_tags)

    if len(results) == 1:
        result = results[0]

        if not isinstance(result.content, bytes):
            res = io.StringIO(result.content)
        else:
            res = io.BytesIO(result.content)

        mime = result.mime_type
        name = result.name

    else:
        zip = utils.ZipCreator("results.zip", mode="names")
        zip.fill_zip(results)

        res = zip.content

        mime = MimeType.zip

        name = "results.zip"

    return StreamingResponse(
        content=res,
        status_code=200,
        media_type=mime.value,
        headers={"Content-Disposition": f"attachment; filename={name}"},
    )
