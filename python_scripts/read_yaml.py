import yaml

def replace_tabs_in_yaml(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    updated_content = content.replace('\t', ' ' * 4) # Replace with 4 spaces or desired indentation
    # print(f"Updated content:\n{updated_content}")
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

def print_yaml(yaml_data, level=0):
    indent = ' ' * (level * 4)
    if isinstance(yaml_data, dict):
        for key, value in yaml_data.items():
            if isinstance(value, int) \
               or isinstance(value, str) \
               or isinstance(value, float):
                print(f"{indent}{key}: {value}")
            else:
                print(f"{indent}{key}:")
                print_yaml(value, level + 1)
    elif isinstance(yaml_data, list):
        for item in yaml_data:
            print(f"{indent}-")
            print_yaml(item, level + 1)
    else:
        print(f"{indent}{yaml_data}")

# Example usage:
file_path = './rsss_config/cache_dm.out'
# Replace tabs with spaces in the YAML file
print(f"Replacing tabs with spaces in the YAML file: {file_path}")
replace_tabs_in_yaml(file_path)

with open(file_path, 'r') as file:
    content_lst = file.readlines()

print(f"Reading YAML file: {file_path}")
yaml_data = read_yaml_file(file_path)

if yaml_data:
    print("YAML content:")
    print_yaml(yaml_data)
