import argparse
import os

def main():
    parser = argparse.ArgumentParser(description='Version Updater')
    parser.add_argument('--version', default="", help="New Version")
    args = parser.parse_args()
    version = os.getenv('VERSION') or args.version
    print(f"Version is {version}")

    with open('setup.py', 'r') as file:
        lines = file.readlines()

    version_line_index = None
    install_start_index = None
    install_end_index = None

    for i, line in enumerate(lines):
        stripped_line = line.strip()
        if stripped_line.startswith('version'):
            version_line_index = i
        elif stripped_line.startswith('install_requires=['):
            install_start_index = i
            # Find the end of the install_requires list
            for j in range(i + 1, len(lines)):
                if lines[j].strip().startswith('],'):
                    install_end_index = j
                    break

    if version_line_index is None:
        print("Version line not found in setup.py")
        return

    if install_start_index is None or install_end_index is None:
        print("install_requires section not found in setup.py")
        return

    # Read and format requirements without trailing comma for the last item
    with open('requirements.txt', 'r') as req_file:
        requirements = req_file.read().splitlines()

    formatted_requirements = []
    for idx, req in enumerate(requirements):
        comma = ',' if idx < len(requirements) - 1 else ''
        formatted_requirements.append(f"        '{req}'{comma}\n")

    # Build the new lines for setup.py
    new_lines = []
    for i, line in enumerate(lines):
        if i == version_line_index:
            new_lines.append(f'    version="{version}",\n')
        elif i == install_start_index:
            new_lines.append(line)
            new_lines.extend(formatted_requirements)
        elif install_start_index < i < install_end_index:
            continue  # Skip old install_requires lines
        else:
            new_lines.append(line)

    with open('setup.py', 'w') as file:
        file.writelines(new_lines)

if __name__ == '__main__':
    main()
