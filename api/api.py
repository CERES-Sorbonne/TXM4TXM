import os
from io import StringIO
from typing import List
from pathlib import Path

from fastapi import FastAPI, UploadFile, Form, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse, HTMLResponse, FileResponse
from starlette.templating import Jinja2Templates

from transformers import utils, pipeline
from transformers.enums import Output, Tag

from transformers import concurrent_pipeline as pipeline

main_dir = Path(__file__).parent

app = FastAPI(root_path="/txm4txm")

host = os.getenv("TXM4TXM_SERVER", "")

app.mount("/static", StaticFiles(directory=main_dir / "static"), name="static")
templates = Jinja2Templates(directory=os.path.join(main_dir, "templates"))


@app.get("/", response_class=HTMLResponse, tags=["main"])
async def read_root():
    return templates.TemplateResponse("index.html", {"request": {}, "host": host})


@app.post("/upload", tags=["main"], response_class=FileResponse)
async def write_upload(files: List[UploadFile] = File(...), output: List[str] = Form(...)):
    outputs: dict[Output, list[Tag]]
    output_types: list[Output]
    
    results: List[File]
    result: File

    if not files:
        return HTMLResponse("No files uploaded")
    if not output:
        return HTMLResponse("No output selected")

    files = [utils.File(f.filename, await f.read()) for f in files]

    outputs = {Output(o): [Tag("text")] for o in output if "-" not in o}

    for o in output:
        o = o.split("-")
        try:
            if len(o) == 2:
                outputs[Output(o[0])].append(Tag(o[1]))
        except KeyError:
            print(f"Seems like {o[0]} has been unchecked, cannot set {o[1]}")

    if Output.conllu in outputs:
        outputs[Output.conllu].append(Tag.id)

    output_types = [k for k in outputs]
    output_tags = [outputs[k] for k in outputs]

    results = pipeline.pipeline(files, output_types, output_tags)

    if len(results) == 1:
        result = results[0]

    else:
        result = utils.ZipCreator("results", mode="types")
        result.fill_zip(results)

    if isinstance(result.content, str):
        result.content = StringIO(result.content)

    return StreamingResponse(
        content=result.content,
        status_code=200,
        media_type=result.mime_type,
        headers={"Content-Disposition": f"attachment; filename={result.name}"},
    )
