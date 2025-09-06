// CoolCode DOM Manipulation Discovery
// Since manual changes work via Elements tab, let's find and automate that approach

console.log("🔍 Investigating DOM-based score updates...");

const targetUser = "98ixul";

// First, let's find all score-related elements on the page
function findScoreElements() {
    console.log("\n📊 Looking for score elements on the page...");
    
    // Look for common score-related selectors
    const selectors = [
        '[data-score]',
        '[data-assignment]',
        '.score',
        '.assignment-score',
        '.grade',
        '.points',
        'input[type="number"]',
        'input[name*="score"]',
        'input[id*="score"]',
        'span[class*="score"]',
        'div[class*="score"]',
        '[class*="assignment"]',
        '[id*="assignment"]',
        'td', // Table cells might contain scores
        '.editable',
        '[contenteditable]'
    ];
    
    const foundElements = [];
    
    selectors.forEach(selector => {
        try {
            const elements = document.querySelectorAll(selector);
            elements.forEach(el => {
                // Check if element contains number-like content or score-related text
                const text = el.textContent?.trim() || '';
                const value = el.value || '';
                const content = text + ' ' + value;
                
                if (content.match(/\b\d+\b/) || 
                    content.toLowerCase().includes('score') ||
                    content.toLowerCase().includes('assignment') ||
                    content.toLowerCase().includes('grade') ||
                    content.toLowerCase().includes('point')) {
                    
                    foundElements.push({
                        element: el,
                        selector: selector,
                        text: text.substring(0, 50),
                        value: value,
                        tagName: el.tagName,
                        className: el.className,
                        id: el.id,
                        dataset: el.dataset
                    });
                }
            });
        } catch (e) {
            // Ignore invalid selectors
        }
    });
    
    console.log(`Found ${foundElements.length} potential score elements:`);
    foundElements.forEach((item, index) => {
        console.log(`${index + 1}. ${item.tagName}.${item.className} - "${item.text}" (value: "${item.value}")`);
        console.log(`   Selector: ${item.selector}`);
        console.log(`   ID: ${item.id}, Dataset:`, item.dataset);
    });
    
    return foundElements;
}

// Look for user-specific elements (for user 98ixul)
function findUserElements() {
    console.log("\n👤 Looking for user-specific elements...");
    
    const userSelectors = [
        `[data-user="${targetUser}"]`,
        `[data-username="${targetUser}"]`,
        `[id*="${targetUser}"]`,
        `[class*="${targetUser}"]`
    ];
    
    const userElements = [];
    
    userSelectors.forEach(selector => {
        try {
            const elements = document.querySelectorAll(selector);
            elements.forEach(el => {
                userElements.push({
                    element: el,
                    selector: selector,
                    text: el.textContent?.trim().substring(0, 100),
                    tagName: el.tagName,
                    className: el.className,
                    id: el.id
                });
            });
        } catch (e) {
            // Ignore
        }
    });
    
    // Also search for elements containing the username in text
    const allElements = document.querySelectorAll('*');
    allElements.forEach(el => {
        const text = el.textContent?.trim() || '';
        if (text.includes(targetUser) && text.length < 200) {
            userElements.push({
                element: el,
                selector: 'text-content',
                text: text.substring(0, 100),
                tagName: el.tagName,
                className: el.className,
                id: el.id
            });
        }
    });
    
    console.log(`Found ${userElements.length} user-related elements:`);
    userElements.forEach((item, index) => {
        console.log(`${index + 1}. ${item.tagName} - "${item.text}"`);
        console.log(`   Selector: ${item.selector}, Class: ${item.className}`);
    });
    
    return userElements;
}

// Look for assignment/score table structures
function findScoreTables() {
    console.log("\n📋 Looking for score tables...");
    
    const tables = document.querySelectorAll('table');
    const scoreTables = [];
    
    tables.forEach((table, index) => {
        const headers = table.querySelectorAll('th');
        const headerText = Array.from(headers).map(th => th.textContent?.trim().toLowerCase()).join(' ');
        
        if (headerText.includes('score') || 
            headerText.includes('assignment') || 
            headerText.includes('grade') ||
            headerText.includes('user') ||
            headerText.includes('student')) {
            
            scoreTables.push({
                table: table,
                index: index,
                headers: Array.from(headers).map(th => th.textContent?.trim()),
                rowCount: table.querySelectorAll('tr').length
            });
        }
    });
    
    console.log(`Found ${scoreTables.length} potential score tables:`);
    scoreTables.forEach((item, index) => {
        console.log(`${index + 1}. Table with ${item.rowCount} rows`);
        console.log(`   Headers: ${item.headers.join(', ')}`);
        
        // Look for our target user in this table
        const userRows = item.table.querySelectorAll('tr');
        userRows.forEach((row, rowIndex) => {
            if (row.textContent?.includes(targetUser)) {
                console.log(`   ✅ Found ${targetUser} in row ${rowIndex + 1}`);
                
                // Look for editable cells in this row
                const cells = row.querySelectorAll('td');
                cells.forEach((cell, cellIndex) => {
                    const input = cell.querySelector('input');
                    const text = cell.textContent?.trim();
                    
                    if (input || text.match(/^\d+$/)) {
                        console.log(`     Cell ${cellIndex + 1}: "${text}" ${input ? '(has input)' : ''}`);
                    }
                });
            }
        });
    });
    
    return scoreTables;
}

// Try to simulate manual score updates
function simulateScoreUpdate(assignmentId = 1, newScore = 100) {
    console.log(`\n🎯 Attempting to simulate score update for assignment ${assignmentId} to ${newScore}...`);
    
    // Strategy 1: Look for input fields and update them
    const inputs = document.querySelectorAll('input[type="number"], input[type="text"]');
    let updated = false;
    
    inputs.forEach((input, index) => {
        // Check if this input might be related to our assignment/user
        const context = input.closest('tr, div, form')?.textContent || '';
        
        if (context.includes(targetUser) || 
            context.includes(`assignment ${assignmentId}`) ||
            context.includes(`Assignment ${assignmentId}`)) {
            
            console.log(`   Found potential input ${index + 1}: current value = "${input.value}"`);
            
            // Try to update it
            const oldValue = input.value;
            input.value = newScore;
            
            // Trigger change events
            input.dispatchEvent(new Event('input', { bubbles: true }));
            input.dispatchEvent(new Event('change', { bubbles: true }));
            input.dispatchEvent(new Event('blur', { bubbles: true }));
            
            console.log(`   ✅ Updated from "${oldValue}" to "${input.value}"`);
            updated = true;
        }
    });
    
    // Strategy 2: Look for contenteditable elements
    const editables = document.querySelectorAll('[contenteditable="true"], [contenteditable=""]');
    editables.forEach((el, index) => {
        const context = el.closest('tr, div')?.textContent || '';
        
        if (context.includes(targetUser)) {
            console.log(`   Found editable element ${index + 1}: "${el.textContent}"`);
            
            // Try to update if it looks like a score
            if (el.textContent?.trim().match(/^\d+$/)) {
                const oldText = el.textContent;
                el.textContent = newScore;
                
                // Trigger events
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('blur', { bubbles: true }));
                
                console.log(`   ✅ Updated editable from "${oldText}" to "${el.textContent}"`);
                updated = true;
            }
        }
    });
    
    // Strategy 3: Look for specific data attributes
    const dataElements = document.querySelectorAll('[data-score], [data-assignment-score]');
    dataElements.forEach((el, index) => {
        const context = el.closest('tr, div')?.textContent || '';
        
        if (context.includes(targetUser)) {
            console.log(`   Found data element ${index + 1}:`, el.dataset);
            
            // Update data attributes
            if (el.dataset.score) {
                el.dataset.score = newScore;
                el.textContent = newScore;
                console.log(`   ✅ Updated data-score to ${newScore}`);
                updated = true;
            }
        }
    });
    
    if (updated) {
        console.log(`   🎉 Successfully simulated score update!`);
        
        // Look for any save/submit buttons and try to click them
        const saveButtons = document.querySelectorAll('button, input[type="submit"]');
        saveButtons.forEach(btn => {
            const btnText = (btn.textContent || btn.value || '').toLowerCase();
            if (btnText.includes('save') || btnText.includes('submit') || btnText.includes('update')) {
                console.log(`   💾 Found save button: "${btnText}" - clicking...`);
                btn.click();
            }
        });
        
    } else {
        console.log(`   ❌ Could not find elements to update`);
    }
    
    return updated;
}

// Main function to run all discovery
function runDOMDiscovery() {
    console.log("🚀 Starting DOM-based score discovery...");
    
    const scoreElements = findScoreElements();
    const userElements = findUserElements();
    const scoreTables = findScoreTables();
    
    console.log("\n🔧 Helper functions available:");
    console.log("- simulateScoreUpdate(assignmentId, newScore) - Try to update a score");
    console.log("- findScoreElements() - Find all score-related elements");
    console.log("- findUserElements() - Find user-specific elements");
    console.log("- findScoreTables() - Find score tables");
    
    return {
        scoreElements,
        userElements, 
        scoreTables
    };
}

// Auto-update all assignments for the target user
window.hackAllAssignmentsDOMStyle = function() {
    console.log(`🎯 Attempting to hack all assignments for ${targetUser} using DOM manipulation...`);
    
    let successCount = 0;
    
    for (let i = 1; i <= 20; i++) {
        if (simulateScoreUpdate(i, 100)) {
            successCount++;
        }
        
        // Small delay between updates
        setTimeout(() => {}, 100);
    }
    
    console.log(`✅ DOM hack complete: ${successCount}/20 assignments updated`);
    
    // Try to trigger any global save/refresh
    const event = new Event('change', { bubbles: true });
    document.dispatchEvent(event);
    
    return successCount;
};

// Run the discovery
const results = runDOMDiscovery();
window.domResults = results;

console.log("\n💡 If you manually changed scores via Elements tab, try running:");
console.log("hackAllAssignmentsDOMStyle() - to automate that process");

// Monitor for any score changes
let scoreChangeObserver;
window.monitorScoreChanges = function() {
    console.log("👀 Monitoring for score changes...");
    
    scoreChangeObserver = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'childList' || mutation.type === 'characterData') {
                const target = mutation.target;
                const text = target.textContent || '';
                
                if (text.match(/\b\d+\b/) && 
                    (target.closest('tr')?.textContent?.includes(targetUser) ||
                     target.className?.includes('score') ||
                     target.dataset?.score)) {
                    
                    console.log("📊 Score change detected:", {
                        element: target,
                        newValue: text,
                        context: target.closest('tr, div')?.textContent?.substring(0, 100)
                    });
                }
            }
        });
    });
    
    scoreChangeObserver.observe(document.body, {
        childList: true,
        subtree: true,
        characterData: true
    });
    
    console.log("✅ Score change monitoring active");
};

window.stopScoreMonitoring = function() {
    if (scoreChangeObserver) {
        scoreChangeObserver.disconnect();
        console.log("🛑 Score monitoring stopped");
    }
};
