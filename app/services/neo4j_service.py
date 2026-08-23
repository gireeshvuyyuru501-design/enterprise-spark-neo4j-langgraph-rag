from neo4j import GraphDatabase
from app.config import settings

class Neo4jService:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )

    def close(self):
        self.driver.close()

    def health(self) -> bool:
        with self.driver.session() as session:
            return session.run("RETURN 1 AS ok").single()["ok"] == 1

    def search(self, question: str, limit: int = 4):
        q = question.lower()
        cypher = """
        MATCH (e:Employee)
        OPTIONAL MATCH (e)-[:WORKS_ON]->(p:Project)
        OPTIONAL MATCH (e)-[:HAS_SKILL]->(s:Skill)
        WITH e, collect(DISTINCT p.name) AS projects, collect(DISTINCT s.name) AS skills
        WHERE toLower(e.name) CONTAINS $q
           OR any(x IN projects WHERE toLower(x) CONTAINS $q)
           OR any(x IN skills WHERE toLower(x) CONTAINS $q)
           OR any(token IN split($q, ' ') WHERE size(token) > 2 AND (
               toLower(e.name) CONTAINS token OR
               any(x IN projects WHERE toLower(x) CONTAINS token) OR
               any(x IN skills WHERE toLower(x) CONTAINS token)
           ))
        RETURN e.name AS employee, e.department AS department, projects, skills
        LIMIT $limit
        """
        with self.driver.session() as session:
            rows = session.run(cypher, q=q, limit=limit)
            out = []
            for r in rows:
                content = (
                    f"Employee: {r['employee']}; Department: {r['department']}; "
                    f"Projects: {', '.join(r['projects']) or 'None'}; "
                    f"Skills: {', '.join(r['skills']) or 'None'}"
                )
                out.append({"source_type": "graph", "source": "neo4j", "content": content})
            return out
