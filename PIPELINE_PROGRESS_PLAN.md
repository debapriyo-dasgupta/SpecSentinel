# Pipeline Progress UI - Implementation Plan

## 🎯 Goal
Replace the generic "waiting" screen with real-time pipeline stage progress showing:
- PLAN → ANALYZE → MATCH → SCORE → REPORT
- Visual indication when each stage completes
- Progress bar or stage indicators

## 📋 Current Behavior

**Frontend (frontend/static/js/app.js):**
- Shows generic "Analyzing..." message
- No stage-by-stage feedback
- User waits blindly for ~10 seconds

**Backend (src/api/app.py):**
- Logs pipeline stages to files
- No real-time communication with frontend
- Returns only final result

## 🔧 Proposed Solution

### Option 1: Server-Sent Events (SSE) - RECOMMENDED ⭐
**Pros:**
- Real-time updates from server to client
- Simple to implement
- Works with existing FastAPI
- No WebSocket complexity

**Cons:**
- One-way communication only (server → client)
- Requires new endpoint

### Option 2: WebSocket
**Pros:**
- Two-way communication
- Real-time updates

**Cons:**
- More complex to implement
- Overkill for one-way progress updates

### Option 3: Polling
**Pros:**
- Simplest to implement
- Works with existing endpoints

**Cons:**
- Not truly real-time
- More server load
- Requires storing progress state

## ✅ Recommended Approach: Server-Sent Events (SSE)

### Architecture:

```
Frontend (JavaScript)          Backend (FastAPI)
     |                              |
     |  POST /analyze/stream        |
     |----------------------------->|
     |                              |
     |  SSE: {"stage": "PLAN",      |
     |        "status": "started"}  |
     |<-----------------------------|
     |                              |
     |  SSE: {"stage": "PLAN",      |
     |        "status": "completed",|
     |        "duration": 0.123}    |
     |<-----------------------------|
     |                              |
     |  SSE: {"stage": "ANALYZE",   |
     |        "status": "started"}  |
     |<-----------------------------|
     |                              |
     |  ... (continue for all       |
     |       stages)                |
     |                              |
     |  SSE: {"stage": "COMPLETE",  |
     |        "result": {...}}      |
     |<-----------------------------|
```

## 📝 Implementation Steps

### Step 1: Backend Changes

#### 1.1 Create SSE Endpoint (src/api/app.py)
```python
from fastapi.responses import StreamingResponse
import asyncio
import json

@app.post("/analyze/stream")
async def analyze_spec_stream(file: UploadFile = File(...)):
    """Stream pipeline progress using Server-Sent Events"""
    
    async def event_generator():
        # Parse spec
        content = await file.read()
        spec = _parse_spec(content, file.filename)
        
        # Run pipeline with progress callbacks
        async for event in _run_pipeline_with_progress(spec, file.filename):
            yield f"data: {json.dumps(event)}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
```

#### 1.2 Modify Pipeline to Yield Progress (src/api/app.py)
```python
async def _run_pipeline_with_progress(spec: dict, spec_name: str):
    """Run pipeline and yield progress events"""
    
    # PLAN stage
    yield {"stage": "PLAN", "status": "started", "message": "Planning analysis..."}
    paths_count = len(spec.get('paths', {}))
    schemas_count = len(spec.get('components', {}).get('schemas', {}) or {})
    yield {"stage": "PLAN", "status": "completed", "paths": paths_count, "schemas": schemas_count}
    
    # ANALYZE stage
    yield {"stage": "ANALYZE", "status": "started", "message": "Extracting signals..."}
    extractor = OpenAPISignalExtractor(spec)
    signals = extractor.extract_all()
    yield {"stage": "ANALYZE", "status": "completed", "signals_count": len(signals)}
    
    # MATCH stage
    yield {"stage": "MATCH", "status": "started", "message": "Matching rules..."}
    matcher = RuleMatcher(store, n_results_per_signal=3)
    findings = matcher.match_signals(signals)
    yield {"stage": "MATCH", "status": "completed", "findings_count": len(findings)}
    
    # SCORE stage
    yield {"stage": "SCORE", "status": "started", "message": "Computing health score..."}
    health = compute_health_score(findings)
    yield {"stage": "SCORE", "status": "completed", "health_score": health.total}
    
    # REPORT stage
    yield {"stage": "REPORT", "status": "started", "message": "Generating report..."}
    report = build_report(spec_name, health, findings)
    yield {"stage": "REPORT", "status": "completed"}
    
    # Final result
    yield {"stage": "COMPLETE", "status": "completed", "result": report}
```

### Step 2: Frontend Changes

#### 2.1 Update HTML (frontend/templates/index.html)
```html
<!-- Replace loading message with progress UI -->
<div id="progress-container" style="display: none;">
    <h3>Analysis Progress</h3>
    <div class="pipeline-stages">
        <div class="stage" id="stage-plan">
            <span class="stage-icon">⏳</span>
            <span class="stage-name">PLAN</span>
            <span class="stage-status">Waiting...</span>
        </div>
        <div class="stage" id="stage-analyze">
            <span class="stage-icon">⏳</span>
            <span class="stage-name">ANALYZE</span>
            <span class="stage-status">Waiting...</span>
        </div>
        <div class="stage" id="stage-match">
            <span class="stage-icon">⏳</span>
            <span class="stage-name">MATCH</span>
            <span class="stage-status">Waiting...</span>
        </div>
        <div class="stage" id="stage-score">
            <span class="stage-icon">⏳</span>
            <span class="stage-name">SCORE</span>
            <span class="stage-status">Waiting...</span>
        </div>
        <div class="stage" id="stage-report">
            <span class="stage-icon">⏳</span>
            <span class="stage-name">REPORT</span>
            <span class="stage-status">Waiting...</span>
        </div>
    </div>
    <div class="progress-bar">
        <div class="progress-fill" id="progress-fill"></div>
    </div>
</div>
```

#### 2.2 Update JavaScript (frontend/static/js/app.js)
```javascript
async function analyzeSpec(file) {
    // Show progress container
    document.getElementById('progress-container').style.display = 'block';
    document.getElementById('results').style.display = 'none';
    
    // Create FormData
    const formData = new FormData();
    formData.append('file', file);
    
    // Use EventSource for SSE
    const eventSource = new EventSource('/api/analyze/stream');
    
    eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        updateProgress(data);
        
        if (data.stage === 'COMPLETE') {
            eventSource.close();
            displayResults(data.result);
        }
    };
    
    eventSource.onerror = (error) => {
        console.error('SSE Error:', error);
        eventSource.close();
        showError('Analysis failed');
    };
}

function updateProgress(data) {
    const stage = data.stage.toLowerCase();
    const stageElement = document.getElementById(`stage-${stage}`);
    
    if (data.status === 'started') {
        stageElement.querySelector('.stage-icon').textContent = '⏳';
        stageElement.querySelector('.stage-status').textContent = data.message;
        stageElement.classList.add('active');
    } else if (data.status === 'completed') {
        stageElement.querySelector('.stage-icon').textContent = '✅';
        stageElement.querySelector('.stage-status').textContent = 'Completed';
        stageElement.classList.remove('active');
        stageElement.classList.add('completed');
        
        // Update progress bar
        const stages = ['plan', 'analyze', 'match', 'score', 'report'];
        const currentIndex = stages.indexOf(stage);
        const progress = ((currentIndex + 1) / stages.length) * 100;
        document.getElementById('progress-fill').style.width = `${progress}%`;
    }
}
```

#### 2.3 Add CSS (frontend/static/css/styles.css)
```css
.pipeline-stages {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin: 20px 0;
}

.stage {
    display: flex;
    align-items: center;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 5px;
    background: #f9f9f9;
}

.stage.active {
    background: #e3f2fd;
    border-color: #2196F3;
}

.stage.completed {
    background: #e8f5e9;
    border-color: #4CAF50;
}

.stage-icon {
    font-size: 24px;
    margin-right: 10px;
}

.stage-name {
    font-weight: bold;
    min-width: 100px;
}

.stage-status {
    color: #666;
    margin-left: auto;
}

.progress-bar {
    width: 100%;
    height: 20px;
    background: #e0e0e0;
    border-radius: 10px;
    overflow: hidden;
    margin-top: 20px;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #4CAF50, #2196F3);
    transition: width 0.3s ease;
    width: 0%;
}
```

### Step 3: Frontend Proxy Update (frontend/app.py)
```python
@app.route('/api/analyze/stream', methods=['POST'])
def analyze_stream():
    """Proxy SSE stream from backend"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    files = {'file': (file.filename, file.stream, file.content_type)}
    
    # Stream response from backend
    response = requests.post(
        f'{BACKEND_API_URL}/analyze/stream',
        files=files,
        stream=True
    )
    
    def generate():
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                yield chunk
    
    return Response(generate(), mimetype='text/event-stream')
```

## 📊 Visual Mockup

```
┌─────────────────────────────────────────┐
│  Analysis Progress                      │
├─────────────────────────────────────────┤
│                                         │
│  ✅ PLAN          Completed             │
│  ✅ ANALYZE       Completed             │
│  ⏳ MATCH         Matching rules...     │
│  ⏳ SCORE         Waiting...            │
│  ⏳ REPORT        Waiting...            │
│                                         │
│  ▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░░░░░░░  60%   │
│                                         │
└─────────────────────────────────────────┘
```

## 🎨 Alternative: Simpler Progress Bar Only

If SSE is too complex, we can use a simpler approach:

### Simpler Option: Estimated Progress Bar
```javascript
// Show progress bar with estimated timing
function showEstimatedProgress() {
    const stages = [
        { name: 'PLAN', duration: 100 },
        { name: 'ANALYZE', duration: 1000 },
        { name: 'MATCH', duration: 8000 },
        { name: 'SCORE', duration: 100 },
        { name: 'REPORT', duration: 100 }
    ];
    
    let elapsed = 0;
    const total = stages.reduce((sum, s) => sum + s.duration, 0);
    
    stages.forEach((stage, index) => {
        setTimeout(() => {
            updateStageUI(stage.name, 'started');
        }, elapsed);
        
        elapsed += stage.duration;
        
        setTimeout(() => {
            updateStageUI(stage.name, 'completed');
            const progress = ((index + 1) / stages.length) * 100;
            updateProgressBar(progress);
        }, elapsed);
    });
}
```

## 🔍 Comparison

| Feature | SSE (Recommended) | Estimated Progress |
|---------|-------------------|-------------------|
| Real-time | ✅ Yes | ❌ No (simulated) |
| Accurate | ✅ Yes | ⚠️ Approximate |
| Complexity | ⚠️ Medium | ✅ Low |
| Backend changes | ✅ Required | ❌ None |
| User experience | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

## 📋 Files to Modify

### Backend:
1. `src/api/app.py` - Add SSE endpoint and progress generator
2. `src/engine/reporter.py` - (Optional) Add progress callbacks

### Frontend:
1. `frontend/templates/index.html` - Add progress UI
2. `frontend/static/js/app.js` - Add SSE handling
3. `frontend/static/css/styles.css` - Add progress styles
4. `frontend/app.py` - Add SSE proxy route

## ⏱️ Estimated Implementation Time

- **SSE Approach:** 2-3 hours
- **Estimated Progress:** 30 minutes

## 🎯 Recommendation

**Use Server-Sent Events (SSE)** for:
- ✅ Real-time accurate progress
- ✅ Better user experience
- ✅ Professional appearance
- ✅ Actual stage completion feedback

This provides the best user experience and shows exactly what's happening in the backend!

## 🚀 Next Steps

1. Review this plan
2. Choose approach (SSE recommended)
3. Implement backend changes first
4. Test SSE endpoint
5. Implement frontend changes
6. Test end-to-end
7. Deploy

Would you like me to proceed with the SSE implementation?