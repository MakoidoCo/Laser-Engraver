import os, json, sys, logging
from typing import Dict

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
from Config.setup import *

# Configuración del logger
folder_creator_log = logging.getLogger(os.path.splitext(os.path.basename(__file__))[0])
folder_creator_log.addHandler(HANDLER)
folder_creator_log.setLevel(LOGLEVEL)

class FolderCreator:
    def __init__(self, base_path: str) -> None:
        self.base_path = base_path

    def create_folders(self, structure: Dict[str, any], parent_path: str = "") -> None:
        for key, value in structure.items():
            folder_path = os.path.join(parent_path, key) if parent_path else os.path.join(self.base_path, key)
            
            if os.path.exists(folder_path):
                folder_creator_log.warning(f"Folder already exists: {folder_path}")
            else:
                os.makedirs(folder_path, exist_ok=True)
                folder_creator_log.info(f"Created folder: {folder_path}")

            if isinstance(value, dict):
                self.create_folders(value, folder_path)
            else:
                for item in value:
                    item_folder_path = os.path.join(folder_path, item)
                    if os.path.exists(item_folder_path):
                        folder_creator_log.warning(f"Folder already exists: {item_folder_path}")
                    else:
                        os.makedirs(item_folder_path, exist_ok=True)
                        folder_creator_log.info(f"Created folder: {item_folder_path}")

def main() -> None:
    base_path = "Products"

    folder_creator_log.info("Starting folder creation process.")

    with open("Products/products.json", "r") as f:
        products = json.load(f)
        folder_creator_log.info("Opened products.json file.")

    creator = FolderCreator(base_path)
    creator.create_folders(products)

    folder_creator_log.info("Folder creation process completed.")

if __name__ == "__main__":
    main()
