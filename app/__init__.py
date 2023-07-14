from sqlalchemy.ext.asyncio import create_async_engine
from config import DATABASE_URI

engine = create_async_engine(DATABASE_URI)

from app.common_requests import execute_insert
from app.common_requests import get_html
from app.users import process_all_names
from app.groups import process_all_fields
from app.events import fill_event_table_with_interval
from app.events import delete_events
