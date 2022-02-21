from jinja2 import Template


def get_template(path: str) -> Template:
    with open(path, "r", encoding="utf-8") as f:
        return Template(f.read())
