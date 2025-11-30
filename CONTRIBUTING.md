# Contributing to DeFlock America Strategy

## 🎯 Contribution Types (Priority Order)

### 1. **FOIA Data** ⭐ Highest Priority
1.  File FOIA using FOIA-TEMPLATE.md
2.	Add response to data/foia-responses/[CITY]/
3.	Open issue: “FOIA Results: [City]”

### 2. **City Localization**
- `cp CITY-TEMPLATES/template.md CITY-TEMPLATES/[your-city].md` 
- Fill council contacts, Flock contract status, local news

### 3. **Plaintiff Leads** 
Open issue using ISSUE_TEMPLATE/plaintiff-lead.md
Ideal: Abortion travel, DV survivor, protest organizer


### 4. **Code Contributions**
- `scripts/foia-bulk-filer.py` - FOIA automation
- `.github/workflows/foia-tracker.yml` - Status dashboard

## 📋 Contribution Workflow
1.	Fork repo → Your city branch
2.	Update files → Test locally
3.	Commit: “Add [City/State] FOIA + council info”
4.	PR → main (auto-tested by workflows)
5.	Discuss → Merge → Live update

## 🛡️ Code of Conduct
Focus on **actionable intelligence** against Flock Safety. No speculation.

**✅ Good:** “Filed Norfolk FOIA, got 1,247 queries from CBP”
**❌ Bad:** “Flock is evil” (no action)