# Dengue Analysis Agent Hypothesis Generation Workflow

This document outlines the structured analytical process I follow when functioning as an analysis agent for dengue virus networks. These self-prompts guide my reasoning and ensure methodological consistency across analysis sessions.

Each step of the workflow includes creating a report file in the session directory following a standard naming convention (step1_*, step2_*, etc.), enabling clear documentation and review of the entire analytical process.

## 1. Session Initialization

**Key Questions:**
- What is the source network? (NDEx UUID, CX2 file, or previous analysis)
- What specific biological question are we investigating?
- What contextual knowledge about dengue proteins is relevant?
- What analysis parameters should be used?

**Process:**
```
1. Identify network source and create a new session
2. Document initial parameters and biological context
3. Set up session directory structure
4. Record any hypotheses or expectations before analysis begins
```

**Report Output:**
- Create `step1_session_initialization.md` in the session directory
- Include network source details, research questions, and initial parameters
- Document expected outcomes and session structure

## 2. Network Evaluation

**Key Questions:**
- Is this network suitable for propagation analysis?
- What are the key properties (node count, density, modularity)?
- Are viral proteins properly annotated?
- What experimental data annotations are present?

**Process:**
```
1. Load network and extract basic statistics
2. Identify viral proteins and their annotations
3. Assess network completeness and annotation quality
4. Note any limitations that may affect interpretation
```

**Report Output:**
- Create `step2_network_evaluation.md` in the session directory
- Include complete network statistics (nodes, edges, density)
- List all identified viral proteins with their attributes
- Document available experimental data types
- Provide visual representation of network structure if possible

## 3. Propagation Parameter Selection

**Key Questions:**
- Which algorithm variant is appropriate? (single vs. multi-seed)
- What restart probability balances local vs. global exploration?
- Are node type weights biologically justified?
- What termination conditions are appropriate?

**Process:**
```
1. Select propagation algorithm based on virus-host interaction model
2. Justify parameter selections based on network properties
3. Document any deviations from default parameters
4. Consider biological rationale for parameter choices
```

**Report Output:**
- Create `step3_parameter_selection.md` in the session directory
- Document selected algorithm and all parameters
- Justify each parameter choice with biological rationale
- Include visualizations of parameter sensitivity if applicable

## 4. Propagation Execution

**Key Questions:**
- How should multiple viral proteins be handled?
- What computational resources are required?
- How will results be stored and documented?

**Process:**
```
1. Run propagation for each viral protein of interest
2. Monitor progress and record any anomalies
3. Save all results in structured session directories
4. Generate summary statistics during execution
```

**Report Output:**
- Create `step4_propagation_execution.md` in the session directory
- Document runtime statistics for each propagation run
- Track successful completions and any errors encountered
- Include paths to propagation result files

## 5. Result Analysis

**Key Questions:**
- How do propagation weights distribute across the network?
- Which host pathways show strongest viral protein connections?
- Are there unexpected high-weight nodes requiring investigation?
- How consistent are results across different viral proteins?

**Process:**
```
1. Analyze distribution of propagation weights
2. Identify top-weighted host proteins for each viral protein
3. Perform pathway enrichment analysis where possible
4. Compare viral protein propagation patterns
```

**Report Output:**
- Create `step5_result_analysis.md` in the session directory
- Include tables of top-weighted nodes for each viral protein
- Provide comparative analysis across viral proteins
- Generate heatmaps or network visualizations of key results
- Include pathway enrichment results if available

## 6. Hypothesis Formulation

**Key Questions:**
- What molecular mechanisms could explain the observed patterns?
- How do these connections relate to known viral strategies?
- What alternative explanations must be considered?
- How specific are these mechanisms to dengue vs. other viruses?

**Process:**
```
1. Formulate 2-5 testable hypotheses based on propagation patterns
2. For each, specify clear null and alternative hypotheses
3. Evaluate confidence based on supporting evidence
4. Ensure mechanistic specificity in hypothesis statements
```

**Report Output:**
- Create `step6_hypothesis_formulation.md` in the session directory
- Document all generated hypotheses in structured format
- Include formal null/alternative statements for each hypothesis
- Justify each hypothesis with evidence from propagation results
- Rate confidence level with supporting rationale

## 7. Experimental Design

**Key Questions:**
- What experiments would falsify each hypothesis?
- What controls are essential?
- What quantitative predictions can be made?
- What techniques would be most appropriate?

**Process:**
```
1. Design 2-3 specific experiments per hypothesis
2. Specify expected outcomes under null and alternative hypotheses
3. Consider both in vitro and in vivo approaches where applicable
4. Recommend priority order based on feasibility and impact
```

**Report Output:**
- Create `step7_experimental_design.md` in the session directory
- Detail experimental protocols for each hypothesis
- Include control conditions and expected outcomes
- Provide diagrams of experimental workflow where helpful
- Document rationale for prioritization of experiments

## 8. Session Documentation

**Key Questions:**
- How should the session be named for clear reference?
- What key findings should be highlighted?
- What follow-up analyses are recommended?
- What limitations should be noted?

**Process:**
```
1. Create comprehensive session report
2. Document all key parameters, results, and hypotheses
3. Generate visualizations that clarify key findings
4. Recommend specific follow-up investigations
```

**Report Output:**
- Create `step8_final_summary.md` in the session directory
- Include executive summary of the entire analysis
- Compile links to all step reports
- Summarize key findings and hypotheses
- Document limitations and recommended follow-up analyses
- Create `session_metadata.json` with structured session information

---

## Example Self-Prompt Application

```
[SESSION: dengue_NS3_analysis_20250427]

[SELF-PROMPT: Network Evaluation]
Examining network properties:
- 3,245 nodes, 12,567 edges
- Network density: 0.0024 (sparse, as expected for PPI networks)
- NS3 protein properly annotated with viral_protein=true
- 76% of nodes have experimental data annotations (phosphoproteomics and expression)
- Suitable for propagation analysis with strong experimental context

[Creating step2_network_evaluation.md]

[SELF-PROMPT: Propagation Parameter Selection]
For NS3 analysis, selecting:
- Single-seed random walk with restart
- Restart probability = 0.15 (lower than default to explore broader network context)
- Higher weights for proteins with phosphoproteomic data (2.0) to emphasize signaling effects
- Max steps increased to 150 to ensure convergence in this larger network

[Creating step3_parameter_selection.md]

[SELF-PROMPT: Hypothesis Formulation]
Based on propagation results, I propose the following hypotheses:
1. NS3 protease activity directly cleaves MAVS to suppress host interferon response
   - Key evidence: High propagation weights to MAVS and downstream interferon pathway 
   - H0: NS3 presence does not affect MAVS integrity or function
   - H1: NS3 directly cleaves MAVS at specific recognition sites
2. NS3 helicase domain interacts with host RNA processing machinery to favor viral RNA
   - Key evidence: Enrichment of RNA processing proteins in high-weight nodes
   - H0: NS3 does not differentially affect host vs. viral RNA processing
   - H1: NS3 preferentially enhances viral RNA processing through interactions with host machinery

[Creating step6_hypothesis_formulation.md]
