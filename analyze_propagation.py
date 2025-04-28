#!/usr/bin/env python3

"""
Script to analyze propagation results from the dengue network.
"""

import json
import sys
import os
from tools.utils.network_utils import load_cx2_from_file, cx2_to_networkx

def analyze_propagation_network(network_path):
    """Analyze a propagation result network and print key properties."""
    print(f"Analyzing propagation network: {network_path}")
    
    # Load the CX2 network and convert to NetworkX
    cx2_network = load_cx2_from_file(network_path)
    G = cx2_to_networkx(cx2_network)
    
    # Get network attributes
    network_name = G.graph.get('name', 'Unknown')
    print(f"\nNetwork: {network_name}")
    
    # Find nodes with propagation weights
    nodes_with_weights = []
    for node, attrs in G.nodes(data=True):
        if 'propagation_weight' in attrs:
            nodes_with_weights.append((
                node, 
                attrs.get('name', 'Unknown'),
                attrs.get('propagation_weight', 0)
            ))
    
    print(f"\nNodes with propagation weights: {len(nodes_with_weights)}")
    
    # Sort and display top nodes
    sorted_nodes = sorted(nodes_with_weights, key=lambda x: x[2], reverse=True)
    print("\nTop weighted nodes:")
    for i, (node_id, name, weight) in enumerate(sorted_nodes[:20]):
        print(f"  {i+1}. {name} (ID: {node_id}): {weight:.4f}")
    
    # Extract source nodes
    source_nodes = []
    if 'seed_nodes' in G.graph:
        try:
            source_node_ids = json.loads(G.graph['seed_nodes'])
            for node_id in source_node_ids:
                if node_id in G:
                    name = G.nodes[node_id].get('name', 'Unknown')
                    source_nodes.append((node_id, name))
        except:
            # Fallback method
            for node, attrs in G.nodes(data=True):
                if attrs.get('viral_protein', False) or attrs.get('type', '') == 'viral':
                    source_nodes.append((node, attrs.get('name', 'Unknown')))
    
    print(f"\nSource nodes:")
    for node_id, name in source_nodes:
        print(f"  - {name} (ID: {node_id})")
    
    # Look at connections of top nodes
    if sorted_nodes:
        top_node_id = sorted_nodes[0][0]
        top_node_name = sorted_nodes[0][1]
        
        print(f"\nConnections of top node {top_node_name} (ID: {top_node_id}):")
        for neighbor in G.neighbors(top_node_id):
            neighbor_name = G.nodes[neighbor].get('name', 'Unknown')
            weight = G.nodes[neighbor].get('propagation_weight', 0)
            edge_data = G.get_edge_data(top_node_id, neighbor)
            interaction = edge_data.get('interaction', '') if edge_data else ''
            
            print(f"  - {neighbor_name} (ID: {neighbor}) - Weight: {weight:.4f}")
            if interaction:
                print(f"    Interaction: {interaction}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: analyze_propagation.py <propagation_network_file_path>")
        sys.exit(1)
    
    analyze_propagation_network(sys.argv[1])
