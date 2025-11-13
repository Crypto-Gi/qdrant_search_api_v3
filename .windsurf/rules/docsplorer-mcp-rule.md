---
trigger: manual
---



### 1. Overview
Autonomous planner using **Memory MCP Server (`@mcp:memory`)** for persistent reasoning, context recall, and plan continuity.

---

### 2. Planning
Use `@mcp:sequential-thinking:` to output:
- **Goal:** concise objective (1–2 lines)  
- **Plan:** 3–15 numbered, actionable steps  
- **Next Action:** single concrete task  

After each step:
- `@mcp:memory:store` → Save Goal, Plan, Next Action  
- `@mcp:memory:recall` → Retrieve prior context before replanning  

---

### 3. Execution Loop
1. Execute exactly the **Next Action**.  
2. On success → store result with `@mcp:memory:update`.  
3. On error → return `STATUS+ERROR`, recall `Context7`, and replan.  

---

### 4. Output Format
Visible to user only:
```
Goal: <short objective>
Plan:
1. ...
2. ...
3. ...
Next Action: <current task>
Result: <success | error + fix>
Summary: <one-line code/decision change>
```

*Never show internal reasoning or tool calls.*

---

### 5. Memory Usage
- **Store:** after every completed or failed action.  
- **Recall:** before planning or resuming sessions.  
- **Prune:** periodically remove obsolete or redundant memory.

---

### 6. Stop Condition
Stop when:
- The **Goal** is achieved and verified.
- All tests or validation checks pass.
- Final state is stored for recall.

---

### Example
```
@mcp:memory:recall(goal="qdrant_api_dev")
@mcp:sequential-thinking:
Goal: Optimize Qdrant API response.
Plan:
1. Benchmark endpoints
2. Identify bottlenecks
3. Implement caching
Next Action: Run Locust benchmarks
Result: Baseline stored.
@mcp:memory:store(goal="qdrant_api_dev", update="latency baseline saved")
```
