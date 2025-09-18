#!/usr/bin/env python3

"""
Full dengue virus network analysis following the self-prompt framework.
"""

import os
import json
from datetime import datetime
import networkx as nx
from tools.utils.ndex_utils import get_ndex_client
from tools.utils.network_utils import cx2_to_networkx, save_cx2_to_file
from tools.utils.session_utils import create_session, create_analysis_dir, register_file
from tools.dengue.viral_propagation import run_viral_propagation
from ndex2.cx2 import RawCX2NetworkFactory

def dengue_network_analysis(
    uuid, 
    session_id=None, 
    restart_prob=0.15, 
    max_steps=150, 
    specific_protein=None
):
    """
    Run the full dengue analysis workflow for a network.
    
    Args:
        uuid: NDEx UUID of the dengue network
        session_id: Optional existing session ID
        restart_prob: Restart probability for propagation
        max_steps: Maximum steps for propagation
        specific_protein: Optional specific viral protein name to focus on
    """
    # [SELF-PROMPT: Session Initialization]
    print(f"[SELF-PROMPT: Session Initialization]")
    print(f"Analyzing dengue virus network: {uuid}")
    
    if not session_id:
        # Create a new session
        session_name = f"Dengue Network Analysis {uuid[:8]}"
        session_id, session_dir = create_session(session_name)
    else:
        # Use existing session
        from os.path import join as path_join
        from tools.utils.session_utils import BASE_OUTPUT_DIR
        session_dir = path_join(BASE_OUTPUT_DIR, session_id)
    
    print(f"Session created: {session_id}")
    print(f"Session directory: {session_dir}")
    
    # [SELF-PROMPT: Network Evaluation]
    print(f"\n[SELF-PROMPT: Network Evaluation]")
    
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
    network_name = G.graph.get('name', 'Unnamed')
    node_count = G.number_of_nodes()
    edge_count = G.number_of_edges()
    avg_degree = sum(dict(G.degree()).values()) / node_count
    
    print(f"Network name: {network_name}")
    print(f"Nodes: {node_count}")
    print(f"Edges: {edge_count}")
    print(f"Average degree: {avg_degree:.2f}")
    print(f"Network density: {edge_count / (node_count * (node_count - 1) / 2):.4f}")
    
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
    
    # Create an evaluation directory
    eval_id, eval_dir = create_analysis_dir(session_dir, "network_evaluation")
    
    # Save evaluation results
    evaluation = {
        "network_name": network_name,
        "network_uuid": uuid,
        "node_count": node_count,
        "edge_count": edge_count,
        "avg_degree": avg_degree,
        "viral_proteins": [{
            "id": vp[0], 
            "name": vp[1]
        } for vp in viral_proteins],
        "experimental_properties": list(experimental_props),
        "analysis_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    eval_file = os.path.join(eval_dir, "network_evaluation.json")
    with open(eval_file, 'w') as f:
        json.dump(evaluation, f, indent=2)
    
    register_file(session_dir, eval_id, "network_evaluation.json", "json", "Network evaluation results")
    
    # [SELF-PROMPT: Propagation Parameter Selection]
    print(f"\n[SELF-PROMPT: Propagation Parameter Selection]")
    
    # Select appropriate propagation parameters based on network properties
    # Lower restart probability (0.15) to explore broader network context
    # Higher max steps (150) to ensure convergence in this network
    
    print(f"For {network_name}, selecting propagation parameters:")
    print(f"  - Algorithm: Single-seed random walk with restart")
    print(f"  - Restart probability: {restart_prob} (lower than default 0.2 to explore broader context)")
    print(f"  - Maximum steps: {max_steps} (increased to ensure convergence)")
    
    # [SELF-PROMPT: Propagation Execution]
    print(f"\n[SELF-PROMPT: Propagation Execution]")
    
    # Filter to specific protein if requested
    if specific_protein:
        process_all = False
        specific_proteins = [specific_protein]
        print(f"Running propagation for specific protein: {specific_protein}")
    else:
        process_all = True
        specific_proteins = None
        print(f"Running propagation for all viral proteins")
    
    # Run propagation with selected parameters
    propagation_results = run_viral_propagation(
        network_source=uuid,
        session_id=session_id,
        restart_prob=restart_prob,
        max_steps=max_steps,
        process_all_proteins=process_all,
        specific_proteins=specific_proteins,
        upload_networks=False
    )
    
    print(f"Propagation completed, analysis ID: {propagation_results['analysis_id']}")
    
    # [SELF-PROMPT: Result Analysis]
    print(f"\n[SELF-PROMPT: Result Analysis]")
    
    # For each viral protein, analyze the propagation results
    for viral_protein_name, results in propagation_results['viral_proteins'].items():
        if 'error' in results:
            print(f"Error processing {viral_protein_name}: {results['error']}")
            continue
            
        print(f"\nAnalysis for {viral_protein_name}:")
        
        # Get the CX2 file for this viral protein
        cx2_file = propagation_results.get('cx2_files', {}).get(viral_protein_name)
        if not cx2_file:
            print(f"  No CX2 file found for {viral_protein_name}")
            continue
            
        print(f"  Propagation statistics:")
        print(f"    - Execution time: {results['execution_time']:.2f} seconds")
        print(f"    - Walk stats: {results['walk_stats']}")
        
        # Load the propagation network to get top nodes
        from os.path import join as path_join
        from tools.utils.session_utils import get_latest_analysis_dir
        from tools.utils.network_utils import load_cx2_from_file
        
        analysis_dir = get_latest_analysis_dir(session_dir, 'propagation')
        prop_file = path_join(analysis_dir, cx2_file)
        
        if os.path.exists(prop_file):
            # Load propagation network
            prop_network = cx2_to_networkx(load_cx2_from_file(prop_file))
            
            # Get top nodes by propagation weight
            nodes_with_weights = []
            for node, attrs in prop_network.nodes(data=True):
                if 'propagation_weight' in attrs:
                    nodes_with_weights.append((
                        node, 
                        attrs.get('name', 'Unknown'),
                        attrs.get('propagation_weight', 0)
                    ))
            
            # Sort and print top nodes
            sorted_nodes = sorted(nodes_with_weights, key=lambda x: x[2], reverse=True)
            print(f"\n  Top weighted nodes for {viral_protein_name}:")
            for i, (node_id, name, weight) in enumerate(sorted_nodes[:10]):
                print(f"    {i+1}. {name} (ID: {node_id}): {weight:.4f}")
    
    return session_id, propagation_results

if __name__ == "__main__":
    # Run dengue analysis for the network with documentation
    uuid = "557f787b-fad5-11ef-b81d-005056ae3c32"
    session_id, results = dengue_network_analysis(uuid)
    print(f"\nAnalysis complete. Session ID: {session_id}")
