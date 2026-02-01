from .model import *


def parse_kv(line: str):
    result = {}
    for token in line.split():
        if "=" in token:
            k, v = token.split("=", 1)
            if "|" in v:
                result[k] = v.split("|")
            else:
                result[k] = v
    return result


def parse_declare(lines):
    area = None
    nodes = {}

    for line in lines:
        line = line.strip()
        if not line or line.startswith("--"):
            continue

        fields = parse_kv(line)

        if "area" in fields:
            w, h = map(float, fields["area"])
            area = Area(w, h)

        elif "node" in fields:
            nid = fields["node"]
            color = tuple(map(int, fields["color"]))
            buffer_size = int(fields.get("buffer", 0))

            ranges = []
            if "range" in fields:
                ranges = list(map(float, fields["range"]))

            nodes[nid] = Node(
                nid=nid,
                type=fields["type"],
                group=int(fields.get("group", 0)),
                color=color,
                buffer_size=buffer_size,
                ranges=ranges,
            )

    return area, nodes


def parse_events(lines):
    timeline = []
    current_time = None
    current_events = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.startswith("Time="):
            if current_time is not None:
                timeline.append(TimeFrame(current_time, current_events))
            current_time = float(line.split("=")[1])
            current_events = []
            continue

        fields = parse_kv(line)
        if "event" in fields:
            current_events.append(Event(fields["event"], fields))

    if current_time is not None:
        timeline.append(TimeFrame(current_time, current_events))
    
    timeline.sort(key=lambda tf: tf.time)

    merged = [] # merge timeFrame with equam times
    for tf in timeline:
        if not merged or merged[-1].time != tf.time:
            merged.append(TimeFrame(tf.time, list(tf.events)))
        else:
            merged[-1].events.extend(tf.events)

    return merged
    # return timeline


def parse_log_file(filename):
    declare_lines = []
    event_lines = []
    mode = None

    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            if line.startswith("--Declare"):
                mode = "declare"
                continue
            elif line.startswith("--Events"):
                mode = "events"
                continue

            if mode == "declare":
                declare_lines.append(line)
            elif mode == "events":
                event_lines.append(line)

    area, nodes = parse_declare(declare_lines)
    timeline = parse_events(event_lines)

    return area, nodes, timeline
