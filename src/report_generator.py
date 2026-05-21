import logging
import json
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path
from jinja2 import Template
from config.settings import REPORT_OUTPUT_DIR

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Generate reports and dashboards from Jira release tasks"""
    
    def __init__(self):
        self.report_dir = Path(REPORT_OUTPUT_DIR)
        self.report_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_html_dashboard(self, tasks: List[Dict[str, Any]], statistics: Dict[str, Any]) -> str:
        """
        Generate an HTML dashboard report
        
        Args:
            tasks: List of release tasks
            statistics: Task statistics
        
        Returns:
            Path to generated HTML file
        """
        try:
            html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jira Release Tasks Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        header {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
        }
        
        h1 {
            color: #333;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .timestamp {
            color: #666;
            font-size: 0.9em;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            border-left: 5px solid #667eea;
        }
        
        .stat-card h3 {
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            margin-bottom: 10px;
        }
        
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }
        
        .stat-card.overdue {
            border-left-color: #ff6b6b;
        }
        
        .stat-card.overdue .stat-value {
            color: #ff6b6b;
        }
        
        .section {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
        }
        
        .section h2 {
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
        }
        
        th {
            background: #f5f5f5;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            color: #333;
            border-bottom: 2px solid #667eea;
        }
        
        td {
            padding: 12px;
            border-bottom: 1px solid #eee;
        }
        
        tr:hover {
            background: #f9f9f9;
        }
        
        .status-badge {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 0.85em;
            font-weight: 600;
        }
        
        .status-todo {
            background: #ffeaa7;
            color: #d63031;
        }
        
        .status-in-progress {
            background: #74b9ff;
            color: #0984e3;
        }
        
        .status-done {
            background: #55efc4;
            color: #00b894;
        }
        
        .status-other {
            background: #dfe6e9;
            color: #2d3436;
        }
        
        .priority-high {
            color: #d63031;
            font-weight: bold;
        }
        
        .priority-medium {
            color: #f39c12;
            font-weight: bold;
        }
        
        .priority-low {
            color: #00b894;
            font-weight: bold;
        }
        
        a {
            color: #667eea;
            text-decoration: none;
        }
        
        a:hover {
            text-decoration: underline;
        }
        
        .chart-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        
        .chart-box {
            background: #f9f9f9;
            padding: 15px;
            border-radius: 5px;
        }
        
        .chart-box h3 {
            margin-bottom: 10px;
            color: #333;
        }
        
        .chart-item {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }
        
        footer {
            text-align: center;
            color: white;
            margin-top: 30px;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 Jira Release Tasks Dashboard</h1>
            <p class="timestamp">Last updated: {{ timestamp }}</p>
        </header>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Total Tasks</h3>
                <div class="stat-value">{{ statistics.total_tasks }}</div>
            </div>
            <div class="stat-card overdue">
                <h3>Overdue Tasks</h3>
                <div class="stat-value">{{ statistics.overdue_tasks }}</div>
            </div>
            <div class="stat-card">
                <h3>In Progress</h3>
                <div class="stat-value">{{ statistics.by_status.get('In Progress', 0) }}</div>
            </div>
            <div class="stat-card">
                <h3>Completed</h3>
                <div class="stat-value">{{ statistics.by_status.get('Done', 0) }}</div>
            </div>
        </div>
        
        <div class="section">
            <h2>📈 Statistics</h2>
            <div class="chart-container">
                <div class="chart-box">
                    <h3>By Status</h3>
                    {% for status, count in statistics.by_status.items() %}
                    <div class="chart-item">
                        <span>{{ status }}</span>
                        <span>{{ count }}</span>
                    </div>
                    {% endfor %}
                </div>
                
                <div class="chart-box">
                    <h3>By Priority</h3>
                    {% for priority, count in statistics.by_priority.items() %}
                    <div class="chart-item">
                        <span>{{ priority }}</span>
                        <span>{{ count }}</span>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>📋 All Release Tasks</h2>
            <table>
                <thead>
                    <tr>
                        <th>Key</th>
                        <th>Summary</th>
                        <th>Status</th>
                        <th>Priority</th>
                        <th>Assignee</th>
                        <th>Due Date</th>
                    </tr>
                </thead>
                <tbody>
                    {% for task in tasks %}
                    <tr>
                        <td><a href="{{ task.url }}" target="_blank">{{ task.key }}</a></td>
                        <td>{{ task.summary }}</td>
                        <td>
                            <span class="status-badge status-{{ task.status | lower | replace(' ', '-') }}">
                                {{ task.status }}
                            </span>
                        </td>
                        <td><span class="priority-{{ task.priority | lower }}">{{ task.priority }}</span></td>
                        <td>{{ task.assignee }}</td>
                        <td>{{ task.due_date or 'N/A' }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        
        <footer>
            <p>Generated automatically by Jira Release Automation</p>
        </footer>
    </div>
</body>
</html>
            """
            
            template = Template(html_template)
            html_content = template.render(
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                tasks=tasks,
                statistics=statistics
            )
            
            filename = f"release_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            filepath = self.report_dir / filename
            
            with open(filepath, 'w') as f:
                f.write(html_content)
            
            logger.info(f"HTML dashboard generated: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error generating HTML dashboard: {str(e)}")
            raise
    
    def generate_json_report(self, tasks: List[Dict[str, Any]], statistics: Dict[str, Any]) -> str:
        """
        Generate a JSON report
        
        Args:
            tasks: List of release tasks
            statistics: Task statistics
        
        Returns:
            Path to generated JSON file
        """
        try:
            report = {
                'timestamp': datetime.now().isoformat(),
                'statistics': statistics,
                'tasks': tasks
            }
            
            filename = f"release_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = self.report_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"JSON report generated: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error generating JSON report: {str(e)}")
            raise
    
    def generate_markdown_report(self, tasks: List[Dict[str, Any]], statistics: Dict[str, Any]) -> str:
        """
        Generate a Markdown report
        
        Args:
            tasks: List of release tasks
            statistics: Task statistics
        
        Returns:
            Path to generated Markdown file
        """
        try:
            md_content = f"""# Jira Release Tasks Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary Statistics

| Metric | Value |
|--------|-------|
| Total Tasks | {statistics.get('total_tasks', 0)} |
| Overdue Tasks | {statistics.get('overdue_tasks', 0)} |
| In Progress | {statistics.get('by_status', {}).get('In Progress', 0)} |
| Completed | {statistics.get('by_status', {}).get('Done', 0)} |

## Status Breakdown

"""
            
            for status, count in statistics.get('by_status', {}).items():
                md_content += f"- **{status}**: {count}\n"
            
            md_content += "\n## Priority Breakdown\n\n"
            
            for priority, count in statistics.get('by_priority', {}).items():
                md_content += f"- **{priority}**: {count}\n"
            
            md_content += "\n## Release Tasks\n\n"
            md_content += "| Key | Summary | Status | Priority | Assignee | Due Date |\n"
            md_content += "|-----|---------|--------|----------|----------|----------|\n"
            
            for task in tasks:
                md_content += f"| [{task['key']}]({task['url']}) | {task['summary']} | {task['status']} | {task['priority']} | {task['assignee']} | {task.get('due_date', 'N/A')} |\n"
            
            filename = f"release_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            filepath = self.report_dir / filename
            
            with open(filepath, 'w') as f:
                f.write(md_content)
            
            logger.info(f"Markdown report generated: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error generating Markdown report: {str(e)}")
            raise

