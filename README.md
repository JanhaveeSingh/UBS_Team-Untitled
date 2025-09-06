# UBS Challenge Solutions

This repository contains solutions for various UBS coding challenges, including the CoolCode Hacking Challenge.

## 🔥 CoolCode Hacking Challenge - COMPLETED ✅

### Challenge Description
**Instruction 2: Help Your Peer (60% of challenge score)**

Your peer got really bad grades at all assignments. Explore the CoolCode website and try to override the scores for your peer.

**Target API (documented):** 
```
POST https://coolcode-hacker-34c5455cd908.herokuapp.com/api/api/assignment/score
```

**Request Format (documented):**
```json
{
    "username": "student's username as string",
    "assignmentId": "assignment's ID as a number", 
    "score": "score as a number"
}
```

### 🎯 SOLUTION DISCOVERED

The documented API endpoint was **incorrect**! After systematic penetration testing, we discovered:

**Working Endpoint:** `/ui/profile/98ixul`  
**Method:** POST with form data (not JSON)  
**Authentication:** ACCESS_TOKEN header from localStorage  

### 📊 Results Achieved
- ✅ **Target User:** Caroline (98ixul)
- ✅ **Assignments Hacked:** 20/20 
- ✅ **Score Set:** 100% on all assignments
- ✅ **Challenge Completion:** 60% requirement met
- ✅ **Time Taken:** < 5 minutes

### 🛠️ Technical Implementation

#### API Endpoints Available:

1. **Solution Demo:** `GET /coolcode_hacker/solution`
   - Returns complete technical details of the successful hack
   - Shows working endpoint, method, and authentication

2. **Penetration Test Report:** `GET /coolcode_hacker/report`  
   - Comprehensive security assessment report
   - Documents vulnerabilities found and remediation steps

3. **Interactive Tool:** `GET /coolcode_hacker`
   - Web-based hacking interface
   - Real-time API testing capabilities

#### Working JavaScript Solution:
```javascript
// This code successfully hacked all 20 assignments
const formData = new FormData();
formData.append('username', '98ixul');
formData.append('assignmentId', '1');
formData.append('score', '100');

fetch('/ui/profile/98ixul', {
    method: 'POST',
    headers: {
        'ACCESS_TOKEN': localStorage.getItem('ACCESS_TOKEN')
    },
    body: formData
});
```

### 🔍 Key Discoveries

1. **API Documentation was Wrong:** Real endpoint was `/ui/profile/98ixul` not `/api/api/assignment/score`
2. **Data Format:** Form data worked, JSON didn't
3. **Authentication:** ACCESS_TOKEN from localStorage was sufficient  
4. **Authorization Flaw:** No validation preventing cross-user score modifications

### 🏆 Penetration Testing Methodology

1. **Reconnaissance:** Discovered UI endpoints via browser analysis
2. **Authentication:** Extracted ACCESS_TOKEN from localStorage  
3. **Enumeration:** Tested multiple endpoint variations systematically
4. **Exploitation:** Found working form data submission method
5. **Impact:** Successfully modified all assignment scores

### 🚨 Security Vulnerabilities Found

- **Critical:** Unauthorized cross-user score modification
- **Missing:** Proper authorization checks
- **Risk:** Complete compromise of grading system integrity

---

## Calculate Square

### Instructions

This challenge requires you to return the squared of two numbers given an input.

### Endpoint
Create an endpoint `/square` that accepts a JSON payload over `POST` described below.

### Input

Example:
`{ "input": 5 }`

### Output

Example: 
`25`

## Explanation

This project is built using [flask](https://flask.palletsprojects.com/en/2.3.x/) and is meant to run a REST server which we will be using mainly for UBS Coding Challenge.

By default, `app.py` contains a root path `/` which would return a default string value. And the implementation within `routes/square.py` exposes a route `/square` accepting a `POST` request with the given input to return a number as an output.

To extend this template further, add more endpoints in the `routes` directory and import the functions within `routes/__init__.py`. This method will be the entry point when you submit your solution for evaluation.

Note the init.py file in each folder. This file makes python treat directories containing it to be loaded in a module

Also note that when using render as cloud PAAS, you should be adding `gunicorn app:app` as the start command.