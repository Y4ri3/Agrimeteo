"""Écrit le contrat OpenAPI sur la sortie standard (voir `make openapi`)."""

import json

from app.main import app


def render() -> str:
    return json.dumps(app.openapi(), indent=2, ensure_ascii=False, sort_keys=True) + "\n"


if __name__ == "__main__":
    print(render(), end="")
