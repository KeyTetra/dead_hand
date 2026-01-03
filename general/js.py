from datetime import datetime
import json
j = []
with open("list.txt", 'r', encoding='utf-8') as f:
    i = 0
    for line in f:
        # Process each line here
        print(line.strip())
        pack = {
            "id": i,
            "url": line.strip(),
            "timestamp": str(datetime.utcnow()),
            "status": 0
        }
        j.append(pack)
        i += 1

with open('data.json', 'w') as f:
    json.dump(j, f)