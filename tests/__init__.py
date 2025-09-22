import json
from pathlib import Path

import fractal_tasks_template

PACKAGE_DIR = Path(fractal_tasks_template.__file__).parent
MANIFEST_FILE = PACKAGE_DIR / "__FRACTAL_MANIFEST__.json"
with MANIFEST_FILE.open("r") as f:
    MANIFEST = json.load(f)
