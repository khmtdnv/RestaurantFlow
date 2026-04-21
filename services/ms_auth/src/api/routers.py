from api.auth import router as router_auth
from api.users import router as router_users

all_routers = [
    router_users,
    router_auth,
]
