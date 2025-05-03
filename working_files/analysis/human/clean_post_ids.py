import json

# STEP 1: Define the mapping from placeholder post numbers to actual post_ids
feed_content_1_post_ids = [
    "post-3fa5ef", "post-a02de3", "post-9e09d3", "post-c31764", "post-6be7d0",
    "post-a41a79", "post-b50e43", "post-3b6b25", "post-8b9e63", "post-e7bb58"
]
feed_content_2_post_ids = [
    "post-ddbcb2", "post-1718ae", "post-0e91a2", "post-cca0c0", "post-c890f0",
    "post-7d2e8b", "post-f7530f", "post-950c89", "post-c84e51", "post-29054b",
    "post-735100", "post-eda706", "post-9b758b", "post-ccb7b4", "post-21477d",
    "post-bd8ac4", "post-66bc98", "post-5de5ff", "post-6900e8", "post-33e715"
]
post_id_mapping = {
    f"post-{i+1}": real_id
    for i, real_id in enumerate(feed_content_1_post_ids + feed_content_2_post_ids)
}

# STEP 2: Normalize feeds and remap post IDs
def normalize_and_remap(record):
    def normalize_feed(feed):
        if isinstance(feed, list):
            actions = []
            for item in feed:
                if isinstance(item, dict) and "actions" in item:
                    actions.extend(item["actions"])
                elif isinstance(item, dict):
                    actions.append(item)
            return {"actions": actions}
        elif isinstance(feed, dict):
            return {"actions": feed.get("actions", [])}
        else:
            return {"actions": []}

    record["social_feed_1"] = normalize_feed(record.get("social_feed_1", {}))
    record["social_feed_2"] = normalize_feed(record.get("social_feed_2", {}))

    for feed_key in ["social_feed_1", "social_feed_2"]:
        for action in record[feed_key]["actions"]:
            target = action.get("target")
            if target in post_id_mapping:
                action["target"] = post_id_mapping[target]
    
    return record

# STEP 3: Read input file, apply processing, and save output
def process_jsonl(input_path, output_path):
    with open(input_path, "r") as infile:
        records = [json.loads(line) for line in infile]

    cleaned_records = [normalize_and_remap(r) for r in records]

    with open(output_path, "w") as outfile:
        for rec in cleaned_records:
            outfile.write(json.dumps(rec) + "\n")

# Example usage
process_jsonl("human_unclean.jsonl", "human_cleaned.jsonl")
