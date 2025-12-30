"""
Docker Build Utilities
"""
from typing import Dict, Optional


class DockerBuildHelper:
    """Helper class for Docker build operations"""
    
    @staticmethod
    def detect_framework(repo_structure: Dict[str, bool]) -> str:
        """
        Detect framework based on repository structure
        
        Args:
            repo_structure: Dictionary of file existence checks
            
        Returns:
            Detected framework name
        """
        if repo_structure.get("package.json"):
            if repo_structure.get("next.config.js"):
                return "Next.js"
            elif repo_structure.get("vue.config.js"):
                return "Vue"
            else:
                return "React"
        elif repo_structure.get("index.html"):
            return "Static HTML"
        
        return "Unknown"
    
    @staticmethod
    def get_build_output_dir(framework: str) -> str:
        """
        Get the typical build output directory for a framework
        
        Args:
            framework: Framework name
            
        Returns:
            Build output directory name
        """
        framework_outputs = {
            "React": "build",
            "Next.js": ".next",
            "Vue": "dist",
            "Static HTML": "."
        }
        
        return framework_outputs.get(framework, "build")
