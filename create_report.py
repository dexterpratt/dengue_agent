#!/usr/bin/env python3

"""
Script to create a session report for the dengue analysis.
"""

import os
import sys
from datetime import datetime
from tools.utils.session_utils import register_file

def create_session_report(session_dir):
    """Create a session report markdown file."""
    # Create report directory
    report_dir = os.path.join(session_dir, f'report_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
    os.makedirs(report_dir, exist_ok=True)
    
    # Create report file
    report_file = os.path.join(report_dir, 'session_report.md')
    
    # Report content
    report_content = """# Dengue Test Network Analysis Report

## Session Information
- **Session ID:** {session_id}
- **Created:** 2025-04-27

## Network Overview
The test dengue network contains:
- 400 nodes (including 9 viral proteins) and 500 edges
- Average degree: 2.5 (relatively sparse network)
- Node types: 32.8% med_z, 32.5% high_z, 32.5% low_z, 2.2% viral

## Viral Proteins
- DENV2 16681 NS2A (ID: 398)
- DENV2 16681 NS1 (ID: 395)
- DENV2 16681 Capsid Anchor (ID: 389)
- DENV2 16681 NS4B (ID: 387)
- DENV2 16681 Capsid (ID: 385)
- DENV2 16681 NS3 (ID: 383)
- DENV2 16681 NS2B3 (ID: 382)
- DENV2 16681 NS5 (ID: 381)
- DENV2 16681 NS4A (ID: 379)

## Propagation Analysis
Propagation was performed with parameters:
- Restart probability: 0.15
- Max steps: 150
- Include all nodes: False

Results showed limited connectivity in this test network:

| Viral Protein | Steps | Restarts | Top Host Interactions |
|---------------|-------|----------|----------------------|
| NS2A | 6 | 1 | ACTR5, MRPL10, NFRKB |
| NS1 | 3 | 0 | Limited data |
| Capsid Anchor | 2 | 0 | Limited data |
| NS4B | 4 | 0 | Limited data |
| Capsid | 4 | 0 | Limited data |
| NS3 | 2 | 0 | HSPH1 |
| NS2B3 | 4 | 1 | Limited data |
| NS5 | 3 | 0 | Limited data |
| NS4A | 3 | 0 | Limited data |

## Key Observations

1. The test network has very sparse connectivity
2. All propagation runs terminated with "dead_end" status
3. NS2A showed the highest connectivity (3 host proteins)
4. NS3 only connected to one host protein (HSPH1, a heat shock protein)

## Limitations

This was a test network primarily used to verify the functionality of the refactored tools. For real biological insights, a more comprehensive network would be needed.
""".format(session_id=os.path.basename(session_dir))
    
    # Write report to file
    with open(report_file, 'w') as f:
        f.write(report_content)
    
    # Register file in session
    analysis_id = os.path.basename(report_dir)
    register_file(session_dir, analysis_id, 'session_report.md', 'md', 'Session summary report')
    
    print(f"Report created: {report_file}")
    return report_file

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: create_report.py <session_directory>")
        sys.exit(1)
    
    create_session_report(sys.argv[1])
