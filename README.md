# FastAPI Hello World

A minimal FastAPI application that serves a “Hello world” HTML page.

## Run locally

Create and activate a virtual environment, then install the application and test dependencies:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

Start the application:

```sh
python -m uvicorn main:app --reload
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in a browser.

## Run tests

With the virtual environment activated, run:

```sh
python -m pytest
```
