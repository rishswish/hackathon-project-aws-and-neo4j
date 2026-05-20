import os
os.environ['OTEL_SDK_DISABLED'] = 'true'

from dotenv import load_dotenv
load_dotenv()

from strands import Agent, tool
from neo4j import GraphDatabase

NEO4J_URI      = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")


def _run(cypher: str, **params) -> list[dict]:
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    with driver.session() as s:
        result = s.run(cypher, **params)
        rows = [dict(r) for r in result]
    driver.close()
    return rows


# ── Tools ─────────────────────────────────────────────────────────────────────

@tool
def get_role_requirements(role_name: str) -> str:
    """Return every skill required for a given role, sorted by importance.

    Use this to understand what skills a target role demands before
    recommending a learning plan.
    """
    rows = _run(
        """
        MATCH (r:Role {name: $role})-[req:REQUIRES]->(s:Skill)
        RETURN s.name AS skill, s.category AS category, req.importance AS importance
        ORDER BY req.importance DESC
        """,
        role=role_name,
    )
    if not rows:
        return f"Role '{role_name}' not found. Available roles: Junior Developer, Backend Engineer, Frontend Engineer, Full Stack Engineer, Data Analyst, Data Scientist, ML Engineer, MLOps Engineer, Data Engineer, DevOps Engineer, Cloud Architect, Security Engineer, Solutions Architect."
    lines = [f"Requirements for '{role_name}':"]
    for r in rows:
        stars = "★" * r["importance"]
        lines.append(f"  {stars} {r['skill']} ({r['category']})")
    return "\n".join(lines)


@tool
def find_skill_gap(target_role: str, known_skills: str) -> str:
    """Find which skills are missing to qualify for a target role.

    known_skills: comma-separated list of skills the user already has,
    e.g. "Python, SQL, Git"

    Returns missing skills grouped by category, and a readiness percentage.
    """
    skills_list = [s.strip() for s in known_skills.split(",") if s.strip()]
    rows = _run(
        """
        MATCH (r:Role {name: $role})-[req:REQUIRES]->(s:Skill)
        WHERE NOT s.name IN $known
        RETURN s.name AS skill, s.category AS category, req.importance AS importance
        ORDER BY req.importance DESC
        """,
        role=target_role,
        known=skills_list,
    )
    total_rows = _run(
        "MATCH (r:Role {name: $role})-[:REQUIRES]->(s) RETURN count(s) AS total",
        role=target_role,
    )
    total = total_rows[0]["total"] if total_rows else 0
    missing = len(rows)
    have = total - missing
    pct = round(100 * have / total) if total else 0

    if not rows:
        return f"You already have all skills for '{target_role}'. Readiness: 100%"

    lines = [f"Skill gap for '{target_role}' (readiness: {pct}% — {have}/{total} skills covered):"]
    lines.append("\nMissing skills:")
    for r in rows:
        stars = "★" * r["importance"]
        lines.append(f"  {stars} {r['skill']} ({r['category']})")
    return "\n".join(lines)


@tool
def find_learning_path(from_skill: str, to_skill: str) -> str:
    """Find the shortest prerequisite chain between two skills using graph traversal.

    This is the key graph-native operation: Neo4j's shortestPath() algorithm
    traverses PREREQUISITE_OF edges to find the minimum learning steps.
    A vector database or SQL cannot do this.

    Example: from_skill="Python", to_skill="TensorFlow"
    Returns: Python → Scikit-learn → Machine Learning → Deep Learning → TensorFlow
    """
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
        return (
            f"No prerequisite path found from '{from_skill}' to '{to_skill}'. "
            "They may not be connected, or you may already be there."
        )
    path = rows[0]["path"]
    steps = rows[0]["steps"]
    return f"Shortest learning path ({steps} steps):\n  " + " → ".join(path)


@tool
def recommend_courses(skill_name: str) -> str:
    """Return courses that teach a specific skill, sorted by free first then shortest.

    Use this after identifying a skill gap to give concrete next steps.
    """
    rows = _run(
        """
        MATCH (c:Course)-[:TEACHES]->(s:Skill {name: $skill})
        RETURN c.name AS course, c.provider AS provider, c.hours AS hours, c.free AS free
        ORDER BY c.free DESC, c.hours ASC
        """,
        skill=skill_name,
    )
    if not rows:
        return f"No courses found for '{skill_name}' in the database."
    lines = [f"Courses to learn '{skill_name}':"]
    for r in rows:
        tag = "FREE" if r["free"] else f"~{r['hours']}h"
        lines.append(f"  [{tag}] {r['course']} — {r['provider']}")
    return "\n".join(lines)


@tool
def find_best_matching_roles(known_skills: str) -> str:
    """Given a comma-separated list of skills, rank all roles by how many of
    their required skills the user already has (highest match % first).

    Use this to answer: 'What role am I closest to right now?'
    """
    skills_list = [s.strip() for s in known_skills.split(",") if s.strip()]
    rows = _run(
        """
        MATCH (r:Role)-[:REQUIRES]->(s:Skill)
        WITH r, count(s) AS total_required
        MATCH (r)-[:REQUIRES]->(s:Skill)
        WHERE s.name IN $known
        WITH r, total_required, count(s) AS matched, collect(s.name) AS matched_skills
        RETURN r.name AS role, r.level AS level, r.avg_salary AS salary,
               matched, total_required,
               round(100.0 * matched / total_required) AS match_pct,
               matched_skills
        ORDER BY match_pct DESC
        """,
        known=skills_list,
    )
    if not rows:
        return "No roles found. Make sure skill names match exactly (e.g. 'Python', 'SQL', 'Docker')."
    lines = ["Role match ranking based on your skills:\n"]
    for r in rows:
        bar = "█" * int(r["match_pct"] // 10) + "░" * (10 - int(r["match_pct"] // 10))
        lines.append(
            f"  {r['match_pct']:3.0f}% [{bar}] {r['role']} ({r['level']}, ${r['salary']:,}/yr)\n"
            f"         You have: {', '.join(r['matched_skills'])}"
        )
    return "\n".join(lines)


@tool
def find_highest_impact_skill(target_role: str, known_skills: str) -> str:
    """Find the single most valuable skill to learn next for a target role.

    Ranks missing skills by their importance to the role AND by how many
    other missing skills it unlocks as a prerequisite — the highest-leverage
    next step.
    """
    skills_list = [s.strip() for s in known_skills.split(",") if s.strip()]
    rows = _run(
        """
        MATCH (r:Role {name: $role})-[req:REQUIRES]->(missing:Skill)
        WHERE NOT missing.name IN $known
        OPTIONAL MATCH (missing)-[:PREREQUISITE_OF*1..3]->(unlocks:Skill)
        WHERE (r)-[:REQUIRES]->(unlocks) AND NOT unlocks.name IN $known
        WITH missing, req.importance AS importance, count(DISTINCT unlocks) AS unlocks_count
        RETURN missing.name AS skill, missing.category AS category,
               importance, unlocks_count,
               (importance + unlocks_count) AS total_score
        ORDER BY total_score DESC
        LIMIT 5
        """,
        role=target_role,
        known=skills_list,
    )
    if not rows:
        return f"No missing skills found for '{target_role}' with your current skills."
    lines = [f"Highest-impact skills to learn next for '{target_role}':\n"]
    for i, r in enumerate(rows, 1):
        lines.append(
            f"  {i}. {r['skill']} ({r['category']})\n"
            f"     Role importance: {'★' * r['importance']}  |  "
            f"Unlocks {r['unlocks_count']} other required skills"
        )
    return "\n".join(lines)


# ── Agent ─────────────────────────────────────────────────────────────────────

agent = Agent(
    system_prompt="""You are a career navigator powered by a skill knowledge graph in Neo4j.

You help people find the most efficient path from where they are today to the role they want.

Your answers are always grounded in the graph — you never guess or fabricate skill requirements,
learning paths, or course recommendations. If the data isn't in the graph, you say so.

When a user tells you their current skills and target role:
1. Call find_skill_gap to see what's missing
2. Call find_highest_impact_skill to recommend what to learn first
3. Call find_learning_path for any skill that needs prerequisite steps
4. Call recommend_courses for the top 2-3 priority skills

Always show the reasoning chain: gap → priority skill → learning path → courses.
Be specific and concrete. Never invent salary numbers or course details not returned by tools.""",
    tools=[
        get_role_requirements,
        find_skill_gap,
        find_learning_path,
        recommend_courses,
        find_best_matching_roles,
        find_highest_impact_skill,
    ],
)

# ── Demo ──────────────────────────────────────────────────────────────────────

DEMO_QUERIES = [
    {
        "query": "I know Python, SQL, and Git. I want to become a Data Scientist. What's my fastest path?",
        "insight": "Graph traversal finds prerequisite chains SQL can't compute — e.g. Python → Scikit-learn → ML → Deep Learning",
    },
    {
        "query": "I'm a Frontend Engineer who knows JavaScript, React, CSS/HTML, and TypeScript. What's my readiness for a Full Stack role and what should I learn first?",
        "insight": "find_highest_impact_skill scores each gap by role importance + how many other required skills it unlocks",
    },
    {
        "query": "I know Python, Docker, and Linux. Which roles am I closest to right now?",
        "insight": "find_best_matching_roles ranks all 13 roles by match % — graph COUNT across relationships, not guesswork",
    },
    {
        "query": "What's the shortest learning path from SQL to Snowflake?",
        "insight": "shortestPath() on PREREQUISITE_OF edges — a uniquely graph-native operation",
    },
]

if __name__ == "__main__":
    print("=" * 70)
    print("SKILL GAP NAVIGATOR — Neo4j Knowledge Graph + AWS Bedrock + Strands")
    print("=" * 70)

    for demo in DEMO_QUERIES:
        print(f"\n{'=' * 70}")
        print(f"USER: {demo['query']}")
        print("=" * 70)
        response = agent(demo["query"])
        print(response.message["content"][0]["text"])
        print(f"\n>> {demo['insight']}")

    print("\n" + "=" * 70)
    print("INTERACTIVE MODE — type your question (Ctrl+C to exit)")
    print("=" * 70)
    while True:
        try:
            query = input("\nYou: ").strip()
            if not query:
                continue
            response = agent(query)
            print(f"\nAgent: {response.message['content'][0]['text']}")
        except KeyboardInterrupt:
            print("\nGoodbye.")
            break
