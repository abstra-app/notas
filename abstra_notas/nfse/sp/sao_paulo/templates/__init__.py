from pathlib import Path
from jinja2 import Template

current_path = Path(__file__).parent


def load_template(class_name):
    with open(current_path / f"{class_name}.xml", "r", encoding="utf-8") as file:
        return Template(file.read())
