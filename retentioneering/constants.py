"""
Default column names and constants used across the toolkit.
"""

# Default column names expected in event data
COL_USER_ID = "user_id"
COL_EVENT = "event"
COL_TIMESTAMP = "timestamp"

# Special synthetic event names
EVENT_SESSION_START = "session_start"
EVENT_SESSION_END = "session_end"
EVENT_PATH_START = "path_start"
EVENT_PATH_END = "path_end"

# Default parameters
DEFAULT_SESSION_TIMEOUT_MINUTES = 30
DEFAULT_MAX_STEPS = 20
DEFAULT_N_CLUSTERS = 3
