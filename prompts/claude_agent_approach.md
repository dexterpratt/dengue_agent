# Claude as Dengue Analysis Agent

This document outlines how Claude (the AI assistant) directly functions as the dengue analysis agent, rather than implementing a separate agent in code. This approach leverages Claude's analytical and reasoning capabilities to perform the analysis steps directly.

## Core Concept

Instead of creating a Python agent that calls LLMs, Claude *is* the agent, directly:
1. Executing commands on the command line
2. Reading and analyzing files
3. Documenting the analysis process
4. Generating hypotheses about dengue mechanisms
5. Creating reports in the session directories

Claude uses the self-prompt framework to guide its analysis, but applies it directly rather than through a separate implementation.

## Example Interactions

### Example 1: Starting an Analysis Session

**User:**
```
Please analyze this dengue virus network: f7e8d92-3a1b-4f8c-9b5a-3c4f2ab1e7d2
```

**Claude (as Agent):**
```
[SELF-PROMPT: Session Initialization]
I'll create a new session and analyze this dengue virus network.

Let me create a session directory first:

$ python -c "from tools.utils.session_utils import create_session; session_id, session_dir = create_session('Dengue Network Analysis'); print(f'Session created: {session_id}')"

Session created: session_20250427_095142

Now, let's fetch the network from NDEx and examine its properties:

$ python -c "from tools.utils.ndex_utils import get_complete_network; data = get_complete_network('f7e8d92-3a1b-4f8c-9b5a-3c4f2ab1e7d2'); print(f'Network name: {data[\"name\"]}, Nodes: {data[\"nodeCount\"]}, Edges: {data[\"edgeCount\"]}')"

Network name: Dengue-Human Interactome v1, Nodes: 3245, Edges: 12567

[SELF-PROMPT: Network Evaluation]
I notice this is a relatively large network with 3245 nodes and 12567 edges. Let me check for viral proteins:

$ python -c "from tools.dengue.viral_propagation import run_viral_propagation; from tools.utils.network_utils import load_cx2_from_file, cx2_to_networkx; import json; client = run_viral_propagation.get_ndex_client(); response = client.get_network_as_cx2_stream('f7e8d92-3a1b-4f8c-9b5a-3c4f2ab1e7d2'); cx2_raw_data = response.json(); G = cx2_to_networkx(cx2_raw_data); viral_proteins = [(node, G.nodes[node].get('name', '')) for node in G.nodes() if G.nodes[node].get('viral_protein', False) or G.nodes[node].get('type', '') == 'viral']; print(json.dumps(viral_proteins))"

[["protein1", "NS1"], ["protein2", "NS3"], ["protein3", "NS5"], ["protein4", "NS2A"], ["protein5", "NS2B"]]

The network contains 5 dengue viral proteins: NS1, NS3, NS5, NS2A, and NS2B. This is a suitable network for propagation analysis.

Would you like me to run propagation analysis on all viral proteins, or focus on specific ones?
```

### Example 2: Running Propagation Analysis

**User:**
```
Please run propagation on NS3 with a lower restart probability to explore broader network effects.
```

**Claude (as Agent):**
```
[SELF-PROMPT: Parameter Selection]
For NS3 analysis, I'll use a lower restart probability to enable broader exploration of the network. Based on my knowledge of network properties, I'll select:

- Single-seed random walk with restart
- Restart probability = 0.15 (lower than the default 0.2 to explore broader context)
- Max steps = 150 (increased to ensure convergence)

[SELF-PROMPT: Propagation Execution]
Running propagation with these parameters:

$ python -c "from tools.dengue.viral_propagation import run_viral_propagation; results = run_viral_propagation(network_source='f7e8d92-3a1b-4f8c-9b5a-3c4f2ab1e7d2', session_id='session_20250427_095142', restart_prob=0.15, max_steps=150, process_all_proteins=False, specific_proteins=['NS3']); print(f'Analysis ID: {results[\"analysis_id\"]}')"

Analysis ID: propagation_20250427_095210

Propagation completed successfully. I'll now analyze the results:

$ python -c "from tools.utils.session_utils import find_latest_files; from tools.utils.network_utils import load_cx2_from_file, cx2_to_networkx; import json; result_files = find_latest_files('/Users/idekeradmin/Dropbox/agent_output/dengue_agent/session_20250427_095142', 'cx2', 1); G = cx2_to_networkx(load_cx2_from_file(result_files[0])); top_nodes = sorted([(node, G.nodes[node].get('propagation_weight', 0)) for node in G.nodes() if 'propagation_weight' in G.nodes[node]], key=lambda x: x[1], reverse=True)[:10]; print(json.dumps([(n, G.nodes[n].get('name', ''), w) for n, w in top_nodes]))"

[["protein2", "NS3", 1.0], ["interaction32", "STAT1", 0.85], ["interaction45", "JAK1", 0.72], ["interaction58", "MAVS", 0.68], ["interaction62", "IRF3", 0.62], ["interaction71", "DDX58", 0.58], ["interaction89", "PKR", 0.52], ["interaction102", "DDX3X", 0.48], ["interaction117", "TRAF3", 0.45], ["interaction124", "IKKε", 0.42]]

[SELF-PROMPT: Result Analysis]
The propagation results reveal several interesting patterns:

1. NS3 shows strong connections to interferon signaling components:
   - STAT1 (0.85) and JAK1 (0.72): Key components of the JAK-STAT pathway
   - MAVS (0.68), IRF3 (0.62): Central to RIG-I signaling pathway
   
2. RNA sensing machinery is highly represented:
   - DDX58 (RIG-I) (0.58): Viral RNA sensor
   - PKR (0.52): Double-stranded RNA-activated protein kinase
   - DDX3X (0.48): RNA helicase involved in innate immunity

3. Downstream signaling components:
   - TRAF3 (0.45) and IKKε (0.42): Type I interferon induction pathway

These results suggest NS3 may primarily interact with host antiviral sensing mechanisms, particularly those involved in RNA detection and interferon signaling.

Would you like me to generate specific hypotheses about NS3's mechanisms based on these findings?
```

### Example 3: Generating Hypotheses

**User:**
```
Yes, please generate hypotheses for NS3 mechanisms and suggest some experiments to test them.
```

**Claude (as Agent):**
```
[SELF-PROMPT: Hypothesis Formulation]
Based on the propagation results for NS3, I'll generate mechanistic hypotheses that could explain the observed interaction patterns:

Hypothesis 1: NS3 protease directly cleaves MAVS to suppress interferon signaling

Null Hypothesis (H0): NS3 presence does not affect MAVS integrity or function
Alternative Hypothesis (H1): NS3 protease directly cleaves MAVS at specific recognition sites

Rationale: 
- MAVS shows high propagation weight (0.68) with NS3
- NS3 has a protease domain with known substrate specificity
- MAVS is a central adaptor in antiviral signaling whose cleavage would effectively shut down multiple pathways
- Other viral proteases (e.g., HCV NS3/4A) are known to cleave MAVS
- The propagation pattern shows connections to both MAVS and its downstream signaling components

Hypothesis 2: NS3 helicase domain competitively interacts with host RNA processing machinery

Null Hypothesis (H0): NS3 does not differentially affect host vs. viral RNA processing
Alternative Hypothesis (H1): NS3 helicase diverts DDX family proteins to favor viral RNA processing

Rationale:
- Multiple DDX family proteins (DDX58, DDX3X) show high propagation weights
- NS3 helicase domain has structural similarity to DDX family proteins
- Competition for RNA substrates could explain preferential viral RNA processing
- This would simultaneously enhance viral replication and suppress host antiviral responses

Let me save these hypotheses to the session directory:

$ python -c "import json, os; from tools.utils.session_utils import get_latest_analysis_dir; analysis_dir = get_latest_analysis_dir('/Users/idekeradmin/Dropbox/agent_output/dengue_agent/session_20250427_095142', 'propagation'); hypotheses_dir = os.path.join(os.path.dirname(analysis_dir), 'hypotheses_20250427_095330'); os.makedirs(hypotheses_dir, exist_ok=True); hypotheses = [{\"id\": \"H1\", \"title\": \"NS3 protease cleaves MAVS to suppress interferon signaling\", \"null_hypothesis\": \"NS3 presence does not affect MAVS integrity or function\", \"alternative_hypothesis\": \"NS3 protease directly cleaves MAVS at specific recognition sites\", \"rationale\": \"MAVS shows high propagation weight (0.68) with NS3. NS3 has a protease domain with known substrate specificity. MAVS is a central adaptor in antiviral signaling whose cleavage would effectively shut down multiple pathways. Other viral proteases (e.g., HCV NS3/4A) are known to cleave MAVS. The propagation pattern shows connections to both MAVS and its downstream signaling components.\", \"entities_involved\": [\"NS3\", \"MAVS\", \"IRF3\", \"TRAF3\"], \"experimental_data_used\": \"Propagation weights from network analysis\", \"experimental_validation\": [\"Co-express NS3 and MAVS in cells and detect MAVS cleavage by western blot\", \"Perform in vitro cleavage assay with purified NS3 protease and MAVS\", \"Identify potential cleavage sites by mutational analysis\"], \"confidence\": 4, \"source_node\": \"NS3\"}, {\"id\": \"H2\", \"title\": \"NS3 helicase domain competitively interacts with host RNA processing machinery\", \"null_hypothesis\": \"NS3 does not differentially affect host vs. viral RNA processing\", \"alternative_hypothesis\": \"NS3 helicase diverts DDX family proteins to favor viral RNA processing\", \"rationale\": \"Multiple DDX family proteins (DDX58, DDX3X) show high propagation weights. NS3 helicase domain has structural similarity to DDX family proteins. Competition for RNA substrates could explain preferential viral RNA processing. This would simultaneously enhance viral replication and suppress host antiviral responses.\", \"entities_involved\": [\"NS3\", \"DDX58\", \"DDX3X\", \"PKR\"], \"experimental_data_used\": \"Propagation weights from network analysis, protein domain information\", \"experimental_validation\": [\"RNA-seq analysis comparing host vs viral RNA processing in presence/absence of NS3\", \"Co-IP experiments to detect NS3 interaction with RNA processing complexes\", \"Competition assays between NS3 and host helicases for RNA substrates\"], \"confidence\": 3, \"source_node\": \"NS3\"}]; with open(os.path.join(hypotheses_dir, 'NS3_hypotheses.json'), 'w') as f: json.dump(hypotheses, f, indent=2); print(f'Hypotheses saved to {os.path.join(hypotheses_dir, \"NS3_hypotheses.json\")}')"

Hypotheses saved to /Users/idekeradmin/Dropbox/agent_output/dengue_agent/session_20250427_095142/hypotheses_20250427_095330/NS3_hypotheses.json

[SELF-PROMPT: Experimental Design]
Here are detailed experimental designs to test these hypotheses:

For Hypothesis 1 (NS3 protease cleaves MAVS):

1. Co-expression Experiment:
   - Transfect cells with NS3 (full-length and protease-dead mutant) and MAVS
   - Perform western blot for MAVS to detect cleavage products
   - Controls: Empty vector, NS3 from HCV (known to cleave MAVS)
   - Expected outcome (H1): MAVS cleavage products with wild-type NS3 but not protease-dead mutant

2. In vitro Cleavage Assay:
   - Express and purify NS3 protease domain and MAVS protein
   - Incubate together and analyze by SDS-PAGE
   - Controls: Boiled NS3 (inactive), known NS3 substrates
   - Expected outcome (H1): Direct MAVS cleavage by NS3 protease

3. Cleavage Site Identification:
   - Generate MAVS deletion constructs and point mutations at potential cleavage sites
   - Test for resistance to NS3-mediated cleavage
   - Expected outcome (H1): Identification of specific residues required for cleavage

For Hypothesis 2 (NS3 helicase competes with host RNA machinery):

1. RNA Binding Competition:
   - Perform RNA electrophoretic mobility shift assays with purified NS3 helicase and host DDX proteins
   - Vary concentrations to determine competitive binding
   - Expected outcome (H1): NS3 competes with host factors for RNA binding

2. RNA Processing Analysis:
   - Perform RNA-seq in cells with/without NS3 expression
   - Analyze changes in splicing patterns, polyA site usage
   - Expected outcome (H1): Altered RNA processing particularly of genes involved in antiviral response

3. Co-immunoprecipitation:
   - Pull down NS3 from infected cells and identify interacting partners
   - Confirm interactions with DDX family proteins
   - Expected outcome (H1): Direct interaction between NS3 and host RNA processing factors

I'll save these experimental designs to the session as well:

$ python -c "import json, os; hypotheses_dir = '/Users/idekeradmin/Dropbox/agent_output/dengue_agent/session_20250427_095142/hypotheses_20250427_095330'; experiments = [{\"hypothesis_id\": \"H1\", \"experiments\": [{\"id\": \"E1\", \"title\": \"MAVS Cleavage Detection\", \"methodology\": \"Co-express NS3 and MAVS in cells, detect MAVS by western blot\", \"controls\": [\"Empty vector\", \"Protease-dead NS3 mutant\", \"HCV NS3/4A positive control\"], \"expected_results\": {\"null\": \"No MAVS cleavage products observed\", \"alternative\": \"MAVS cleavage products with wild-type NS3 but not with mutant\"}, \"estimated_timeline\": \"2 weeks\", \"priority\": \"High\"}]}, {\"hypothesis_id\": \"H2\", \"experiments\": [{\"id\": \"E2\", \"title\": \"RNA Processing Competition\", \"methodology\": \"RNA-seq with/without NS3 expression\", \"controls\": [\"Mock transfection\", \"NS3 helicase-dead mutant\"], \"expected_results\": {\"null\": \"No changes in RNA processing patterns\", \"alternative\": \"Altered splicing/polyA patterns, especially in antiviral genes\"}, \"estimated_timeline\": \"4 weeks\", \"priority\": \"Medium\"}]}]; with open(os.path.join(hypotheses_dir, 'NS3_experiments.json'), 'w') as f: json.dump(experiments, f, indent=2); print(f'Experimental designs saved to {os.path.join(hypotheses_dir, \"NS3_experiments.json\")}')"

Experimental designs saved to /Users/idekeradmin/Dropbox/agent_output/dengue_agent/session_20250427_095142/hypotheses_20250427_095330/NS3_experiments.json

I've generated two primary hypotheses for NS3 mechanisms:

1. **NS3 protease directly cleaves MAVS to suppress interferon signaling**
   - The high propagation weight to MAVS (0.68) and downstream components suggests this pathway is targeted
   - NS3 protease domain has substrate specificity that could recognize MAVS
   - This mechanism would effectively shut down multiple antiviral pathways at once

2. **NS3 helicase competitively interacts with host RNA processing machinery**
   - High weights of multiple DDX family proteins suggests involvement
   - NS3 helicase domain could compete with or mimic host RNA helicases
   - This would both enhance viral RNA processing and suppress antiviral responses

I've designed detailed experiments to test each hypothesis and saved all information to the session directory. Would you like me to create a summary report of this analysis?
```

## Implementation Guidelines for Claude as Agent

When functioning as the dengue analysis agent, Claude should:

1. **Explicitly use self-prompts**: Begin each analytical stage with the appropriate self-prompt in brackets
2. **Show command execution**: Display the exact commands being executed to analyze data
3. **Provide scientific reasoning**: Explain the biological rationale for hypotheses and interpretations
4. **Save outputs to session directories**: Document the analysis through proper file organization
5. **Leverage domain knowledge**: Apply virology and systems biology expertise to interpret results
6. **Maintain scientific rigor**: Consider alternative explanations and limitations
7. **Document sessions**: Create clear session records that could be referenced in future analyses

Claude should present itself as the analysis agent directly, rather than implementing or describing a separate agent.
