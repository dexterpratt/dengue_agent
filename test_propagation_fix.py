#!/usr/bin/env python3

"""
Test script for the fixed random walk with restart algorithm.
This compares results between different parameter settings to demonstrate 
the impact of the fix.
"""

import os
import json
import time
import networkx as nx
from datetime import datetime

# Import necessary modules from the dengue_agent project
from tools.utils.network_utils import load_cx2_from_file, cx2_to_networkx, get_network_info
from tools.algorithms.propagation import score_multi_seed_random_walk
from tools.utils.session_utils import create_session, create_analysis_dir, register_file

def test_propagation_on_network(
    network_path,
    max_steps_list=[50, 100, 200],
    restart_prob_list=[0.15, 0.2, 0.3]
):
    """
    Test the propagation algorithm with different parameters on the given network.
    
    Args:
        network_path: Path to the CX2 network file
        max_steps_list: List of max_steps values to test
        restart_prob_list: List of restart probability values to test
    """
    print(f"\nTesting propagation on network: {network_path}")
    
    # Load the network
    cx2_network = load_cx2_from_file(network_path)
    G = cx2_to_networkx(cx2_network)
    
    # Get network info
    info = get_network_info(cx2_network)
    print(f"Network: {info['name']}")
    print(f"Nodes: {info['node_count']}, Edges: {info['edge_count']}")
    
    # Identify viral proteins
    viral_proteins = []
    for node_id, attrs in G.nodes(data=True):
        if attrs.get('viral_protein', False) or attrs.get('type', '') == 'viral':
            name = attrs.get('name', str(node_id))
            viral_proteins.append((node_id, name))
    
    print(f"Found {len(viral_proteins)} viral proteins:")
    for node_id, name in viral_proteins:
        print(f"  - {name} (ID: {node_id})")
    
    # Create a session for the test results
    session_name = f"Propagation_Fix_Test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    session_id, session_dir = create_session(session_name)
    print(f"\nCreated session: {session_id}")
    print(f"Session directory: {session_dir}")
    
    # Create analysis directory
    analysis_id, analysis_dir = create_analysis_dir(session_dir, "propagation_test")
    print(f"Analysis directory: {analysis_dir}")
    
    # Test results will be stored here
    all_results = {
        'session_id': session_id,
        'analysis_id': analysis_id,
        'network_info': info,
        'test_configurations': [],
        'viral_proteins': [{'id': vp[0], 'name': vp[1]} for vp in viral_proteins]
    }
    
    # Run tests for different viral proteins
    for node_id, name in viral_proteins:
        print(f"\nTesting propagation from {name} (ID: {node_id})")
        
        protein_results = {
            'viral_protein': {'id': node_id, 'name': name},
            'configurations': []
        }
        
        # Test with different parameter combinations
        for restart_prob in restart_prob_list:
            for max_steps in max_steps_list:
                print(f"  Parameters: restart_prob={restart_prob}, max_steps={max_steps}")
                
                # Run propagation
                start_time = time.time()
                result = score_multi_seed_random_walk(
                    G,
                    [node_id],
                    restart_prob=restart_prob,
                    max_steps=max_steps,
                    allow_revisits=True,
                    seed_selection_strategy='uniform'
                )
                execution_time = time.time() - start_time
                result['execution_time'] = execution_time
                
                # Extract and print key stats
                walk_stats = result['walk_stats']
                node_weights = result['node_weights']
                num_visited_nodes = len(node_weights)
                
                print(f"    Visited nodes: {num_visited_nodes}")
                print(f"    Steps: {walk_stats['steps']}")
                print(f"    Restarts: {walk_stats['restarts']}")
                if 'forced_restarts' in walk_stats:
                    print(f"    Forced restarts: {walk_stats['forced_restarts']}")
                print(f"    Termination reason: {walk_stats['termination_reason']}")
                print(f"    Execution time: {execution_time:.4f} seconds")
                
                # Store configuration and results
                config = {
                    'parameters': {
                        'restart_prob': restart_prob,
                        'max_steps': max_steps
                    },
                    'results': {
                        'visited_nodes': num_visited_nodes,
                        'steps': walk_stats['steps'],
                        'restarts': walk_stats['restarts'],
                        'forced_restarts': walk_stats.get('forced_restarts', 0),
                        'termination_reason': walk_stats['termination_reason'],
                        'execution_time': execution_time
                    }
                }
                protein_results['configurations'].append(config)
                
                # Print top 5 nodes by weight
                print("    Top 5 nodes by weight:")
                top_nodes = sorted(
                    [(node, weight) for node, weight in node_weights.items()],
                    key=lambda x: x[1],
                    reverse=True
                )[:5]
                
                for node, weight in top_nodes:
                    node_name = G.nodes[node].get('name', str(node))
                    print(f"      {node_name} (ID: {node}): {weight:.4f}")
        
        # Add protein results to overall results
        all_results['test_configurations'].append(protein_results)
    
    # Save all results to a JSON file
    results_file = os.path.join(analysis_dir, "propagation_test_results.json")
    with open(results_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    # Register the file
    register_file(session_id, analysis_id, "propagation_test_results.json", "json", "Propagation test results")
    
    print(f"\nTest completed. Results saved to: {results_file}")
    return results_file

if __name__ == "__main__":
    # Test on the provided dengue test network
    test_network_path = "tests/test_dengue_network.cx2"
    
    if not os.path.exists(test_network_path):
        print(f"Error: Test network file not found at {test_network_path}")
        exit(1)
    
    results_file = test_propagation_on_network(test_network_path)
    print(f"\nTest results saved to: {results_file}")
