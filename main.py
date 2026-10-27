from fastapi import FastAPI
from fastapi.responses import HTMLResponse


app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)


@app.get("/", response_class=HTMLResponse)
def hello_world() -> str:
    return """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Hello world</title>
  </head>
  <body>
    <h1>Hello world</h1>
  </body>
</html>
"""
