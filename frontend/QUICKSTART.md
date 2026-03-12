# SpecSentinel Frontend - Quick Start Guide

Get up and running with the SpecSentinel frontend in 5 minutes!

## 🚀 Step-by-Step Setup

### Step 1: Start the Backend Server

```bash
# From project root directory
cd src/api
python app.py
```

You should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

✅ Backend is now running at `http://localhost:8000`

### Step 2: Start the Frontend Server

Open a **new terminal** window:

```bash
# From project root directory
cd frontend

# Start a simple HTTP server
python -m http.server 8080
```

You should see:
```
Serving HTTP on :: port 8080 (http://[::]:8080/) ...
```

✅ Frontend is now running at `http://localhost:8080`

### Step 3: Open in Browser

Open your web browser and navigate to:
```
http://localhost:8080
```

You should see the SpecSentinel interface with:
- 🛡️ SpecSentinel logo and header
- Upload File and Paste Spec tabs
- Analyze Specification button

## 📝 Test the Application

### Option A: Upload a Test File

1. Click the **"Upload File"** tab (default)
2. Click **"Choose File"** or drag and drop
3. Select `tests/sample_bad_spec.yaml` from the project
4. Click **"Analyze Specification"**
5. Wait 2-5 seconds for analysis
6. Review the health report!

### Option B: Paste a Spec

1. Click the **"Paste Spec"** tab
2. Copy this minimal OpenAPI spec:

```yaml
openapi: 3.0.0
info:
  title: Test API
  version: 1.0.0
paths:
  /users:
    get:
      summary: Get users
      responses:
        '200':
          description: Success
```

3. Paste it into the text area
4. Click **"Analyze Specification"**
5. Review the results!

## 🎯 What to Expect

After analysis, you'll see:

1. **Health Score** (0-100)
   - Animated circular progress
   - Color-coded band (Poor/Moderate/Good/Excellent)
   - Finding counts by severity

2. **Category Breakdown**
   - Security, Design, Error Handling, Documentation, Governance
   - Individual scores with progress bars

3. **Findings List**
   - Detailed issues with severity badges
   - Evidence and fix guidance
   - Filterable by severity

4. **Priority Recommendations**
   - Top actions to improve your API

5. **Export Options**
   - Download JSON report
   - Download text report

## 🔧 Troubleshooting

### Backend Not Running?

**Error**: "Failed to analyze specification. Please check if the backend server is running."

**Fix**:
```bash
# Terminal 1: Start backend
cd src/api
python app.py
```

### Port Already in Use?

**Error**: "Address already in use"

**Fix**: Use a different port
```bash
# Try port 8081 instead
python -m http.server 8081

# Then open: http://localhost:8081
```

### CORS Errors?

**Error**: Browser console shows CORS errors

**Fix**: Make sure you're using an HTTP server, not opening the file directly (file://)

### Can't Find Test File?

The test file is located at:
```
SpecSentinal_IBM_Hackathon/tests/sample_bad_spec.yaml
```

## 🎨 Features to Try

1. **Drag & Drop**: Drag a YAML/JSON file onto the upload area
2. **Severity Filters**: Click Critical/High/Medium/Low to filter findings
3. **Export Reports**: Download JSON or text format reports
4. **Multiple Analyses**: Click "Analyze New Spec" to test another file

## 📊 Understanding Your Results

### Health Score Bands

| Score | Band | Meaning |
|-------|------|---------|
| 86-100 | ✅ Excellent | Best practices followed |
| 71-85 | 🟢 Good | Minor issues only |
| 41-70 | 🟡 Moderate | Needs improvement |
| 0-40 | 🔴 Poor | Critical issues found |

### Severity Levels

- **🔴 Critical**: Security vulnerabilities, must fix immediately
- **🟠 High**: Important issues, fix soon
- **🟡 Medium**: Should be addressed
- **🔵 Low**: Nice-to-have improvements

## 🎓 Next Steps

1. **Analyze Your Own API**
   - Upload your OpenAPI specification
   - Review findings and recommendations
   - Implement suggested fixes

2. **Explore Categories**
   - Check each category score
   - Understand what affects each category
   - Prioritize improvements

3. **Export Reports**
   - Share JSON reports with your team
   - Use text reports for documentation
   - Track improvements over time

4. **Customize**
   - Edit `js/app.js` to change API endpoint
   - Modify `css/styles.css` to match your brand
   - Extend functionality as needed

## 💡 Pro Tips

1. **Use the Paste Method** for quick tests and iterations
2. **Filter by Critical/High** to focus on important issues first
3. **Export JSON** to integrate with CI/CD pipelines
4. **Check Category Breakdown** to understand where to focus efforts
5. **Read Fix Guidance** for each finding to learn best practices

## 🆘 Need Help?

1. **Check Backend Logs**: Look at the terminal running `python app.py`
2. **Check Browser Console**: Press F12 → Console tab
3. **Test Backend Directly**: 
   ```bash
   curl http://localhost:8000/health
   ```
4. **Review Documentation**: See `frontend/README.md` for detailed docs

## ✅ Success Checklist

- [ ] Backend server running on port 8000
- [ ] Frontend server running on port 8080
- [ ] Browser opened to http://localhost:8080
- [ ] Test file analyzed successfully
- [ ] Health score displayed
- [ ] Findings visible
- [ ] Export buttons working

---

**Ready to analyze your APIs!** 🚀

For more details, see [frontend/README.md](README.md)