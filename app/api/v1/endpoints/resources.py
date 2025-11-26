from fastapi import APIRouter

from app.db.sql.models.station import Station
from app.db.sql.models.crawler import Crawler
from app.db.sql.models.platform import Platform
from app.db.sql.models.black import Black
from app.db.sql.models.rt import Rt
from app.db.sql.models.role import Role

from app.domain.schemas import resources as schemas
from app.api.factories.crud_router import create_crud_router

# Main router that holds all sub-routers
router = APIRouter()

# 1. Stations
router.include_router(create_crud_router(
    model_class=Station,
    read_schema=schemas.StationRead,
    create_schema=schemas.StationCreate,
    update_schema=schemas.StationUpdate,
    prefix="/stations",
    tags=["Stations"]
))

# 2. Crawlers
router.include_router(create_crud_router(
    model_class=Crawler,
    read_schema=schemas.CrawlerRead,
    create_schema=schemas.CrawlerCreate,
    update_schema=schemas.CrawlerUpdate,
    prefix="/crawlers",
    tags=["Crawlers"]
))

# 3. Platforms
router.include_router(create_crud_router(
    model_class=Platform,
    read_schema=schemas.PlatformRead,
    create_schema=schemas.PlatformCreate,
    update_schema=schemas.PlatformUpdate,
    prefix="/platforms",
    tags=["Platforms"]
))

# 4. Blacks
router.include_router(create_crud_router(
    model_class=Black,
    read_schema=schemas.BlackRead,
    create_schema=schemas.BlackCreate,
    update_schema=schemas.BlackUpdate,
    prefix="/blacks",
    tags=["Blacks"]
))

# 5. Roles
router.include_router(create_crud_router(
    model_class=Role,
    read_schema=schemas.RoleRead,
    create_schema=schemas.RoleCreate,
    update_schema=schemas.RoleUpdate,
    prefix="/roles",
    tags=["Roles"]
))

# 6. RTs
router.include_router(create_crud_router(
    model_class=Rt,
    read_schema=schemas.RtRead,
    create_schema=schemas.RtCreate,
    update_schema=schemas.RtUpdate,
    prefix="/rts",
    tags=["RTs"]
))