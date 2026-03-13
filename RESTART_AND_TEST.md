# Restart and Test Pipeline Progress

## Quick Start Guide

### Step 1: Stop Running Servers

If you have servers running, stop them:
- Press `Ctrl+C` in both terminal windows

### Step 2: Restart Backend

```powershell
# In Terminal 1
cd c:\Users\DebapriyoDasgupta\IBM_Hackathon_26\SpecSentinal_IBM_Hackathon
python run_app.py
```

Wait for:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 3: Restart Frontend

```powershell
# In Terminal 2 (new terminal)
cd c:\Users\DebapriyoDasgupta\IBM_Hackathon_26\SpecSentinal_IBM_Hackathon\frontend
python app.py
```

Wait for:
```
 * Running on http://0.0.0.0:5000
```

### Step 4: Test Real-Time Progress

1. **Open Browser**: http://localhost:5000

2. **Upload Test File**: 
   - Use `tests/petStoreSwagger.json` or any OpenAPI spec
   - Click "Choose File" or drag & drop

3. **Click "Analyze Specification"**

4. **Watch the Magic! ✨**
   
   You should see:
   ```
   ⏳ PLAN → ⏳ ANALYZE → ⏳ MATCH → ⏳ SCORE → ⏳ REPORT
   ```
   
   Then in real-time:
   ```
   🔄 PLAN (pulsing, active)
   ↓
   ✅ PLAN (0.12s) → 🔄 ANALYZE (pulsing)
   ↓
   ✅ PLAN (0.12s) → ✅ ANALYZE (0.45s) → 🔄 MATCH (pulsing)
   ↓
   ... continues through all stages ...
   ↓
   ✅ All stages complete!
   ```

5. **Progress Bar**: Should fill from 0% to 100% as stages complete

6. **Final Result**: Health report displays when complete

## What to Look For

### ✅ Success Indicators

1. **Visual Progress**:
   - Stages light up one by one
   - Active stage has pulsing animation
   - Completed stages show green checkmark ✅
   - Duration appears under each completed stage

2. **Progress Bar**:
   - Fills gradually (not instantly)
   - Smooth animation
   - Reaches 100% when all stages done

3. **Messages**:
   - "Planning analysis..."
   - "Extracting signals from spec..."
   - "Matching rules from vector database..."
   - "Computing health score..."
   - "Generating report..."

4. **Final Display**:
   - Health score appears
   - Findings are listed
   - No errors in browser console

### ❌ Troubleshooting

**Problem**: Generic "please wait" message, no progress stages
- **Solution**: Hard refresh browser (Ctrl+Shift+R)
- **Reason**: Browser cached old JavaScript

**Problem**: Stages don't update
- **Solution**: Check browser console (F12) for errors
- **Check**: Backend logs for SSE endpoint errors

**Problem**: Connection error
- **Solution**: Verify both servers are running
- **Check**: http://localhost:8000/health (backend)
- **Check**: http://localhost:5000/api/health (frontend)

**Problem**: Stages skip or jump
- **Solution**: Normal if stages complete very quickly
- **Note**: Small files process faster than large ones

## Verify Logs

### Backend Logs
Check `logs/specsentinel.pipeline.log`:
```
2026-03-13 17:30:15 [INFO] [PLAN] Starting... spec_name=petstore.json
2026-03-13 17:30:15 [INFO] [PLAN] Completed in 0.123s paths=10 schemas=5
2026-03-13 17:30:15 [INFO] [ANALYZE] Starting... spec_name=petstore.json
2026-03-13 17:30:16 [INFO] [ANALYZE] Completed in 0.456s signals_count=25
...
```

### Frontend Logs
Check terminal output:
```
INFO:frontend.app:Proxying streaming analyze request for file: petstore.json
INFO:frontend.app:Backend streaming response status: 200
```

## Browser Console

Open Developer Tools (F12) → Console tab

**Expected Output**:
```javascript
Sending file to backend with SSE: petstore.json
Response status: 200
SSE event: {stage: "PLAN", status: "started", message: "Planning analysis..."}
SSE event: {stage: "PLAN", status: "completed", duration: 0.123, paths: 10, schemas: 5}
SSE event: {stage: "ANALYZE", status: "started", message: "Extracting signals..."}
...
SSE event: {stage: "COMPLETE", status: "completed", result: {...}}
Received final report: {...}
```

## Performance Notes

- **Small specs** (< 100 lines): ~2-5 seconds total
- **Medium specs** (100-500 lines): ~5-15 seconds total
- **Large specs** (> 500 lines): ~15-30 seconds total

Each stage typically takes:
- PLAN: 0.1-0.5s
- ANALYZE: 0.5-2s
- MATCH: 1-5s (depends on vector DB)
- SCORE: 0.1-0.5s
- REPORT: 0.1-0.5s
- AI-ENHANCE: 2-10s (if LLM available)

## Success Criteria

✅ All stages show in sequence  
✅ Active stage has pulsing animation  
✅ Completed stages show checkmark and duration  
✅ Progress bar fills smoothly  
✅ Messages update for each stage  
✅ Final report displays correctly  
✅ No errors in console or logs  

## Next Steps After Testing

If everything works:
1. ✅ Mark "Test end-to-end pipeline progress" as complete
2. 📝 Document any issues found
3. 🎉 Celebrate the real-time progress feature!

If issues occur:
1. Check browser console for JavaScript errors
2. Check backend logs for Python errors
3. Verify both servers restarted with new code
4. Try hard refresh (Ctrl+Shift+R)
5. Test with different spec files

---

**Ready to test?** Follow the steps above and watch your pipeline come to life! 🚀