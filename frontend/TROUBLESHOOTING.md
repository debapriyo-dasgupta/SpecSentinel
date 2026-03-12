# SpecSentinel Frontend - Troubleshooting Guide

## Common Issues and Solutions

### Issue 1: File Upload Requires Multiple Clicks

**Symptoms:**
- Clicking "Choose File" doesn't open file dialog immediately
- Need to click multiple times

**Solution:**
This has been fixed in the latest version. If you still experience this:

1. **Clear browser cache**: Ctrl+Shift+Delete (Chrome/Edge) or Cmd+Shift+Delete (Mac)
2. **Hard refresh**: Ctrl+F5 (Windows) or Cmd+Shift+R (Mac)
3. **Check console**: Press F12, look for JavaScript errors

**Technical Details:**
The issue was caused by event propagation. Fixed by:
- Adding `stopPropagation()` to prevent event bubbling
- Properly handling the file input change event
- Syncing drag-and-drop with file input

### Issue 2: "Cannot convert undefined or null to object" Error

**Symptoms:**
- Analysis completes on backend
- Frontend shows "Analysis Failed" with this error
- Report is generated but not displayed

**Root Causes:**

1. **Backend response format mismatch**
2. **Missing fields in response**
3. **Network/CORS issues**

**Debugging Steps:**

1. **Check Browser Console** (F12 → Console tab)
   ```
   Look for:
   - "Received report:" log with the actual response
   - Any red error messages
   - Network errors
   ```

2. **Check Network Tab** (F12 → Network tab)
   ```
   - Find the /analyze request
   - Click on it
   - Check "Response" tab
   - Verify JSON structure
   ```

3. **Expected Response Format:**
   ```json
   {
     "spec_name": "my-api",
     "health_score": {
       "total": 74.3,
       "band": "Good",
       "category_scores": {
         "security": 48,
         "design": 82,
         "error_handling": 88,
         "documentation": 92,
         "governance": 94
       },
       "finding_counts": {
         "critical": 2,
         "high": 5,
         "medium": 8,
         "low": 3
       }
     },
     "findings": [...],
     "recommendations": [...]
   }
   ```

**Solutions:**

**A. If backend response is missing fields:**

Check backend version. Update to latest:
```bash
cd src/api
git pull
python app.py
```

**B. If response structure is different:**

The frontend now has defensive checks. Check console logs:
```javascript
// Look for these logs:
"Sending file to backend: filename.yaml"
"Response status: 200"
"Received report: {...}"
```

**C. If you see the report in console but UI shows error:**

This means the response structure doesn't match. Check:
1. Is `health_score` present?
2. Is `health_score.category_scores` an object?
3. Are all required fields present?

**Manual Fix:**
Open browser console and run:
```javascript
// This will show you what's missing
console.log('Report structure:', {
  hasHealthScore: !!currentReport?.health_score,
  hasCategoryScores: !!currentReport?.health_score?.category_scores,
  hasFindings: !!currentReport?.findings,
  hasRecommendations: !!currentReport?.recommendations
});
```

### Issue 3: Backend Not Running

**Symptoms:**
- "Failed to analyze specification. Please check if the backend server is running."
- Network errors in console

**Solution:**

1. **Start Backend:**
   ```bash
   cd src/api
   python app.py
   ```

2. **Verify Backend is Running:**
   ```bash
   curl http://localhost:8000/health
   ```

   Should return:
   ```json
   {
     "status": "ok",
     "rule_counts": {...}
   }
   ```

3. **Check Port:**
   - Backend should be on port 8000
   - Frontend should be on port 8080 (or different)
   - Don't use the same port!

### Issue 4: CORS Errors

**Symptoms:**
- Console shows: "Access to fetch at 'http://localhost:8000/analyze' from origin 'http://localhost:8080' has been blocked by CORS policy"

**Solution:**

1. **Verify backend CORS is enabled** (should be by default):
   ```python
   # In src/api/app.py
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. **Don't use file:// protocol:**
   - ❌ Opening index.html directly (file:///path/to/index.html)
   - ✅ Use HTTP server (http://localhost:8080)

3. **Restart backend** after CORS changes

### Issue 5: Results Not Displaying

**Symptoms:**
- Analysis completes
- No error shown
- Results section doesn't appear

**Debugging:**

1. **Check if results section is hidden:**
   ```javascript
   // In browser console
   document.getElementById('resultsSection').style.display
   // Should be 'block' after analysis
   ```

2. **Check for JavaScript errors:**
   - Open console (F12)
   - Look for red error messages
   - Check if displayResults() was called

3. **Verify report data:**
   ```javascript
   // In browser console
   console.log(currentReport);
   ```

**Solution:**
- Clear browser cache
- Hard refresh (Ctrl+F5)
- Check console for specific errors

### Issue 6: Export Not Working

**Symptoms:**
- Export JSON/Text buttons don't download files
- No error shown

**Solution:**

1. **Check browser download settings:**
   - Ensure downloads are allowed
   - Check if popup blocker is active

2. **Try different browser:**
   - Chrome/Edge usually work best
   - Firefox may have stricter security

3. **Check console for errors:**
   ```javascript
   // Should see download initiated
   ```

### Issue 7: Filters Not Working

**Symptoms:**
- Clicking severity filters doesn't filter findings
- All findings still visible

**Solution:**

1. **Check if findings have severity attribute:**
   ```javascript
   // In console after analysis
   document.querySelectorAll('.finding-item').forEach(item => {
     console.log(item.dataset.severity);
   });
   ```

2. **Verify filter buttons:**
   ```javascript
   // Should have data-severity attribute
   document.querySelectorAll('.filter-btn').forEach(btn => {
     console.log(btn.dataset.severity);
   });
   ```

## Debugging Checklist

When something goes wrong, check these in order:

- [ ] Backend is running (http://localhost:8000/health)
- [ ] Frontend is served via HTTP server (not file://)
- [ ] Browser console shows no errors (F12 → Console)
- [ ] Network tab shows successful API calls (F12 → Network)
- [ ] Response format matches expected structure
- [ ] All required fields are present in response
- [ ] JavaScript is enabled in browser
- [ ] No browser extensions blocking requests
- [ ] Correct API_BASE_URL in js/app.js
- [ ] Latest version of frontend code

## Getting Help

### 1. Collect Information

Before asking for help, gather:

```
Browser: Chrome 120 / Firefox 115 / Safari 17
OS: Windows 11 / macOS 14 / Linux
Backend Status: Running / Not Running
Error Message: [exact error text]
Console Logs: [copy from F12 console]
Network Response: [copy from F12 Network tab]
```

### 2. Check Logs

**Backend Logs:**
```bash
# Terminal running python app.py
# Look for errors or warnings
```

**Frontend Logs:**
```javascript
// Browser console (F12)
// Look for:
// - "Sending file to backend:"
// - "Response status:"
// - "Received report:"
// - Any error messages
```

### 3. Test Backend Directly

```bash
# Test with curl
curl -X POST http://localhost:8000/analyze \
  -F "file=@tests/sample_bad_spec.yaml" \
  -H "accept: application/json"

# Should return JSON report
```

### 4. Verify Frontend Files

```bash
# Check all files exist
ls -la frontend/
# Should show:
# - index.html
# - css/styles.css
# - js/app.js
# - README.md
```

## Advanced Debugging

### Enable Verbose Logging

Add to top of `js/app.js`:
```javascript
const DEBUG = true;

function debugLog(...args) {
    if (DEBUG) console.log('[DEBUG]', ...args);
}
```

Then use throughout code:
```javascript
debugLog('File selected:', file.name);
debugLog('Response received:', report);
```

### Test API Endpoints Manually

**Health Check:**
```bash
curl http://localhost:8000/health
```

**Analyze File:**
```bash
curl -X POST http://localhost:8000/analyze \
  -F "file=@myspec.yaml" \
  -H "accept: application/json" \
  | jq .
```

**Analyze Text:**
```bash
curl -X POST http://localhost:8000/analyze/text \
  -H "Content-Type: application/json" \
  -d '{
    "spec": {"openapi": "3.0.0", "info": {"title": "Test", "version": "1.0.0"}, "paths": {}},
    "name": "test"
  }' | jq .
```

### Check Response Structure

```javascript
// In browser console after analysis
function validateReport(report) {
    const checks = {
        'Has report': !!report,
        'Has health_score': !!report?.health_score,
        'Has total': typeof report?.health_score?.total === 'number',
        'Has band': typeof report?.health_score?.band === 'string',
        'Has category_scores': !!report?.health_score?.category_scores,
        'Has finding_counts': !!report?.health_score?.finding_counts,
        'Has findings': Array.isArray(report?.findings),
        'Has recommendations': Array.isArray(report?.recommendations)
    };
    
    console.table(checks);
    return Object.values(checks).every(v => v);
}

// Run after analysis
validateReport(currentReport);
```

## Still Having Issues?

1. **Update to latest version:**
   ```bash
   git pull
   ```

2. **Clear everything and restart:**
   ```bash
   # Stop backend (Ctrl+C)
   # Stop frontend (Ctrl+C)
   # Clear browser cache
   # Restart backend
   cd src/api && python app.py
   # Restart frontend
   cd frontend && python -m http.server 8080
   ```

3. **Try a different browser:**
   - Chrome (recommended)
   - Firefox
   - Edge

4. **Check for conflicting extensions:**
   - Disable ad blockers
   - Disable privacy extensions
   - Try incognito/private mode

---

**Last Updated**: 2026-03-12  
**Version**: 1.0.1