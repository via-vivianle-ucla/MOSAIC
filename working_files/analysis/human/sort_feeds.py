import json

# STEP 1: Load the cleaned full dataset
with open("human_cleaned.jsonl", "r") as infile:
    full_cleaned_records = [json.loads(line) for line in infile]

# STEP 2: Split into two files — one for each feed
feed_1_output = []
feed_2_output = []

for rec in full_cleaned_records:
    pid = rec.get("prolific_id")
    feed_1_output.append({
        "prolific_id": pid,
        "actions": rec.get("social_feed_1", {}).get("actions", [])
    })
    feed_2_output.append({
        "prolific_id": pid,
        "actions": rec.get("social_feed_2", {}).get("actions", [])
    })

# STEP 3: Write each feed to a new JSONL file
with open("human_reactions_feed_1_cleaned.jsonl", "w") as f1:
    for entry in feed_1_output:
        f1.write(json.dumps(entry) + "\n")

with open("human_reactions_feed_2_cleaned.jsonl", "w") as f2:
    for entry in feed_2_output:
        f2.write(json.dumps(entry) + "\n")
