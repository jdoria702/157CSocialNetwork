from django.conf import settings
from neo4j import GraphDatabase

with GraphDatabase.driver(
    settings.NEO4J_URI,
    auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
) as driver:
    driver.verify_connectivity()


def create_user_node(user, bio=""):
    query = """
    CREATE (u:User {django_id: $django_id})
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

def get_all_users_except_current(current_user_id):
    query = """
    MATCH (u:User)
    WHERE u.django_id <> $current_user_id
    RETURN u
    """

    records, summary, keys = driver.execute_query(
        query,
        current_user_id=current_user_id
    )

    print(f"Retrieved all users except current user ID: {current_user_id}, in {summary.result_available_after} ms.")
    return [record["u"] for record in records]
    
def follow_user(current_user_id, target_user_id):
    query = """
    MATCH (follower:User {django_id: $current_user_id})
    MATCH (followee:User {django_id: $target_user_id})
    MERGE (follower)-[:FOLLOWS]->(followee)
    """

    summary = driver.execute_query(
        query,
        current_user_id=current_user_id,
        target_user_id=target_user_id
    ).summary

    print(f"User ID {current_user_id} followed user ID {target_user_id}, in {summary.result_available_after} ms."
          
)
    
def unfollow_user(current_user_id, target_user_id):
    query = """
    MATCH (follower:User {django_id: $current_user_id})-[r:FOLLOWS]->(followee:User {django_id: $target_user_id})
    DELETE r
    """

    summary = driver.execute_query(
        query,
        current_user_id=current_user_id,
        target_user_id=target_user_id
    ).summary

    print(f"User ID {current_user_id} unfollowed user ID {target_user_id}, in {summary.result_available_after} ms.")

def get_following(current_user_id):
    query = """
    MATCH (follower:User {django_id: $current_user_id})-[:FOLLOWS]->(followee:User)
    RETURN followee
    """

    records, summary, keys = driver.execute_query(
        query,
        current_user_id=current_user_id
    )

    print(f"Retrieved following list for user ID: {current_user_id}, in {summary.result_available_after} ms.")
    return [record["followee"] for record in records]

def get_followers(current_user_id):
    query = """
    MATCH (follower:User)-[:FOLLOWS]->(followee:User {django_id: $current_user_id})
    RETURN follower
    """

    records, summary, keys = driver.execute_query(
        query,
        current_user_id=current_user_id
    )

    print(f"Retrieved followers list for user ID: {current_user_id}, in {summary.result_available_after} ms.")
    return [record["follower"] for record in records]

def get_mutual_followers(current_user_id, other_user_id):
    query = """
    MATCH (u1:User {django_id: $current_user_id})-[:FOLLOWS]->(mutual:User)<-[:FOLLOWS]-(u2:User {django_id: $other_user_id})
    RETURN mutual
    """

    records, summary, keys = driver.execute_query(
        query,
        current_user_id=current_user_id,
        other_user_id=other_user_id
    )

    print(f"Retrieved mutual followers between user ID {current_user_id} and user ID {other_user_id}, in {summary.result_available_after} ms.")
    return [record["mutual"] for record in records]

def get_friend_recommendations(current_user_id, limit=5):
    query = """
    MATCH (u:User {django_id: $current_user_id})-[:FOLLOWS]->(f:User)-[:FOLLOWS]->(rec:User)
    WHERE NOT (u)-[:FOLLOWS]->(rec) AND u.django_id <> rec.django_id
    RETURN rec, COUNT(*) AS mutual_followers
    ORDER BY mutual_followers DESC
    LIMIT $limit
    """

    records, summary, keys = driver.execute_query(
        query,
        current_user_id=current_user_id,
        limit=limit
    )

    print(f"Retrieved friend recommendations for user ID: {current_user_id}, in {summary.result_available_after} ms.")
    return [record["rec"] for record in records]

def search_users(query, current_user_id):
    cypher = """
    MATCH (u:User)
    WHERE u.django_id <> $current_user_id
      AND (
        toLower(u.username) CONTAINS toLower($query)
        OR toLower(u.first_name) CONTAINS toLower($query)
        OR toLower(u.last_name) CONTAINS toLower($query)
      )
    RETURN u
    LIMIT 20
    """

    records, summary, keys = driver.execute_query(
        cypher,
        query=query,
        current_user_id=current_user_id
    )

    users = []

    for record in records:
        node = record["u"]
        users.append({
            "django_id": node["django_id"],
            "username": node.get("username", ""),
            "first_name": node.get("first_name", ""),
            "last_name": node.get("last_name", ""),
            "bio": node.get("bio", "")
        })

    return users

def get_popular_users(limit=5):
    query = """
    MATCH (u:User)<-[:FOLLOWS]-(follower:User)
    RETURN u, COUNT(follower) AS followers_count
    ORDER BY followers_count DESC
    LIMIT $limit
    """

    records, summary, keys = driver.execute_query(
        query,
        limit=limit
    )

    print(f"Retrieved popular users, in {summary.result_available_after} ms.")
    return [
        {
            "django_id": record["u"]["django_id"],
            "username": record["u"].get("username", ""),
            "first_name": record["u"].get("first_name", ""),
            "last_name": record["u"].get("last_name", ""),
            "bio": record["u"].get("bio", ""),
            "followers_count": record["followers_count"]
        }
        for record in records
    ]