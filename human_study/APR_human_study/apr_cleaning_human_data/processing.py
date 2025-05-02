import re
import json

# Define valid ranges for each feed
FEED_RANGES = {
    "social_feed_1": range(1, 11),
    "social_feed_2": range(11, 31)
}

# Normalize known variants to canonical labels
ACTION_ALIASES = {
    "like post": "like-post",
    "share post": "share-post",
    "comment post": "comment-post",
    "add note": "add-note",
    "ignore": "ignore"
}

# Regex patterns
COMMENT_PATTERN = re.compile(
    r"(?P<action>[\w-]+)\s*:\s*(?P<post>\d+)\s*:\s*(?P<text>.+)",
    re.IGNORECASE
)
LIST_PATTERN = re.compile(
    r"(?P<action>[\w-]+)\s*:\s*(?P<posts>[\d,\s]+)",
    re.IGNORECASE
)
def normalize_action(raw_action):
    raw_action = raw_action.strip().lower()
    for alias, canonical in ACTION_ALIASES.items():
        if raw_action.startswith(alias):
            return canonical
    return raw_action

def parse_feed(feed_key, raw_text, user_id):
    lines = raw_text.strip().splitlines()
    results = {k: [] for k in ["like-post", "share-post", "comment-post", "add-note", "ignore"]}
    valid_range = set(FEED_RANGES[feed_key])
    seen_posts = set()

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Try comment/add-note
        match_comment = COMMENT_PATTERN.match(line)
        if match_comment:
            action = normalize_action(match_comment.group("action"))
            post = int(match_comment.group("post"))
            if post not in valid_range:
                continue
            text = match_comment.group("text").strip()
            if action in results:
                  results[action].append(f"{post}: {text}")
            else:
                print(f"⚠️ Unknown normalized action: '{action}', skipping.")
                continue
            seen_posts.add(post)
            continue

        # Try like/share/ignore list
        match_list = LIST_PATTERN.match(line)
        if match_list:
            action = normalize_action(match_list.group("action"))
            post_ids = [int(p.strip()) for p in match_list.group("posts").split(",") if p.strip().isdigit()]
            filtered = [p for p in post_ids if p in valid_range]
            key = action if action in results else f"{action}-post"
            if key in results:
                try:
                    results[key].extend(filtered)
                    seen_posts.update(filtered)
                except KeyError:
                    print(f"⚠️ Skipping invalid manual action '{action}' for user {user_id}")
                    with open("rejected_lines.txt", "a", encoding="utf-8") as log:
                        log.write(f"{user_id} | {feed_key} | {line} | manual-keyerror\n")
                    continue
            else:
                print(f"⚠️ Unknown normalized action: '{action}', skipping user {user_id} line: '{line}'")
                with open("rejected_lines.txt", "a", encoding="utf-8") as log:
                    log.write(f"{user_id} | {feed_key} | {line} | unknown-list-action\n")
                continue
            continue

        # Unknown format — ask user
        print(f"Unknown line format for user {user_id} in {feed_key}: '{line}'")
        raw_input_action = input("Enter action type (like/share/comment/add-note/ignore) or 'skip': ").strip()
        action = normalize_action(raw_input_action)
        if raw_input_action == "skip":
            with open("rejected_lines.txt", "a", encoding="utf-8") as log:
                log.write(f"{user_id} | {feed_key} | {line}\n")
            continue
        if action in ["comment", "add-note"]:
            try:
                post = int(input("Enter post ID: "))
                if post not in valid_range:
                    continue
                text = input("Enter comment or note text: ")
                key = action if action in results else f"{action}-post"
                if key in results:
                    results[key].append(f"{post}: {text}")
                    seen_posts.add(post)
                else:
                    print(f"⚠️ Skipping invalid manual action '{action}' for user {user_id}")
                    with open("rejected_lines.txt", "a", encoding="utf-8") as log:
                        log.write(f"{user_id} | {feed_key} | {action}: {post}: {text} | manual-keyerror\n")
                    continue

            except ValueError:
                continue
        elif action in ["like", "share", "ignore"]:
            try:
                post_ids = input("Enter comma-separated post IDs: ")
                ids = [int(p.strip()) for p in post_ids.split(",")]
                filtered = [p for p in ids if p in valid_range]
                results[f"{action}-post"].extend(filtered)
                seen_posts.update(filtered)
            except ValueError:
                continue

    # Compute ignore: all valid posts not seen
    results["ignore"] = sorted(valid_range - seen_posts)
    return results

def flatten_feed_actions(feed_dict):
    actions = []
    for key, values in feed_dict.items():
        if not values:
            continue
        action_type = key.split("-")[0]
        if action_type in ["like", "share", "ignore"]:
            for post_id in values:
                actions.append({
                    "action": action_type,
                    "target": f"post-{post_id}"
                })
        elif action_type in ["comment", "add"]:
            for val in values:
                if isinstance(val, str) and ":" in val:
                    post_id, content = val.split(":", 1)
                    actions.append({
                        "action": action_type if action_type != "add" else "add-note",
                        "target": f"post-{post_id.strip()}",
                        "content": content.strip()
                    })
                else:
                    print(f"⚠️ Unexpected format in {key}: {val} — skipping.")
    return {"actions": actions}

def process_record(entry):
    result = {"prolific_id": entry["prolific_id"]}
    for feed_key in ["social_feed_1", "social_feed_2"]:
        parsed = parse_feed(feed_key, entry.get(feed_key, ""), entry.get("prolific_id", "unknown"))
        result[feed_key] = flatten_feed_actions(parsed)
    return result


# ---------- Example usage ----------

if __name__ == "__main__":
    # Replace this list with actual .jsonl or .csv parsing if needed
    raw_data = []
    input_path = "raw201to401.jsonl"
    with open(input_path, "r", encoding="utf-8") as infile:
        for line in infile:
            if line.strip():  # skip empty lines
                raw_data.append(json.loads(line))

    cleaned = [process_record(entry) for entry in raw_data]

    # Save to file
    with open("cleaned_social_data201to401.jsonl", "w") as f:
        for record in cleaned:
            f.write(json.dumps(record) + "\n")

    print("✅ Cleaned data saved to cleaned_social_data201to401.jsonl")
