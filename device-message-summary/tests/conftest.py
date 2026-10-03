import warnings

# Suppress StarletteDeprecationWarning when importing FastAPI TestClient
warnings.filterwarnings("ignore", message=".*httpx.*")
warnings.filterwarnings("ignore", message=".*starlette.*")
