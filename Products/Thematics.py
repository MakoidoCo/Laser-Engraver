import os
import json

def create_folders(base_path, structure):
    for key, value in structure.items():
        folder_path = os.path.join(base_path, key)
        if not os.path.exists(folder_path):  # Verificar si la carpeta ya existe
            os.makedirs(folder_path)
        
        if isinstance(value, dict):
            create_folders(folder_path, value)
        else:
            for item in value:
                item_folder_path = os.path.join(folder_path, item)
                if not os.path.exists(item_folder_path):  # Verificar si la carpeta ya existe
                    os.makedirs(item_folder_path)

# Directorio base donde se crearán las carpetas
base_path = 'Products'

# Cargar la estructura de productos desde JSON
with open('products.json', 'r') as f:
    products = json.load(f)

# Crear las carpetas según la estructura definida en 'products'
create_folders(base_path, products)
