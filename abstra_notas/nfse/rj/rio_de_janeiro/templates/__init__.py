from jinja2 import Environment, FileSystemLoader, Template
from pathlib import Path


def load_template(nome_template: str) -> Template:
    """
    Carrega um template Jinja2 a partir do nome do arquivo.
    """
    template_path = Path(__file__).parent
    env = Environment(loader=FileSystemLoader(template_path))
    return env.get_template(f"{nome_template}.xml")