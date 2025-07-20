from jinja2 import Template
from pathlib import Path

def load_template(template_name: str) -> Template:
    """
    Load a Jinja2 template by its name.

    :param template_name: The name of the template to load.
    :return: A Jinja2 Template object.
    """

    return Template((Path(__file__).parent / f"{template_name}.xml").read_text(encoding="utf-8"))
