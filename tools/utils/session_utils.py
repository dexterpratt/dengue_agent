#!/usr/bin/env python3

"""
Session management utilities for dengue_agent analysis sessions.
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Base output directory
BASE_OUTPUT_DIR = "/Users/idekeradmin/Dropbox/agent_output/dengue_agent"

def create_session(name: Optional[str] = None) -> Tuple[str, str]:
    """
    Create a new analysis session with a unique ID.
    
    Args:
        name: Optional name for the session
        
    Returns:
        Tuple of (session_id, session_dir)
    """
    # Create timestamp-based session ID
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if name:
        # Sanitize name by replacing spaces and special chars with underscores
        sanitized_name = name.replace(' ', '_').replace('/', '_')
        session_id = f"session_{sanitized_name}_{timestamp}"
    else:
        session_id = f"session_{timestamp}"
    
    # Create session directory
    session_dir = os.path.join(BASE_OUTPUT_DIR, session_id)
    os.makedirs(session_dir, exist_ok=True)
    
    # Create session metadata file
    metadata = {
        "session_id": session_id,
        "name": name,
        "created_at": timestamp,
        "status": "created",
        "analyses": []
    }
    
    metadata_path = os.path.join(session_dir, "session_metadata.json")
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"Created new session: {session_id}")
    print(f"Session directory: {session_dir}")
    
    return session_id, session_dir

def create_analysis_dir(session_dir: str, analysis_type: str) -> Tuple[str, str]:
    """
    Create a directory for a specific analysis within a session.
    
    Args:
        session_dir: Path to the session directory
        analysis_type: Type of analysis (e.g., "propagation", "hypotheses")
        
    Returns:
        Tuple of (analysis_id, analysis_dir)
    """
    # Create timestamp-based analysis ID
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    analysis_id = f"{analysis_type}_{timestamp}"
    
    # Create analysis directory
    analysis_dir = os.path.join(session_dir, analysis_id)
    os.makedirs(analysis_dir, exist_ok=True)
    
    # Update session metadata
    metadata_path = os.path.join(session_dir, "session_metadata.json")
    
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        metadata["analyses"].append({
            "id": analysis_id,
            "type": analysis_type,
            "created_at": timestamp,
            "status": "created",
            "files": []
        })
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    print(f"Created {analysis_type} directory: {analysis_dir}")
    
    return analysis_id, analysis_dir

def update_analysis_status(session_dir: str, analysis_id: str, status: str, 
                          results: Optional[Dict] = None) -> None:
    """
    Update the status of an analysis in the session metadata.
    
    Args:
        session_dir: Path to the session directory
        analysis_id: ID of the analysis to update
        status: New status of the analysis
        results: Optional results to store in metadata
    """
    metadata_path = os.path.join(session_dir, "session_metadata.json")
    
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        # Find the analysis
        for analysis in metadata["analyses"]:
            if analysis["id"] == analysis_id:
                analysis["status"] = status
                analysis["updated_at"] = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                if results:
                    if "results" not in analysis:
                        analysis["results"] = {}
                    analysis["results"].update(results)
                
                break
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    print(f"Updated analysis {analysis_id} status to: {status}")

def register_file(session_dir: str, analysis_id: str, file_path: str, 
                 file_type: str, description: str) -> None:
    """
    Register a file in the session metadata.
    
    Args:
        session_dir: Path to the session directory
        analysis_id: ID of the analysis the file belongs to
        file_path: Path to the file
        file_type: Type of file (e.g., "cx2", "json", "csv")
        description: Description of the file
    """
    metadata_path = os.path.join(session_dir, "session_metadata.json")
    
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        # Find the analysis
        for analysis in metadata["analyses"]:
            if analysis["id"] == analysis_id:
                file_info = {
                    "path": file_path,
                    "type": file_type,
                    "description": description,
                    "created_at": datetime.now().strftime("%Y%m%d_%H%M%S")
                }
                
                if "files" not in analysis:
                    analysis["files"] = []
                
                analysis["files"].append(file_info)
                break
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    print(f"Registered file: {file_path}")

def list_sessions() -> List[Dict]:
    """
    List all available sessions in the base output directory.
    
    Returns:
        List of session metadata dictionaries
    """
    sessions = []
    
    # Ensure base directory exists
    if not os.path.exists(BASE_OUTPUT_DIR):
        return sessions
    
    # Scan for session directories
    for item in os.listdir(BASE_OUTPUT_DIR):
        item_path = os.path.join(BASE_OUTPUT_DIR, item)
        
        if os.path.isdir(item_path) and item.startswith("session_"):
            metadata_path = os.path.join(item_path, "session_metadata.json")
            
            if os.path.exists(metadata_path):
                try:
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)
                    sessions.append(metadata)
                except:
                    # Skip if metadata is corrupted
                    continue
    
    # Sort by creation time (newest first)
    sessions.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    return sessions

def get_session(session_id: str) -> Optional[Dict]:
    """
    Get metadata for a specific session.
    
    Args:
        session_id: ID of the session
        
    Returns:
        Session metadata dictionary or None if not found
    """
    session_dir = os.path.join(BASE_OUTPUT_DIR, session_id)
    metadata_path = os.path.join(session_dir, "session_metadata.json")
    
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        return metadata
    
    return None

def get_latest_analysis_dir(session_dir: str, analysis_type: str) -> Optional[str]:
    """
    Get the directory of the most recent analysis of a specific type.
    
    Args:
        session_dir: Path to the session directory
        analysis_type: Type of analysis to look for
        
    Returns:
        Path to the latest analysis directory or None if not found
    """
    metadata_path = os.path.join(session_dir, "session_metadata.json")
    
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        # Filter analyses by type and sort by creation time
        analyses = [a for a in metadata.get("analyses", []) if a.get("type") == analysis_type]
        analyses.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        if analyses:
            analysis_id = analyses[0]["id"]
            analysis_dir = os.path.join(session_dir, analysis_id)
            
            if os.path.exists(analysis_dir):
                return analysis_dir
    
    return None

def find_latest_files(session_dir: str, file_type: str, count: int = 1) -> List[str]:
    """
    Find the most recent files of a specific type across all analyses in a session.
    
    Args:
        session_dir: Path to the session directory
        file_type: Type of file to look for
        count: Maximum number of files to return
        
    Returns:
        List of file paths
    """
    metadata_path = os.path.join(session_dir, "session_metadata.json")
    matching_files = []
    
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        # Collect all files of the specified type
        all_files = []
        for analysis in metadata.get("analyses", []):
            for file_info in analysis.get("files", []):
                if file_info.get("type") == file_type:
                    file_info["analysis_id"] = analysis["id"]
                    all_files.append(file_info)
        
        # Sort by creation time (newest first)
        all_files.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        # Return the specified number of files
        matching_files = [os.path.join(session_dir, f["analysis_id"], f["path"]) 
                         for f in all_files[:count] if os.path.exists(os.path.join(session_dir, f["analysis_id"], f["path"]))]
    
    return matching_files

if __name__ == "__main__":
    # Example usage
    session_id, session_dir = create_session("Example Analysis")
    analysis_id, analysis_dir = create_analysis_dir(session_dir, "propagation")
    
    # Register some example files
    register_file(session_dir, analysis_id, "results.json", "json", "Propagation results")
    register_file(session_dir, analysis_id, "network.cx2", "cx2", "Propagation network")
    
    # Update status
    update_analysis_status(session_dir, analysis_id, "completed", {"node_count": 100})
    
    # List all sessions
    sessions = list_sessions()
    print(f"Found {len(sessions)} sessions")
