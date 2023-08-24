import sys
import subprocess
from pathlib import Path
from importlib import import_module

from loguru import logger

logger.add(Path(__file__).parent / "logs/{time}.log", rotation="12:00", compression="zip", backtrace=True, diagnose=True)


def main():
    install_dependencies()
    init_modules()


def install_dependencies():
    project_path = Path(__file__).parent
    return subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", project_path / "requirements.txt"])


def init_modules():
    module_paths = (Path(__file__).parent / "modules").iterdir()
    for module_path in module_paths:
        is_module = (module_path.is_file() and module_path.name.endswith(".py")) or \
                    (module_path.is_dir() and (module_path / "__init__.py").exists())
        if not is_module:
            continue

        module_name = module_path.name.rsplit(".py", 1)[0]
        logger.debug(f"importing module {module_name}")
        try:
            module = import_module(f"modules.{module_name}")
        except ModuleNotFoundError:
            logger.exception(f"cannot import {module_name}")
            continue

        if not (hasattr(module, "init") and callable(module.init)):
            logger.error(f"{module_name} is not MICA module")
            continue
        try:
            module.init()
        except:
            logger.exception(f"cannot init {module_name}")


if __name__ == "__main__":
    main()
