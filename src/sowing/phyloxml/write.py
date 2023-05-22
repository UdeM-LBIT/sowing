from ..net import Net, Order
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


def map_node(node: Net):
    element = ET.Element(phylo("clade"))

    name_element = ET.SubElement(element, phylo("name"))
    name_element.text = node.data

    element.extend(map(map_edge, node.children))
    return Net(element)


def write(net: Net):
    root = ET.Element(phylo("phyloxml"))
    phylogeny = ET.SubElement(root, phylo("phylogeny"))

    clades = net.map(map_node, Order.Post).data
    phylogeny.append(clades)

    return ET.tostring(
        element=root,
        default_namespace=NAMESPACE,
        encoding="unicode",
        xml_declaration=True,
    )
