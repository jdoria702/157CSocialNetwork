from django.conf import settings
from neo4j import GraphDatabase

with GraphDatabase.driver(
    settings.NEO4J_URI,
    auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
) as driver:
    driver.verify_connectivity()


def create_user_node(user, bio=""):
    query = """
    MERGE (u:User {django_id: $django_id})
    SET u.username = $username,
        u.email = $email,
        u.first_name = $first_name,
        u.last_name = $last_name,
        u.bio = $bio
    """

    # with driver.session() as session:
    #     session.run(
    #         query,
    #         django_id=user.id,
    #         username=user.username,
    #         email=user.email,
    #         first_name=user.first_name,
    #         last_name=user.last_name,
    #         bio=bio
    #     )
    #     print(f"Created/Updated Neo4j node for user: {user.username}")

    summary = driver.execute_query(query, django_id=user.id, username=user.username, email=user.email,
                                   first_name=user.first_name, last_name=user.last_name, bio=bio).summary
    
    print(f"Created/Updated Neo4j node for user: {user.username}, in {summary.result_available_after} ms.")