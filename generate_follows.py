import csv
import random

START_ID = 10001
END_ID = 11000
NUM_USERS = 100
NUM_FOLLOWS = 500

user_ids = list(range(START_ID, END_ID))
pairs = set()

while len(pairs) < NUM_FOLLOWS:
    follower_id = random.choice(user_ids)
    following_id = random.choice(user_ids)

    if follower_id != following_id:
        pairs.add((follower_id, following_id))

with open("data/follows.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["follower_id", "following_id"])
    writer.writerows(pairs)