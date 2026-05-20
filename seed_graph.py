import os
os.environ['OTEL_SDK_DISABLED'] = 'true'

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

NEO4J_URI      = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# ── Data ──────────────────────────────────────────────────────────────────────

ROLES = [
    {"name": "Junior Developer",    "level": "entry",  "avg_salary": 65000},
    {"name": "Backend Engineer",    "level": "mid",    "avg_salary": 110000},
    {"name": "Frontend Engineer",   "level": "mid",    "avg_salary": 105000},
    {"name": "Full Stack Engineer", "level": "mid",    "avg_salary": 115000},
    {"name": "Data Analyst",        "level": "mid",    "avg_salary": 85000},
    {"name": "Data Scientist",      "level": "senior", "avg_salary": 130000},
    {"name": "ML Engineer",         "level": "senior", "avg_salary": 145000},
    {"name": "MLOps Engineer",      "level": "senior", "avg_salary": 140000},
    {"name": "Data Engineer",       "level": "senior", "avg_salary": 125000},
    {"name": "DevOps Engineer",     "level": "mid",    "avg_salary": 120000},
    {"name": "Cloud Architect",     "level": "senior", "avg_salary": 155000},
    {"name": "Security Engineer",   "level": "senior", "avg_salary": 135000},
    {"name": "Solutions Architect", "level": "senior", "avg_salary": 150000},
]

SKILLS = [
    # Programming
    {"name": "Python",                      "category": "Programming"},
    {"name": "JavaScript",                  "category": "Programming"},
    {"name": "SQL",                         "category": "Programming"},
    {"name": "Java",                        "category": "Programming"},
    {"name": "Go",                          "category": "Programming"},
    {"name": "Bash/Shell",                  "category": "Programming"},
    {"name": "R",                           "category": "Programming"},
    # Fundamentals
    {"name": "Data Structures & Algorithms","category": "Fundamentals"},
    {"name": "System Design",               "category": "Fundamentals"},
    {"name": "Git",                         "category": "Fundamentals"},
    {"name": "Linux",                       "category": "Fundamentals"},
    # Frontend
    {"name": "React",                       "category": "Frontend"},
    {"name": "TypeScript",                  "category": "Frontend"},
    {"name": "CSS/HTML",                    "category": "Frontend"},
    {"name": "Vue.js",                      "category": "Frontend"},
    # Backend
    {"name": "REST APIs",                   "category": "Backend"},
    {"name": "FastAPI",                     "category": "Backend"},
    {"name": "Django",                      "category": "Backend"},
    {"name": "Node.js",                     "category": "Backend"},
    {"name": "PostgreSQL",                  "category": "Backend"},
    {"name": "Redis",                       "category": "Backend"},
    # Data
    {"name": "Pandas",                      "category": "Data"},
    {"name": "NumPy",                       "category": "Data"},
    {"name": "Statistics",                  "category": "Data"},
    {"name": "Data Visualization",          "category": "Data"},
    {"name": "Excel/Spreadsheets",          "category": "Data"},
    # ML / AI
    {"name": "Machine Learning",            "category": "ML/AI"},
    {"name": "Deep Learning",               "category": "ML/AI"},
    {"name": "TensorFlow",                  "category": "ML/AI"},
    {"name": "PyTorch",                     "category": "ML/AI"},
    {"name": "Scikit-learn",                "category": "ML/AI"},
    {"name": "LLMs & Prompt Engineering",   "category": "ML/AI"},
    {"name": "Linear Algebra",              "category": "ML/AI"},
    # Cloud / DevOps
    {"name": "AWS",                         "category": "Cloud"},
    {"name": "Docker",                      "category": "DevOps"},
    {"name": "Kubernetes",                  "category": "DevOps"},
    {"name": "Terraform",                   "category": "DevOps"},
    {"name": "CI/CD Pipelines",             "category": "DevOps"},
    # Data Engineering
    {"name": "Apache Spark",                "category": "Data Engineering"},
    {"name": "Apache Kafka",                "category": "Data Engineering"},
    {"name": "dbt",                         "category": "Data Engineering"},
    {"name": "Airflow",                     "category": "Data Engineering"},
    {"name": "Snowflake",                   "category": "Data Engineering"},
    # Security
    {"name": "IAM & Access Control",        "category": "Security"},
    {"name": "Network Security",            "category": "Security"},
    {"name": "OWASP & Secure Coding",       "category": "Security"},
]

# (skill, prerequisite_skill)  →  you need the second before learning the first
PREREQUISITES = [
    ("Pandas",                   "Python"),
    ("NumPy",                    "Python"),
    ("Scikit-learn",             "Python"),
    ("Scikit-learn",             "Statistics"),
    ("Machine Learning",         "Statistics"),
    ("Machine Learning",         "Scikit-learn"),
    ("Machine Learning",         "Linear Algebra"),
    ("Deep Learning",            "Machine Learning"),
    ("Deep Learning",            "Linear Algebra"),
    ("TensorFlow",               "Deep Learning"),
    ("PyTorch",                  "Deep Learning"),
    ("LLMs & Prompt Engineering","Machine Learning"),
    ("FastAPI",                  "Python"),
    ("FastAPI",                  "REST APIs"),
    ("Django",                   "Python"),
    ("Django",                   "SQL"),
    ("Node.js",                  "JavaScript"),
    ("React",                    "JavaScript"),
    ("React",                    "CSS/HTML"),
    ("TypeScript",               "JavaScript"),
    ("Vue.js",                   "JavaScript"),
    ("PostgreSQL",               "SQL"),
    ("Data Visualization",       "Python"),
    ("Data Visualization",       "Statistics"),
    ("dbt",                      "SQL"),
    ("Apache Spark",             "Python"),
    ("Apache Spark",             "SQL"),
    ("Apache Kafka",             "Linux"),
    ("Airflow",                  "Python"),
    ("Airflow",                  "Docker"),
    ("Kubernetes",               "Docker"),
    ("Terraform",                "AWS"),
    ("Terraform",                "Linux"),
    ("CI/CD Pipelines",          "Docker"),
    ("CI/CD Pipelines",          "Git"),
    ("System Design",            "REST APIs"),
    ("System Design",            "Data Structures & Algorithms"),
    ("IAM & Access Control",     "AWS"),
    ("OWASP & Secure Coding",    "REST APIs"),
    ("Network Security",         "Linux"),
    ("Snowflake",                "SQL"),
    ("Snowflake",                "dbt"),
    ("R",                        "Statistics"),
]

# (role, skill, importance 1-5)
ROLE_REQUIREMENTS = [
    ("Junior Developer",    "Python",                       4),
    ("Junior Developer",    "Git",                          4),
    ("Junior Developer",    "Data Structures & Algorithms", 3),
    ("Junior Developer",    "SQL",                          2),

    ("Backend Engineer",    "Python",                       5),
    ("Backend Engineer",    "SQL",                          4),
    ("Backend Engineer",    "REST APIs",                    5),
    ("Backend Engineer",    "FastAPI",                      4),
    ("Backend Engineer",    "PostgreSQL",                   3),
    ("Backend Engineer",    "Docker",                       3),
    ("Backend Engineer",    "System Design",                3),
    ("Backend Engineer",    "Git",                          4),

    ("Frontend Engineer",   "JavaScript",                   5),
    ("Frontend Engineer",   "React",                        5),
    ("Frontend Engineer",   "TypeScript",                   4),
    ("Frontend Engineer",   "CSS/HTML",                     5),
    ("Frontend Engineer",   "Git",                          4),

    ("Full Stack Engineer", "JavaScript",                   5),
    ("Full Stack Engineer", "Python",                       4),
    ("Full Stack Engineer", "React",                        5),
    ("Full Stack Engineer", "REST APIs",                    5),
    ("Full Stack Engineer", "SQL",                          3),
    ("Full Stack Engineer", "Docker",                       3),
    ("Full Stack Engineer", "Git",                          4),

    ("Data Analyst",        "SQL",                          5),
    ("Data Analyst",        "Python",                       4),
    ("Data Analyst",        "Pandas",                       4),
    ("Data Analyst",        "Statistics",                   4),
    ("Data Analyst",        "Data Visualization",           4),
    ("Data Analyst",        "Excel/Spreadsheets",           3),

    ("Data Scientist",      "Python",                       5),
    ("Data Scientist",      "Machine Learning",             5),
    ("Data Scientist",      "Statistics",                   5),
    ("Data Scientist",      "SQL",                          4),
    ("Data Scientist",      "Pandas",                       5),
    ("Data Scientist",      "NumPy",                        4),
    ("Data Scientist",      "Data Visualization",           4),
    ("Data Scientist",      "Linear Algebra",               3),

    ("ML Engineer",         "Python",                       5),
    ("ML Engineer",         "Machine Learning",             5),
    ("ML Engineer",         "Deep Learning",                4),
    ("ML Engineer",         "TensorFlow",                   4),
    ("ML Engineer",         "PyTorch",                      4),
    ("ML Engineer",         "Docker",                       4),
    ("ML Engineer",         "AWS",                          3),
    ("ML Engineer",         "LLMs & Prompt Engineering",    3),
    ("ML Engineer",         "Linear Algebra",               4),

    ("MLOps Engineer",      "Python",                       5),
    ("MLOps Engineer",      "Docker",                       5),
    ("MLOps Engineer",      "Kubernetes",                   4),
    ("MLOps Engineer",      "AWS",                          4),
    ("MLOps Engineer",      "CI/CD Pipelines",              5),
    ("MLOps Engineer",      "Machine Learning",             4),
    ("MLOps Engineer",      "Terraform",                    3),

    ("Data Engineer",       "Python",                       5),
    ("Data Engineer",       "SQL",                          5),
    ("Data Engineer",       "Apache Spark",                 4),
    ("Data Engineer",       "Apache Kafka",                 4),
    ("Data Engineer",       "Airflow",                      4),
    ("Data Engineer",       "dbt",                          4),
    ("Data Engineer",       "AWS",                          3),
    ("Data Engineer",       "Snowflake",                    3),

    ("DevOps Engineer",     "Linux",                        5),
    ("DevOps Engineer",     "Docker",                       5),
    ("DevOps Engineer",     "Kubernetes",                   5),
    ("DevOps Engineer",     "CI/CD Pipelines",              5),
    ("DevOps Engineer",     "Terraform",                    4),
    ("DevOps Engineer",     "AWS",                          4),
    ("DevOps Engineer",     "Bash/Shell",                   4),
    ("DevOps Engineer",     "Python",                       3),

    ("Cloud Architect",     "AWS",                          5),
    ("Cloud Architect",     "Terraform",                    5),
    ("Cloud Architect",     "Kubernetes",                   4),
    ("Cloud Architect",     "System Design",                5),
    ("Cloud Architect",     "Network Security",             4),
    ("Cloud Architect",     "IAM & Access Control",         4),
    ("Cloud Architect",     "Docker",                       3),

    ("Security Engineer",   "Network Security",             5),
    ("Security Engineer",   "OWASP & Secure Coding",        5),
    ("Security Engineer",   "IAM & Access Control",         5),
    ("Security Engineer",   "Linux",                        4),
    ("Security Engineer",   "Python",                       3),
    ("Security Engineer",   "AWS",                          3),

    ("Solutions Architect", "AWS",                          5),
    ("Solutions Architect", "System Design",                5),
    ("Solutions Architect", "Terraform",                    3),
    ("Solutions Architect", "IAM & Access Control",         3),
    ("Solutions Architect", "REST APIs",                    4),
    ("Solutions Architect", "Docker",                       3),
]

COURSES = [
    {"name": "Python for Everybody",                   "provider": "Coursera",              "hours": 30,  "free": True},
    {"name": "The Complete JavaScript Course",         "provider": "Udemy",                 "hours": 70,  "free": False},
    {"name": "SQL for Data Science",                   "provider": "Coursera",              "hours": 20,  "free": True},
    {"name": "AWS Cloud Practitioner",                 "provider": "AWS Training",          "hours": 40,  "free": True},
    {"name": "Docker & Kubernetes: Practical Guide",   "provider": "Udemy",                 "hours": 23,  "free": False},
    {"name": "Machine Learning Specialization",        "provider": "Coursera (Andrew Ng)",  "hours": 90,  "free": False},
    {"name": "Deep Learning Specialization",           "provider": "Coursera (Andrew Ng)",  "hours": 120, "free": False},
    {"name": "Fast.ai Practical Deep Learning",        "provider": "fast.ai",               "hours": 60,  "free": True},
    {"name": "React - The Complete Guide",             "provider": "Udemy",                 "hours": 50,  "free": False},
    {"name": "Statistics for Data Science",            "provider": "edX",                   "hours": 40,  "free": True},
    {"name": "System Design Interview",                "provider": "Educative",             "hours": 30,  "free": False},
    {"name": "Data Engineering Zoomcamp",              "provider": "DataTalks.Club",        "hours": 80,  "free": True},
    {"name": "Apache Kafka for Beginners",             "provider": "Udemy",                 "hours": 10,  "free": False},
    {"name": "Terraform on AWS",                       "provider": "Udemy",                 "hours": 18,  "free": False},
    {"name": "Linear Algebra for ML",                  "provider": "Khan Academy",          "hours": 25,  "free": True},
    {"name": "AWS Solutions Architect",                "provider": "AWS Training",          "hours": 60,  "free": False},
    {"name": "LangChain & LLM Apps",                  "provider": "DeepLearning.AI",       "hours": 10,  "free": True},
    {"name": "Cybersecurity Fundamentals",             "provider": "edX (IBM)",             "hours": 30,  "free": True},
    {"name": "dbt Fundamentals",                       "provider": "dbt Learn",             "hours": 5,   "free": True},
    {"name": "Apache Spark with Python",               "provider": "Udemy",                 "hours": 16,  "free": False},
]

# (course, skill)
COURSE_TEACHES = [
    ("Python for Everybody",                 "Python"),
    ("The Complete JavaScript Course",       "JavaScript"),
    ("The Complete JavaScript Course",       "Node.js"),
    ("SQL for Data Science",                 "SQL"),
    ("SQL for Data Science",                 "Pandas"),
    ("AWS Cloud Practitioner",               "AWS"),
    ("Docker & Kubernetes: Practical Guide", "Docker"),
    ("Docker & Kubernetes: Practical Guide", "Kubernetes"),
    ("Machine Learning Specialization",      "Machine Learning"),
    ("Machine Learning Specialization",      "Scikit-learn"),
    ("Machine Learning Specialization",      "Statistics"),
    ("Deep Learning Specialization",         "Deep Learning"),
    ("Deep Learning Specialization",         "TensorFlow"),
    ("Fast.ai Practical Deep Learning",      "Deep Learning"),
    ("Fast.ai Practical Deep Learning",      "PyTorch"),
    ("React - The Complete Guide",           "React"),
    ("React - The Complete Guide",           "TypeScript"),
    ("Statistics for Data Science",          "Statistics"),
    ("Statistics for Data Science",          "Data Visualization"),
    ("System Design Interview",              "System Design"),
    ("Data Engineering Zoomcamp",            "Apache Spark"),
    ("Data Engineering Zoomcamp",            "Apache Kafka"),
    ("Data Engineering Zoomcamp",            "Airflow"),
    ("Data Engineering Zoomcamp",            "dbt"),
    ("Apache Kafka for Beginners",           "Apache Kafka"),
    ("Terraform on AWS",                     "Terraform"),
    ("Linear Algebra for ML",               "Linear Algebra"),
    ("AWS Solutions Architect",              "AWS"),
    ("AWS Solutions Architect",              "IAM & Access Control"),
    ("LangChain & LLM Apps",               "LLMs & Prompt Engineering"),
    ("Cybersecurity Fundamentals",           "Network Security"),
    ("Cybersecurity Fundamentals",           "OWASP & Secure Coding"),
    ("dbt Fundamentals",                     "dbt"),
    ("Apache Spark with Python",             "Apache Spark"),
]

# ── Seeding ───────────────────────────────────────────────────────────────────

def seed(driver):
    with driver.session() as s:
        print("Clearing existing data...")
        s.run("MATCH (n) DETACH DELETE n")

        print(f"Creating {len(ROLES)} roles...")
        for r in ROLES:
            s.run(
                "MERGE (r:Role {name: $name}) SET r.level = $level, r.avg_salary = $avg_salary",
                **r,
            )

        print(f"Creating {len(SKILLS)} skills...")
        for sk in SKILLS:
            s.run(
                "MERGE (s:Skill {name: $name}) SET s.category = $category",
                **sk,
            )

        print(f"Creating {len(PREREQUISITES)} prerequisite relationships...")
        for skill, prereq in PREREQUISITES:
            s.run(
                """
                MATCH (prereq:Skill {name: $prereq}), (skill:Skill {name: $skill})
                MERGE (prereq)-[:PREREQUISITE_OF]->(skill)
                """,
                skill=skill, prereq=prereq,
            )

        print(f"Creating {len(ROLE_REQUIREMENTS)} role→skill requirements...")
        for role, skill, importance in ROLE_REQUIREMENTS:
            s.run(
                """
                MATCH (r:Role {name: $role}), (s:Skill {name: $skill})
                MERGE (r)-[:REQUIRES {importance: $importance}]->(s)
                """,
                role=role, skill=skill, importance=importance,
            )

        print(f"Creating {len(COURSES)} courses...")
        for c in COURSES:
            s.run(
                "MERGE (c:Course {name: $name}) SET c.provider = $provider, c.hours = $hours, c.free = $free",
                **c,
            )

        print(f"Creating {len(COURSE_TEACHES)} course→skill relationships...")
        for course, skill in COURSE_TEACHES:
            s.run(
                """
                MATCH (c:Course {name: $course}), (s:Skill {name: $skill})
                MERGE (c)-[:TEACHES]->(s)
                """,
                course=course, skill=skill,
            )

        result = s.run("""
            MATCH (n) RETURN labels(n)[0] AS label, count(n) AS count
            ORDER BY label
        """)
        print("\nGraph summary:")
        for row in result:
            print(f"  {row['label']}: {row['count']} nodes")

        result = s.run("MATCH ()-[r]->() RETURN type(r) AS rel, count(r) AS count ORDER BY rel")
        for row in result:
            print(f"  [{row['rel']}]: {row['count']} edges")


if __name__ == "__main__":
    print(f"Connecting to {NEO4J_URI}...")
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    driver.verify_connectivity()
    seed(driver)
    driver.close()
    print("\nDone — graph is ready.")
