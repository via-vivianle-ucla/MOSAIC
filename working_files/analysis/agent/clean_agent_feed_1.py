import json

# Step 1: Load the reactions.json file
with open("agent_reactions.json", "r") as f:
    user_reactions = json.load(f)

# Step 2: Define which post_ids belong to Feed 1
feed_1_post_ids = {
    "post-3fa5ef", "post-a02de3", "post-9e09d3", "post-c31764", "post-6be7d0",
    "post-a41a79", "post-b50e43", "post-3b6b25", "post-8b9e63", "post-e7bb58"
}

# Step 3: Separate actions into Feed 1 and BAD feed formats
feed_1_output = []
bad_feed_output = []

for user_id, data in user_reactions.items():
    feed1_actions = []
    bad_actions = []
    for action in data.get("actions", []):
        target = action.get("target")
        if target is None:
            continue
        target = target.strip()
        formatted_action = {k: v for k, v in action.items() if k in ["action", "target", "content"]}
        if target in feed_1_post_ids:
            feed1_actions.append(formatted_action)
        else:
            bad_actions.append(formatted_action)
    feed_1_output.append({"prolific_id": user_id, "actions": feed1_actions})
    bad_feed_output.append({"prolific_id": user_id, "actions": bad_actions})

# Step 4: Save to two JSONL files
with open("agent_reactions_feed_1_by_user.jsonl", "w") as f1:
    for entry in feed_1_output:
        f1.write(json.dumps(entry) + "\n")

with open("bad_feed_1.jsonl", "w") as bf:
    for entry in bad_feed_output:
        bf.write(json.dumps(entry) + "\n")
