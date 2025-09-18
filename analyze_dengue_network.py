#!/usr/bin/env python3

"""
Script to analyze the dengue network with UUID 557f787b-fad5-11ef-b81d-005056ae3c32.
"""

from tools.utils.ndex_utils import get_ndex_client
from tools.utils.network_utils import cx2_to_networkx
from ndex2.cx2 import RawCX2NetworkFactory

def analyze_dengue_network(uuid):
    """Analyze the dengue network with the given UUID."""
    # Get the network from NDEx
    client = get_ndex_client()
    response = client.get_network_as_cx2_stream(uuid)
    cx2_raw_data = response.json()
    
    # Create CX2Network object
    factory = RawCX2NetworkFactory()
    cx2_network = factory.get_cx2network(cx2_raw_data)
    
    # Convert to NetworkX
    G = cx2_to_networkx(cx2_network)
    
    # Print basic network statistics
    print(f"Network Analysis: {G.graph.get('name', 'Unnamed')}")
    print(f"Nodes: {G.number_of_nodes()}")
    print(f"Edges: {G.number_of_edges()}")
    print(f"Average degree: {sum(dict(G.degree()).values()) / G.number_of_nodes():.2f}")
    
    # Find viral proteins
    viral_proteins = []
    for node, attrs in G.nodes(data=True):
        if attrs.get('viral_protein', False) or attrs.get('type', '') == 'viral':
            viral_proteins.append((node, attrs.get('name', 'Unknown')))
    
    print(f"\nViral Proteins ({len(viral_proteins)}):")
    for node_id, name in viral_proteins:
        print(f"  - {name} (ID: {node_id})")
    
    # Find nodes with Bait field (potential viral proteins)
    baits = {}
    for node, attrs in G.nodes(data=True):
        if 'Bait' in attrs:
            bait = attrs['Bait']
            if bait not in baits:
                baits[bait] = []
            baits[bait].append((node, attrs.get('name', 'Unknown')))
    
    print(f"\nBait Categories ({len(baits)}):")
    for bait, nodes in baits.items():
        print(f"  - {bait}: {len(nodes)} nodes")
    
    # Find experimental data properties
    experimental_props = set()
    for _, attrs in G.nodes(data=True):
        for key, value in attrs.items():
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                if key not in ('x', 'y', 'z', 'id'):
                    experimental_props.add(key)
    
    print(f"\nExperimental Data Properties:")
    for prop in sorted(experimental_props):
        print(f"  - {prop}")
    
    # Print node type distribution
    node_types = {}
    for _, attrs in G.nodes(data=True):
        node_type = attrs.get('type', 'unknown')
        if node_type not in node_types:
            node_types[node_type] = 0
        node_types[node_type] += 1
    
    print(f"\nNode Type Distribution:")
    for node_type, count in sorted(node_types.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {node_type}: {count} nodes ({count/G.number_of_nodes()*100:.1f}%)")
    
    return G, viral_proteins, experimental_props

if __name__ == "__main__":
    analyze_dengue_network("557f787b-fad5-11ef-b81d-005056ae3c32")
