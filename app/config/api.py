from config.renderer import ORJSONRenderer
import logging
from config.security.authentication import SessionAuthentication, TokenAuthentication
from ninja import NinjaAPI
from config.decorators import debug_superuser_member_required
from ovh_server.api import router as ovh_router

logger = logging.getLogger(__name__)

api = NinjaAPI(
    title="Picsellia API",
    csrf=True,
    auth=TokenAuthentication(),
    version="1",
    urls_namespace="api",
    renderer=ORJSONRenderer(),
    description="Picsellia API",
    docs_url="/docs",
)

api.add_router("v1", ovh_router, tags=["ovh", "job"])
