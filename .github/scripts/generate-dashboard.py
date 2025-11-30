#!/usr/bin/env python3
"""
Auto-generate FOIA dashboard from GitHub issues + data/foia-responses/
"""

import os
import json
import pandas as pd
from github import Github
from datetime import datetime
import yaml

GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
g = Github(GITHUB_TOKEN)

def scan_foia_folder():
    """Scan data/foia-responses/ for responses."""
    responses = {}
    try:
        for city_dir in os.listdir('data/foia-responses/'):
            city_path = f'data/foia-responses/{city_dir}'
            if os.path.isdir(city_path):
                files = os.listdir(city_path)
                responses[city_dir] = {
                    'files': len([f for f in files if f.endswith(('.csv','.json','.pdf'))]),
                    'size_mb': sum(os.path.getsize(f'data/foia-responses/{city_dir}/{f}') for f in files)/1e6
                }
    except:
        pass
    return responses

def scan_github_issues(repo):
    """Parse FOIA issues for status."""
    foia_issues = {}
    for issue in repo.get_issues(state='all'):
        if 'FOIA' in issue.title.upper() or '#foia' in issue.body.lower():
            city = extract_city(issue.title)
            if city:
                foia_issues[city] = {
                    'number': issue.number,
                    'status': issue.state,
                    'opened': issue.created_at.isoformat(),
                    'assignees': [u.login for u in issue.assignees]
                }
    return foia_issues

def generate_markdown(dashboard_data):
    """Generate README status table."""
    md = f"""
## 📊 FOIA Tracker Dashboard (Auto-generated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')})

| City | FOIA Filed | Responses | Size | Status | Issue |
|------|------------|-----------|------|--------|-------|

"""
    
    for city, data in sorted(dashboard_data.items()):
        status_emoji = data.get('status', '⚪')
        issue_link = data.get('issue_link', '')
        md += f"| {city} | ✅ | {data.get('files', 0)} | {data.get('size_mb', 0):.1f}MB | {status_emoji} | {issue_link} |\n"
    
    with open('README.md', 'r') as f:
        content = f.read()
    
    # Inject table into README
    updated = content.replace('<!-- FOIA-DASHBOARD -->', md)
    with open('README.md', 'w') as f:
        f.write(updated)

if __name__ == '__main__':
    repo = g.get_repo("USERNAME/deflock-america-strategy")
    responses = scan_foia_folder()
    issues = scan_github_issues(repo)
    
    dashboard = {**responses, **issues}
    generate_markdown(dashboard)
    
    # Save JSON for other workflows
    with open('foia-status.json', 'w') as f:
        json.dump(dashboard, f, indent=2)
    
    print("✅ Dashboard updated!")
