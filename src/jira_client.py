import logging
from jira import JIRA
from typing import List, Dict, Any
from config.settings import JIRA_SERVER, JIRA_USERNAME, JIRA_API_TOKEN, JIRA_PROJECT_KEY
from datetime import datetime

logger = logging.getLogger(__name__)

class JiraClient:
    """Client for interacting with Jira API"""
    
    def __init__(self):
        """Initialize Jira client with credentials"""
        try:
            self.jira = JIRA(
                server=JIRA_SERVER,
                basic_auth=(JIRA_USERNAME, JIRA_API_TOKEN)
            )
            logger.info(f"Successfully connected to Jira: {JIRA_SERVER}")
        except Exception as e:
            logger.error(f"Failed to connect to Jira: {str(e)}")
            raise
    
    def get_release_tasks(self, status: List[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch release tasks from Jira
        
        Args:
            status: List of statuses to filter (e.g., ['To Do', 'In Progress', 'Done'])
        
        Returns:
            List of release tasks with details
        """
        try:
            # Build JQL query
            jql_parts = [f"project = {JIRA_PROJECT_KEY}"]
            
            if status:
                status_query = ' OR '.join([f'status = "{s}"' for s in status])
                jql_parts.append(f"({status_query})")
            
            jql = ' AND '.join(jql_parts)
            logger.info(f"Executing JQL query: {jql}")
            
            # Fetch issues
            issues = self.jira.search_issues(jql, maxResults=False)
            
            tasks = []
            for issue in issues:
                task = {
                    'key': issue.key,
                    'summary': issue.fields.summary,
                    'status': issue.fields.status.name,
                    'priority': issue.fields.priority.name if issue.fields.priority else 'None',
                    'assignee': issue.fields.assignee.displayName if issue.fields.assignee else 'Unassigned',
                    'created': issue.fields.created,
                    'updated': issue.fields.updated,
                    'description': issue.fields.description or 'N/A',
                    'components': [c.name for c in issue.fields.components] if issue.fields.components else [],
                    'labels': issue.fields.labels if issue.fields.labels else [],
                    'due_date': issue.fields.duedate,
                    'url': f"{JIRA_SERVER}/browse/{issue.key}"
                }
                tasks.append(task)
            
            logger.info(f"Retrieved {len(tasks)} release tasks")
            return tasks
            
        except Exception as e:
            logger.error(f"Error fetching release tasks: {str(e)}")
            return []
    
    def get_task_by_key(self, task_key: str) -> Dict[str, Any]:
        """
        Fetch a specific task by key
        
        Args:
            task_key: Jira issue key (e.g., 'RELEASE-123')
        
        Returns:
            Task details dictionary
        """
        try:
            issue = self.jira.issue(task_key)
            task = {
                'key': issue.key,
                'summary': issue.fields.summary,
                'status': issue.fields.status.name,
                'priority': issue.fields.priority.name if issue.fields.priority else 'None',
                'assignee': issue.fields.assignee.displayName if issue.fields.assignee else 'Unassigned',
                'created': issue.fields.created,
                'updated': issue.fields.updated,
                'description': issue.fields.description or 'N/A',
                'components': [c.name for c in issue.fields.components] if issue.fields.components else [],
                'labels': issue.fields.labels if issue.fields.labels else [],
                'due_date': issue.fields.duedate,
                'url': f"{JIRA_SERVER}/browse/{issue.key}"
            }
            return task
        except Exception as e:
            logger.error(f"Error fetching task {task_key}: {str(e)}")
            return {}
    
    def get_tasks_by_status(self, status: str) -> List[Dict[str, Any]]:
        """
        Fetch tasks filtered by status
        
        Args:
            status: Status name (e.g., 'To Do', 'In Progress', 'Done')
        
        Returns:
            List of tasks with the specified status
        """
        return self.get_release_tasks(status=[status])
    
    def get_overdue_tasks(self) -> List[Dict[str, Any]]:
        """
        Fetch tasks that are overdue
        
        Returns:
            List of overdue tasks
        """
        try:
            jql = f'project = {JIRA_PROJECT_KEY} AND duedate < now() AND status != Done'
            logger.info(f"Fetching overdue tasks with JQL: {jql}")
            
            issues = self.jira.search_issues(jql, maxResults=False)
            
            tasks = []
            for issue in issues:
                task = {
                    'key': issue.key,
                    'summary': issue.fields.summary,
                    'status': issue.fields.status.name,
                    'priority': issue.fields.priority.name if issue.fields.priority else 'None',
                    'assignee': issue.fields.assignee.displayName if issue.fields.assignee else 'Unassigned',
                    'due_date': issue.fields.duedate,
                    'url': f"{JIRA_SERVER}/browse/{issue.key}"
                }
                tasks.append(task)
            
            logger.info(f"Retrieved {len(tasks)} overdue tasks")
            return tasks
            
        except Exception as e:
            logger.error(f"Error fetching overdue tasks: {str(e)}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about release tasks
        
        Returns:
            Dictionary with task statistics
        """
        try:
            all_tasks = self.get_release_tasks()
            
            stats = {
                'total_tasks': len(all_tasks),
                'by_status': {},
                'by_priority': {},
                'by_assignee': {},
                'overdue_tasks': len(self.get_overdue_tasks())
            }
            
            for task in all_tasks:
                # By status
                status = task['status']
                stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
                
                # By priority
                priority = task['priority']
                stats['by_priority'][priority] = stats['by_priority'].get(priority, 0) + 1
                
                # By assignee
                assignee = task['assignee']
                stats['by_assignee'][assignee] = stats['by_assignee'].get(assignee, 0) + 1
            
            return stats
            
        except Exception as e:
            logger.error(f"Error generating statistics: {str(e)}")
            return {}

