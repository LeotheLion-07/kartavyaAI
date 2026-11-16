import os
import sys

# Add backend directory to sys.path so backend modules and packages resolve properly
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
backend_dir = os.path.join(parent_dir, "backend")

if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# When running in serverless environments, default to writable /tmp storage
if os.getenv("VERCEL"):
    os.environ.setdefault("DATABASE_URL", "sqlite:////tmp/kartavya.db")
    os.environ.setdefault("UPLOAD_DIR", "/tmp/uploads")

from main import app  # noqa: E402
