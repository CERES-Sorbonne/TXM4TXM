import io
import os
import zipfile
from enum import Enum
from typing import List, Iterable  # , Optional
from pathlib import Path


from fastapi import FastAPI, UploadFile, Request, Form, HTTPException, File  # , Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse, HTMLResponse

from transformers import enums, utils, pipeline

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


@app.post("/upload", tags=["main"])
async def write_upload(
    files: List[UploadFile] = File(...), output: List[str] = Form(...)
):
    print(f"{output = }")
    print(f"{files = }")

    if len(files) == 1 and files[0].filename == "":
        raise HTTPException(status_code=400, detail="No File Provided")
    # parse all files
    try:
        to_process = [
            utils.File(name=f.filename, file=f.file.read().decode("utf-8"))
            for f in files
        ]
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Invalid File Provided")
    # process result
    result, result_type = pipeline.pipeline(to_process, output, tags=None)


