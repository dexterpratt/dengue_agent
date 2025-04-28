#!/usr/bin/env python3

"""
Dengue Analysis Agent Workflow

This script demonstrates how the agent (in this case, Claude) would use the 
dengue_agent tools to perform analysis of viral-host protein interactions.
"""

import os
import json
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

# Import tools
from tools.utils.session_utils import (
    create_session, create_analysis_dir, update_analysis_status,
    register_file, get_latest_analysis_dir, find_latest_files
)
from tools.utils.network_utils import (
    cx2_to_networkx, load_cx2_from_file, save_cx2_to_file,
    find_latest_cx2_file, get_network_info
)
from tools.dengue.viral_propagation import run_viral_propagation
from tools.analysis.hypothesis_gen import analyze_network

# Sample NDEx UUIDs for dengue-related networks
# These are placeholders - replace with actual UUIDs when available
SAMPLE_NETWORKS = {
    "dengue_ppi": "12345678-1234-1234-1234-123456789abc",  # Replace with actual UUID
    "dengue_phospho": "87654321-4321-4321-4321-cba987654321"  # Replace with actual UUID
}

class DengueAnalysisAgent:
    """
    Agent for analyzing dengue virus-host interactions using network propagation
    and hypothesis generation. This is a programmatic representation of how the
    agent would operate, though in practice, many of these tasks would be performed
    through direct CLI commands and file operations.
    """
    
    def __init__(self):
        """Initialize the agent with basic context about dengue virus."""
        # Load agent knowledge base and self-prompts
        self.self_prompts = self._load_self_prompts()
        
        # Context about dengue viral proteins
        self.dengue_proteins = {
            "NS1": "Non-structural protein 1: secreted protein involved in immune evasion and pathogenesis",
            "NS2A": "Non-structural protein 2A: involved in viral replication and assembly",
            "NS2B": "Non-structural protein 2B: cofactor for NS3 protease",
            "NS3": "Non-structural protein 3: multifunctional enzyme with protease and helicase domains",
            "NS4A": "Non-structural protein 4A: involved in viral replication complex formation",
            "NS4B": "Non-structural protein 4B: inhibits interferon signaling",
            "NS5": "Non-structural protein 5: RNA-dependent RNA polymerase and methyltransferase"
        }
        
        # Log agent initialization
        print("[AGENT] Dengue Analysis Agent initialized")
        print("[AGENT] Self-prompt framework loaded")
        print(f"[AGENT] Knowledge base loaded for {len(self.dengue_proteins)} viral proteins")
    
    def _load_self_prompts(self) -> Dict[str, str]:
        """Load the self-prompts from the prompts directory."""
        prompt_file = "prompts/agent_self_prompts.md"
        
        if not os.path.exists(prompt_file):
            print(f"[AGENT ERROR] Self-prompts file not found: {prompt_file}")
            return {}
        
        # In a real implementation, we would parse the markdown file
        # Here we'll just return a simplified structure
        return {
            "session_initialization": "Initialize session and document context",
            "network_evaluation": "Evaluate network properties and suitability",
            "parameter_selection": "Select and justify propagation parameters",
            "propagation_execution": "Execute propagation algorithms",
            "result_analysis": "Analyze propagation results",
            "hypothesis_formulation": "Generate mechanistic hypotheses",
            "experimental_design": "Design experiments to test hypotheses",
            "session_documentation": "Document findings and recommendations"
        }
    
    def initialize_session(self, session_name: str) -> Dict[str, Any]:
        """
        Create a new analysis session.
        
        Args:
            session_name: Name for the new session
            
        Returns:
            Dictionary with session information
        """
        print(f"\n[SELF-PROMPT: Session Initialization]")
        print("Creating new analysis session and documenting context")
        
        # Create session
        session_id, session_dir = create_session(session_name)
        
        # Create session metadata
        metadata = {
            "session_id": session_id,
            "name": session_name,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "dengue_context": {
                "viral_proteins": list(self.dengue_proteins.keys()),
                "analysis_focus": "Host pathway perturbation by viral proteins"
            }
        }
        
        # Save session context
        context_file = os.path.join(session_dir, "agent_context.json")
        with open(context_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"[AGENT] Session created: {session_id}")
        print(f"[AGENT] Session directory: {session_dir}")
        
        return {
            "session_id": session_id,
            "session_dir": session_dir,
            "metadata": metadata
        }
    
    def run_propagation_analysis(self, 
                               source_network: str,
                               session_info: Dict[str, Any],
                               restart_prob: float = 0.2,
                               max_steps: int = 100,
                               include_all_nodes: bool = False) -> Dict[str, Any]:
        """
        Run propagation analysis on a source network.
        
        Args:
            source_network: NDEx UUID or file path to network
            session_info: Session information from initialize_session
            restart_prob: Restart probability for random walk
            max_steps: Maximum steps per propagation
            include_all_nodes: Whether to include all nodes in output
            
        Returns:
            Dictionary with propagation results
        """
        session_id = session_info["session_id"]
        session_dir = session_info["session_dir"]
        
        print(f"\n[SELF-PROMPT: Network Evaluation]")
        print(f"Evaluating network source: {source_network}")
        
        # Check if source is an NDEx UUID
        is_ndex = len(source_network) == 36 and source_network.count('-') == 4
        if is_ndex:
            print(f"[AGENT] Source identified as NDEx UUID")
        else:
            print(f"[AGENT] Source identified as file path")
        
        print(f"\n[SELF-PROMPT: Parameter Selection]")
        print(f"Setting propagation parameters:")
        print(f"- Restart probability: {restart_prob}")
        print(f"- Maximum steps: {max_steps}")
        print(f"- Include all nodes: {include_all_nodes}")
        
        # Justification for parameters
        if restart_prob < 0.2:
            print("[AGENT] Using lower restart probability to explore broader network context")
        elif restart_prob > 0.2:
            print("[AGENT] Using higher restart probability to focus on direct interactions")
            
        if max_steps > 100:
            print("[AGENT] Increased max steps to ensure convergence in potentially larger network")
        
        print(f"\n[SELF-PROMPT: Propagation Execution]")
        print(f"Running viral propagation with selected parameters")
        
        # In a real run, we'd call the actual propagation function
        # results = run_viral_propagation(
        #     network_source=source_network,
        #     session_id=session_id,
        #     restart_prob=restart_prob,
        #     max_steps=max_steps,
        #     include_all_nodes=include_all_nodes
        # )
        
        # For demonstration purposes, we'll create mock results
        mock_propagation_dir = os.path.join(session_dir, f"propagation_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
        os.makedirs(mock_propagation_dir, exist_ok=True)
        
        # Create mock results
        mock_results = {
            "session_id": session_id,
            "analysis_id": "propagation_" + datetime.now().strftime("%Y%m%d_%H%M%S"),
            "source_network": {
                "name": "Dengue-Human PPI Network",
                "node_count": 3245,
                "edge_count": 12567
            },
            "viral_proteins": {
                "NS1": {"node_id": "protein1", "execution_time": 12.5},
                "NS3": {"node_id": "protein2", "execution_time": 15.2},
                "NS5": {"node_id": "protein3", "execution_time": 14.8}
            },
            "parameters": {
                "restart_prob": restart_prob,
                "max_steps": max_steps,
                "include_all_nodes": include_all_nodes
            }
        }
        
        # Save mock results
        results_file = os.path.join(mock_propagation_dir, "propagation_results.json")
        with open(results_file, 'w') as f:
            json.dump(mock_results, f, indent=2)
        
        print(f"[AGENT] Propagation complete")
        print(f"[AGENT] Results saved to {results_file}")
        print(f"[AGENT] Processed {len(mock_results['viral_proteins'])} viral proteins")
        
        return mock_results
    
    def analyze_propagation_results(self, 
                                   propagation_results: Dict[str, Any],
                                   session_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze propagation results and identify key patterns.
        
        Args:
            propagation_results: Results from run_propagation_analysis
            session_info: Session information from initialize_session
            
        Returns:
            Dictionary with analysis results
        """
        session_id = session_info["session_id"]
        session_dir = session_info["session_dir"]
        
        print(f"\n[SELF-PROMPT: Result Analysis]")
        print(f"Analyzing propagation results for {len(propagation_results['viral_proteins'])} viral proteins")
        
        # In a real implementation, we would load the propagation networks and analyze them
        # Here we'll simulate the analysis with mock findings
        
        analysis = {
            "session_id": session_id,
            "viral_proteins": {},
            "pathways": {
                "JAK-STAT": ["NS3", "NS5"],
                "RIG-I": ["NS1", "NS3"],
                "Autophagy": ["NS4A", "NS4B"],
                "Unfolded Protein Response": ["NS1"]
            },
            "key_findings": [
                "NS3 shows strongest connection to interferon signaling components",
                "NS5 highly connected to transcriptional regulators",
                "NS1 has unexpected connections to ER stress pathway proteins"
            ]
        }
        
        # For each viral protein, create mock analysis
        for protein in propagation_results['viral_proteins'].keys():
            analysis['viral_proteins'][protein] = {
                "top_connected_host_proteins": [
                    {"name": "STAT1", "weight": 0.85, "function": "Transcription factor"},
                    {"name": "JAK1", "weight": 0.72, "function": "Kinase"},
                    {"name": "MAVS", "weight": 0.68, "function": "Antiviral signaling"},
                    {"name": "IRF3", "weight": 0.62, "function": "Transcription factor"},
                    {"name": "DDX58", "weight": 0.58, "function": "RNA helicase"}
                ],
                "enriched_pathways": ["Interferon signaling", "RIG-I signaling"],
                "unexpected_findings": "Strong connection to RNA processing machinery"
            }
        
        # Save analysis results
        analysis_dir = os.path.join(session_dir, f"analysis_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
        os.makedirs(analysis_dir, exist_ok=True)
        
        analysis_file = os.path.join(analysis_dir, "propagation_analysis.json")
        with open(analysis_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        print(f"[AGENT] Analysis complete")
        print(f"[AGENT] Key findings:")
        for finding in analysis["key_findings"]:
            print(f"  - {finding}")
        
        return analysis
    
    def generate_hypotheses(self, 
                          analysis_results: Dict[str, Any],
                          session_info: Dict[str, Any],
                          target_protein: str = None) -> Dict[str, Any]:
        """
        Generate mechanistic hypotheses based on analysis results.
        
        Args:
            analysis_results: Results from analyze_propagation_results
            session_info: Session information from initialize_session
            target_protein: Optional specific viral protein to focus on
            
        Returns:
            Dictionary with generated hypotheses
        """
        session_id = session_info["session_id"]
        session_dir = session_info["session_dir"]
        
        print(f"\n[SELF-PROMPT: Hypothesis Formulation]")
        
        if target_protein:
            print(f"Generating hypotheses focused on viral protein: {target_protein}")
            proteins_to_analyze = [target_protein]
        else:
            print(f"Generating hypotheses for all viral proteins in analysis")
            proteins_to_analyze = list(analysis_results['viral_proteins'].keys())
        
        # Create hypotheses directory
        hypotheses_dir = os.path.join(session_dir, f"hypotheses_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
        os.makedirs(hypotheses_dir, exist_ok=True)
        
        # Generate hypotheses for each viral protein
        all_hypotheses = []
        
        for protein in proteins_to_analyze:
            print(f"\n[AGENT] Generating hypotheses for {protein}")
            
            # In a real implementation, we would generate hypotheses based on the network analysis
            # Here we'll use mock hypotheses
            
            protein_hypotheses = []
            
            if protein == "NS3":
                protein_hypotheses = [
                    {
                        "id": "H1",
                        "title": "NS3 protease cleaves MAVS to inhibit interferon",
                        "null_hypothesis": "NS3 does not affect MAVS integrity or function",
                        "alternative_hypothesis": "NS3 protease directly cleaves MAVS at specific sites to inhibit interferon signaling",
                        "rationale": "NS3 has high propagation weights to MAVS and downstream interferon components. NS3 protease domain specificity is compatible with MAVS sequence motifs. Previous studies have shown other viral proteases target MAVS.",
                        "entities_involved": ["NS3", "MAVS", "RIG-I", "IRF3"],
                        "experimental_data_used": "Propagation weights, protein domain information",
                        "experimental_validation": [
                            "Co-express NS3 and MAVS in cells and detect MAVS cleavage by western blot",
                            "Perform in vitro cleavage assay with purified NS3 protease and MAVS",
                            "Identify potential cleavage sites by mutational analysis"
                        ],
                        "confidence": 4,
                        "source_node": protein
                    },
                    {
                        "id": "H2",
                        "title": "NS3 helicase diverts host RNA processing machinery",
                        "null_hypothesis": "NS3 does not affect host RNA processing",
                        "alternative_hypothesis": "NS3 helicase redirects host RNA processing machinery to favor viral RNA",
                        "rationale": "High propagation weights to DDX58 and other RNA helicases suggest competitive or cooperative interactions. NS3 helicase domain has structural similarity to host DDX family proteins.",
                        "entities_involved": ["NS3", "DDX58", "DDX3X", "RNA processing complex"],
                        "experimental_data_used": "Propagation weights, structural information",
                        "experimental_validation": [
                            "RNA-seq analysis comparing host vs viral RNA processing in presence/absence of NS3",
                            "Co-IP experiments to detect NS3 interaction with RNA processing complexes",
                            "Competition assays between NS3 and host helicases for RNA substrates"
                        ],
                        "confidence": 3,
                        "source_node": protein
                    }
                ]
            
            elif protein == "NS5":
                protein_hypotheses = [
                    {
                        "id": "H3",
                        "title": "NS5 methyltransferase masks viral RNA from RIG-I",
                        "null_hypothesis": "NS5 methylation activity does not affect RIG-I recognition of viral RNA",
                        "alternative_hypothesis": "NS5 methylates viral RNA caps to evade RIG-I recognition",
                        "rationale": "Propagation analysis shows connection between NS5 and RIG-I pathway. NS5 methyltransferase domain is known to be essential for viral replication.",
                        "entities_involved": ["NS5", "RIG-I", "MDA5", "Viral RNA"],
                        "experimental_data_used": "Propagation weights, enzymatic activities",
                        "experimental_validation": [
                            "Compare RIG-I binding to methylated vs unmethylated viral RNAs",
                            "Assess interferon induction by RNA with different methylation patterns",
                            "Create methyltransferase-dead NS5 mutant and measure RIG-I activation"
                        ],
                        "confidence": 4,
                        "source_node": protein
                    }
                ]
            
            else:
                protein_hypotheses = [
                    {
                        "id": f"H{len(all_hypotheses) + 1}",
                        "title": f"{protein} disrupts cellular pathway",
                        "null_hypothesis": f"{protein} does not affect cellular function",
                        "alternative_hypothesis": f"{protein} specifically disrupts host processes",
                        "rationale": "Based on propagation pattern and viral protein function.",
                        "entities_involved": [protein, "Host factors"],
                        "experimental_data_used": "Propagation weights",
                        "experimental_validation": [
                            "Experimental validation 1",
                            "Experimental validation 2"
                        ],
                        "confidence": 3,
                        "source_node": protein
                    }
                ]
            
            # Add to all hypotheses
            all_hypotheses.extend(protein_hypotheses)
            
            # Save protein-specific hypotheses
            protein_file = os.path.join(hypotheses_dir, f"{protein}_hypotheses.json")
            with open(protein_file, 'w') as f:
                json.dump(protein_hypotheses, f, indent=2)
            
            print(f"[AGENT] Generated {len(protein_hypotheses)} hypotheses for {protein}")
        
        # Save all hypotheses
        all_hypotheses_file = os.path.join(hypotheses_dir, "all_hypotheses.json")
        with open(all_hypotheses_file, 'w') as f:
            json.dump(all_hypotheses, f, indent=2)
        
        print(f"\n[AGENT] Generated total of {len(all_hypotheses)} hypotheses")
        print(f"[AGENT] Hypotheses saved to {all_hypotheses_file}")
        
        return {
            "session_id": session_id,
            "hypotheses_dir": hypotheses_dir,
            "all_hypotheses": all_hypotheses,
            "protein_counts": {p: len([h for h in all_hypotheses if h["source_node"] == p]) for p in proteins_to_analyze}
        }
    
    def create_experiment_designs(self, 
                                hypotheses_results: Dict[str, Any],
                                session_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create detailed experimental designs to test the hypotheses.
        
        Args:
            hypotheses_results: Results from generate_hypotheses
            session_info: Session information from initialize_session
            
        Returns:
            Dictionary with experimental designs
        """
        session_id = session_info["session_id"]
        session_dir = session_info["session_dir"]
        
        print(f"\n[SELF-PROMPT: Experimental Design]")
        print(f"Designing experiments to test generated hypotheses")
        
        # Create experiments directory
        experiments_dir = os.path.join(session_dir, f"experiments_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
        os.makedirs(experiments_dir, exist_ok=True)
        
        all_hypotheses = hypotheses_results["all_hypotheses"]
        experiment_designs = []
        
        for hypothesis in all_hypotheses:
            hypothesis_id = hypothesis["id"]
            protein = hypothesis["source_node"]
            
            print(f"[AGENT] Designing experiments for hypothesis {hypothesis_id}: {hypothesis['title']}")
            
            # Extract basic experimental validations from the hypothesis
            basic_experiments = hypothesis.get("experimental_validation", [])
            
            # In a real implementation, we would generate detailed experimental designs
            # Here we'll expand the basic validations with more details
            
            detailed_design = {
                "hypothesis_id": hypothesis_id,
                "title": hypothesis["title"],
                "viral_protein": protein,
                "experiments": []
            }
            
            for i, basic_exp in enumerate(basic_experiments):
                # Create a more detailed version of the experiment
                detailed_exp = {
                    "id": f"{hypothesis_id}_E{i+1}",
                    "title": basic_exp,
                    "methodology": "Detailed methodology would be described here",
                    "controls": [
                        "Negative control: mock infection/transfection",
                        "Positive control: known interaction",
                        "Specificity control: related viral protein"
                    ],
                    "expected_results": {
                        "if_null_hypothesis": "No difference compared to controls",
                        "if_alternative_hypothesis": "Significant difference in measured outcome"
                    },
                    "required_resources": [
                        "Cell lines: Huh7, A549",
                        "Reagents: Antibodies, plasmids",
                        "Equipment: Confocal microscope, plate reader"
                    ],
                    "estimated_timeline": "4-6 weeks",
                    "priority": "High" if i == 0 else "Medium"
                }
                
                detailed_design["experiments"].append(detailed_exp)
            
            experiment_designs.append(detailed_design)
            
            # Save individual experiment design
            design_file = os.path.join(experiments_dir, f"{hypothesis_id}_experiments.json")
            with open(design_file, 'w') as f:
                json.dump(detailed_design, f, indent=2)
        
        # Save all experiment designs
        all_designs_file = os.path.join(experiments_dir, "all_experiment_designs.json")
        with open(all_designs_file, 'w') as f:
            json.dump(experiment_designs, f, indent=2)
        
        print(f"[AGENT] Created {len(experiment_designs)} experimental designs")
        print(f"[AGENT] Designs saved to {all_designs_file}")
        
        return {
            "session_id": session_id,
            "experiments_dir": experiments_dir,
            "experiment_designs": experiment_designs
        }
    
    def create_session_report(self, 
                            session_info: Dict[str, Any],
                            propagation_results: Dict[str, Any],
                            analysis_results: Dict[str, Any],
                            hypotheses_results: Dict[str, Any],
                            experiment_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a comprehensive session report summarizing findings.
        
        Args:
            session_info: Session information from initialize_session
            propagation_results: Results from run_propagation_analysis
            analysis_results: Results from analyze_propagation_results
            hypotheses_results: Results from generate_hypotheses
            experiment_results: Results from create_experiment_designs
            
        Returns:
            Dictionary with report information
        """
        session_id = session_info["session_id"]
        session_dir = session_info["session_dir"]
        
        print(f"\n[SELF-PROMPT: Session Documentation]")
        print(f"Creating comprehensive session report")
        
        # Create report directory
        report_dir = os.path.join(session_dir, f"report_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
        os.makedirs(report_dir, exist_ok=True)
        
        # Create a markdown report
        report_content = f"""# Dengue Virus Analysis Report

## Session Information
- **Session ID:** {session_id}
- **Session Name:** {session_info['metadata']['name']}
- **Created:** {session_info['metadata']['created_at']}

## Analysis Overview
This session analyzed dengue virus protein interactions with host proteins using network propagation.
The analysis focused on {len(propagation_results['viral_proteins'])} viral proteins and their impact on host pathways.

## Key Findings

### Propagation Results
- Network contained {propagation_results['source_network']['node_count']} nodes and {propagation_results['source_network']['edge_count']} edges
- Viral proteins analyzed: {', '.join(propagation_results['viral_proteins'].keys())}

### Pathway Analysis
The following pathways showed significant connection to viral proteins:
{chr(10).join([f"- {pathway}: {', '.join(proteins)}" for pathway, proteins in analysis_results['pathways'].items()])}

### Top Hypotheses
{chr(10).join([f"- **{h['id']}:** {h['title']} (Confidence: {h['confidence']}/5)" for h in hypotheses_results['all_hypotheses'][:3]])}

## Recommendations for Follow-up

1. Prioritize experimental validation of hypothesis {hypotheses_results['all_hypotheses'][0]['id']}
2. Investigate the unexpected connection between {analysis_results['key_findings'][2]}
3. Consider comparative analysis with other flaviviruses to identify dengue-specific mechanisms

## Limitations

- Propagation analysis is based on protein-protein interactions that may include false positives
- Hypotheses require experimental validation
- Current analysis focuses on direct interactions rather than multi-step signaling effects

## Attachments

- Propagation results: {propagation_results['analysis_id']}/propagation_results.json
- Hypothesis files: {os.path.basename(hypotheses_results['hypotheses_dir'])}/all_hypotheses.json
- Experiment designs: {os.path.basename(experiment_results['experiments_dir'])}/all_experiment_designs.json
"""
        
        # Save the report
        report_file = os.path.join(report_dir, "session_report.md")
        with open(report_file, 'w') as f:
            f.write(report_content)
        
        print(f"[AGENT] Session report created: {report_file}")
        
        return {
            "session_id": session_id,
            "report_dir": report_dir,
            "report_file": report_file
        }

# Example usage of the agent
def run_example_analysis():
    """Run an example analysis workflow with the Dengue Analysis Agent."""
    print("Starting example dengue virus analysis workflow")
    
    # Initialize agent
    agent = DengueAnalysisAgent()
    
    # Create session
    session_info = agent.initialize_session("Dengue NS3 Pathway Analysis")
    
    # Run propagation analysis
    # In a real run, use an actual network source
    propagation_results = agent.run_propagation_analysis(
        source_network=SAMPLE_NETWORKS["dengue_ppi"],
        session_info=session_info,
        restart_prob=0.15,  # Lower to explore broader connections
        max_steps=150      # Higher to ensure convergence
    )
    
    # Analyze results
    analysis_results = agent.analyze_propagation_results(
        propagation_results=propagation_results,
        session_info=session_info
    )
    
    # Generate hypotheses
    hypotheses_results = agent.generate_hypotheses(
        analysis_results=analysis_results,
        session_info=session_info,
        target_protein="NS3"  # Focus on NS3
    )
    
    # Design experiments
    experiment_results = agent.create_experiment_designs(
        hypotheses_results=hypotheses_results,
        session_info=session_info
    )
    
    # Create session report
    report_results = agent.create_session_report(
        session_info=session_info,
        propagation_results=propagation_results,
        analysis_results=analysis_results,
        hypotheses_results=hypotheses_results,
        experiment_results=experiment_results
    )
    
    print("\nAnalysis workflow complete!")
    print(f"Session directory: {session_info['session_dir']}")
    print(f"Final report: {report_results['report_file']}")

if __name__ == "__main__":
    run_example_analysis()
