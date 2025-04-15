import yaml

def replace_tabs_in_yaml(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    updated_content = content.replace('\t', ' ' * 4) # Replace with 4 spaces or desired indentation
    # print(f"Updated content:\n{updated_content}")
    with open(file_path, 'w') as file:
        file.write(updated_content)

def extract_array_metrics(file_path, array_type="Data"):
    assert array_type in ["Data", "Tag"], \
        "Invalid array type. Choose 'Data' or 'Tag'."

    with open(file_path, 'r') as f:
        data = yaml.safe_load(f)

    array_side = "Data side" if array_type == "Data" else "Tag side"
    # Extracting required values
    access_time_ns = data['Time Components'][array_side]['Access time (with Output driver) (ns)']

    array_type_key = 'Data array' if array_type == "Data" else 'Tag array'
    height_mm = data['Area Components'][array_type_key]['Height (mm)']
    width_mm = data['Area Components'][array_type_key]['Width (mm)']

    leakage_power_mw = data['Power Components'][array_type_key]['Total leakage power of a bank (mW)']

    dynamic_read_core = data['Power Components'][array_type_key]['Total dynamic read energy/access (nJ)']
    dynamic_write_core = data['Power Components'][array_type_key]['Total dynamic write energy/access (nJ)']

    # Calculate total dynamic read/write energy by summing H-tree (0 here) and core read/write energy
    dynamic_read_nj = dynamic_read_core  # H-tree = 0, so no need to add
    dynamic_write_nj = dynamic_write_core  # H-tree = 0

    # Final result
    output_dict = {
        "access_time_ns": access_time_ns,
        "height_mm": height_mm,
        "width_mm": width_mm,
        "leakage_power_mw": leakage_power_mw,
        "dynamic_read_nj": dynamic_read_nj,
        "dynamic_write_nj": dynamic_write_nj,
    }

    return output_dict

def print_dict(dict_name, dict_value):
    print(f"{dict_name} = {{")
    for key, value in dict_value.items():
        print(f"    \"{key}\": {value},")
    print("}")

# Example usage:
if __name__ == "__main__":
    file_path = "./rsss_config/cache_dm_45nm_matched.cfg.stdout"  # Replace with your actual file path
    replace_tabs_in_yaml(file_path)
    result = extract_array_metrics(file_path)
    print_dict("data_array_45nm", result)

    result = extract_array_metrics(file_path, "Tag")
    print_dict("tag_array_45nm", result)
