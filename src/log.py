import datetime

def log(level, msg):
    ts = datetime.datetime.utcnow().isoformat(timespec="seconds")
    print(f"[{ts}] [{level}] {msg}")

def info(msg): log("INFO", msg)
def warn(msg): log("WARN", msg)
def error(msg): log("ERROR", msg)
