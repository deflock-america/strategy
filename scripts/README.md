# 👩‍💻Example Usage
### 1. Generate files only (safest)
`python scripts/foia-bulk-filer.py --generate-only --config foia-targets.csv`

### 2. Test email sending (dry run)
```python scripts/foia-bulk-filer.py --test-send \
  --smtp-user your@gmail.com \
  --smtp-pass your-app-password```

### 3. LIVE SEND (⚠️ DANGER ⚠️)
```python scripts/foia-bulk-filer.py --send \
  --smtp-user your@gmail.com \
  --smtp-pass your-app-password```

### 4. Custom targets
`python scripts/foia-bulk-filer.py --generate-only --config my-cities.csv`

#🛡️ Safety Features
-  ✅ Generate-only mode (default) - no emails sent
-  ✅ Test mode - simulates sending without transmission
-  ✅ Per-city files - review before sending
-  ✅ CSV-driven - easy target management
-  ✅ Logs everything to console

# ⚖️ Legal Compliance
-  ✅ Uses real clerk emails from public directories
-  ✅ Requests only public records (FOIA/Public Records Act)  
-  ✅ Template based on Washington precedent [web:27]
-  ✅ No spam - legitimate government records requests
-  ✅ CCs ACLU/EFF for accountability
