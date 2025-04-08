class DevelopmentError(Exception):
    def __init__(self, msg: str):
        message = f"""If you are seeing this, it means something happened that should not have happened.
If you are not the developer, know that this isn't your fault. If you would please contact the developers
and explain to them what happened, that would be very much appreciate it as it will help us fix the issue.
If you are the developer, then it's time to breakout the debugger and do a trace.

Error: {msg}
"""
        super().__init__(message)