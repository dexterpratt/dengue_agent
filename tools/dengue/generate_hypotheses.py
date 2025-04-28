#!/usr/bin/env python3

"""
Dengue-specific hypothesis generation module.
Uses the assistant agent to generate hypotheses from network analysis.
"""

import os
import json
import time
import re
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
import networkx as nx
from ndex2.cx2 import CX2Network, RawCX2NetworkFactory

# Import from tools package
from tools.utils.network_utils import (
    cx2_to_networkx, load_cx2_from_file, save_cx2_to_file,
    find_latest_cx2_file, get_network_info
)
from tools.utils.session_utils import (
    create_session, create_analysis_dir, update_analysis_status,
    register_file, get_latest_analysis_dir, find_latest_files
)
from tools.utils.ndex_utils import get_ndex_client
from tools.analysis.hypothesis_gen import (
    AgentPromptManager,
    analyze_network,
    generate_hypotheses,
    create_hypothesis_network
)

def extract_uuid(input_str):
    """Extract just the UUID from a string that might be a full NDEx URL"""
    # Match pattern for UUIDs in NDEx URLs
    uuid_pattern = r'(?:https?://(?:www\.)?ndexbio\.org/(?:v3/)?networks/)?([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})'
    match = re.search(uuid_pattern, input_str)
    if match:
        return match.group(1)
    return input_str  # Return original if no UUID pattern found

def generate_dengue_hypotheses(
    network_sources: List[str],
    session_id: Optional[str] = None,
    session_name: Optional[str] = None,
    n_hypotheses: int = 2,
    upload_network: bool = False,
    agent_response: Optional[str] = None,
    domain_name: str = "dengue virus"
) -> List[Dict[str, Any]]:
    """
    Generate hypotheses for dengue viral protein networks using the assistant agent.
    
    Args:
        network_sources: List of network sources, each can be one of:
            - NDEx UUID
            - Path to a CX2 file
            - Directory containing propagation result files
        session_id: Optional existing session ID to use
        session_name: Optional name for the session if creating new
        n_hypotheses: Number of hypotheses per viral protein
        upload_network: Whether to upload the hypothesis network to NDEx (default: False)
        agent_response: Optional pre-existing agent response text
        domain_name: Domain name for context (default: "dengue virus")
        
    Returns:
        List of all generated hypotheses
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
            session_id, session_dir = create_session(session_name or "Hypothesis Generation")
    else:
        # Create new session
        session_id, session_dir = create_session(session_name or "Hypothesis Generation")
    
    print(f"Using session: {session_id}")
    print(f"Session directory: {session_dir}")
    
    # Create analysis directory for this hypothesis generation run
    analysis_id, analysis_dir = create_analysis_dir(session_dir, "hypotheses")
    print(f"Analysis directory: {analysis_dir}")
    
    # Update analysis status
    update_analysis_status(session_dir, analysis_id, "running", {
        "parameters": {
            "n_hypotheses": n_hypotheses,
            "upload_network": upload_network,
            "domain_name": domain_name
        }
    })
    
    # Initialize the prompt manager
    prompt_manager = AgentPromptManager()
    
    # Store all hypotheses from all viral proteins
    all_hypotheses = []
    all_network_stats = {}
    
    # Initialize results storage
    results = {
        'session_id': session_id,
        'analysis_id': analysis_id,
        'networks_processed': [],
        'hypotheses': {},
        'cx2_files': {},
        'ndex_networks': {}
    }
    
    # Process each network source
    for i, source in enumerate(network_sources):
        print(f"\nProcessing network source {i+1}/{len(network_sources)}: {source}")
        
        # Identify source type (NDEx UUID, CX2 file, or directory)
        network_info = {}
        source_type = "unknown"
        cx2_network = None
        
        try:
            # Check if it's an NDEx UUID
            if re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', extract_uuid(source)):
                source_type = "ndex"
                ndex_uuid = extract_uuid(source)
                
                # Get NDEx client
                client = get_ndex_client()
                
                # Get network as CX2
                print(f"Loading network {ndex_uuid} from NDEx...")
                response = client.get_network_as_cx2_stream(ndex_uuid)
                factory = RawCX2NetworkFactory()
                cx2_network = factory.get_cx2network(response.json())
                
                # Set source info
                network_info['source_type'] = 'ndex'
                network_info['uuid'] = ndex_uuid
                
            # Check if it's a CX2 file
            elif source.endswith('.cx2') and os.path.exists(source):
                source_type = "file"
                print(f"Loading network from CX2 file: {source}")
                cx2_network = load_cx2_from_file(source)
                
                # Set source info
                network_info['source_type'] = 'file'
                network_info['file_path'] = source
                
            # Check if it's a directory with propagation results
            elif os.path.isdir(source):
                source_type = "directory"
                print(f"Looking for propagation results in directory: {source}")
                
                # Find latest CX2 file in the directory
                cx2_files = find_cx2_files(source)
                if not cx2_files:
                    print(f"No CX2 files found in directory: {source}")
                    continue
                
                # Use the most recent CX2 file
                latest_cx2_file = find_latest_cx2_file(source)
                print(f"Using latest CX2 file: {latest_cx2_file}")
                cx2_network = load_cx2_from_file(latest_cx2_file)
                
                # Set source info
                network_info['source_type'] = 'directory'
                network_info['directory'] = source
                network_info['file_used'] = os.path.basename(latest_cx2_file)
                
            else:
                print(f"Unknown source type: {source}")
                results['networks_processed'].append({
                    'source': source,
                    'status': 'error',
                    'error': 'Unknown source type'
                })
                continue
            
            # Get network name and attributes
            network_name = cx2_network.get_name()
            network_attrs = cx2_network.get_network_attributes()
            if not network_name:
                # Fallback to network attributes
                network_name = network_attrs.get('name', f"network-{i}")
            
            print(f"Loaded network '{network_name}'")
            network_info['name'] = network_name
            
            # Make a copy of the network in the analysis directory
            source_file_path = os.path.join(analysis_dir, f"source_network_{i}.cx2")
            save_cx2_to_file(cx2_network, source_file_path)
            register_file(session_dir, analysis_id, f"source_network_{i}.cx2", "cx2", 
                         f"Source network: {network_name}")
            
            # Convert to NetworkX for analysis
            G = cx2_to_networkx(cx2_network)
            print(f"Converted to NetworkX graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
            
            # Adapt network attributes for dengue-specific context
            # Check if this is a viral protein propagation network
            viral_protein_name = network_attrs.get('viral_protein_name', None)
            viral_protein_id = network_attrs.get('viral_protein_id', None)
            
            if viral_protein_name and viral_protein_id:
                # This is a viral protein network, update attributes
                network_attrs['source_node_name'] = viral_protein_name
                network_attrs['source_node_id'] = viral_protein_id
            
            # Analyze network
            print("Analyzing network...")
            network_stats = analyze_network(G, network_attrs)
            
            # Store network stats
            network_stats_file = os.path.join(analysis_dir, f"network_stats_{i}.json")
            with open(network_stats_file, 'w') as f:
                # Convert NetworkX graph references to strings to avoid JSON serialization issues
                stats_json = {k: v for k, v in network_stats.items() if k != 'G'}
                json.dump(stats_json, f, indent=2)
            register_file(session_dir, analysis_id, f"network_stats_{i}.json", "json", 
                         f"Network analysis for {network_name}")
            
            # Store network stats for later reference
            if 'source_node' in network_stats and network_stats['source_node']['name']:
                viral_protein = network_stats['source_node']['name']
                all_network_stats[viral_protein] = network_stats
                
                # Format the prompt for this network
                prompt = prompt_manager.format_hypothesis_prompt(
                    network_stats, 
                    n_hypotheses=n_hypotheses,
                    domain_name=domain_name
                )
                
                # Save the formatted prompt
                prompt_file = os.path.join(analysis_dir, f"prompt_{viral_protein.replace(' ', '_')}.txt")
                with open(prompt_file, 'w') as f:
                    f.write(prompt)
                register_file(session_dir, analysis_id, f"prompt_{viral_protein.replace(' ', '_')}.txt", "txt", 
                             f"Hypothesis prompt for {viral_protein}")
                
                if agent_response:
                    # Use provided agent response if available
                    print(f"Using provided agent response for {viral_protein}")
                    hypotheses = generate_hypotheses(
                        network_stats,
                        prompt_manager,
                        agent_response,
                        n_hypotheses=n_hypotheses,
                        domain_name=domain_name
                    )
                else:
                    # If no agent response, we'll need to wait for the agent to provide one
                    print(f"Please provide the agent's response for {viral_protein} using the formatted prompt.")
                    # Save placeholder for hypotheses to indicate they need to be generated
                    hypotheses = [{
                        "id": "placeholder",
                        "title": "Placeholder - awaiting agent response",
                        "source_node": viral_protein
                    }]
                
                # Add hypotheses to the overall list if they're not placeholders
                if hypotheses[0].get("id") != "placeholder":
                    all_hypotheses.extend(hypotheses)
                
                # Save individual protein hypotheses to file
                protein_filename = f"hypotheses_{viral_protein.replace(' ', '_')}.json"
                protein_filepath = os.path.join(analysis_dir, protein_filename)
                
                with open(protein_filepath, 'w') as f:
                    json.dump(hypotheses, f, indent=2)
                
                register_file(session_dir, analysis_id, protein_filename, "json", 
                             f"Hypotheses for {viral_protein}")
                
                # Add to results
                results['hypotheses'][viral_protein] = hypotheses
                results['networks_processed'].append({
                    'source': source,
                    'network_name': network_name,
                    'viral_protein': viral_protein,
                    'hypotheses_count': len(hypotheses),
                    'status': 'success' if hypotheses[0].get("id") != "placeholder" else 'awaiting_response'
                })
                
                print(f"Processed hypotheses for {viral_protein}")
            else:
                print("Warning: No source node (viral protein) found in network")
                results['networks_processed'].append({
                    'source': source,
                    'network_name': network_name,
                    'status': 'error',
                    'error': 'No source node (viral protein) found'
                })
            
        except Exception as e:
            print(f"Error processing network source {source}: {str(e)}")
            results['networks_processed'].append({
                'source': source,
                'status': 'error',
                'error': str(e)
            })
    
    # Save the overall results
    results_file = os.path.join(analysis_dir, "hypothesis_generation_results.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    register_file(session_dir, analysis_id, "hypothesis_generation_results.json", "json", 
                 "Hypothesis generation results")
    
    # Create and save hypothesis network if we have non-placeholder hypotheses
    if all_hypotheses:
        print("\nCreating hypothesis network...")
        network_name = f"Dengue Virus Protein Hypotheses"
        hypothesis_network = create_hypothesis_network(all_hypotheses, network_name)
        
        # Save network to file
        network_filename = "hypothesis_network.cx2"
        network_filepath = os.path.join(analysis_dir, network_filename)
        save_cx2_to_file(hypothesis_network, network_filepath)
        
        register_file(session_dir, analysis_id, network_filename, "cx2", 
                     "Hypothesis network visualization")
        
        results['cx2_files']['hypothesis_network'] = network_filename
        print(f"Saved hypothesis network to {network_filepath}")
        
        # Upload to NDEx if requested
        if upload_network:
            print("Uploading hypothesis network to NDEx...")
            client = get_ndex_client()
            cx2_data = hypothesis_network.to_cx2()
            uuid = client.save_new_cx2_network(cx2_data)
            print(f"Upload successful. Network UUID: {uuid}")
            
            # Save UUID to results
            results['ndex_networks']['hypothesis_network'] = uuid
            
            # Update results file
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2)
    
    # Update analysis status
    if all_hypotheses:
        update_analysis_status(session_dir, analysis_id, "completed", {
            "total_hypotheses": len(all_hypotheses),
            "networks_processed": len(network_sources),
            "successful_networks": sum(1 for n in results['networks_processed'] if n['status'] == 'success')
        })
    else:
        update_analysis_status(session_dir, analysis_id, "awaiting_agent_response", {
            "networks_processed": len(network_sources)
        })
    
    # Display summary of generated hypotheses
    print("\nHypothesis Generation Summary:")
    for viral_protein, stats in all_network_stats.items():
        protein_hypotheses = [h for h in all_hypotheses if h['source_node'] == viral_protein]
        
        if protein_hypotheses:
            print(f"\n{viral_protein}: {len(protein_hypotheses)} hypotheses")
            for h in protein_hypotheses:
                print(f"  [{h['id']}] {h['title']} (Confidence: {h.get('confidence', 'N/A')}/5)")
        else:
            placeholder_hypotheses = results['hypotheses'].get(viral_protein, [])
            if placeholder_hypotheses and placeholder_hypotheses[0].get("id") == "placeholder":
                print(f"\n{viral_protein}: Awaiting agent response")
    
    print(f"\nTotal hypotheses: {len(all_hypotheses)}")
    print(f"Analysis directory: {analysis_dir}")
    
    # Include session and analysis IDs in the results
    results['session_id'] = session_id
    results['analysis_id'] = analysis_id
    
    return all_hypotheses

if __name__ == "__main__":
    # This module is not meant to be run directly
    print("This module provides dengue hypothesis generation functions for use in generate_hypotheses.py")
