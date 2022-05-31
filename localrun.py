import os
import re

import uvicorn
from dotenv import load_dotenv


load_dotenv()

if __name__ == "__main__":
    from hatch.app import app

    RELEASE_HOST = os.environ.get("RELEASE_HOST", default=None)

    if RELEASE_HOST:
        m = re.match(r"https?://([^:]+):(\d+)", RELEASE_HOST)
        if m:
            host = m.group(1)
            port = int(m.group(2))

            uvicorn.run(app, host=host, port=port)
