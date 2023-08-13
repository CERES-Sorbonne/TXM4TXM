import io
import os
from typing import List
from pathlib import Path


from fastapi import FastAPI, UploadFile, Form, File  # , Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse, HTMLResponse, FileResponse

from transformers import utils, pipeline
from transformers.enums import MimeType, Output, Tag

main_dir = Path(__file__).parent
root_dir = main_dir.parent

host = os.getenv("TXM_SERVER", "")
app = FastAPI()

templates = main_dir / "templates"

app.mount("/static", StaticFiles(directory=main_dir / "static"), name="static")


@app.get("/", response_class=HTMLResponse, tags=["main"])
async def read_root():
    with open(templates / "index.html") as f:
        return f.read()


@app.post("/upload", tags=["main"], response_class=FileResponse)
async def write_upload(
    files: List[UploadFile] = File(...), output: List[str] = Form(...)
):
    files = [utils.File(f.filename, await f.read()) for f in files]

    # result_names: List[str]
    # result: List[str | bytes]
    # result_mime: List[MimeType]
    results: List[File]
    result: File

    # print(f"{output = }")
    # print(f"{files = }")

    outputs = {Output(o): [Tag("text")] for o in output if not "-" in o}
    for o in output:
        o = o.split("-")
        if len(o) == 2:
            outputs[o[0]].append(Tag(o[1]))

    output_types = [k for k in outputs]
    output_tags = [outputs[k] for k in outputs]

    # print(f"{outputs = }")
    # print(len(outputs))
    # print(f"{output_types = }")
    # print(f"{output_tags = }")
    #
    # res = pipeline.pipeline(files, output_types, output_tags)


    # result_names, result, result_mime = pipeline.pipeline(files, output_types, output_tags).values()

    results = pipeline.pipeline(files, output_types, output_tags)

    if len(results) == 1:
        result = results[0]

        if not isinstance(result.content, bytes):
            res = io.StringIO(result.content)
        else:
            res = io.BytesIO(result.content)

        return StreamingResponse(
            content=res,
            status_code=200,
            media_type=result.mime_type.value,
            headers={"Content-Disposition": f"attachment; filename={result.name}"},
        )


    # zip_io = io.BytesIO()
    # with zipfile.ZipFile(zip_io, mode="w", compression=zipfile.ZIP_DEFLATED) as temp_zip:
    #     for result in results:
    #         print(f"{result.name = }; {result.mime_type = }")
    #         if result.mime_type == MimeType.zip:
    #             temp_zip.mkdir(result.name)
    #             with zipfile.ZipFile(io.BytesIO(result.content), mode="r") as z:
    #                 for f in z.namelist():
    #                     temp_zip.writestr(f"{result.name}/{f}", z.read(f))
    #             continue
    #
    #         temp_zip.writestr(f"{result.name}", result.content)
    #
    # zip_io.seek(0)

    zipfile = utils.ZipCreator(results)


    return StreamingResponse(
        content=zipfile,
        status_code=200,
        media_type=MimeType.zip.value,
        headers={"Content-Disposition": "attachment; filename=results.zip"},
    )









