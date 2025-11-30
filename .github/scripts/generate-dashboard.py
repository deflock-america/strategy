#!/usr/bin/env python3
"""
DeFlock America FOIA Dashboard Generator - PRODUCTION READY
Scans data/foia-responses/ + GitHub issues → Updates README table
"""

import os
import json
import glob
import re
from datetime import datetime
from github import Github
import requests

# GitHub setup
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
REPO_NAME = os.environ.get('GITHUB_REPOSITORY', 'YOURUSERNAME/deflock-america-strategy')
g = Github(GITHUB_TOKEN)

def scan_foia_folder():
    """Scan data/foia-responses/ for real FOIA data."""
    responses = {}
    
    foia_path = 'data/foia-responses'
    if not os.path.exists(foia_path):
        return responses
    
    for city_dir in os.listdir(foia_path):
        city_path = os.path.join(foia_path, city_dir)
        if os.path.isdir(city_path):
            files = glob.glob(os.path.join(city_path, '*'))
            data_files = [f for f in files if f.endswith(('.csv', '.json', '.pdf', '.txt'))]
            
            total_size = sum(os.path.getsize(f) for f in data_files) / (1024 * 1024)  # MB
            
            responses[city_dir.replace('-', ' ').title()] = {
                'files': len(data_files),
                'size_mb': round(total_size, 1),
                'status': '🟢' if len(data_files) > 0 else '🔴'
            }
    
    return responses

def scan_github_issues():
    """Scan issues for FOIA + plaintiff leads."""
    try:
        repo_name = REPO_NAME.split('/') 
        repo = g.get_repo(f"{repo_name[0]}/{repo_name[1]}")
        foia_issues = {}
        
        for issue in repo.get_issues(state='all'):
            title_lower = issue.title.lower()
            if any(keyword in title_lower for keyword in ['foia', 'records', 'plaintiff']):
                city_match = re.search(r'([a-zA-Z\s]+?)[,\s]+([A-Z]{2})?', issue.title)
                if city_match:
                    city = city_match.group(1).strip().title()
                    foia_issues[city] = {
                        'number': issue.number,
                        'status': '🟢' if issue.state == 'open' else '🟡',
                        'url': issue.html_url
                    }
        return foia_issues
    except Exception as e:
        print(f"⚠️ GitHub issues scan failed: {e}")
        return {}

def generate_status_table(foia_data, issues_data):
    """Generate Markdown table for README."""
    table_lines = []
    table_lines.append("## 📊 FOIA Tracker Dashboard (Auto-generated: " + datetime.now().strftime('%Y-%m-%d %H:%M UTC') + ")")
    table_lines.append("")
    table_lines.append("| City | FOIA Filed | Files | Size | Status | Issue |")
    table_lines.append("|------|------------|-------|------|--------|-------|")
    
    # Combine FOIA data + issues
    all_cities = set(list(foia_data.keys()) + list(issues_data.keys()))
    
    for city in sorted(all_cities):
        row_data = foia_data.get(city, {'files': 0, 'size_mb': 0.0, 'status': '⚪'})
        issue_data = issues_data.get(city, {})
        
        issue_link = f"[#{issue_data.get('number', '')}]({issue_data.get('url', '')})" if issue_data else ""
        
        table_lines.append(f"| {city} | ✅ | **{row_data['files']}** | {row_data['size_mb']}MB | {row_data['status']} | {issue_link} |")
    
    # CALCULATE TOTALS FIRST
    total_files = sum(d['files'] for d in foia_data.values())
    total_size = sum(d['size_mb'] for d in foia_data.values())
    total_cities = len(foia_data)
    
    table_lines.append(f"| **TOTAL** | **{total_cities} cities** | **{total_files}** | **{total_size:.1f}MB** | | |")
    
    return '\n'.join(table_lines)

def update_readme(table_md):
    """Inject table into README.md."""
    try:
        # Read existing README
        try:
            with open('README.md', 'r') as f:
                content = f.read()
        except FileNotFoundError:
            content = "# DeFlock America Strategy\n\n" + table_md + "\n\n"
        
        # Replace or insert FOIA dashboard section
        if '<!-- FOIA-DASHBOARD -->' in content:
            content = content.replace('<!-- FOIA-DASHBOARD -->', table_md)
        else:
            # Insert after first header or at top
            content = re.sub(r'^#{1,6}\s', f'{table_md}\n\n\\g<0>', content, flags=re.MULTILINE | re.DOTALL, count=1)
            if '<!-- FOIA-DASHBOARD -->' not in content:
                content = table_md + "\n\n" + content
        
        with open('README.md', 'w') as f:
            f.write(content)
        
        print("✅ README updated successfully!")
        return True, total_files, total_size
        
    except Exception as e:
        print(f"❌ README update failed: {e}")
        return False, 0, 0

def send_discord_if_configured(foia_data, total_files, total_size):
    """Send Discord update if webhook exists."""
    webhook = os.environ.get('DISCORD_WEBHOOK')
    if not webhook:
        print("⚠️ No Discord webhook configured")
        return
    
    try:
        cities_str = ', '.join(list(foia_data.keys())[:3])  # First 3 cities
        payload = {
            "content": f"📊 **FOIA Dashboard Updated** ({datetime.now().strftime('%H:%M EST')})\n"
                      f"• **{len(foia_data)} cities** | **{total_files} files** | **{total_size:.1f}MB**\n"
                      f"• Cities: {cities_str}{'...' if len(foia_data) > 3 else ''}\n"
                      f"🔗 https://{REPO_NAME.split('/')[0]}.github.io/{REPO_NAME.split('/')[1]}/"
        }
        response = requests.post(webhook, json=payload)
        print(f"✅ Discord notified: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Discord notification failed: {e}")

if __name__ == '__main__':
    print("🚀 DeFlock America FOIA Dashboard Generator")
    print(f"📂 Scanning {REPO_NAME}")
    
    # Scan data
    foia_data = scan_foia_folder()
    issues_data = scan_github_issues()
    
    # Generate table
    table_md = generate_status_table(foia_data, issues_data)
    
    # Update README (defines totals here)
    success, total_files, total_size = update_readme(table_md)
    
    if success:
        print("✅ SUCCESS: Dashboard generated!")
        print("\n" + table_md[:500] + "...")
        
        # Discord notification (totals now defined)
        send_discord_if_configured(foia_data, total_files, total_size)
    else:
        print("❌ FAILED: Check logs above")
        exit(1)
