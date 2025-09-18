#!/usr/bin/env python3

"""
Script to run NS2B3 propagation analysis with the selected parameters.
"""

import os
import json
from datetime import datetime
from tools.utils.ndex_utils import get_ndex_client
from tools.utils.network_utils import cx2_to_networkx, load_cx2_from_file
from tools.dengue.viral_propagation import run_viral_propagation
from ndex2.cx2 import RawCX2NetworkFactory

def run_ns2b3_propagation(
    uuid, 
    session_dir,
    restart_prob=0.15,
    max_cumulative_score=15.0,
    max_steps=150,
    allow_revisits=True
):
    """Run propagation analysis for NS2B3."""
    # Create step4 report directory
    step4_dir = os.path.join(session_dir, "step4_propagation_execution")
    os.makedirs(step4_dir, exist_ok=True)
    
    # Start the report
    report = [
        "# Step 4: Propagation Execution for NS2B3 Analysis",
        "",
        "## Execution Parameters",
        f"- **Network UUID:** {uuid}",
        f"- **Restart Probability:** {restart_prob}",
        f"- **Maximum Cumulative Score:** {max_cumulative_score}",
        f"- **Maximum Steps:** {max_steps}",
        f"- **Allow Revisits:** {allow_revisits}",
        f"- **Execution Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Type Score Weights",
        "```",
        "type_score_dict = {",
        "    'high_z': 1.5,    # Higher confidence interactions receive more weight",
        "    'med_z': 1.0,     # Medium confidence serves as the baseline",
        "    'low_z': 0.7,     # Lower confidence interactions receive less weight",
        "    'viral': 2.0,     # Viral proteins receive highest weight",
        "    'default': 1.0    # Default for any uncategorized nodes",
        "}",
        "```",
        "",
        "## Execution Progress"
    ]
    
    # Define type score dictionary
    type_score_dict = {
        'high_z': 1.5,    # Higher confidence interactions receive more weight
        'med_z': 1.0,     # Medium confidence serves as the baseline
        'low_z': 0.7,     # Lower confidence interactions receive less weight
        'viral': 2.0,     # Viral proteins receive highest weight
        'default': 1.0    # Default for any uncategorized nodes
    }
    
    # Save type scores to a file
    type_scores_file = os.path.join(step4_dir, "type_scores.json")
    with open(type_scores_file, 'w') as f:
        json.dump(type_score_dict, f, indent=2)
    
    # Extract session_id from the session_dir path
    session_id = os.path.basename(session_dir)
    
    # Add execution start to report
    report.append(f"Propagation started at {datetime.now().strftime('%H:%M:%S')}...")
    
    # Run the propagation specifically for NS2B3
    try:
        # Run viral propagation with the specified parameters
        propagation_results = run_viral_propagation(
            network_source=uuid,
            session_id=session_id,
            restart_prob=restart_prob,
            max_score=max_cumulative_score,
            max_steps=max_steps,
            allow_revisits=allow_revisits,
            type_scores_file=type_scores_file,  # Use the type scores file we created
            process_all_proteins=False,
            specific_proteins=["DENV2 16681 NS2B3"],  # Focus on NS2B3 only with full name
            upload_networks=False
        )
        
        # Document the execution in the report
        report.append(f"Propagation completed at {datetime.now().strftime('%H:%M:%S')}")
        report.append("")
        report.append("## Execution Results")
        
        # Extract the results for NS2B3
        ns2b3_results = None
        for protein_name, results in propagation_results['viral_proteins'].items():
            if 'NS2B3' in protein_name:
                ns2b3_results = results
                report.append(f"### {protein_name} Results")
                report.append(f"- **Execution Time:** {results.get('execution_time', 'Unknown')} seconds")
                
                # Add walk statistics
                walk_stats = results.get('walk_stats', {})
                if walk_stats:
                    report.append("- **Walk Statistics:**")
                    report.append(f"  - Steps: {walk_stats.get('steps', 'Unknown')}")
                    report.append(f"  - Restarts: {walk_stats.get('restarts', 'Unknown')}")
                    report.append(f"  - Termination Reason: {walk_stats.get('termination_reason', 'Unknown')}")
                
                # Get the CX2 file path
                cx2_file = propagation_results.get('cx2_files', {}).get(protein_name)
                if cx2_file:
                    report.append(f"- **Result File:** {cx2_file}")
                    report.append("")
                
                break
        
        # If we didn't find NS2B3 results, note it in the report
        if ns2b3_results is None:
            report.append("No results found for NS2B3. This indicates an issue with the propagation execution.")
        
        # Save report
        report_path = os.path.join(step4_dir, "step4_propagation_execution.md")
        with open(report_path, 'w') as f:
            f.write('\n'.join(report))
        
        print(f"Propagation execution report created: {report_path}")
        
        # Get the propagation network and analyze the top nodes
        if ns2b3_results and cx2_file:
            # Find the propagation directory
            from tools.utils.session_utils import get_latest_analysis_dir
            propagation_dir = get_latest_analysis_dir(session_dir, 'propagation')
            
            if propagation_dir:
                # Load the propagation network
                prop_file_path = os.path.join(propagation_dir, cx2_file)
                if os.path.exists(prop_file_path):
                    network = cx2_to_networkx(load_cx2_from_file(prop_file_path))
                    
                    # Get top nodes by propagation weight
                    nodes_with_weights = []
                    for node, attrs in network.nodes(data=True):
                        if 'propagation_weight' in attrs:
                            nodes_with_weights.append((
                                node, 
                                attrs.get('name', 'Unknown'),
                                attrs.get('propagation_weight', 0),
                                attrs.get('type', 'Unknown')
                            ))
                    
                    # Sort and get top 20 nodes
                    sorted_nodes = sorted(nodes_with_weights, key=lambda x: x[2], reverse=True)
                    top_nodes = sorted_nodes[:20]
                    
                    # Add to report
                    report.append("## Top 20 Nodes by Propagation Weight")
                    report.append("")
                    report.append("| Rank | Node Name | Node ID | Type | Propagation Weight |")
                    report.append("|------|----------|---------|------|-------------------|")
                    
                    for i, (node_id, name, weight, node_type) in enumerate(top_nodes):
                        report.append(f"| {i+1} | {name} | {node_id} | {node_type} | {weight:.4f} |")
                    
                    # Save the enhanced report
                    with open(report_path, 'w') as f:
                        f.write('\n'.join(report))
                    
                    # Also save the top nodes data as JSON for further analysis
                    top_nodes_data = [{
                        "rank": i+1,
                        "name": name,
                        "id": node_id,
                        "type": node_type,
                        "propagation_weight": weight
                    } for i, (node_id, name, weight, node_type) in enumerate(top_nodes)]
                    
                    json_path = os.path.join(step4_dir, "top_nodes.json")
                    with open(json_path, 'w') as f:
                        json.dump(top_nodes_data, f, indent=2)
                    
                    print(f"Top nodes data saved to: {json_path}")
                else:
                    print(f"Propagation result file not found: {prop_file_path}")
            else:
                print("Propagation directory not found")
        
        return propagation_results, step4_dir
    
    except Exception as e:
        # Document the error in the report
        report.append(f"Error during propagation execution: {str(e)}")
        
        # Save report even if there was an error
        report_path = os.path.join(step4_dir, "step4_propagation_execution.md")
        with open(report_path, 'w') as f:
            f.write('\n'.join(report))
        
        print(f"Propagation execution failed: {str(e)}")
        print(f"Error report created: {report_path}")
        
        raise

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python run_ns2b3_propagation.py <ndex_uuid> <session_directory>")
        sys.exit(1)
    
    uuid = sys.argv[1]
    session_dir = sys.argv[2]
    
    run_ns2b3_propagation(uuid, session_dir)
