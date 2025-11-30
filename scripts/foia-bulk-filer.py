#!/usr/bin/env python3
"""
DeFlock America FOIA Bulk Filer
Automated FOIA request generator + email sender for Flock Safety resistance campaign.

WARNING: Customize targets/emails before running. Comply with local anti-spam laws.
"""

import csv
import smtplib
import os
from email.mime.text import MimeText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import argparse
from datetime import datetime
import yaml

# Load FOIA template from project root
FOIA_TEMPLATE = Path(__file__).parent.parent / "FOIA-TEMPLATE.md"

class FOIABulkFiler:
    def __init__(self, config_file="foia-targets.csv"):
        self.config_file = config_file
        self.load_template()
    
    def load_template(self):
        """Load FOIA template and prepare for substitution."""
        with open(FOIA_TEMPLATE, 'r') as f:
            self.template = f.read()
    
    def generate_request(self, city, state, clerk_email, clerk_name="City Clerk"):
        """Generate personalized FOIA request."""
        request = self.template.replace("[INSERT DATE]", datetime.now().strftime("%Y-%m-%d"))
        request = request.replace("[CITY]", city)
        request = request.replace("[STATE]", state)
        request = request.replace("[YOUR NAME]", "DeFlock America Coalition")
        request = request = request.replace("cityclerk@[city].gov", clerk_email)
        return request
    
    def load_targets(self):
        """Load city targets from CSV."""
        targets = []
        with open(self.config_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                targets.append({
                    'city': row['city'],
                    'state': row['state'],
                    'clerk_email': row['clerk_email'],
                    'clerk_name': row.get('clerk_name', 'City Clerk'),
                    'status': 'pending'
                })
        return targets
    
    def save_generated(self, requests, output_dir="generated-foia"):
        """Save generated requests to files."""
        Path(output_dir).mkdir(exist_ok=True)
        for i, req in enumerate(requests):
            filename = f"{output_dir}/foia-{i+1:03d}-{req['city'].lower().replace(' ', '-')}.md"
            with open(filename, 'w') as f:
                f.write(req['content'])
            print(f"✅ Saved: {filename}")
    
    def send_emails(self, requests, smtp_server, smtp_port, smtp_user, smtp_pass, test_mode=False):
        """Send FOIA requests via SMTP."""
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        
        for req in requests:
            if test_mode:
                print(f"📧 [TEST MODE] Would send to {req['to']}")
                continue
                
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = req['to']
            msg['Subject'] = f"Public Records Request: Flock Safety ALPR Data - {req['city']}, {req['state']}"
            
            msg.attach(MimeText(req['content'], 'plain'))
            
            server.send_message(msg)
            print(f"✅ SENT: {req['city']} → {req['to']}")
        
        server.quit()

def main():
    parser = argparse.ArgumentParser(description="DeFlock America FOIA Bulk Filer")
    parser.add_argument("--generate-only", action="store_true", help="Generate files only, no email")
    parser.add_argument("--send", action="store_true", help="Send emails (dangerous!)")
    parser.add_argument("--test-send", action="store_true", help="Test email sending (dry run)")
    parser.add_argument("--config", default="foia-targets.csv", help="Target CSV file")
    parser.add_argument("--smtp-server", default="smtp.gmail.com", help="SMTP server")
    parser.add_argument("--smtp-port", type=int, default=587, help="SMTP port")
    parser.add_argument("--smtp-user", help="SMTP username")
    parser.add_argument("--smtp-pass", help="SMTP password")
    
    args = parser.parse_args()
    
    filer = FOIABulkFiler(args.config)
    targets = filer.load_targets()
    
    print(f"🚀 Loading {len(targets)} cities from {args.config}")
    
    requests = []
    for target in targets:
        content = filer.generate_request(
            target['city'], target['state'], 
            target['clerk_email'], target['clerk_name']
        )
        requests.append({
            'city': target['city'],
            'state': target['state'],
            'to': target['clerk_email'],
            'content': content
        })
    
    # Save generated requests
    filer.save_generated(requests)
    
    if args.generate_only:
        print("✅ Files generated. Done.")
        return
    
    if args.send or args.test_send:
        if not args.smtp_user or not args.smtp_pass:
            print("❌ Need --smtp-user and --smtp-pass for sending")
            return
        
        print("📧 Sending emails...")
        filer.send_emails(
            requests, args.smtp_server, args.smtp_port,
            args.smtp_user, args.smtp_pass, 
            test_mode=args.test_send
        )
        print("✅ Bulk send complete!")

if __name__ == "__main__":
    main()
