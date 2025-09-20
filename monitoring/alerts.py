"""
Alerting system for the Where's My Taxi ML pipeline.

This module provides GitHub-based alerting capabilities including:
- Creating GitHub issues for failures
- Updating issue status
- Sending alerts to GitHub Discussions
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

try:
    from github import Github
    GITHUB_AVAILABLE = True
except ImportError:
    GITHUB_AVAILABLE = False


@dataclass
class Alert:
    """Alert data structure."""
    title: str
    severity: str  # "critical", "high", "medium", "low"
    message: str
    timestamp: str
    source: str
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'title': self.title,
            'severity': self.severity,
            'message': self.message,
            'timestamp': self.timestamp,
            'source': self.source,
            'metadata': self.metadata
        }


class AlertManager:
    """GitHub-based alert manager."""
    
    def __init__(self, github_token: Optional[str] = None, 
                 repo_name: Optional[str] = None):
        """
        Initialize alert manager.
        
        Args:
            github_token: GitHub personal access token
            repo_name: Repository name (e.g., 'owner/repo')
        """
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        self.repo_name = repo_name or os.getenv('GITHUB_REPOSITORY', 'satyam-gaikwad/wheres-my-taxi')
        self.github_client = None
        self.repo = None
        
        if self.github_token and GITHUB_AVAILABLE:
            try:
                self.github_client = Github(self.github_token)
                self.repo = self.github_client.get_repo(self.repo_name)
            except Exception as e:
                print(f"Warning: Could not initialize GitHub client: {e}")
    
    def create_alert(self, title: str, message: str, severity: str = "medium",
                    source: str = "pipeline", metadata: Optional[Dict] = None) -> Alert:
        """Create an alert."""
        return Alert(
            title=title,
            severity=severity,
            message=message,
            timestamp=datetime.utcnow().isoformat(),
            source=source,
            metadata=metadata or {}
        )
    
    def send_github_issue_alert(self, alert: Alert, labels: Optional[List[str]] = None) -> bool:
        """
        Send alert as GitHub issue.
        
        Args:
            alert: Alert to send
            labels: Additional labels for the issue
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.repo:
            print("Warning: GitHub repository not available for issue creation")
            return False
        
        try:
            # Create issue body
            body = f"""
## Alert Details

**Severity:** {alert.severity}
**Source:** {alert.source}
**Timestamp:** {alert.timestamp}

## Message
{alert.message}

## Metadata
```json
{json.dumps(alert.metadata, indent=2)}
```

---
*This issue was automatically created by the monitoring system.*
            """.strip()
            
            # Set labels
            issue_labels = ['monitoring', f'severity-{alert.severity}']
            if labels:
                issue_labels.extend(labels)
            
            # Create issue
            issue = self.repo.create_issue(
                title=f"[ALERT] {alert.title}",
                body=body,
                labels=issue_labels
            )
            
            print(f"Created GitHub issue #{issue.number}: {alert.title}")
            return True
            
        except Exception as e:
            print(f"Error creating GitHub issue: {e}")
            return False
    
    def send_pipeline_failure_alert(self, error_message: str, 
                                  pipeline_metrics: Optional[Dict] = None) -> bool:
        """Send pipeline failure alert."""
        alert = self.create_alert(
            title="Pipeline Execution Failed",
            message=f"The ML pipeline execution failed with error: {error_message}",
            severity="high",
            source="pipeline",
            metadata=pipeline_metrics or {}
        )
        
        return self.send_github_issue_alert(alert, labels=['pipeline-failure', 'urgent'])
    
    def send_model_performance_alert(self, metrics: Dict[str, Any], 
                                   threshold_r2: float = 0.5) -> bool:
        """Send model performance alert if metrics are below threshold."""
        r2_score = metrics.get('r2_score', 0)
        
        if r2_score < threshold_r2:
            alert = self.create_alert(
                title="Model Performance Below Threshold",
                message=f"Model R² score ({r2_score:.3f}) is below threshold ({threshold_r2})",
                severity="medium",
                source="model_training",
                metadata=metrics
            )
            
            return self.send_github_issue_alert(alert, labels=['model-performance', 'quality'])
        
        return True
    
    def send_data_quality_alert(self, metrics: Dict[str, Any], 
                              quality_threshold: float = 0.8) -> bool:
        """Send data quality alert if quality is below threshold."""
        quality_score = metrics.get('data_quality_score', 1.0)
        
        if quality_score < quality_threshold:
            alert = self.create_alert(
                title="Data Quality Below Threshold",
                message=f"Data quality score ({quality_score:.3f}) is below threshold ({quality_threshold})",
                severity="medium",
                source="data_processing",
                metadata=metrics
            )
            
            return self.send_github_issue_alert(alert, labels=['data-quality', 'quality'])
        
        return True
    
    def close_resolved_issues(self, issue_title_pattern: str) -> int:
        """Close resolved issues matching a pattern."""
        if not self.repo:
            return 0
        
        try:
            # Find open issues with monitoring label
            issues = self.repo.get_issues(state='open', labels=['monitoring'])
            closed_count = 0
            
            for issue in issues:
                if issue_title_pattern in issue.title:
                    # Add resolution comment and close
                    issue.create_comment("Issue appears to be resolved. Closing automatically.")
                    issue.edit(state='closed')
                    closed_count += 1
                    print(f"Closed resolved issue #{issue.number}: {issue.title}")
            
            return closed_count
            
        except Exception as e:
            print(f"Error closing resolved issues: {e}")
            return 0
    
    def send_workflow_status_update(self, status: str, metrics: Dict[str, Any]) -> bool:
        """
        Send workflow status update via GitHub API.
        
        Args:
            status: Workflow status ("success", "failure", "warning")
            metrics: Pipeline metrics
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.github_token:
            print("Warning: No GitHub token available for status updates")
            return False
        
        try:
            # Use GitHub's statuses API to update commit status
            # This requires the commit SHA, which we can get from environment
            commit_sha = os.getenv('GITHUB_SHA')
            if not commit_sha:
                print("Warning: No commit SHA available for status update")
                return False
            
            # Map status to GitHub state
            state_map = {
                'success': 'success',
                'failure': 'failure',
                'warning': 'success',  # GitHub doesn't have warning state
                'running': 'pending'
            }
            
            github_state = state_map.get(status, 'pending')
            
            # Create status description
            description = f"Pipeline {status}"
            if 'execution_time' in metrics:
                description += f" in {metrics['execution_time']:.1f}s"
            
            # Send status update
            url = f"https://api.github.com/repos/{self.repo_name}/statuses/{commit_sha}"
            headers = {
                'Authorization': f'token {self.github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            data = {
                'state': github_state,
                'description': description,
                'context': 'ml-pipeline/monitoring'
            }
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            print(f"Updated commit status: {status}")
            return True
            
        except Exception as e:
            print(f"Error updating workflow status: {e}")
            return False
    
    def log_alert_locally(self, alert: Alert, log_file: str = "monitoring/logs/alerts.log"):
        """Log alert to local file as fallback."""
        try:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            
            with open(log_file, 'a') as f:
                f.write(f"{alert.timestamp} [{alert.severity.upper()}] {alert.title}: {alert.message}\n")
                
            print(f"Alert logged locally: {alert.title}")
            return True
            
        except Exception as e:
            print(f"Error logging alert locally: {e}")
            return False
    
    def send_alert(self, alert: Alert, use_github: bool = True, 
                  fallback_to_log: bool = True) -> bool:
        """
        Send alert using available methods.
        
        Args:
            alert: Alert to send
            use_github: Whether to try GitHub issue creation
            fallback_to_log: Whether to log locally if GitHub fails
            
        Returns:
            bool: True if alert was sent successfully
        """
        success = False
        
        # Try GitHub issue creation
        if use_github and self.repo:
            success = self.send_github_issue_alert(alert)
        
        # Fallback to local logging
        if not success and fallback_to_log:
            success = self.log_alert_locally(alert)
        
        return success