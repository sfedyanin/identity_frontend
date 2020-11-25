import re

##########################
# 'all-auth' settings
##########################
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = "none"
SOCIALACCOUNT_QUERY_EMAIL = True
LOGIN_REDIRECT_URL = "/"

DATA_UPLOAD_MAX_NUMBER_FIELDS = 5000

###########################
# Identify settings
###########################
DATA_DIR = "/data"
DAG_DIR = "/data/dags"
MONGO_USERNAME = "vdx_agent"
MONGO_PASSWORD = "demo_password"
COLLECTION_DBNAME = "agent_collections"
AGENT_TASK_RESPONSE_DB = "task_status"
AGENT_COLLECTION_DB = "agent_collections"
AGENT_TASK_RESPONSE_COLL = "celery_taskmeta"

EXPLORER_CONNECTION_NAME = 'default'
EXPLORER_CONNECTIONS = {'default': 'default'}
EXPLORER_DEFAULT_CONNECTION = 'default'
EXPLORER_TASKS_ENABLED = True
EXPLORER_ASYNC_SCHEMA = True

ATTRIBUTE_REGEX = re.compile(r'\{([A-z_\.]+)\}')
COLL_TSTAMP = "%Y%m%dT%H%M%S"
# SERVERSIDE_TABLES:
# Tables rendered by the platform will be fitlered/searched on the server-side
SERVERSIDE_TABLES = False

# ACCESS_RECALCULATION_INTERVAL
# How long to wait (seconds) before re-evaluating the system access_items
ACCESS_RECALCULATION_INTERVAL = 10
PROPERTY_RECALC = 10

# Max depth of IAM network graph (500 generations, or levels by default)
MAX_IAM_NET_DEPTH = 500
# This configures the weights set by the IAM network for different features
# Each path is weighted at 1 by default.
# Each value is a delta which is added to the weight for each entity type
#   E.g. approval: 0.2, will give a role with 4 approvals a weight of 1.8
IAM_NETWORK_WEIGHTS = {
    "approval": 0.2,
}

# BATCH_TIMEOUT = 10
# BATCH_ARGS = ["host_string", "ssh_user"]

# AGENT_TASK_POOL_TIME: Duration(s) tasks remain in pool for batch submission
AGENT_TASK_POOL_TIME = 5
RETRY_BACKOFF = 2
MAX_WORKORDER_READ_RETRIES = 50
# Ensure this matches the AGENT CONFIGURATION!
PROPSEARCH_DEPTH_LIMIT = 50

WO_MANAGE_TIMEOUT = 30
SYNC_ACCESS_TIMEOUT = 300

MAPPING_PLATFORM_LOC = [-6.2489, 53.3331]

# Max amount of workorders to submit in a single iter of submit_pending_workorders()
MAX_ACTIVE_WO_PER_PLATFORM = 10

# How many separate tasks should be sent to the agent for a WorkOrder
#   e.g. a WO with 50 servers, and segmentation of 5 will send 5 tasks
#         each with the arguments for 10 servers 
# This allows for parallelisation if there are sufficient worker threads
WO_AGENT_TASK_SEGMENTATION = 5

# SQL explorer
EXPLORER_ENABLE_TASKS = False
EXPLORER_ASYNC_SCHEMA = False
