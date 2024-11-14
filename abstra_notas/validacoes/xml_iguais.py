from lxml.etree import ElementBase
from typing import List


def assert_xml_iguais(
    xml1: ElementBase,
    xml2: ElementBase,
    path: List[str] = [],
    ignorar_tags: List[str] = [],
):
    xml1: ElementBase = xml1
    xml2: ElementBase = xml2

    path_str = " -> ".join(path)

    # mesma tag
    if xml1.tag in ignorar_tags and xml2.tag in ignorar_tags:
        return

    assert xml1.tag == xml2.tag, f"Tags diferentes: {path_str} {xml1.tag} != {xml2.tag}"

    # mesmos atributos
    for k, v in xml1.items():
        assert (
            xml2.get(k) == v
        ), f"Atributos diferentes: {path_str} {k} {v} != {xml2.get(k)}"

    # mesmos filhos
    children1 = [c1.tag for c1 in xml1 if c1.tag not in ignorar_tags]
    children2 = [c2.tag for c2 in xml2 if c2.tag not in ignorar_tags]
    assert (
        children1 == children2
    ), f"Filhos diferentes: {[c1.tag for c1 in xml1]} != {[c2.tag for c2 in xml2]}"

    if len(xml1) == 0:
        assert (
            xml1.text == xml2.text
        ), f"Textos diferentes: {path_str} -> {xml1.tag} {xml1.text} != {xml2.text}"
    else:
        for c1, c2 in zip(xml1, xml2):
            assert_xml_iguais(c1, c2, path + [xml1.tag], ignorar_tags=ignorar_tags)
