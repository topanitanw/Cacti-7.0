import yaml

def replace_tabs_in_yaml(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    updated_content = content.replace('\t', ' ' * 4) # Replace with 4 spaces or desired indentation
    print(f"Updated content:\n{updated_content}")
    with open(file_path, 'w') as file:
        file.write(updated_content)

def read_yaml_file(file_path):
    with open(file_path, 'r') as file:
        try:
            data = yaml.safe_load(file)
            return data
        except yaml.YAMLError as e:
            print(f"Error reading YAML file: {e}")
            return None

# Example usage:
file_path = 'rsss_config/cache_dm.out'
replace_tabs_in_yaml(file_path)

with open(file_path, 'r') as file:
    content_lst = file.readlines()

# print(f"Content list: {content_lst[88:92]}")
# print(f"err line: |{content_lst[231]}|")
# print(f"err char: |{content_lst[231][38:45]}|")
yaml_data = read_yaml_file(file_path)

if yaml_data:
    print(yaml_data)
