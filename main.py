from pathlib import Path
from importlib import import_module

from loguru import logger

logger.add("logs/{time}.log", rotation="12:00", compression="zip", backtrace=True, diagnose=True)


def main():
    init_modules()


def init_modules():
    module_paths = Path("modules").iterdir()
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

        if hasattr(module, "init") and callable(module.init):
            module.init()
        else:
            logger.error(f"{module_name} is not MICA module")


if __name__ == "__main__":
    main()
