#!/usr/bin/env python3

"""
Network analysis script for the test dengue network.
"""

import json
import sys
from tools.utils.network_utils import load_cx2_from_file, cx2_to_networkx

def analyze_network(network_path):
    """Analyze a network file and print key properties."""
    print(f"Analyzing network: {network_path}")
    
    # Load the CX2 network and convert to NetworkX
    cx2_network = load_cx2_from_file(network_path)
    G = cx2_to_networkx(cx2_network)
    
    # Basic network statistics
    print(f"\nBasic Network Statistics:")
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

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: analyze_network.py <network_file_path>")
        sys.exit(1)
    
    analyze_network(sys.argv[1])
