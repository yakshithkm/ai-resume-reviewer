# Security Features Testing Guide

This guide helps you manually verify the security features in the AI Resume Reviewer application.

## Prerequisites

- Server running at http://127.0.0.1:5000
- Browser DevTools open (F12)
- Console tab visible

## Test 1: CSRF Protection ✓

### Verify CSRF Token is Sent

1. **Upload a resume normally**
   - Select a resume + job description
   - Click "Analyze Resume"
   - Check Console for: `✓ CSRF token found and will be sent: ...`
   - Request should succeed

### Test Missing CSRF Token (Advanced)

1. **Open DevTools Console**
2. **Remove CSRF meta tag temporarily:**
   ```javascript
   document.querySelector('meta[name="csrf-token"]').remove();
   ```
3. **Try uploading again**
4. **Expected result:** Should see warning in console and request may fail
5. **Refresh page to restore CSRF token**

## Test 2: Rate Limiting ⏱

### Trigger Rate Limit (10 uploads per minute)

1. **Prepare small test files**
   - Use the minimal_resume.txt and job_description.txt from test_edge_cases/

2. **Upload rapidly:**
   - Upload the same files 10-12 times quickly
   - Click Analyze, wait 2 seconds, repeat

3. **Expected results:**
   - First 10 uploads: Should process normally
   - 11th+ upload within 1 minute: Should show error
   - Error message: "Too many requests. Please wait a moment and try again."
   - Console log: `⚠ Rate limit exceeded - too many requests`
   - HTTP Status: 429

4. **Wait 60 seconds** and try again - should work

### Check Footer Indicators

Look at the bottom of the page:
- 🛡 CSRF Protection Enabled (green shield)
- 🏎 Rate Limiting Active (orange gauge)

## Test 3: PDF Export (Both Themes)

### Light Theme Export

1. **Ensure light theme is active** (toggle at top right if needed)
2. **Upload and analyze a resume**
3. **Click "Export PDF"**
4. **Verify:**
   - PDF downloads successfully
   - Charts are visible and colored
   - Suggestions section renders with clean bullet points
   - No `[object Object]` or strange text

### Dark Theme Export

1. **Toggle to dark theme** (moon icon)
2. **Upload and analyze the same resume**
3. **Click "Export PDF"**
4. **Verify:**
   - PDF is exported in light colors (not dark background)
   - Charts render correctly
   - Text is readable

## Test 4: Batch Processing

### Upload Multiple Resumes

1. **Select 2-3 resume files** (Ctrl+Click or Shift+Click in file picker)
2. **Select 1 job description**
3. **Click "Analyze Resume"**
4. **Expected results:**
   - Progress bar shows upload
   - Batch Analysis Summary appears
   - Shows count of resumes processed
   - Displays per-file match score
   - Shows matching/missing skills for each

## Console Messages to Look For

### Successful Upload (CSRF OK)
```
✓ CSRF token found and will be sent: eyJ...
Response status: 200
Response data: {analysis: {...}}
```

### Rate Limit Hit
```
⚠ Rate limit exceeded - too many requests
Response status: 429
```

### CSRF Failure
```
✖ CSRF validation failed
Response status: 400
```

## Troubleshooting

### CSRF token not found
- **Cause:** Page cached or meta tag missing
- **Fix:** Hard refresh (Ctrl+Shift+R)

### Rate limit not triggering
- **Cause:** Requests too slow or Redis not configured
- **Fix:** Upload faster (within 60 seconds) or check RATELIMIT_STORAGE_URI in .env

### PDF export fails
- **Cause:** jsPDF library not loaded
- **Fix:** Check browser console for script loading errors, refresh page

## Expected Security Behavior

| Test | Expected Outcome |
|------|------------------|
| Normal upload with CSRF | ✅ Success |
| Upload without CSRF token | ❌ 400 Bad Request |
| 10 uploads in 60 seconds | ✅ All succeed |
| 11th upload in 60 seconds | ❌ 429 Too Many Requests |
| Wait 60 seconds, retry | ✅ Success |
| PDF export light theme | ✅ Clean PDF with light colors |
| PDF export dark theme | ✅ Clean PDF (charts in light colors) |
| Batch upload 3 resumes | ✅ Batch summary with all 3 |

## Notes

- Rate limits are per IP address
- CSRF tokens are session-based
- Rate limit window is 60 seconds (rolling)
- Maximum 10 uploads/minute for single endpoint
- Maximum 5 uploads/minute for batch endpoint
