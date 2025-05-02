import json

# Step 1: Load the reactions.json file
with open("agent_reactions_feed2.json", "r") as f:
    user_reactions = json.load(f)

# Step 2: Define which post_ids belong to Feed 2
feed_2_post_ids = {
    "post-ddbcb2", "post-1718ae", "post-0e91a2", "post-cca0c0", "post-c890f0",
    "post-7d2e8b", "post-f7530f", "post-950c89", "post-c84e51", "post-29054b",
    "post-735100", "post-eda706", "post-9b758b", "post-ccb7b4", "post-21477d",
    "post-bd8ac4", "post-66bc98", "post-5de5ff", "post-6900e8", "post-33e715"
}

# Step 3: Separate actions into Feed 2 and BAD feed formats
feed_2_output = []
bad_feed_output = []

for user_id, data in user_reactions.items():
    feed2_actions = []
    bad_actions = []
    for action in data.get("actions", []):
        target = action.get("target")
        if target is None:
            continue
        target = target.strip()
        formatted_action = {k: v for k, v in action.items() if k in ["action", "target", "content"]}
        if target in feed_2_post_ids:
            feed2_actions.append(formatted_action)
        else:
            bad_actions.append(formatted_action)
    feed_2_output.append({"prolific_id": user_id, "actions": feed2_actions})
    bad_feed_output.append({"prolific_id": user_id, "actions": bad_actions})

# Step 4: Save to two JSONL files
with open("agent_reactions_feed_2_by_user.jsonl", "w") as f2:
    for entry in feed_2_output:
        f2.write(json.dumps(entry) + "\n")

with open("bad_feed_2.jsonl", "w") as bf:
    for entry in bad_feed_output:
        bf.write(json.dumps(entry) + "\n")
