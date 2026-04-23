import datetime


def log(level: str, msg: str) -> None:
    ts = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    print(f"[{ts}] [{level}] {msg}")

def info(msg: str) -> None:
    log("INFO", msg)

def warn(msg: str) -> None:
    log("WARN", msg)

def error(msg: str) -> None:
    log("ERROR", msg)
