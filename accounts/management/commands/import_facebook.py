import random
from django.core.management.base import BaseCommand
from accounts.neo4j_service import driver

# Synthetic users get django_ids starting here, so they never collide with real Django users.
ID_OFFSET = 1_000_000

FIRST_NAMES = [
    "Alex", "Sam", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Jamie",
    "Avery", "Quinn", "Drew", "Skyler", "Cameron", "Reese", "Parker", "Rowan",
    "Charlie", "Emerson", "Finley", "Hayden", "Kendall", "Logan", "Peyton",
    "Sage", "Blake", "Dakota", "Elliot", "Frankie", "Harper", "Jesse",
    "Kai", "Lane", "Marley", "Nico", "Oakley", "Phoenix", "River", "Shawn",
    "Tatum", "Wren", "Aiden", "Bailey", "Carter", "Devin", "Ellis", "Gray",
    "Indigo", "Justice", "Lennon", "Micah",
]

LAST_NAMES = [
    "Smith", "Johnson", "Lee", "Garcia", "Brown", "Davis", "Miller", "Wilson",
    "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris",
    "Martin", "Thompson", "Young", "King", "Wright", "Lopez", "Hill", "Scott",
    "Green", "Adams", "Baker", "Nelson", "Carter", "Mitchell", "Perez",
    "Roberts", "Turner", "Phillips", "Campbell", "Parker", "Evans", "Edwards",
    "Collins", "Stewart", "Sanchez", "Morris", "Rogers", "Reed", "Cook",
    "Morgan", "Bell", "Murphy", "Bailey", "Rivera", "Cooper",
]

BIOS = [
    "", "", "",
    "Coffee enthusiast.",
    "Just here to follow friends.",
    "Avid reader and weekend hiker.",
    "Software dev by day.",
    "Photographer and traveler.",
    "Music, movies, more music.",
    "Trying new recipes weekly.",
    "Sports fan.",
    "Student.",
]


def make_profile(node_id, rng):
    first = rng.choice(FIRST_NAMES)
    last = rng.choice(LAST_NAMES)
    username = f"{first.lower()}{last.lower()}{node_id}"
    return {
        "django_id": ID_OFFSET + node_id,
        "username": username,
        "email": f"{username}@example.com",
        "first_name": first,
        "last_name": last,
        "bio": rng.choice(BIOS),
    }


def batched(items, size):
    for i in range(0, len(items), size):
        yield items[i:i + size]


class Command(BaseCommand):
    help = "Import the SNAP ego-Facebook dataset into Neo4j as User nodes and FOLLOWS edges."

    def add_arguments(self, parser):
        parser.add_argument("--path", default="data/facebook_combined.txt",
                            help="Path to facebook_combined.txt edge list.")
        parser.add_argument("--seed", type=int, default=42)
        parser.add_argument("--mutual", type=float, default=0.35,
                            help="Fraction of edges that become mutual follows.")
        parser.add_argument("--batch", type=int, default=1000)
        parser.add_argument("--clear", action="store_true",
                            help="Delete previously imported synthetic users before importing.")

    def handle(self, *args, **opts):
        rng = random.Random(opts["seed"])

        driver.execute_query(
            "CREATE INDEX user_django_id IF NOT EXISTS FOR (u:User) ON (u.django_id)"
        )

        if opts["clear"]:
            self.stdout.write("Clearing previously imported synthetic users...")
            driver.execute_query(
                "MATCH (u:User) WHERE u.django_id >= $offset DETACH DELETE u",
                offset=ID_OFFSET,
            )

        self.stdout.write(f"Reading edges from {opts['path']}...")
        edges = []
        node_ids = set()
        with open(opts["path"]) as f:
            for line in f:
                a, b = line.split()
                a, b = int(a), int(b)
                edges.append((a, b))
                node_ids.add(a)
                node_ids.add(b)

        self.stdout.write(f"Found {len(node_ids)} nodes and {len(edges)} edges.")

        # Build user profiles.
        profiles = [make_profile(nid, rng) for nid in sorted(node_ids)]

        self.stdout.write("Creating User nodes...")
        for chunk in batched(profiles, opts["batch"]):
            driver.execute_query(
                """
                UNWIND $rows AS row
                MERGE (u:User {django_id: row.django_id})
                SET u.username = row.username,
                    u.email = row.email,
                    u.first_name = row.first_name,
                    u.last_name = row.last_name,
                    u.bio = row.bio
                """,
                rows=chunk,
            )

        # Convert undirected edges to directed FOLLOWS with the requested split.
        mutual = opts["mutual"]
        one_way = (1.0 - mutual) / 2.0
        directed = []
        for a, b in edges:
            r = rng.random()
            if r < mutual:
                directed.append((a, b))
                directed.append((b, a))
            elif r < mutual + one_way:
                directed.append((a, b))
            else:
                directed.append((b, a))

        self.stdout.write(f"Creating {len(directed)} FOLLOWS relationships...")
        rows = [{"a": ID_OFFSET + a, "b": ID_OFFSET + b} for a, b in directed]
        for chunk in batched(rows, opts["batch"]):
            driver.execute_query(
                """
                UNWIND $rows AS row
                MATCH (a:User {django_id: row.a})
                MATCH (b:User {django_id: row.b})
                MERGE (a)-[:FOLLOWS]->(b)
                """,
                rows=chunk,
            )

        self.stdout.write(self.style.SUCCESS("Import complete."))
