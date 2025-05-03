import json

# Step 1: Load agents_cleaned.jsonl (demographics with old prolific_ids)
with open("agents_cleaned.jsonl") as f:
    demo_rows = [json.loads(line) for line in f]

# Step 2: Load correct prolific_ids from agent reactions file
with open("agent_reactions_feed_2_by_user.jsonl") as f:
    agent_ids = [json.loads(line)["prolific_id"] for line in f]

# Step 3: Replace each agent's prolific_id with the one from the reactions
aligned_demo_rows = []
for new_id, demo_row in zip(agent_ids, demo_rows):
    demo_copy = demo_row.copy()
    demo_copy["prolific_id"] = new_id  # overwrite with the reaction ID
    aligned_demo_rows.append(demo_copy)

# Step 4: Save to new file
with open("agents_aligned_demographics2.jsonl", "w") as out:
    for row in aligned_demo_rows:
        out.write(json.dumps(row) + "\n")
