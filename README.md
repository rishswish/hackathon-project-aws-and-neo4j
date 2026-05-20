# PathGraph AI
### Graph-Powered Career Navigation — Zero Hallucinations, Provable Paths

Built with Neo4j AuraDB · AWS Bedrock · Strands Agents

---

## 1. The Problem (2 min)

Every developer has asked an AI "how do I become an ML Engineer?" and gotten a confident, well-formatted answer that might be completely wrong.

The problem isn't the LLM. The problem is that **LLMs guess**. They fabricate prerequisites, skip critical skills, and give the same generic path to everyone regardless of what they already know. That's not career advice — that's a hallucination dressed up as a plan.

I tested this myself. I asked three different AI tools how to go from knowing Python to becoming a Data Scientist. Each one gave a different order for the same prerequisites. None of them could tell me *why* they chose that order. None of them could show their work.

**The root cause:** these tools use vector search or raw LLM generation to answer a question that is fundamentally a graph problem. "What's the shortest learning path from skill A to skill B?" is a pathfinding query. "Which skill unlocks the most other required skills?" is a multi-hop traversal query. You cannot answer either of those reliably without a graph.

So I stopped asking the LLM to guess and made it query a knowledge graph instead.

---

## 2. The Tech Stack (3 min)

### Neo4j AuraDB — The Knowledge Graph

The entire skill ecosystem of the tech industry lives in Neo4j as a property graph:

```
(Role)-[:REQUIRES {importance}]->(Skill)
(Skill)-[:PREREQUISITE_OF]->(Skill)
(Course)-[:TEACHES]->(Skill)
```

- **13 roles** — Junior Developer to Cloud Architect
- **44 skills** — across Programming, ML/AI, DevOps, Data Engineering, Security
- **20 courses** — mapped to the exact skills they teach
- **150+ relationships** — encoding the real prerequisite structure of the industry

What Neo4j enables that nothing else can:
- `shortestPath()` across prerequisite edges — the minimum learning sequence between any two skills
- Multi-hop impact scoring — which skill unlocks the most downstream required skills
- Honest empty results — if a path doesn't exist, it says so instead of fabricating one

### AWS Bedrock — The Language Layer

Claude Sonnet on Amazon Bedrock is the interface between the user and the graph. Its only job is to explain graph results in plain English. It does not generate answers — it reads them from Neo4j and translates them.

### Strands Agents — The Glue

Strands Agents connects Bedrock to five graph-backed tools via the `@tool` decorator. Each tool is a Cypher query. The agent decides which tools to call and in what order based on the user's question.

| Tool | What it does | Why it's graph-native |
|------|-------------|----------------------|
| `find_skill_gap` | Exact missing skills for a target role | Set difference across REQUIRES edges |
| `find_learning_path` | Shortest prerequisite chain between skills | `shortestPath()` — impossible in SQL |
| `find_highest_impact_skill` | Skill that unlocks the most other required skills | Multi-hop reachability traversal |
| `find_best_matching_roles` | Ranks all roles by your current match % | COUNT aggregation across all relationships |
| `recommend_courses` | Courses that teach a specific skill | Direct TEACHES edge lookup |

### Why This Stack Eliminates Hallucinations

The LLM controls the conversation. The graph controls the answers. Every fact the agent states came from a Cypher query — not from model weights. If you don't believe the answer, open Neo4j Browser and run the query yourself. The result will be identical.

This is the principle the research behind this workshop proves: grounding agents in knowledge graphs reduces hallucinations by 73% compared to standalone LLMs. PathGraph AI takes that principle and applies it to a real, everyday problem.

---

## 3. Live Demo + Code (5 min)

### Demo Query 1 — Skill Gap + Learning Path
```
"I know Python, SQL, and Git. How do I become a Data Scientist?"
```
What happens under the hood:
1. `find_skill_gap("Data Scientist", "Python, SQL, Git")` → returns 5 missing skills
2. `find_highest_impact_skill("Data Scientist", "Python, SQL, Git")` → scores Statistics as #1 (unlocks 3 other required skills)
3. `find_learning_path("Python", "Machine Learning")` → `Python → Scikit-learn → Machine Learning`
4. `recommend_courses("Statistics")` → returns free courses first

---

### Demo Query 2 — Shortest Path (the graph moment)
```
"What's the shortest learning path from SQL to Snowflake?"
```
Cypher running under the hood:
```cypher
MATCH (start:Skill {name: "SQL"}), (end:Skill {name: "Snowflake"})
MATCH path = shortestPath((start)-[:PREREQUISITE_OF*]->(end))
RETURN [n IN nodes(path) | n.name] AS path
```
Result: `SQL → dbt → Snowflake`

Two hops. Computed by the graph in milliseconds. The LLM cannot change this answer — it can only explain it.

---

### Demo Query 3 — Role Matching
```
"I know Python, Docker, and Linux. Which roles am I closest to right now?"
```
The graph scores all 13 roles simultaneously using relationship COUNT — not cosine similarity, not LLM inference. You get an exact percentage match for every role, ranked.

---

### The Code

**The tool that makes it graph-native** — `find_learning_path` in `skill_agent.py`:

```python
@tool
def find_learning_path(from_skill: str, to_skill: str) -> str:
    """Find the shortest prerequisite chain between two skills using graph traversal."""
    rows = _run(
        """
        MATCH (start:Skill {name: $from_skill}), (end:Skill {name: $to_skill})
        MATCH path = shortestPath((start)-[:PREREQUISITE_OF*]->(end))
        RETURN [n IN nodes(path) | n.name] AS path, length(path) AS steps
        """,
        from_skill=from_skill,
        to_skill=to_skill,
    )
    if not rows:
        return "No prerequisite path found — they may not be connected."
    path = rows[0]["path"]
    steps = rows[0]["steps"]
    return f"Shortest learning path ({steps} steps):\n  " + " → ".join(path)
```

This is 15 lines of code. It answers a question that would take hundreds of lines in SQL and still be wrong.

**The agent** — `skill_agent.py`:
```python
agent = Agent(
    system_prompt="You are a career navigator powered by a skill knowledge graph in Neo4j.
    Your answers are always grounded in the graph — you never guess or fabricate.",
    tools=[
        get_role_requirements,
        find_skill_gap,
        find_learning_path,
        recommend_courses,
        find_best_matching_roles,
        find_highest_impact_skill,
    ],
)
```

**The graph seed** — `seed_graph.py` populates Neo4j with all roles, skills, prerequisites, and courses in under 10 seconds.

---

## Running It Yourself

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Add your credentials
cp .env.example .env
# fill in NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, AWS credentials

# 3. Seed the graph
python seed_graph.py

# 4. Run the agent
python skill_agent.py
```

---

## The Bigger Point

I did not build a smarter chatbot. I built a system where the LLM has less room to be wrong.

Every answer PathGraph AI gives is traceable to a specific node, edge, or path in Neo4j. Judges can verify any output by opening Neo4j Browser and running the Cypher query directly. The agent cannot hallucinate a learning path because it never generates one — it reads it from a graph that was deliberately designed and verified by a human.

The LLM is the interface. The graph is the truth. That separation is what makes this reliable.

---

## Files

```
hackathon-skill-agent/
├── skill_agent.py      # Strands agent + all 5 Neo4j-backed tools
├── seed_graph.py       # Populates Neo4j with roles, skills, courses
├── requirements.txt    # Dependencies
└── .env.example        # Credentials template
```

---

## Stack

| Technology | Role |
|-----------|------|
| Neo4j AuraDB | Knowledge graph — roles, skills, prerequisites, courses |
| AWS Bedrock (Claude Sonnet) | LLM — explains graph results in plain English |
| Strands Agents | Agent framework — routes queries to graph-backed tools |
| Cypher | Graph query language — `shortestPath()`, multi-hop traversal |
