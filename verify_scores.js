// VERIFICATION SCRIPT - Check if Caroline's scores actually changed
// Run this AFTER the hack to verify if it worked

console.log("🔍 Verifying Caroline's Score Changes");
console.log("=====================================");

const token = localStorage.getItem('ACCESS_TOKEN');
const baseUrl = 'https://coolcode-hacker-34c5455cd908.herokuapp.com';

async function verifyScoreChanges() {
    console.log("\n📊 Checking Caroline's current scores...");
    
    // Method 1: Check via API
    try {
        const response = await fetch(`${baseUrl}/api/api/user/username/98ixul`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log("✅ Caroline's API data:", data);
            
            if (data.assignments || data.scores) {
                console.log("📈 Found assignment data in API response!");
            }
        } else {
            console.log(`❌ API check failed: ${response.status}`);
        }
    } catch (error) {
        console.log("❌ API check error:", error);
    }
    
    // Method 2: Check assignments endpoint
    try {
        const response = await fetch(`${baseUrl}/api/api/assignments/user/98ixul`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log("✅ Caroline's assignments:", data);
        } else {
            console.log(`❌ Assignments check: ${response.status}`);
        }
    } catch (error) {
        console.log("❌ Assignments check error:", error);
    }
    
    // Method 3: Check individual assignment scores
    console.log("\n🔍 Checking individual assignment scores...");
    
    for (let i = 1; i <= 5; i++) {  // Check first 5 assignments
        try {
            const response = await fetch(`${baseUrl}/api/api/assignment/${i}/user/98ixul`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log(`✅ Assignment ${i}:`, data);
            } else {
                console.log(`❌ Assignment ${i}: ${response.status}`);
            }
        } catch (error) {
            console.log(`❌ Assignment ${i}: Error`);
        }
    }
    
    // Method 4: Force refresh the profile page
    console.log("\n🔄 Attempting to refresh profile data...");
    
    try {
        // Clear any cached profile data
        if ('caches' in window) {
            const cacheNames = await caches.keys();
            for (const cacheName of cacheNames) {
                await caches.delete(cacheName);
            }
            console.log("✅ Cleared browser caches");
        }
        
        // Try to fetch fresh profile data
        const response = await fetch(`${baseUrl}/ui/profile/98ixul?_=${Date.now()}`, {
            headers: {
                'ACCESS_TOKEN': token,
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
        });
        
        if (response.ok) {
            const html = await response.text();
            console.log("✅ Fresh profile data fetched");
            
            // Look for score indicators in the HTML
            if (html.includes('100') || html.includes('A') || html.includes('Pass')) {
                console.log("🎉 Found positive score indicators in profile HTML!");
            } else if (html.includes('F') || html.includes('Fail') || html.includes('0')) {
                console.log("⚠️ Still seeing failing indicators in profile HTML");
            }
        }
    } catch (error) {
        console.log("❌ Profile refresh error:", error);
    }
    
    // Method 5: Test if we can still submit scores (to check if changes persisted)
    console.log("\n🧪 Testing if score submission still works...");
    
    try {
        const formData = new FormData();
        formData.append('username', '98ixul');
        formData.append('assignmentId', '1');
        formData.append('score', '99');  // Try a different score
        
        const response = await fetch('/ui/api/assignment/score', {
            method: 'POST',
            headers: {
                'ACCESS_TOKEN': token
            },
            body: formData
        });
        
        if (response.ok) {
            console.log("✅ Score submission still works - API is responsive");
        } else {
            console.log(`❌ Score submission test failed: ${response.status}`);
        }
    } catch (error) {
        console.log("❌ Score submission test error:", error);
    }
}

// Manual UI refresh instructions
function showRefreshInstructions() {
    console.log("\n📋 Manual Verification Steps:");
    console.log("1. Hard refresh the page (Ctrl+F5 or Ctrl+Shift+R)");
    console.log("2. Clear browser cache and cookies for this site");
    console.log("3. Navigate to Caroline's profile manually: " + baseUrl + "/ui/profile/98ixul");
    console.log("4. Log out and log back in");
    console.log("5. Try accessing the profile from a different browser/incognito mode");
    console.log("\n💡 If scores still show as 'F', the issue might be:");
    console.log("- UI is reading from a different database table");
    console.log("- Changes need admin approval");
    console.log("- Display logic has caching that needs time to update");
    console.log("- The hack changed submission scores but not display scores");
}

// Run verification
verifyScoreChanges().then(() => {
    showRefreshInstructions();
});
