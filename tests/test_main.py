from html.parser import HTMLParser
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from fastapi.testclient import TestClient


class DocumentParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title_parts = []
        self.heading_parts = []
        self.in_title = False
        self.in_h1 = False

    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self.in_title = True
        elif tag == "h1":
            self.in_h1 = True

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        elif tag == "h1":
            self.in_h1 = False

    def handle_data(self, data):
        if self.in_title:
            self.title_parts.append(data)
        if self.in_h1:
            self.heading_parts.append(data)


@pytest.fixture(scope="session")
def app():
    module_path = Path(__file__).resolve().parents[1] / "main.py"
    if module_path.is_file():
        import importlib.util

        spec = importlib.util.spec_from_file_location("main", module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.app

    # Keep the pre-implementation RED run behavioral while main.py is absent.
    placeholder = FastAPI()

    @placeholder.get("/")
    def placeholder_root():
        return PlainTextResponse("Not implemented", status_code=404)

    @placeholder.get("/{path:path}")
    def placeholder_unknown(path):
        return PlainTextResponse("Not implemented", status_code=200)

    return placeholder


@pytest.fixture
def client(app):
    return TestClient(app)


def test_root_returns_http_200(client):
    response = client.get("/")

    assert response.status_code == 200


def test_root_returns_html_content_type(client):
    response = client.get("/")

    assert response.headers["content-type"].split(";")[0] == "text/html"


def test_root_is_html_document_with_title_and_hello_heading(client):
    response = client.get("/")
    body = response.text
    parser = DocumentParser()
    parser.feed(body)

    assert body.lstrip().lower().startswith("<!doctype html>")
    assert "<html" in body.lower()
    assert "<head" in body.lower()
    assert "<body" in body.lower()
    assert "".join(parser.title_parts).strip()
    assert "".join(parser.heading_parts).strip() == "Hello world"


def test_unknown_path_returns_http_404(client):
    response = client.get("/this-path-does-not-exist")

    assert response.status_code == 404


@pytest.mark.parametrize(
    "path", ["/docs", "/redoc", "/openapi.json", "/docs/oauth2-redirect"]
)
def test_default_documentation_routes_are_disabled(client, path):
    response = client.get(path)

    assert response.status_code == 404


def test_application_exposes_only_the_root_get_endpoint(app):
    endpoints = [
        (route.path, set(route.methods or ()))
        for route in app.routes
        if hasattr(route, "methods")
    ]

    assert endpoints == [("/", {"GET"})]
