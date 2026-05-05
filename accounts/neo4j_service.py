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

    summary = driver.execute_query(query, django_id=user.id, username=user.username, email=user.email,
                                   first_name=user.first_name, last_name=user.last_name, bio=bio).summary
    
    print(f"Created/Updated Neo4j node for user: {user.username}, in {summary.result_available_after} ms.")
    return

def get_user_node(django_id):
    query = """
    MATCH (u:User {django_id: $django_id})
    RETURN u
    """

    records, summary, keys = driver.execute_query(
        query,
        django_id=django_id
    )

    if records:
        print(f"Retrieved Neo4j node for user ID: {django_id}, in {summary.result_available_after} ms.")
        return records[0]["u"]   # <-- this is the Node object
    
    print(f"No Neo4j node found for user ID: {django_id}, in {summary.result_available_after} ms.")
    return None

def update_user_node(user, bio=""):
    query = """
    MATCH (u:User {django_id: $django_id})
    SET u.username = $username,
        u.email = $email,
        u.first_name = $first_name,
        u.last_name = $last_name,
        u.bio = $bio
    RETURN u
    """

    records, summary, keys = driver.execute_query(
        query,
        django_id=user.id,
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        bio=bio
    )

    if records:
        print(f"Updated Neo4j node for user: {user.username}, in {summary.result_available_after} ms.")
        return records[0]["u"]   # Neo4j Node object

    print(f"No Neo4j node found for user: {user.username}, in {summary.result_available_after} ms.")
    return None