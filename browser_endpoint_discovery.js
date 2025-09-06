// CoolCode Endpoint Discovery Script
// Run this in the browser console while on https://coolcode-hacker-34c5455cd908.herokuapp.com/ui/
// This will help find the exact working endpoint for score updates

console.log("🔍 Starting CoolCode Endpoint Discovery...");

// Get the ACCESS_TOKEN from localStorage
const token = localStorage.getItem('ACCESS_TOKEN');
console.log("🔑 ACCESS_TOKEN:", token ? token.substring(0, 20) + "..." : "NOT FOUND");

if (!token) {
    console.error("❌ ACCESS_TOKEN not found in localStorage. Please log in first!");
    console.log("💡 Try: Go to https://coolcode-hacker-34c5455cd908.herokuapp.com/ui/ and log in with:");
    console.log("   Username: CX8de3ce71-3cbTY");
    console.log("   Password: Gunraj@260905");
} else {
    console.log("✅ ACCESS_TOKEN found! Starting endpoint discovery...");
}

// Base URL
const baseUrl = "https://coolcode-hacker-34c5455cd908.herokuapp.com";
const targetUser = "98ixul"; // Caroline
const testAssignmentId = 1;
const testScore = 100;

// Test different endpoints and methods
const endpointsToTest = [
    // UI Profile endpoints
    { url: `${baseUrl}/ui/profile/${targetUser}`, method: "POST", type: "form" },
    { url: `${baseUrl}/ui/profile/${targetUser}`, method: "POST", type: "json" },
    { url: `${baseUrl}/ui/profile/${targetUser}/score`, method: "POST", type: "form" },
    { url: `${baseUrl}/ui/profile/${targetUser}/score`, method: "POST", type: "json" },
    
    // UI API endpoints
    { url: `${baseUrl}/ui/api/assignment/score`, method: "POST", type: "form" },
    { url: `${baseUrl}/ui/api/assignment/score`, method: "POST", type: "json" },
    { url: `${baseUrl}/ui/api/score/update`, method: "POST", type: "form" },
    { url: `${baseUrl}/ui/api/score/update`, method: "POST", type: "json" },
    
    // Assignment specific endpoints
    { url: `${baseUrl}/ui/assignment/${testAssignmentId}/score`, method: "POST", type: "form" },
    { url: `${baseUrl}/ui/assignment/${testAssignmentId}/score`, method: "POST", type: "json" },
    { url: `${baseUrl}/ui/assignment/score`, method: "POST", type: "form" },
    { url: `${baseUrl}/ui/assignment/score`, method: "POST", type: "json" },
    
    // User specific endpoints
    { url: `${baseUrl}/ui/user/${targetUser}/assignment/${testAssignmentId}`, method: "POST", type: "form" },
    { url: `${baseUrl}/ui/user/${targetUser}/assignment/${testAssignmentId}`, method: "POST", type: "json" },
    { url: `${baseUrl}/ui/user/${targetUser}/score`, method: "POST", type: "form" },
    { url: `${baseUrl}/ui/user/${targetUser}/score`, method: "POST", type: "json" },
    
    // Direct API endpoints
    { url: `${baseUrl}/api/assignment/score`, method: "POST", type: "json" },
    { url: `${baseUrl}/api/api/assignment/score`, method: "POST", type: "json" },
    { url: `${baseUrl}/api/score`, method: "POST", type: "json" },
    { url: `${baseUrl}/api/user/${targetUser}/score`, method: "POST", type: "json" },
    
    // PUT methods
    { url: `${baseUrl}/ui/profile/${targetUser}`, method: "PUT", type: "form" },
    { url: `${baseUrl}/ui/profile/${targetUser}`, method: "PUT", type: "json" },
    { url: `${baseUrl}/ui/api/assignment/score`, method: "PUT", type: "json" },
    
    // PATCH methods  
    { url: `${baseUrl}/ui/profile/${targetUser}`, method: "PATCH", type: "json" },
    { url: `${baseUrl}/ui/api/assignment/score`, method: "PATCH", type: "json" }
];

// Function to test an endpoint
async function testEndpoint(endpoint) {
    try {
        let body, headers;
        
        if (endpoint.type === "form") {
            // Form data
            const formData = new FormData();
            formData.append('username', targetUser);
            formData.append('assignmentId', testAssignmentId.toString());
            formData.append('score', testScore.toString());
            body = formData;
            headers = {
                'ACCESS_TOKEN': token
            };
        } else {
            // JSON data
            body = JSON.stringify({
                username: targetUser,
                assignmentId: testAssignmentId,
                score: testScore
            });
            headers = {
                'Content-Type': 'application/json',
                'ACCESS_TOKEN': token,
                'Authorization': `Bearer ${token}`
            };
        }
        
        const response = await fetch(endpoint.url, {
            method: endpoint.method,
            headers: headers,
            body: body
        });
        
        const responseText = await response.text();
        
        return {
            endpoint: endpoint,
            status: response.status,
            success: response.ok,
            response: responseText.substring(0, 200),
            headers: Object.fromEntries(response.headers.entries())
        };
        
    } catch (error) {
        return {
            endpoint: endpoint,
            status: 'ERROR',
            success: false,
            error: error.message
        };
    }
}

// Function to run all tests
async function runEndpointDiscovery() {
    console.log("🚀 Testing endpoints...");
    const results = [];
    
    for (let i = 0; i < endpointsToTest.length; i++) {
        const endpoint = endpointsToTest[i];
        console.log(`Testing ${i + 1}/${endpointsToTest.length}: ${endpoint.method} ${endpoint.url} (${endpoint.type})`);
        
        const result = await testEndpoint(endpoint);
        results.push(result);
        
        // Log immediate results
        if (result.success) {
            console.log(`✅ SUCCESS: ${endpoint.method} ${endpoint.url} (${endpoint.type}) - Status: ${result.status}`);
            console.log(`   Response: ${result.response}`);
        } else if (result.status === 'ERROR') {
            console.log(`❌ ERROR: ${endpoint.method} ${endpoint.url} (${endpoint.type}) - ${result.error}`);
        } else {
            console.log(`⚠️ FAILED: ${endpoint.method} ${endpoint.url} (${endpoint.type}) - Status: ${result.status}`);
        }
        
        // Small delay to be nice to the server
        await new Promise(resolve => setTimeout(resolve, 200));
    }
    
    // Summary
    console.log("\n" + "=".repeat(80));
    console.log("📊 ENDPOINT DISCOVERY SUMMARY");
    console.log("=".repeat(80));
    
    const successfulEndpoints = results.filter(r => r.success);
    const failedEndpoints = results.filter(r => !r.success);
    
    console.log(`✅ Successful endpoints: ${successfulEndpoints.length}`);
    successfulEndpoints.forEach(result => {
        const ep = result.endpoint;
        console.log(`   ${ep.method} ${ep.url} (${ep.type}) - Status: ${result.status}`);
    });
    
    console.log(`\n❌ Failed endpoints: ${failedEndpoints.length}`);
    
    if (successfulEndpoints.length > 0) {
        console.log("\n🎯 RECOMMENDED ENDPOINT TO USE:");
        const best = successfulEndpoints[0];
        console.log(`   Method: ${best.endpoint.method}`);
        console.log(`   URL: ${best.endpoint.url}`);
        console.log(`   Data Type: ${best.endpoint.type}`);
        console.log(`   Status: ${best.status}`);
        console.log(`   Response: ${best.response}`);
        
        // Generate code for the working endpoint
        console.log("\n📝 WORKING CODE:");
        if (best.endpoint.type === "form") {
            console.log(`
const formData = new FormData();
formData.append('username', '${targetUser}');
formData.append('assignmentId', '1'); // Change as needed
formData.append('score', '100');

fetch('${best.endpoint.url}', {
    method: '${best.endpoint.method}',
    headers: {
        'ACCESS_TOKEN': localStorage.getItem('ACCESS_TOKEN')
    },
    body: formData
}).then(response => response.text()).then(data => console.log(data));
            `);
        } else {
            console.log(`
fetch('${best.endpoint.url}', {
    method: '${best.endpoint.method}',
    headers: {
        'Content-Type': 'application/json',
        'ACCESS_TOKEN': localStorage.getItem('ACCESS_TOKEN'),
        'Authorization': 'Bearer ' + localStorage.getItem('ACCESS_TOKEN')
    },
    body: JSON.stringify({
        username: '${targetUser}',
        assignmentId: 1, // Change as needed
        score: 100
    })
}).then(response => response.text()).then(data => console.log(data));
            `);
        }
    } else {
        console.log("\n😞 No working endpoints found. Try:");
        console.log("1. Make sure you're logged in");
        console.log("2. Check the Network tab in dev tools while manually changing a score");
        console.log("3. Look for any CSRF tokens or additional headers needed");
    }
    
    return results;
}

// Also add a function to check current scores
async function checkCurrentScores() {
    console.log("\n🔍 Checking current scores for user: " + targetUser);
    
    const checkEndpoints = [
        `${baseUrl}/ui/profile/${targetUser}`,
        `${baseUrl}/ui/api/user/${targetUser}`,
        `${baseUrl}/api/user/${targetUser}`,
        `${baseUrl}/ui/user/${targetUser}`,
        `${baseUrl}/api/scores/${targetUser}`
    ];
    
    for (const endpoint of checkEndpoints) {
        try {
            const response = await fetch(endpoint, {
                headers: {
                    'ACCESS_TOKEN': token,
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (response.ok) {
                const data = await response.text();
                console.log(`✅ ${endpoint}:`);
                console.log(`   ${data.substring(0, 300)}...`);
            } else {
                console.log(`❌ ${endpoint}: Status ${response.status}`);
            }
        } catch (error) {
            console.log(`❌ ${endpoint}: Error - ${error.message}`);
        }
    }
}

// Run the discovery
if (token) {
    console.log("Starting in 2 seconds...");
    setTimeout(async () => {
        await checkCurrentScores();
        const results = await runEndpointDiscovery();
        
        console.log("\n🎯 Copy the successful endpoint details and send them back!");
        console.log("📋 Results stored in variable 'endpointResults'");
        window.endpointResults = results;
    }, 2000);
} else {
    console.log("Please log in first and then run this script again.");
}

// Helper function to test a single assignment update
window.testSingleUpdate = function(assignmentId = 1, score = 100) {
    const workingEndpoint = window.endpointResults?.find(r => r.success);
    if (!workingEndpoint) {
        console.log("No working endpoint found yet. Run the discovery first.");
        return;
    }
    
    console.log(`Testing assignment ${assignmentId} with score ${score}...`);
    
    if (workingEndpoint.endpoint.type === "form") {
        const formData = new FormData();
        formData.append('username', targetUser);
        formData.append('assignmentId', assignmentId.toString());
        formData.append('score', score.toString());
        
        fetch(workingEndpoint.endpoint.url, {
            method: workingEndpoint.endpoint.method,
            headers: { 'ACCESS_TOKEN': token },
            body: formData
        }).then(response => response.text()).then(data => {
            console.log(`Result: ${data}`);
        });
    } else {
        fetch(workingEndpoint.endpoint.url, {
            method: workingEndpoint.endpoint.method,
            headers: {
                'Content-Type': 'application/json',
                'ACCESS_TOKEN': token,
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                username: targetUser,
                assignmentId: assignmentId,
                score: score
            })
        }).then(response => response.text()).then(data => {
            console.log(`Result: ${data}`);
        });
    }
};

console.log("🔧 Helper function 'testSingleUpdate(assignmentId, score)' is available for manual testing");
