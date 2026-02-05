import re

TIME_RE = re.compile(r"^(\d{1,2}:\d{2})")


def parse_sauna_text(raw_text):
    lines = [l.strip() for l in raw_text.splitlines() if l.strip()]

    result = {
        "date": None,
        "leader": None,
        "sessions": [],
    }

    current_session = None
    
    IGNORE_PATTERNS = [
    "SEANS PŁATNY",
    "ZŁ",
]

    for line in lines:
        if any(p in line.upper() for p in IGNORE_PATTERNS):
            continue
        # DATA (np. "CZWARTEK – 5.02")
        date_match = re.search(r"\b\d{1,2}\.\d{1,2}\b", line)
        if date_match:
            result["date"] = date_match.group(0)
            continue

        # LIDER (linia capslock bez cyfr)
        if line.isupper() and not any(c.isdigit() for c in line):
            result["leader"] = line.title()
            continue

        # START SEANSU
        time_match = TIME_RE.match(line)
        if time_match:
            time_str = time_match.group(1)

            current_session = {
                "time": time_str,
                "description": line[len(time_str):].strip(),
            }

            result["sessions"].append(current_session)
            continue

        # DALSZY OPIS
        if current_session:
            current_session["description"] += " " + line

    return result
