# Command Examples for Claude as Dengue Analysis Agent

This document provides example commands that Claude will use when functioning as the Dengue Analysis Agent. These commands represent the typical operations needed for network analysis and hypothesis generation.

## Session Management

Create a new session:
```python
from tools.utils.session_utils import create_session
session_id, session_dir = create_session("Dengue NS3 Analysis")
print(f"Session created: {session_id}")
print(f"Session directory: {session_dir}")
```

Create an analysis directory within a session:
```python
from tools.utils.session_utils import create_analysis_dir
analysis_id, analysis_dir = create_analysis_dir(session_dir, "propagation")
print(f"Analysis directory created: {analysis_dir}")
```

Register a file with the session:
```python
from tools.utils.session_utils import register_file
register_file(session_dir, analysis_id, "results.json", "json", "Propagation results")
```

## Network Operations

Load a network from NDEx:
```python
from tools.utils.ndex_utils import get_ndex_client, get_complete_network
client = get_ndex_client()
network_data = get_complete_network("12345678-1234-1234-1234-123456789abc")
print(f"Network: {network_data['name']}, Nodes: {network_data['nodeCount']}, Edges: {network_data['edgeCount']}")
```

Load a network from a CX2 file:
```python
from tools.utils.network_utils import load_cx2_from_file, get_network_info
cx2_network = load_cx2_from_file("/path/to/network.cx2")
info = get_network_info(cx2_network)
print(f"Network: {info['name']}, Nodes: {info['node_count']}, Edges: {info['edge_count']}")
```

Convert CX2 to NetworkX for analysis:
```python
from tools.utils.network_utils import cx2_to_networkx
G = cx2_to_networkx(cx2_network)
print(f"NetworkX graph created with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
```

Save a NetworkX graph as CX2:
```python
from tools.utils.network_utils import networkx_to_cx2, save_cx2_to_file
cx2_data = networkx_to_cx2(G)
save_cx2_to_file(cx2_data, "/path/to/output.cx2")
```

## Viral Propagation

Run propagation on a network:
```python
from tools.dengue.viral_propagation import run_viral_propagation
results = run_viral_propagation(
    network_source="12345678-1234-1234-1234-123456789abc",  # NDEx UUID
    session_id=session_id,
    restart_prob=0.15,  # Lower to explore broader network context
    max_steps=150,      # Higher to ensure convergence
    upload_networks=False,  # Don't upload to NDEx, save locally
    process_all_proteins=False,
    specific_proteins=["NS3"]  # Focus on NS3
)
print(f"Propagation complete, analysis ID: {results['analysis_id']}")
```

Analyze propagation results:
```python
import json
from tools.utils.session_utils import find_latest_files
from tools.utils.network_utils import load_cx2_from_file, cx2_to_networkx

# Find the most recent CX2 file
result_files = find_latest_files(session_dir, "cx2", 1)
latest_cx2_file = result_files[0]

# Load and analyze
G = cx2_to_networkx(load_cx2_from_file(latest_cx2_file))

# Get top nodes by propagation weight
top_nodes = sorted(
    [(node, G.nodes[node].get('propagation_weight', 0)) 
     for node in G.nodes() if 'propagation_weight' in G.nodes[node]],
    key=lambda x: x[1], 
    reverse=True
)[:10]

# Print top nodes with names and weights
for node_id, weight in top_nodes:
    name = G.nodes[node_id].get('name', node_id)
    print(f"{name}: {weight:.4f}")
```

## Hypothesis Generation

Save generated hypotheses to session:
```python
import json
import os
from datetime import datetime

hypotheses_dir = os.path.join(session_dir, f"hypotheses_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
os.makedirs(hypotheses_dir, exist_ok=True)

hypotheses = [
    {
        "id": "H1",
        "title": "NS3 protease cleaves MAVS to suppress interferon signaling",
        "null_hypothesis": "NS3 presence does not affect MAVS integrity or function",
        "alternative_hypothesis": "NS3 protease directly cleaves MAVS at specific recognition sites",
        "rationale": "...",
        "entities_involved": ["NS3", "MAVS", "IRF3", "TRAF3"],
        "experimental_data_used": "Propagation weights from network analysis",
        "experimental_validation": [
            "Co-express NS3 and MAVS in cells and detect MAVS cleavage by western blot",
            "Perform in vitro cleavage assay with purified NS3 protease and MAVS",
            "Identify potential cleavage sites by mutational analysis"
        ],
        "confidence": 4,
        "source_node": "NS3"
    }
]

# Save hypotheses to file
hypotheses_file = os.path.join(hypotheses_dir, "NS3_hypotheses.json")
with open(hypotheses_file, 'w') as f:
    json.dump(hypotheses, f, indent=2)
    
print(f"Hypotheses saved to {hypotheses_file}")
```

## Session Documentation

Create a summary report:
```python
import os
from datetime import datetime

report_dir = os.path.join(session_dir, f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
os.makedirs(report_dir, exist_ok=True)

report_content = """# Dengue Virus Analysis Report

## Session Information
- **Session ID:** session_20250427_095142
- **Session Name:** Dengue NS3 Analysis
- **Created:** 2025-04-27 09:51:42

## Analysis Overview
This session analyzed dengue virus protein NS3 interactions with host proteins using network propagation.

## Key Findings

### Propagation Results
- Network contained 3245 nodes and 12567 edges
- NS3 shows strongest connections to interferon signaling components (STAT1, JAK1, MAVS)
- RNA sensing machinery is highly represented in top propagation weights (DDX58, PKR, DDX3X)

### Hypotheses
1. **NS3 protease directly cleaves MAVS to suppress interferon signaling**
   - High propagation weight to MAVS (0.68) suggests direct interaction
   - NS3 protease domain could target MAVS similar to other viral proteases
   - This mechanism would effectively shut down multiple antiviral pathways

2. **NS3 helicase competitively interacts with host RNA processing machinery**
   - High weights of DDX family proteins suggests involvement
   - NS3 helicase domain could compete with or mimic host RNA helicases
   - This would both enhance viral RNA processing and suppress antiviral responses

## Recommended Experiments

1. MAVS cleavage detection via western blot with wild-type and protease-dead NS3
2. In vitro cleavage assay with purified NS3 protease and MAVS
3. RNA-seq with/without NS3 expression to identify changes in RNA processing

## Limitations
- Propagation analysis is based on protein-protein interactions that may include false positives
- Hypotheses require experimental validation
"""

report_file = os.path.join(report_dir, "session_report.md")
with open(report_file, 'w') as f:
    f.write(report_content)
    
print(f"Session report created: {report_file}")
```

## One-line Command Examples

These condensed command examples are useful for quick operations:

```python
# Quick session creation
python -c "from tools.utils.session_utils import create_session; session_id, session_dir = create_session('Dengue Analysis'); print(f'Created: {session_id}')"

# Get network info from NDEx
python -c "from tools.utils.ndex_utils import get_complete_network; data = get_complete_network('12345678-1234-1234-1234-123456789abc'); print(f'Network: {data[\"name\"]}, Nodes: {data[\"nodeCount\"]}')"

# Quick propagation run
python -c "from tools.dengue.viral_propagation import run_viral_propagation; results = run_viral_propagation(network_source='12345678-1234-1234-1234-123456789abc', restart_prob=0.15, specific_proteins=['NS3']); print(f'Analysis ID: {results[\"analysis_id\"]}')"

# List session directories
python -c "from tools.utils.session_utils import list_sessions; sessions = list_sessions(); print('\n'.join([f'{s[\"session_id\"]}: {s[\"name\"]}' for s in sessions]))"
