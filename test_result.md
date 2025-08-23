#====================================================================================================
# START - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================

# THIS SECTION CONTAINS CRITICAL TESTING INSTRUCTIONS FOR BOTH AGENTS
# BOTH MAIN_AGENT AND TESTING_AGENT MUST PRESERVE THIS ENTIRE BLOCK

# Communication Protocol:
# If the `testing_agent` is available, main agent should delegate all testing tasks to it.
#
# You have access to a file called `test_result.md`. This file contains the complete testing state
# and history, and is the primary means of communication between main and the testing agent.
#
# Main and testing agents must follow this exact format to maintain testing data. 
# The testing data must be entered in yaml format Below is the data structure:
# 
## user_problem_statement: {problem_statement}
## backend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.py"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## frontend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.js"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## metadata:
##   created_by: "main_agent"
##   version: "1.0"
##   test_sequence: 3
##   run_ui: false
##
## test_plan:
##   current_focus:
##     - "Auth endpoints and protected routes"
##     - "Create registry flow with token"
##   stuck_tasks: []
##   test_all: false
##   test_priority: "high_first"
##
## agent_communication:
##     -agent: "main"
##     -message: "Auth and protected routes passed. Minor UI polish: replaced native checkbox with shadcn Checkbox, set Inter font. Ready for frontend automated testing on your approval."

#====================================================================================================
# END - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================


#====================================================================================================
# Testing Data - Main Agent and testing sub agent both should log testing data below this section
#====================================================================================================

## user_problem_statement: Build a launchable MVP for a Hitchd-style honeymoon cash registry with Dubai default locale, turn current frontend mock into full-stack with FastAPI+MongoDB.
## backend:
##   - task: "Design API contracts and implement core endpoints"
##     implemented: true
##     working: true
##     file: "/app/backend/server.py"
##     stuck_count: 0
##     priority: "high"
##     needs_retesting: false
##     status_history:
##         -working: true
##         -agent: "testing"
##         -comment: "All endpoints passed; JWT added and re-tested."
##   - task: "Mongo connection and collections"
##     implemented: true
##     working: true
##     file: "/app/backend/server.py"
##     stuck_count: 0
##     priority: "high"
##     needs_retesting: false
##     status_history:
##         -working: true
##         -agent: "testing"
##         -comment: "DB reads/writes/aggregations OK."
##   - task: "JWT Auth (register/login/me)"
##     implemented: true
##     working: true
##     file: "/app/backend/server.py"
##     stuck_count: 0
##     priority: "high"
##     needs_retesting: false
##     status_history:
##         -working: true
##         -agent: "testing"
##         -comment: "Auth endpoints working. Protected registry/fund routes validated."
## frontend:
##   - task: "Landing + Create + Public with mock data"
##     implemented: true
##     working: true
##     file: "/app/frontend/src/pages/*.jsx"
##     stuck_count: 0
##     priority: "high"
##     needs_retesting: false
##     status_history:
##         -working: true
##         -agent: "main"
##         -comment: "Interactive mock done; contributions write to localStorage."
##   - task: "Wire to backend with graceful fallback"
##     implemented: true
##     working: true
##     file: "/app/frontend/src/pages/CreateRegistry.jsx, /app/frontend/src/pages/PublicRegistry.jsx, /app/frontend/src/lib/api.js"
##     stuck_count: 0
##     priority: "high"
##     needs_retesting: true
##     status_history:
##         -working: true
##         -agent: "main"
##         -comment: "Create/Update registry, bulk upsert funds, public fetch, and contributions call backend with fallback to mock."
##   - task: "Auth UI + Protected routes"
##     implemented: true
##     working: true
##     file: "/app/frontend/src/context/AuthContext.jsx, /app/frontend/src/pages/Auth.jsx, /app/frontend/src/App.js"
##     stuck_count: 0
##     priority: "high"
##     needs_retesting: true
##     status_history:
##         -working: true
##         -agent: "main"
##         -comment: "Login/Register flows implemented; /create protected."
## metadata:
##   created_by: "main_agent"
##   version: "1.0"
##   test_sequence: 3
##   run_ui: false
## test_plan:
##   current_focus:
##     - "Verify frontend sync to backend (auth + create + funds)"
##     - "Public page contribute flow (DB write)"
##   stuck_tasks: []
##   test_all: false
##   test_priority: "high_first"
## agent_communication:
##     -agent: "main"
##     -message: "Awaiting user approval to run automated frontend tests."

## metadata:
##   created_by: "main_agent"
##   version: "1.0"
##   test_sequence: 4
##   run_ui: true
## test_plan:
##   current_focus:
##     - "Frontend E2E: auth redirect, signup/login"
##     - "Create registry + save/sync"
##     - "Public page load by slug"
##     - "Contribute modal updates totals"
##   stuck_tasks: []
##   test_all: false
##   test_priority: "high_first"
## agent_communication:
##     -agent: "main"
##     -message: "Proceed with automated frontend testing now. Use http://localhost:3000. Ensure /create redirects to /auth when unauthenticated, then full happy path."
