# Quick test script
import sys
sys.path.insert(0, ".")
try:
    from backend.app.main import app
    from backend.app.services.config_service import config_service
    print("All imports OK!")
    print(f"App title: {app.title}")
    print(f"Config service loaded: {config_service.get_config().is_configured}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
