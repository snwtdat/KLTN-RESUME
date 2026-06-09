from neo4j import GraphDatabase

class KnowledgeGraphDB:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def xoa_du_lieu_cu(self):
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("Đã dọn dẹp sạch Database cũ.")

    def tao_do_thi_tri_thuc(self):
        query = """
        // ==========================================
        // 1. TẠO CÁC NÚT VỊ TRÍ (ROLES)
        // ==========================================
        CREATE (backend:Role {name: 'Backend Developer'})
        CREATE (frontend:Role {name: 'Frontend Developer'})
        CREATE (fullstack:Role {name: 'Fullstack Developer'})
        CREATE (mobile:Role {name: 'Mobile Developer'})
        CREATE (data_sci:Role {name: 'Data Scientist'})
        CREATE (data_eng:Role {name: 'Data Engineer'})
        CREATE (ml_eng:Role {name: 'Machine Learning Engineer'})
        CREATE (devops:Role {name: 'DevOps Engineer'})
        CREATE (cloud_eng:Role {name: 'Cloud Engineer'})
        CREATE (qa:Role {name: 'QA Automation Tester'})
        CREATE (security:Role {name: 'Cybersecurity Engineer'})
        CREATE (game:Role {name: 'Game Developer'})
        CREATE (blockchain:Role {name: 'Blockchain Developer'})

        // ==========================================
        // 2. TẠO CÁC NÚT KỸ NĂNG (SKILLS)
        // ==========================================
        // --- Ngôn ngữ lập trình (Languages) ---
        CREATE (python:Skill {name: 'Python', type: 'Language'})
        CREATE (java:Skill {name: 'Java', type: 'Language'})
        CREATE (js:Skill {name: 'JavaScript', type: 'Language'})
        CREATE (ts:Skill {name: 'TypeScript', type: 'Language'})
        CREATE (go:Skill {name: 'Go', type: 'Language'})
        CREATE (csharp:Skill {name: 'C#', type: 'Language'})
        CREATE (cpp:Skill {name: 'C++', type: 'Language'})
        CREATE (rust:Skill {name: 'Rust', type: 'Language'})
        CREATE (php:Skill {name: 'PHP', type: 'Language'})
        CREATE (ruby:Skill {name: 'Ruby', type: 'Language'})
        CREATE (swift:Skill {name: 'Swift', type: 'Language'})
        CREATE (kotlin:Skill {name: 'Kotlin', type: 'Language'})
        CREATE (dart:Skill {name: 'Dart', type: 'Language'})
        CREATE (solidity:Skill {name: 'Solidity', type: 'Language'})

        // --- Frameworks & Libraries ---
        CREATE (react:Skill {name: 'ReactJS', type: 'Framework'})
        CREATE (angular:Skill {name: 'Angular', type: 'Framework'})
        CREATE (vue:Skill {name: 'VueJS', type: 'Framework'})
        CREATE (node:Skill {name: 'NodeJS', type: 'Framework'})
        CREATE (express:Skill {name: 'ExpressJS', type: 'Framework'})
        CREATE (nestjs:Skill {name: 'NestJS', type: 'Framework'})
        CREATE (spring:Skill {name: 'Spring Boot', type: 'Framework'})
        CREATE (django:Skill {name: 'Django', type: 'Framework'})
        CREATE (flask:Skill {name: 'Flask', type: 'Framework'})
        CREATE (fastapi:Skill {name: 'FastAPI', type: 'Framework'})
        CREATE (dotnet:Skill {name: '.NET', type: 'Framework'})
        CREATE (laravel:Skill {name: 'Laravel', type: 'Framework'})
        CREATE (flutter:Skill {name: 'Flutter', type: 'Framework'})
        CREATE (reactnative:Skill {name: 'React Native', type: 'Framework'})
        CREATE (unity:Skill {name: 'Unity', type: 'Framework'})
        CREATE (unreal:Skill {name: 'Unreal Engine', type: 'Framework'})

        // --- Databases (Cơ sở dữ liệu) ---
        CREATE (sql:Skill {name: 'SQL', type: 'Database'})
        CREATE (mysql:Skill {name: 'MySQL', type: 'Database'})
        CREATE (postgres:Skill {name: 'PostgreSQL', type: 'Database'})
        CREATE (oracle:Skill {name: 'Oracle DB', type: 'Database'})
        CREATE (mongo:Skill {name: 'MongoDB', type: 'Database'})
        CREATE (redis:Skill {name: 'Redis', type: 'Database'})
        CREATE (cassandra:Skill {name: 'Cassandra', type: 'Database'})
        CREATE (elasticsearch:Skill {name: 'Elasticsearch', type: 'Database'})
        CREATE (neo4j:Skill {name: 'Neo4j', type: 'Database'})

        // --- Cloud, DevOps & Tools ---
        CREATE (git:Skill {name: 'Git', type: 'Tool'})
        CREATE (github:Skill {name: 'GitHub', type: 'Tool'})
        CREATE (linux:Skill {name: 'Linux', type: 'OS'})
        CREATE (docker:Skill {name: 'Docker', type: 'Tool'})
        CREATE (k8s:Skill {name: 'Kubernetes', type: 'Tool'})
        CREATE (aws:Skill {name: 'AWS', type: 'Cloud'})
        CREATE (azure:Skill {name: 'Azure', type: 'Cloud'})
        CREATE (gcp:Skill {name: 'GCP', type: 'Cloud'})
        CREATE (cicd:Skill {name: 'CI/CD', type: 'Tool'})
        CREATE (jenkins:Skill {name: 'Jenkins', type: 'Tool'})
        CREATE (terraform:Skill {name: 'Terraform', type: 'Tool'})

        // --- AI, Data & Special Domains ---
        CREATE (ml:Skill {name: 'Machine Learning', type: 'Domain'})
        CREATE (dl:Skill {name: 'Deep Learning', type: 'Domain'})
        CREATE (nlp:Skill {name: 'NLP', type: 'Domain'})
        CREATE (cv:Skill {name: 'Computer Vision', type: 'Domain'})
        CREATE (pandas:Skill {name: 'Pandas', type: 'Library'})
        CREATE (spark:Skill {name: 'Apache Spark', type: 'Tool'})
        CREATE (hadoop:Skill {name: 'Hadoop', type: 'Tool'})
        CREATE (kafka:Skill {name: 'Apache Kafka', type: 'Tool'})
        CREATE (selenium:Skill {name: 'Selenium', type: 'Tool'})
        CREATE (restapi:Skill {name: 'RESTful API', type: 'Domain'})
        CREATE (graphql:Skill {name: 'GraphQL', type: 'Domain'})

        // ==========================================
        // 3. TẠO QUAN HỆ: VỊ TRÍ CẦN KỸ NĂNG GÌ? (REQUIRES)
        // ==========================================
        CREATE
        // Backend
        (backend)-[:REQUIRES]->(java), (backend)-[:REQUIRES]->(python),
        (backend)-[:REQUIRES]->(go), (backend)-[:REQUIRES]->(csharp),
        (backend)-[:REQUIRES]->(node), (backend)-[:REQUIRES]->(spring),
        (backend)-[:REQUIRES]->(django), (backend)-[:REQUIRES]->(fastapi),
        (backend)-[:REQUIRES]->(dotnet), (backend)-[:REQUIRES]->(php),
        (backend)-[:REQUIRES]->(laravel), (backend)-[:REQUIRES]->(sql),
        (backend)-[:REQUIRES]->(postgres), (backend)-[:REQUIRES]->(mongo),
        (backend)-[:REQUIRES]->(redis), (backend)-[:REQUIRES]->(docker),
        (backend)-[:REQUIRES]->(git), (backend)-[:REQUIRES]->(restapi),

        // Frontend
        (frontend)-[:REQUIRES]->(js), (frontend)-[:REQUIRES]->(ts),
        (frontend)-[:REQUIRES]->(react), (frontend)-[:REQUIRES]->(angular),
        (frontend)-[:REQUIRES]->(vue), (frontend)-[:REQUIRES]->(git),
        (frontend)-[:REQUIRES]->(restapi), (frontend)-[:REQUIRES]->(graphql),

        // Fullstack (Kế thừa cả 2)
        (fullstack)-[:REQUIRES]->(js), (fullstack)-[:REQUIRES]->(ts),
        (fullstack)-[:REQUIRES]->(react), (fullstack)-[:REQUIRES]->(node),
        (fullstack)-[:REQUIRES]->(sql), (fullstack)-[:REQUIRES]->(mongo),
        (fullstack)-[:REQUIRES]->(git), (fullstack)-[:REQUIRES]->(docker),

        // Mobile
        (mobile)-[:REQUIRES]->(swift), (mobile)-[:REQUIRES]->(kotlin),
        (mobile)-[:REQUIRES]->(dart), (mobile)-[:REQUIRES]->(flutter),
        (mobile)-[:REQUIRES]->(reactnative), (mobile)-[:REQUIRES]->(git),

        // DevOps & Cloud
        (devops)-[:REQUIRES]->(linux), (devops)-[:REQUIRES]->(docker),
        (devops)-[:REQUIRES]->(k8s), (devops)-[:REQUIRES]->(aws),
        (devops)-[:REQUIRES]->(cicd), (devops)-[:REQUIRES]->(jenkins),
        (devops)-[:REQUIRES]->(terraform), (devops)-[:REQUIRES]->(git),
        (cloud_eng)-[:REQUIRES]->(aws), (cloud_eng)-[:REQUIRES]->(azure),
        (cloud_eng)-[:REQUIRES]->(gcp), (cloud_eng)-[:REQUIRES]->(linux),

        // Data & AI
        (data_sci)-[:REQUIRES]->(python), (data_sci)-[:REQUIRES]->(sql),
        (data_sci)-[:REQUIRES]->(pandas), (data_sci)-[:REQUIRES]->(ml),
        (data_sci)-[:REQUIRES]->(dl), (data_sci)-[:REQUIRES]->(nlp),
        (ml_eng)-[:REQUIRES]->(python), (ml_eng)-[:REQUIRES]->(ml),
        (ml_eng)-[:REQUIRES]->(dl), (ml_eng)-[:REQUIRES]->(docker),
        (data_eng)-[:REQUIRES]->(python), (data_eng)-[:REQUIRES]->(sql),
        (data_eng)-[:REQUIRES]->(spark), (data_eng)-[:REQUIRES]->(hadoop),
        (data_eng)-[:REQUIRES]->(kafka), (data_eng)-[:REQUIRES]->(aws),

        // QA / Tester
        (qa)-[:REQUIRES]->(python), (qa)-[:REQUIRES]->(java),
        (qa)-[:REQUIRES]->(selenium), (qa)-[:REQUIRES]->(cicd),
        (qa)-[:REQUIRES]->(sql),

        // Game Developer
        (game)-[:REQUIRES]->(cpp), (game)-[:REQUIRES]->(csharp),
        (game)-[:REQUIRES]->(unity), (game)-[:REQUIRES]->(unreal),

        // Blockchain
        (blockchain)-[:REQUIRES]->(solidity), (blockchain)-[:REQUIRES]->(rust),
        (blockchain)-[:REQUIRES]->(go), (blockchain)-[:REQUIRES]->(js)

        // ==========================================
        // 4. TẠO QUAN HỆ: LỘ TRÌNH HỌC TẬP (IS_PREREQUISITE_OF)
        // ==========================================
        CREATE
        // JavaScript Ecosystem
        (js)-[:IS_PREREQUISITE_OF]->(ts),
        (js)-[:IS_PREREQUISITE_OF]->(react),
        (js)-[:IS_PREREQUISITE_OF]->(vue),
        (js)-[:IS_PREREQUISITE_OF]->(node),
        (ts)-[:IS_PREREQUISITE_OF]->(angular),
        (ts)-[:IS_PREREQUISITE_OF]->(nestjs),
        (node)-[:IS_PREREQUISITE_OF]->(express),
        (react)-[:IS_PREREQUISITE_OF]->(reactnative),
        
        // Java & C# Ecosystem
        (java)-[:IS_PREREQUISITE_OF]->(spring),
        (csharp)-[:IS_PREREQUISITE_OF]->(dotnet),
        (csharp)-[:IS_PREREQUISITE_OF]->(unity),
        (cpp)-[:IS_PREREQUISITE_OF]->(unreal),
        
        // Python Ecosystem
        (python)-[:IS_PREREQUISITE_OF]->(django),
        (python)-[:IS_PREREQUISITE_OF]->(flask),
        (python)-[:IS_PREREQUISITE_OF]->(fastapi),
        (python)-[:IS_PREREQUISITE_OF]->(pandas),
        (pandas)-[:IS_PREREQUISITE_OF]->(ml),
        (ml)-[:IS_PREREQUISITE_OF]->(dl),
        (dl)-[:IS_PREREQUISITE_OF]->(nlp),
        (dl)-[:IS_PREREQUISITE_OF]->(cv),
        
        // PHP / Mobile
        (php)-[:IS_PREREQUISITE_OF]->(laravel),
        (dart)-[:IS_PREREQUISITE_OF]->(flutter),
        
        // Databases
        (sql)-[:IS_PREREQUISITE_OF]->(mysql),
        (sql)-[:IS_PREREQUISITE_OF]->(postgres),
        (sql)-[:IS_PREREQUISITE_OF]->(oracle),
        
        // DevOps & Cloud Roadmap
        (linux)-[:IS_PREREQUISITE_OF]->(docker),
        (docker)-[:IS_PREREQUISITE_OF]->(k8s),
        (git)-[:IS_PREREQUISITE_OF]->(github),
        (git)-[:IS_PREREQUISITE_OF]->(cicd),
        (cicd)-[:IS_PREREQUISITE_OF]->(jenkins),
        (aws)-[:IS_PREREQUISITE_OF]->(terraform)
        """
        with self.driver.session() as session:
            session.run(query)
            print("Đã bơm thành công Bách khoa toàn thư IT vào Neo4j!")

if __name__ == "__main__":
    # Thay '12345678' bằng mật khẩu Neo4j Desktop của bạn
    db = KnowledgeGraphDB("neo4j://127.0.0.1:7687", "neo4j", "12345678")
    
    db.xoa_du_lieu_cu()
    db.tao_do_thi_tri_thuc()
    db.close()