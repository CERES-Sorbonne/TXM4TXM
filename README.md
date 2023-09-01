# TXM4TXM

## Table of Contents
- [Introduction](#introduction)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Introduction
TXM4TXM was originally destined to be a simple tool to annotate XML files in a way that would be compatible with the TXM software.
In order to annotate the xml files, whilst keeping the original structure, the tool uses a "pivot" file, which translates the original xml file into a dictionary, so practally a json file.
The tool then uses the dictionary to iterate through the original xml file and add the annotations to the correct elements.
Then, from the annotated pivot file, the tool creates a new xml file, which is the original xml file with the annotations added.
This process relies on xmltodict, a python library that converts xml files into dictionaries and vice versa.
Then, the tool was expanded to include a GUI, which allows the user to select the files to be annotated and the annotations to be added.
The GUI was created using the uvicorn library, which allows the creation of a web app from a python script.
It now also include multiple exports. For the tim ebeing, we have:
- TXM export: the original xml file with the annotations added
- JSON export: the pivot file with the annotations added
- CoNNLU export: a CoNNLU file where only the paragraphs are kept and the annotations are in the CoNNLU format
- Hyperbase export: an export for Hyperbase, once again with only the paragraphs and the annotations in the Hyperbase format

## Installation
In order to install the tool, you need to have python 3.8 or higher installed on your computer.
Then, you need to install the dependencies, which are listed in the requirements.txt file.
```bash
pip install -r requirements.txt
```

## Usage
In order to use the tool, you need to run uviorn from the root directory of the project with the following command:
```bash
python -m uvicorn api.api:app [--workers 8 --limit-max-requests 8]
```
The workers and limit-max-requests parameters are optional and can be used to improve the performance of the tool, by running multiple instances of the tool at the same time, you allow multiple users to use the tool at the same time.
That could be useful if you are running the tool on a server, but it is not necessary if you are running the tool locally.
Once the tool is running, you can access it from your browser at the following address:
`http://127.0.0.1:8080` or `http://localhost:8080` if you are running it locally and haven't changed the default port.
You would be greated by a webpage with a few explanations at the end.
You can also visit the `/docs` endpoint to see the documentation of the API.
The documentation is also available, in a different format, at the `/redoc` endpoint.

## License
This project is licensed under the AGPL-3.0 license - see the [LICENSE.txt](LICENSE.txt) file for details.

