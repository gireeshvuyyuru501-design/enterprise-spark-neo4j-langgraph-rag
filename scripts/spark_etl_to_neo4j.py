import os
from pathlib import Path
from dotenv import load_dotenv
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, trim
from neo4j import GraphDatabase

load_dotenv()

spark = (
    SparkSession.builder
    .appName("EnterpriseSparkNeo4jETL")
    .master("local[*]")
    .getOrCreate()
)

employees = (
    spark.read.option("header", True).csv("data/employees.csv")
    .select(
        col("employee_id").cast("int"),
        trim(col("name")).alias("name"),
        trim(col("department")).alias("department"),
        trim(col("skills")).alias("skills"),
    )
)

projects = (
    spark.read.option("header", True).csv("data/projects.csv")
    .select(
        col("project_id").cast("int"),
        trim(col("project_name")).alias("project_name"),
        col("employee_id").cast("int"),
    )
)

employees.createOrReplaceTempView("employees")
projects.createOrReplaceTempView("projects")

summary = spark.sql("""
SELECT e.employee_id, e.name, e.department, e.skills,
       collect_list(p.project_name) AS projects
FROM employees e
LEFT JOIN projects p ON e.employee_id = p.employee_id
GROUP BY e.employee_id, e.name, e.department, e.skills
""")

Path("data/output").mkdir(exist_ok=True)
rows = [r.asDict() for r in summary.collect()]

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI", "bolt://localhost:7687"),
    auth=(os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "password12345")),
)

with driver.session() as session:
    session.run("CREATE CONSTRAINT employee_id IF NOT EXISTS FOR (e:Employee) REQUIRE e.employee_id IS UNIQUE")
    session.run("CREATE CONSTRAINT project_name IF NOT EXISTS FOR (p:Project) REQUIRE p.name IS UNIQUE")
    session.run("CREATE CONSTRAINT skill_name IF NOT EXISTS FOR (s:Skill) REQUIRE s.name IS UNIQUE")

    for row in rows:
        session.run(
            "MERGE (e:Employee {employee_id: $employee_id}) "
            "SET e.name = $name, e.department = $department",
            employee_id=row["employee_id"],
            name=row["name"],
            department=row["department"],
        )

        for skill in (row.get("skills") or "").split("|"):
            skill = skill.strip()
            if skill:
                session.run(
                    "MATCH (e:Employee {employee_id: $employee_id}) "
                    "MERGE (s:Skill {name: $skill}) "
                    "MERGE (e)-[:HAS_SKILL]->(s)",
                    employee_id=row["employee_id"],
                    skill=skill,
                )

        for project in row.get("projects") or []:
            if project:
                session.run(
                    "MATCH (e:Employee {employee_id: $employee_id}) "
                    "MERGE (p:Project {name: $project}) "
                    "MERGE (e)-[:WORKS_ON]->(p)",
                    employee_id=row["employee_id"],
                    project=project,
                )

driver.close()
spark.stop()
print("Spark ETL complete. Neo4j graph loaded.")
