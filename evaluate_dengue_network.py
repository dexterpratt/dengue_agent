#!/usr/bin/env python3

"""
Script to evaluate the dengue network and extract key statistics.
"""

from tools.utils.ndex_utils import get_ndex_client
from tools.utils.network_utils import cx2_to_networkx
from ndex2.cx2 import RawCX2NetworkFactory
import json
import os

def evaluate_network(uuid, output_dir):
    """Evaluate the network and save results to the output directory."""
    # Get the network from NDEx
    client = get_ndex_client()
    response = client.get_network_as_cx2_stream(uuid)
    cx2_raw_data = response.json()
    
    # Create CX2Network object
    factory = RawCX2NetworkFactory()
    cx2_network = factory.get_cx2network(cx2_raw_data)
    
    # Convert to NetworkX
    G = cx2_to_networkx(cx2_network)
    
    # Basic network statistics
    network_name = G.graph.get('name', 'Unnamed')
    node_count = G.number_of_nodes()
    edge_count = G.number_of_edges()
    density = edge_count / (node_count * (node_count - 1) / 2)
    avg_degree = sum(dict(G.degree()).values()) / node_count
    
    print(f"Network: {network_name}")
    print(f"Nodes: {node_count}")
    print(f"Edges: {edge_count}")
    print(f"Density: {density:.6f}")
    print(f"Average degree: {avg_degree:.2f}")
    
    # Find viral proteins
    viral_proteins = []
    for node, attrs in G.nodes(data=True):
        if attrs.get('viral_protein', False) or attrs.get('type', '') == 'viral':
            viral_proteins.append((node, attrs.get('name', 'Unknown')))
    
    print(f"\nViral Proteins ({len(viral_proteins)}):")
    for node_id, name in viral_proteins:
        print(f"  - {name} (ID: {node_id})")
    
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
    
    # Find NS2B3 information specifically
    ns2b3_nodes = [node for node, name in viral_proteins if 'NS2B3' in name]
    
    ns2b3_info = {}
    if ns2b3_nodes:
        ns2b3_node = ns2b3_nodes[0]
        ns2b3_info['id'] = ns2b3_node
        ns2b3_info['name'] = G.nodes[ns2b3_node].get('name', 'Unknown')
        ns2b3_info['attributes'] = {k: v for k, v in G.nodes[ns2b3_node].items()}
        
        # Find direct neighbors
        ns2b3_neighbors = []
        for neighbor in G.neighbors(ns2b3_node):
            neighbor_data = {
                'id': neighbor,
                'name': G.nodes[neighbor].get('name', 'Unknown'),
                'type': G.nodes[neighbor].get('type', 'Unknown'),
                'edge_data': G.get_edge_data(ns2b3_node, neighbor)
            }
            ns2b3_neighbors.append(neighbor_data)
            
        ns2b3_info['neighbors'] = ns2b3_neighbors
        
        print(f"\nNS2B3 Information:")
        print(f"  - Node ID: {ns2b3_info['id']}")
        print(f"  - Name: {ns2b3_info['name']}")
        print(f"  - Direct neighbors: {len(ns2b3_neighbors)}")
        
        print(f"\nNS2B3 Direct Interaction Partners:")
        for i, neighbor in enumerate(ns2b3_neighbors):
            print(f"  {i+1}. {neighbor['name']} (ID: {neighbor['id']}, Type: {neighbor['type']})")
    
    # Print node type distribution
    node_types = {}
    for _, attrs in G.nodes(data=True):
        node_type = attrs.get('type', 'unknown')
        if node_type not in node_types:
            node_types[node_type] = 0
        node_types[node_type] += 1
    
    print(f"\nNode Type Distribution:")
    for node_type, count in sorted(node_types.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {node_type}: {count} nodes ({count/node_count*100:.1f}%)")
    
    # Save evaluation results to file
    results = {
        'network_name': network_name,
        'network_uuid': uuid,
        'node_count': node_count,
        'edge_count': edge_count,
        'density': density,
        'avg_degree': avg_degree,
        'viral_proteins': [{'id': vp[0], 'name': vp[1]} for vp in viral_proteins],
        'experimental_properties': list(sorted(experimental_props)),
        'node_type_distribution': {k: {'count': v, 'percentage': v/node_count*100} for k, v in node_types.items()},
        'ns2b3_info': ns2b3_info
    }
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Save results to JSON
    json_path = os.path.join(output_dir, 'network_evaluation.json')
    with open(json_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nEvaluation results saved to: {json_path}")
    
    return results

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python evaluate_dengue_network.py <ndex_uuid> <output_directory>")
        sys.exit(1)
    
    uuid = sys.argv[1]
    output_dir = sys.argv[2]
    
    evaluate_network(uuid, output_dir)
