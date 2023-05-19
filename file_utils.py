import os

def print_directory_tree(root_path, indent=''):
    items = os.listdir(root_path)
    directories = sorted([item for item in items if os.path.isdir(os.path.join(root_path, item))])
    files = sorted([item for item in items if os.path.isfile(os.path.join(root_path, item))])
    
    for item in directories + files:
        if item.startswith('.') or item.startswith('__'):
            continue
        item_path = os.path.join(root_path, item)
        if os.path.isdir(item_path):
            print(f"{indent}|- {item}/")
            print_directory_tree(item_path, indent + '   ')
        else:
            print(f"{indent}|- {item}")

current_dir = os.path.abspath(os.path.dirname(__file__))
print_directory_tree(current_dir)
