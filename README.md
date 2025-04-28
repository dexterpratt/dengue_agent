# Dengue Analysis Agent

This repository contains tools for analyzing dengue virus protein interactions using network propagation and hypothesis generation. The unique aspect of this project is that the LLM assistant (Claude) functions directly as the analysis agent.

## Architecture

```
.
├── prompts/                      # Templates and documentation for the agent
│   ├── agent_self_prompts.md     # Self-prompt framework for agent reasoning
│   ├── claude_agent_approach.md  # Documents how Claude acts as the agent
│   ├── command_examples.md       # Example commands for the agent to execute
│   ├── hypothesis_generation/    # Templates for hypothesis generation
│   └── network_analysis/         # Templates for network analysis
└── tools/                        # Core analysis tools used by the agent
    ├── algorithms/               # Propagation and network algorithms
    ├── analysis/                 # Analysis functions for networks
    ├── dengue/                   # Dengue-specific analysis modules
    └── utils/                    # Utility functions for network handling
```

## Using Claude as the Analysis Agent

In this framework, Claude (the LLM assistant) directly functions as the analysis agent, rather than implementing a separate agent in code. Claude:

1. Uses the self-prompt framework to guide its analytical process
2. Executes Python commands on the terminal to perform analyses
3. Manages session directories and file storage
4. Applies domain expertise in virology and network biology
5. Generates mechanistic hypotheses based on network patterns
6. Documents all analyses with clear reasoning and evidence

## Agent Workflow

The agent follows this general workflow:

1. **Session Initialization**: Create a session directory for the analysis
2. **Network Evaluation**: Load and assess the network properties
3. **Propagation Analysis**: Run network propagation algorithms on viral proteins
4. **Result Analysis**: Interpret the propagation patterns
5. **Hypothesis Generation**: Formulate mechanistic hypotheses
6. **Experimental Design**: Propose experiments to test hypotheses
7. **Session Documentation**: Create summary reports

## Example Interaction

User: "Please analyze this dengue virus network: <network_uuid>"

Claude:
```
[SELF-PROMPT: Session Initialization]
I'll create a new session and analyze this network.

$ python -c "from tools.utils.session_utils import create_session; session_id, session_dir = create_session('Dengue Analysis'); print(f'Session created: {session_id}')"

Session created: session_20250427_101234

[SELF-PROMPT: Network Evaluation]
Now I'll fetch and examine the network...

$ python -c "from tools.utils.ndex_utils import get_complete_network; data = get_complete_network('<network_uuid>'); print(f'Network: {data[\"name\"]}, Nodes: {data[\"nodeCount\"]}')"

Network: Dengue-Human PPI Network, Nodes: 3245

...
```

## Getting Started

To use this approach:

1. Ensure the NDEx credentials are set: 
   ```
   NDEX_USERNAME=denguemodeling
   NDEX_PASSWORD=modelofdengue
   ```

2. When analyzing networks, reference actual NDEx UUIDs or paths to network files

3. All analysis outputs are saved to `/Users/idekeradmin/Dropbox/agent_output/dengue_agent/`
