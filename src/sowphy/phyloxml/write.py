from sowing.node import Node
from sowing.traversal import Order, traverse, transform
from xml.etree import ElementTree as ET


NAMESPACE = "http://www.phyloxml.org"
phylo = lambda tag: f"{{{NAMESPACE}}}{tag}"


def map_edge(edge):
    child, length = edge
    element = child.data

    if length is not None:
        length_element = ET.SubElement(element, phylo("branch_length"))
        length_element.text = str(length)

    return element


def map_node(node: Node, _):
    element = ET.Element(phylo("clade"))

    name_element = ET.SubElement(element, phylo("name"))
    name_element.text = node.data

    element.extend(map(map_edge, node.children))
    return Node(element), _


def write(root: Node):
    xml = ET.Element(phylo("phyloxml"))
    phylogeny = ET.SubElement(xml, phylo("phylogeny"))

    clades = transform(map_node, traverse(root, Order.Post)).data
    phylogeny.append(clades)

    return ET.tostring(
        element=xml,
        default_namespace=NAMESPACE,
        encoding="unicode",
        xml_declaration=True,
    )
