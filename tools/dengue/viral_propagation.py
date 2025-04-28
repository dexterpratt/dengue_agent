#!/usr/bin/env python3

"""
Dengue-specific viral protein propagation module.
Performs propagation analysis from viral proteins in dengue networks.
"""

import sys
import os
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional, Union
import networkx as nx
import ndex2.client as nc2
from ndex2.cx2 import CX2Network, RawCX2NetworkFactory

# Import from tools package
from tools.algorithms.propagation import score_limited_random_walk_with_restart, score_multi_seed_random_walk
from tools.algorithms.propagation import create_propagation_network
from tools.utils.network_utils import (
    cx2_to_networkx, save_cx2_to_file, load_cx2_from_file, 
    find_latest_cx2_file, get_network_info
)
from tools.utils.session_utils import (
    create_session, create_analysis_dir, update_analysis_status,
    register_file, get_latest_analysis_dir
)
from tools.utils.ndex_utils import get_ndex_client, get_complete_network

def identify_viral_proteins(G: nx.Graph) -> List[Tuple[str, str]]:
    """
    Identify viral proteins in the network
    
    Args:
        G: NetworkX graph
        
    Returns:
        List of tuples (node_id, name) for viral proteins
    """
    viral_proteins = []
    
    for node_id, attrs in G.nodes(data=True):
        # Check if this is a viral protein by looking at viral_protein property or type
        is_viral = attrs.get('viral_protein', False) or attrs.get('type', '') == 'viral'
        
        if is_viral:
            # Get name from attributes
            name = attrs.get('name', '')
            if not name:
                name = attrs.get('GeneSymbol', str(node_id))
            
            viral_proteins.append((node_id, name))
    
    return viral_proteins

def propagate_from_viral_protein(
    G: nx.Graph,
    original_cx2: Union[CX2Network, Dict, List],
    viral_protein_id: str,
    viral_protein_name: str,
    restart_prob: float = 0.2,
    max_score: float = 10.0,
    max_steps: int = 100,
    type_score_dict: Optional[Dict[str, float]] = None,
    default_score: float = 1.0,
    allow_revisits: bool = True,
    include_all_nodes: bool = False
) -> Tuple[Dict, Dict[str, Any]]:
    """
    Propagate from a viral protein and create network with results.
    
    Args:
        G: NetworkX graph
        original_cx2: Original CX2Network (or CX2 data as dict/list)
        viral_protein_id: ID of the viral protein used as seed node
        viral_protein_name: Name of the viral protein
        restart_prob: Restart probability
        max_score: Maximum cumulative score
        max_steps: Maximum steps per propagation
        type_score_dict: Dictionary mapping node types to scores
        default_score: Default node score
        allow_revisits: Allow revisiting nodes
        include_all_nodes: If True, include all nodes, otherwise only nodes with weights
        
    Returns:
        Tuple of (Enhanced CX2 network as dict, propagation results)
    """
    # Run propagation
    start_time = time.time()
    results = score_limited_random_walk_with_restart(
        G,
        viral_protein_id,
        restart_prob=restart_prob,
        max_cumulative_score=max_score,
        max_steps=max_steps,
        type_score_dict=type_score_dict,
        default_score=default_score,
        allow_revisits=allow_revisits
    )
    execution_time = time.time() - start_time
    results['execution_time'] = execution_time
    
    # Create network with propagation results
    network_name = f"Propagation from {viral_protein_name}"
    cx2_data = create_propagation_network(
        original_cx2,
        results['node_weights'],
        [viral_protein_id],
        include_all_nodes=include_all_nodes,
        network_name=network_name
    )
    
    # Use the standard ndex2 library to update network attributes
    from tools.utils.network_utils import create_cx2_from_dict
    cx2_network = create_cx2_from_dict(cx2_data)
    
    # Add viral protein specific attributes
    cx2_network.set_network_attributes({"viral_protein_id": viral_protein_id})
    cx2_network.set_network_attributes({"viral_protein_name": viral_protein_name})
    
    # Convert back to CX2 data format
    return cx2_network.to_cx2(), results

def propagate_from_multiple_viral_proteins(
    G: nx.Graph,
    original_cx2: Union[CX2Network, Dict, List],
    viral_proteins: List[Tuple[str, str]],
    restart_prob: float = 0.2,
    max_score: float = 10.0,
    max_steps: int = 100,
    type_score_dict: Optional[Dict[str, float]] = None,
    default_score: float = 1.0,
    allow_revisits: bool = True,
    include_all_nodes: bool = False,
    seed_selection_strategy: str = 'uniform'
) -> Tuple[Dict, Dict[str, Any]]:
    """
    Propagate from multiple viral proteins and create a combined network.
    
    Args:
        G: NetworkX graph
        original_cx2: Original CX2Network (or CX2 data as dict/list)
        viral_proteins: List of (node_id, name) tuples for viral proteins
        restart_prob: Restart probability
        max_score: Maximum cumulative score
        max_steps: Maximum steps per propagation
        type_score_dict: Dictionary mapping node types to scores
        default_score: Default node score
        allow_revisits: Allow revisiting nodes
        include_all_nodes: If True, include all nodes, otherwise only nodes with weights
        seed_selection_strategy: Strategy for selecting seed nodes during restarts
        
    Returns:
        Tuple of (Enhanced CX2 network as dict, propagation results)
    """
    # Extract just the node IDs for propagation
    viral_protein_ids = [vp[0] for vp in viral_proteins]
    viral_protein_names = [vp[1] for vp in viral_proteins]
    
    # Run multi-seed propagation
    start_time = time.time()
    results = score_multi_seed_random_walk(
        G,
        viral_protein_ids,
        restart_prob=restart_prob,
        max_cumulative_score=max_score,
        max_steps=max_steps,
        type_score_dict=type_score_dict,
        default_score=default_score,
        allow_revisits=allow_revisits,
        seed_selection_strategy=seed_selection_strategy
    )
    execution_time = time.time() - start_time
    results['execution_time'] = execution_time
    
    # Create network with propagation results
    protein_names_str = ", ".join(viral_protein_names[:3])
    if len(viral_protein_names) > 3:
        protein_names_str += f" and {len(viral_protein_names) - 3} more"
    
    network_name = f"Propagation from {protein_names_str}"
    cx2_data = create_propagation_network(
        original_cx2,
        results['node_weights'],
        viral_protein_ids,
        include_all_nodes=include_all_nodes,
        network_name=network_name
    )
    
    # Add viral proteins list as an attribute using the standard library
    from tools.utils.network_utils import create_cx2_from_dict
    cx2_network = create_cx2_from_dict(cx2_data)
    
    # Create JSON representation of viral proteins
    viral_proteins_json = json.dumps([
        {"id": vp_id, "name": vp_name} for vp_id, vp_name in viral_proteins
    ])
    
    # Set the attribute using the CX2Network API
    cx2_network.set_network_attributes({"viral_proteins": viral_proteins_json})
    
    # Convert back to CX2 data format
    return cx2_network.to_cx2(), results

def upload_to_ndex(cx2_data: Union[Dict, List, CX2Network]) -> str:
    """
    Upload a CX2 network to NDEx
    
    Args:
        cx2_data: CX2 network data (as dict, list, or CX2Network object)
        
    Returns:
        UUID of the uploaded network
    """
    # Get NDEx client
    client = get_ndex_client()
    
    # Convert to CX2Network object if needed
    if isinstance(cx2_data, CX2Network):
        cx2_data = cx2_data.to_cx2()
    
    # Upload to NDEx using the standard client method
    response = client.save_new_cx2_network(cx2_data)
    return response

def run_viral_propagation(
    network_source: Union[str, CX2Network, nx.Graph],
    session_id: Optional[str] = None,
    session_name: Optional[str] = None,
    type_scores_file: Optional[str] = None,
    restart_prob: float = 0.2,
    max_score: float = 10.0,
    max_steps: int = 100,
    default_score: float = 1.0,
    allow_revisits: bool = True,
    include_all_nodes: bool = False,
    upload_networks: bool = False,
    process_all_proteins: bool = True,
    specific_proteins: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Main entry point for viral protein propagation
    
    Args:
        network_source: Network source, which can be one of:
            - NDEx UUID (string starting with UUID prefix)
            - Path to a CX2 file (string containing .cx2)
            - CX2Network object
            - NetworkX graph
        session_id: Optional existing session ID to use
        session_name: Optional name for the session if creating new
        type_scores_file: JSON file with node type to score mapping
        restart_prob: Restart probability
        max_score: Maximum cumulative score
        max_steps: Maximum steps per propagation
        default_score: Default node score
        allow_revisits: Allow revisiting nodes
        include_all_nodes: Include all nodes in output network
        upload_networks: Upload networks to NDEx (default: False)
        process_all_proteins: Process all viral proteins
        specific_proteins: List of specific viral protein IDs/names to process
        
    Returns:
        Dictionary with propagation results
    """
    # Set up session
    if session_id:
        # Use existing session
        from os.path import join as path_join
        from tools.utils.session_utils import BASE_OUTPUT_DIR
        session_dir = path_join(BASE_OUTPUT_DIR, session_id)
        if not os.path.exists(session_dir):
            print(f"Warning: Session directory not found: {session_dir}")
            print("Creating new session instead.")
            session_id, session_dir = create_session(session_name or "Viral Propagation")
    else:
        # Create new session
        session_id, session_dir = create_session(session_name or "Viral Propagation")
    
    print(f"Using session: {session_id}")
    print(f"Session directory: {session_dir}")
    
    # Create analysis directory for this propagation run
    analysis_id, analysis_dir = create_analysis_dir(session_dir, "propagation")
    print(f"Analysis directory: {analysis_dir}")
    
    # Update analysis status
    update_analysis_status(session_dir, analysis_id, "running", {
        "parameters": {
            "restart_prob": restart_prob,
            "max_score": max_score,
            "max_steps": max_steps,
            "default_score": default_score,
            "allow_revisits": allow_revisits,
            "include_all_nodes": include_all_nodes,
            "upload_networks": upload_networks,
            "process_all_proteins": process_all_proteins
        }
    })
    
    # Load type scores if provided
    type_score_dict = None
    if type_scores_file and os.path.exists(type_scores_file):
        with open(type_scores_file, 'r') as f:
            print(f"Loading type scores from {type_scores_file}")
            type_score_dict = json.load(f)
            
        # Save a copy in the analysis directory
        type_scores_copy = os.path.join(analysis_dir, "type_scores.json")
        with open(type_scores_copy, 'w') as f:
            json.dump(type_score_dict, f, indent=2)
        
        # Register the file
        register_file(session_dir, analysis_id, "type_scores.json", "json", "Node type scores")
    
    # Load network from source
    network_info = {}
    
    # Check if the source is an NDEx UUID (typical format: "12345678-1234-1234-1234-123456789abc")
    if (isinstance(network_source, str) and 
        (network_source.count('-') == 4 or network_source.startswith('uuid:'))):
        
        # Extract UUID if it starts with 'uuid:'
        if network_source.startswith('uuid:'):
            ndex_uuid = network_source[5:]
        else:
            ndex_uuid = network_source
            
        print(f"Loading network {ndex_uuid} from NDEx...")
        
        try:
            # Get network data
            network_data = get_complete_network(ndex_uuid)
            network_name = network_data.get('name', f"network-{ndex_uuid[:8]}")
            print(f"Loaded network '{network_name}' with {network_data['nodeCount']} nodes and {network_data['edgeCount']} edges")
            
            # Get CX2 network
            client = get_ndex_client()
            response = client.get_network_as_cx2_stream(ndex_uuid)
            cx2_raw_data = response.json()
            
            # Create CX2Network object
            factory = RawCX2NetworkFactory()
            original_cx2 = factory.get_cx2network(cx2_raw_data)
            
            # Set network info
            network_info = {
                'source_type': 'ndex',
                'uuid': ndex_uuid,
                'name': network_name,
                'node_count': network_data['nodeCount'],
                'edge_count': network_data['edgeCount']
            }
            
            # Save a local copy of the network
            cx2_file_path = os.path.join(analysis_dir, f"source_network.cx2")
            save_cx2_to_file(original_cx2, cx2_file_path)
            register_file(session_dir, analysis_id, "source_network.cx2", "cx2", f"Source network: {network_name}")
            
        except Exception as e:
            update_analysis_status(session_dir, analysis_id, "error", {"error": str(e)})
            print(f"Error loading network from NDEx: {str(e)}")
            raise
            
    # Check if the source is a CX2 file path
    elif isinstance(network_source, str) and os.path.exists(network_source) and network_source.endswith('.cx2'):
        print(f"Loading network from file: {network_source}")
        
        try:
            # Load CX2 network
            original_cx2 = load_cx2_from_file(network_source)
            
            # Get network info
            info = get_network_info(original_cx2)
            network_name = info['name']
            print(f"Loaded network '{network_name}' with {info['node_count']} nodes and {info['edge_count']} edges")
            
            # Set network info
            network_info = {
                'source_type': 'file',
                'file_path': network_source,
                'name': network_name,
                'node_count': info['node_count'],
                'edge_count': info['edge_count']
            }
            
            # Make a copy of the original network in the analysis directory
            cx2_file_path = os.path.join(analysis_dir, f"source_network.cx2")
            save_cx2_to_file(original_cx2, cx2_file_path)
            register_file(session_dir, analysis_id, "source_network.cx2", "cx2", f"Source network: {network_name}")
            
        except Exception as e:
            update_analysis_status(session_dir, analysis_id, "error", {"error": str(e)})
            print(f"Error loading network from file: {str(e)}")
            raise
            
    # Check if the source is a CX2Network object
    elif isinstance(network_source, CX2Network):
        print("Using provided CX2Network object")
        
        try:
            # Use the provided CX2Network
            original_cx2 = network_source
            
            # Get network info
            info = get_network_info(original_cx2)
            network_name = info['name']
            print(f"Using network '{network_name}' with {info['node_count']} nodes and {info['edge_count']} edges")
            
            # Set network info
            network_info = {
                'source_type': 'cx2_object',
                'name': network_name,
                'node_count': info['node_count'],
                'edge_count': info['edge_count']
            }
            
            # Save the network to the analysis directory
            cx2_file_path = os.path.join(analysis_dir, f"source_network.cx2")
            save_cx2_to_file(original_cx2, cx2_file_path)
            register_file(session_dir, analysis_id, "source_network.cx2", "cx2", f"Source network: {network_name}")
            
        except Exception as e:
            update_analysis_status(session_dir, analysis_id, "error", {"error": str(e)})
            print(f"Error using provided CX2Network: {str(e)}")
            raise
            
    # Check if the source is a NetworkX graph
    elif isinstance(network_source, nx.Graph):
        print("Using provided NetworkX graph")
        
        try:
            # Convert NetworkX to CX2
            G = network_source
            network_name = G.graph.get('name', 'Unnamed NetworkX Graph')
            original_cx2 = create_cx2_from_dict(networkx_to_cx2(G))
            
            # Set network info
            network_info = {
                'source_type': 'networkx',
                'name': network_name,
                'node_count': G.number_of_nodes(),
                'edge_count': G.number_of_edges()
            }
            
            # Save the network to the analysis directory
            cx2_file_path = os.path.join(analysis_dir, f"source_network.cx2")
            save_cx2_to_file(original_cx2, cx2_file_path)
            register_file(session_dir, analysis_id, "source_network.cx2", "cx2", f"Source network: {network_name}")
            
        except Exception as e:
            update_analysis_status(session_dir, analysis_id, "error", {"error": str(e)})
            print(f"Error using provided NetworkX graph: {str(e)}")
            raise
            
    else:
        update_analysis_status(session_dir, analysis_id, "error", 
                              {"error": f"Unsupported network source type: {type(network_source)}"})
        raise ValueError(f"Unsupported network source type: {type(network_source)}")
    
    # Convert to NetworkX for propagation
    G = cx2_to_networkx(original_cx2)
    
    # Identify viral proteins
    print("Identifying viral proteins...")
    viral_proteins = identify_viral_proteins(G)
    print(f"Found {len(viral_proteins)} viral proteins:")
    for node_id, name in viral_proteins:
        print(f"  {name} (ID: {node_id})")
    
    # Filter to specific proteins if requested
    if not process_all_proteins and specific_proteins:
        filtered_proteins = []
        for node_id, name in viral_proteins:
            if node_id in specific_proteins or name in specific_proteins:
                filtered_proteins.append((node_id, name))
        
        if not filtered_proteins:
            error_msg = f"None of the specified proteins {specific_proteins} were found"
            print(f"Warning: {error_msg}")
            print("Available proteins:")
            for node_id, name in viral_proteins:
                print(f"  {name} (ID: {node_id})")
                
            update_analysis_status(session_dir, analysis_id, "error", {"error": error_msg})
            return {"error": error_msg, "session_id": session_id, "analysis_id": analysis_id}
        
        viral_proteins = filtered_proteins
        print(f"Filtered to {len(viral_proteins)} specified viral proteins")
    
    # Initialize results storage
    all_results = {
        'session_id': session_id,
        'analysis_id': analysis_id,
        'source_network': network_info,
        'propagation_parameters': {
            'restart_prob': restart_prob,
            'max_score': max_score,
            'max_steps': max_steps,
            'default_score': default_score,
            'allow_revisits': allow_revisits,
            'include_all_nodes': include_all_nodes,
            'type_scores': type_score_dict
        },
        'viral_proteins': {},
        'cx2_files': {},
        'ndex_networks': {}
    }
    
    # Save initial results
    results_file = os.path.join(analysis_dir, "propagation_results.json")
    with open(results_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    register_file(session_dir, analysis_id, "propagation_results.json", "json", "Propagation results")
    
    # Run propagation for each viral protein
    total_start_time = time.time()
    
    for i, (node_id, name) in enumerate(viral_proteins):
        print(f"\nProcessing viral protein {i+1}/{len(viral_proteins)}: {name} (ID: {node_id})")
        
        try:
            # Run propagation and create network
            enhanced_network, results = propagate_from_viral_protein(
                G,
                original_cx2,
                node_id,
                name,
                restart_prob=restart_prob,
                max_score=max_score,
                max_steps=max_steps,
                type_score_dict=type_score_dict,
                default_score=default_score,
                allow_revisits=allow_revisits,
                include_all_nodes=include_all_nodes
            )
            
            # Store results
            all_results['viral_proteins'][name] = {
                'node_id': node_id,
                'walk_stats': results['walk_stats'],
                'execution_time': results['execution_time']
            }
            
            print(f"  Propagation completed in {results['execution_time']:.2f} seconds")
            print(f"  Walk stats: {results['walk_stats']}")
            
            # Always save CX2 files to the analysis directory
            sanitized_name = name.replace(' ', '_').replace('/', '_')
            cx2_file_path = os.path.join(analysis_dir, f"{sanitized_name}_propagation.cx2")
            print(f"  Saving CX2 network to file...")
            save_cx2_to_file(enhanced_network, cx2_file_path)
            
            # Register file
            register_file(session_dir, analysis_id, f"{sanitized_name}_propagation.cx2", "cx2", 
                         f"Propagation network for {name}")
            
            # Store file path in results
            all_results['cx2_files'][name] = f"{sanitized_name}_propagation.cx2"
            
            # Upload to NDEx if requested
            if upload_networks:
                print("  Uploading network to NDEx...")
                uuid = upload_to_ndex(enhanced_network)
                print(f"  Upload successful. New network UUID: {uuid}")
                
                # Store network UUID
                all_results['ndex_networks'][name] = uuid
            
            # Save results periodically
            with open(results_file, 'w') as f:
                json.dump(all_results, f, indent=2)
            
        except Exception as e:
            print(f"Error processing viral protein {name}: {str(e)}")
            all_results['viral_proteins'][name] = {
                'node_id': node_id,
                'error': str(e)
            }
            
            # Update results file
            with open(results_file, 'w') as f:
                json.dump(all_results, f, indent=2)
    
    # Calculate total execution time
    total_execution_time = time.time() - total_start_time
    all_results['total_execution_time'] = total_execution_time
    
    # Save final results
    with open(results_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    # Update analysis status
    update_analysis_status(session_dir, analysis_id, "completed", {
        "total_execution_time": total_execution_time,
        "viral_protein_count": len(viral_proteins),
        "successful_propagations": len([p for p in all_results['viral_proteins'].values() if 'error' not in p])
    })
    
    print(f"\nAll propagations completed in {total_execution_time:.2f} seconds")
    print(f"Results saved to {results_file}")
    
    if upload_networks:
        print("\nUploaded networks:")
        for name, uuid in all_results['ndex_networks'].items():
            print(f"  {name}: {uuid}")
    
    # Include session and analysis IDs in the results
    all_results['session_id'] = session_id
    all_results['analysis_id'] = analysis_id
    
    return all_results

if __name__ == "__main__":
    # This module is not meant to be run directly
    print("This module provides dengue viral propagation functions for use in propagate_from_viral_proteins.py")
