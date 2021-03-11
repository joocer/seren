"""
Diablo: Python Graph Library

(C) 2021 Justin Joyce.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import types
from .graph import Graph
from .diablo import Diablo
from .errors import NodeNotFoundError
import orjson as json
try:
    import xmltodict  # type:ignore
except ImportError:
    pass

BTREE_ORDER = 16

def _make_a_list(obj):
    """ internal helper method """
    if isinstance(obj, (list, types.GeneratorType)):
        return obj
    return [obj]


def walk(graph, nids=None):
    """
    Begin a traversal by selecting the matching nodes.

    Parameters:
        *nids: strings
            the identity(s) of the node(s) to select

    Returns:
        A Diablo instance
    """
    if nids:
        nids = _make_a_list(nids)
        if len(nids) > 0:
            return Diablo(
                graph=graph,
                active_nodes=nids)
    else:
        return Diablo(graph, set())


def read_graphml(
        xml_file: str):
    """

    Parameters:
        xml_file: string
    """
    with open(xml_file, 'r') as fd:
        xml_dom = xmltodict.parse(fd.read())

    g = Graph()

    # load the keys
    keys = {}
    for key in xml_dom['graphml'].get('key', {}):
        keys[key['@id']] = key['@attr.name']

    g._nodes = BTree(BTREE_ORDER)
    # load the nodes
    for node in xml_dom['graphml']['graph'].get('node', {}):
        data = {}
        skip = False
        for key in g._make_a_list(node.get('data', {})):
            try:
                data[keys[key['@key']]] = key.get('#text', '')
            except:
                skip = True
        if not skip:
            g._nodes.insert(node['@id'], data)

    g._edges = {}
    for edge in xml_dom['graphml']['graph'].get('edge', {}):
        data = {}
        source = edge['@source']
        target = edge['@target']
        for key in g._make_a_list(edge.get('data', {})):
            data[keys[key['@key']]] = key['#text']
        if source not in g._edges:
            g._edges[source] = []
        g.add_edge(source, target, data.get('relationship'))

    return g


def _load_node_file(filename):
    nodes = []
    with open(filename, 'r') as node_file:
        for line in node_file:
            node = json.loads(line)
            nodes.append((node['nid'], node['attributes'],))
    results = {n:a for n, a in nodes}
    return results

def _load_edge_file(filename):
    edges = []
    with open(filename, 'r') as edge_file:
        for line in edge_file:
            node = json.loads(line)
            edges.append((node['source'], node['target'], node['relationship'],))
    results = {s:[] for s, t, r in edges}
    for s, t, r in edges:
        results[s].append((t,r,))
    return results

def load(path):
    g = Graph()
    g._nodes = _load_node_file(path + '/nodes.jsonl')
    g._edges = _load_edge_file(path + '/edges.jsonl')
    return g
