import xml.etree.ElementTree as ET
from collections import namedtuple

# Data structures for circuit topology
Node = namedtuple('Node', ['id', 'x', 'y'])
Elem = namedtuple('Elem', ['type', 'id', 'from_node', 'to_node'])

def load_circuit(filename):
    """
    Parse an XML‐style circuit file and return:
     - nodes: dict of node_id -> Node(id, x, y)
     - elems: list of Elem(type, id, from_node, to_node)
    """
    tree = ET.parse(filename)
    root = tree.getroot()

    # Parse nodes
    nodes = {}
    for n in root.findall('node'):
        nid = n.attrib['id']
        x = int(n.attrib.get('x', 0))
        y = int(n.attrib.get('y', 0))
        nodes[nid] = Node(nid, x, y)

    # Parse elements
    elems = []
    for tag in ('resistor', 'inductor', 'capacitor', 'voltage'):
        for e in root.findall(tag):
            elems.append(Elem(tag, e.attrib['id'], e.attrib['from'], e.attrib['to']))

    return nodes, elems