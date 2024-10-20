import ast
import json
import os
import re
import io


def count_connections():
    # Specify the directory path (can be absolute or relative)
    directory_path = 'connection-lists'  # Change this to your directory path
    total_connections = 0
    file_info: list[tuple[str, int]] = []
    # example_dict = {
    #     "usr": "suzannecampi",
    #     "name": "Suzanne Campi",
    #     "works_at": ["Microsoft"],
    #     "worked_at": ["Meta", "Apple", "Google"],
    #     "first_deg": ["karimi", "andylukens"]
    # }
    second_deg_connections = {}

    # Loop through each file in the directory
    for filename in os.listdir(directory_path):
        if filename != "nasser-vaziri.txt" and filename != "yatharth.txt":
            print(filename)
            continue
        # Construct the full file path
        file_path = os.path.join(directory_path, filename)

        # Check if it's a file and not a directory
        if os.path.isfile(file_path):
            usr, _ = os.path.splitext(filename)
            usrs_connections = 0
            # Open and read the file
            with open(file_path, 'r') as ff:
                for line in ff.readlines():
                    if line.startswith('#'):
                        continue
                    if line.rstrip('\n') in second_deg_connections:
                        second_deg_connections[line.rstrip('\n')].append(usr)
                    else:
                        second_deg_connections[line.rstrip('\n')] = [usr]

            # total_connections += usrs_connections
            # file_info.append((filename, usrs_connections))

    with open('nasser-yatharth.txt', 'w') as ff:
        for key, value in second_deg_connections.items():
            ff.write(f"('{key}', {value})\n")
    # print(f"Total connections: {total_connections}")
    # distribute_files(file_info)


def read_jumbo() -> list[tuple[str, list[str]]]:
    second_deg_conns: list[tuple[str, list[str]]] = []
    with open('jumbo_list.txt', 'r') as ff:
        for line in ff.readlines():
            second_deg_conns.append(ast.literal_eval(line.rstrip('\n')))
    return second_deg_conns


def remove_first_deg_connections(second_deg_conns: list[tuple[str, list[str]]]):
    first_deg_conns: list[str] = []
    with open('mine.txt', 'r') as ff:
        for line in ff.readlines():
            pattern = re.compile(r'https://www.linkedin.com/in/(.*?)/')
            first_deg_conns.append(pattern.findall(line)[0])

    for second_deg_conn in second_deg_conns:
        if second_deg_conn[0] in first_deg_conns:
            second_deg_conns.remove(second_deg_conn)

    with open('jumbo_list.txt', 'w') as ff:
        for second_deg_conn in second_deg_conns:
            ff.write(f"{second_deg_conn}\n")


def distribute_files(file_info: list[tuple[str, int]]):
    instances = 10
    # Sort the files by usernames count (you can reverse the order if you prefer)
    file_info.sort(key=lambda x: x[1])

    # Initialize data structures to hold the distribution
    distribution = {i: [] for i in range(instances)}  # Files assigned to each instance
    load = {i: 0 for i in range(instances)}  # Sum of usernames for each instance

    # Distribute files
    for filename, count in file_info:
        # Find the instance with the minimum load
        min_load_instance = min(load, key=load.get)

        # Assign the file to this instance
        distribution[min_load_instance].append(filename)

        # Update the load for this instance
        load[min_load_instance] += count

    # At this point, `distribution` holds the filenames for each instance,
    # and `load` shows the total usernames count each instance will process.
    print(load)


def slice_file():
    with open('jumbo_list.txt', 'r') as ff:
        lines = ff.readlines()

    lines_per_instance = 9010
    instances = [lines[0:(1 * lines_per_instance)],
                 lines[(1 * lines_per_instance):(2 * lines_per_instance)],
                 lines[(2 * lines_per_instance):(3 * lines_per_instance)],
                 lines[(3 * lines_per_instance):(4 * lines_per_instance)],
                 lines[(4 * lines_per_instance):(5 * lines_per_instance)],
                 lines[(5 * lines_per_instance):(6 * lines_per_instance)],
                 lines[(6 * lines_per_instance):(7 * lines_per_instance)],
                 lines[(7 * lines_per_instance):(8 * lines_per_instance)],
                 lines[(8 * lines_per_instance):(9 * lines_per_instance)],
                 lines[(9 * lines_per_instance):(10 * lines_per_instance) - 1]]

    ii = 0
    for instance in instances:
        with open(f"2nd-deg-conns/{ii}.txt", 'w') as ff:
            for entry in instance:
                ff.write(entry)
        ii += 1


def missing_connections():
    directory_path = 'connection-lists'

    # Loop through each file in the directory
    for filename in os.listdir(directory_path):
        # Construct the full file path
        file_path = os.path.join(directory_path, filename)

        # Check if it's a file and not a directory
        if os.path.isfile(file_path):
            usr, _ = os.path.splitext(filename)
            with open(file_path, 'r') as ff:
                for line in ff.readlines():
                    if 'Missed pages' in line:
                        pattern = re.compile(r'Missed pages: (\[.*?])')
                        pages = pattern.findall(line)
                        pages = ast.literal_eval(pages[0])
                        if len(pages) > 1:
                            print(pages)


def missing_experience():
    directory_path = '2nd-deg-conns/'
    missing: list[dict] = []
    # Loop through each file in the directory
    for filename in os.listdir(directory_path):
        if filename.endswith('.json') and 'consolidated' not in filename:
            # Construct the full file path
            file_path = os.path.join(directory_path, filename)
            # Check if it's a file and not a directory
            if os.path.isfile(file_path):
                with open(file_path, 'r') as ff:
                    for line in ff.readlines():
                        usr = json.loads(line)
                        if 'works_at' not in usr and 'worked_at' not in usr:
                            missing.append(usr)

    with open('2nd-deg-conns/10.txt', 'a') as ff:
        for usr in missing:
            ff.write(f"('{usr['usr']}', {usr['first_deg']})\n")
    print(f"\nMissing {len(missing)}")


def consolidate_clean():
    directory_path = '2nd-deg-conns/'
    # Loop through each file in the directory
    for filename in os.listdir(directory_path):
        if filename.endswith('.json') and 'consolidated' not in filename and int(filename.removesuffix('.json')) >= 12:
            # Construct the full file path
            file_path = os.path.join(directory_path, filename)
            # Check if it's a file and not a directory
            if os.path.isfile(file_path):
                with open(file_path, 'r') as ff:
                    for line in ff.readlines():
                        usr = json.loads(line)
                        if 'works_at' in usr or 'worked_at' in usr:
                            with open(os.path.join(directory_path, 'consolidated3.json'), 'a') as ff2:
                                try:
                                    clean_usrs = [json.loads(line) for line in ff.readlines()]
                                    if not any(cu['usr'] == usr['usr'] for cu in clean_usrs):
                                        ff2.write(f"{json.dumps(usr)}\n")
                                except io.UnsupportedOperation:
                                    ff2.write(f"{json.dumps(usr)}\n")


def clean_dicts():
    path = '2nd-deg-conns/consolidated3.json'
    remove_white = '<span class=\"white-space-pre\">'
    remove_visual = '<span class=\"visually-hidden\">'
    remove_span = '</span>'
    remove_br = '<br>'

    with open(path, 'r') as ff:
        for line in ff.readlines():
            usr = json.loads(line)
            if 'works_at' in usr:
                for ii, entry in enumerate(usr['works_at']):
                    clean = entry.replace(remove_white, '').replace(remove_visual, '').replace(remove_span, '').replace(
                        remove_br, '')
                    usr['works_at'][ii] = clean.strip()
                    print(f"removing present {usr['works_at'][ii]}")
            if 'worked_at' in usr:
                for ii, entry in enumerate(usr['worked_at']):
                    clean = entry.replace(remove_white, '').replace(remove_visual, '').replace(remove_span, '').replace(
                        remove_br, '')
                    usr['worked_at'][ii] = clean.strip()
                    print(f"removing past {usr['worked_at'][ii]}")
            with open('2nd-deg-conns/consolidated_clean3.json', 'a') as ff2:
                ff2.write(f"{json.dumps(usr)}\n")


def remove_duplicates():
    first_deg_conns: list[str] = []
    with open('mine.txt', 'r') as ff:
        for line in ff.readlines():
            pattern = re.compile(r'https://www.linkedin.com/in/(.*?)/')
            first_deg_conns.append(pattern.findall(line)[0])

    with open('2nd-deg-conns/consolidated_clean.json', 'r') as ff:
        for line in ff.readlines():
            usr = json.loads(line)
            duplicate = False
            for conn in first_deg_conns:
                if conn == usr['usr']:
                    duplicate = True
                    print(f"Found duplicate: {usr}")
                    break
            if not duplicate:
                with open('2nd-deg-conns/consolidated_clean2.json', 'a') as ff2:
                    ff2.write(f"{json.dumps(usr)}\n")


# missing_connections()
# count_connections()
# remove_first_deg_connections(read_jumbo())
# slice_file()
# missing_experience()
# consolidate_clean()
clean_dicts()
# remove_duplicates()
