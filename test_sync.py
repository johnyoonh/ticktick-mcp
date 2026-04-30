import asyncio
from ticktick_mcp.src.db import batch_check, init_db
init_db()
asyncio.run(batch_check('checkpoint'))
