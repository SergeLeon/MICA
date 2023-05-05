from pathlib import Path
from importlib import import_module


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
        print(f"DEBUG: importing module {module_name}")
        try:
            module = import_module(f"modules.{module_name}")
        except ModuleNotFoundError as exc:
            print(f"WARNING: cannot import {module_name}")
            print(exc)
            continue

        if hasattr(module, "init") and callable(module.init):
            module.init()
        else:
            print(f"WARNING: {module_name} is not MICA module")


if __name__ == "__main__":
    main()
