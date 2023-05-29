from PIL import Image
import numpy as np
import json
import random
import time

BLANK = {
    "type": "BLANK",
    "timesRotated": 0
}

DEBUGGING = {
    "type": "DEBUGGING",
    "timesRotated": 0
}

CORNER_BEACH_IMAGE = Image.open('./res/tiles/CornerBeach.png')
SIDE_BEACH_IMAGE = Image.open('./res/tiles/SideBeach.png')
OCEAN_IMAGE = Image.open('./res/tiles/Ocean.png')
CORNER_LAND_IMAGE = Image.open('./res/tiles/CornerLand.png')
LAND_IMAGE = Image.open('./res/tiles/Land.png')
DIAGONAL_SPLIT_IMAGE = Image.open('./res/tiles/DiagonalSplit.png')

BLANK_IMAGE = Image.open('./res/tiles/BLANK.png')
DEBUGGING_IMAGE = Image.open('./res/tiles/DEBUGGING.png')

name_to_image = {'CornerBeach': CORNER_BEACH_IMAGE, 'SideBeach': SIDE_BEACH_IMAGE, 'Ocean': OCEAN_IMAGE, 
                 'CornerLand': CORNER_LAND_IMAGE, 'Land': LAND_IMAGE, 'DiagonalSplit': DIAGONAL_SPLIT_IMAGE,
                 'BLANK': BLANK_IMAGE, 'DEBUGGING': DEBUGGING_IMAGE}

#random.seed(a=9, version=2)

def populate_field(field, size, seed_json):
    # Populate field
    seeds = seed_json['seeds']
    for x in range(0, size):
        column_local = []
        for y in range(0, size):
            for seed in seeds:
                if x == seed['x'] and y == seed['y']:
                    column_local.append(seed['block'])
                else:
                    column_local.append(BLANK)
        field.append(column_local)

def get_most_restricted_node():
    max_restrictions = 0
    node_restriction_count = {}
    most_restricted_nodes = {'1': [], '2': [], '3': [], '4': [], '5': [], '6': [], '7': [], '8': []}

    for x in range(0, size):
        for y in range(0, size):
            if field[x][y] == BLANK:
                continue
            
            # Iterate around blocks to find restricted nodes
            for x_offset in range(-1, 2):
                for y_offset in range(-1, 2):
                    if x_offset == 0 and y_offset == 0:
                        continue
                    
                    target_x = x + x_offset
                    target_y = y + y_offset

                    # Disallow wrapping around array
                    if target_x < 0 or target_y < 0 or target_x > size - 1 or target_y > size - 1:
                        continue

                    # If it's collapsed, continue
                    if field[target_x][target_y] != BLANK:
                        continue

                    # If it's a non-collapsed node, store it

                    # Add to it's restriction count
                    node_coordinate = f'{target_x},{target_y}'
                    if node_restriction_count.get(node_coordinate) == None:
                        node_restriction_count[node_coordinate] = 1
                    else:
                        node_restriction_count[node_coordinate] += 1


                    target_node_restriction_count = node_restriction_count[node_coordinate]
                    if target_node_restriction_count > max_restrictions:
                        max_restrictions = target_node_restriction_count

                    if target_node_restriction_count == 8:
                        return (target_x, target_y)

                    # Add the node to it's new restriction count bracket
                    most_restricted_nodes[str(target_node_restriction_count)].append((target_x, target_y))
        
    msc = most_restricted_nodes[str(max_restrictions)]

    # Return a random one of the most restricted nodes
    random_most_restricted_node = random.choice(msc)

    return random_most_restricted_node

def has_empty_nodes(field):
    for column in field:
        for node in column:
            if node == BLANK:
                return True
    return False

# Setup field
constraints_json = open('./res/constraints.json')
constraints_json = json.load(constraints_json)

field = []

seed_json = open('./res/world_seed.json')
seed_json = json.load(seed_json)

size = seed_json['size']

populate_field(field, size, seed_json)

def wfc_cycle():
    most_restricted_node = get_most_restricted_node()

    x = most_restricted_node[0]
    y = most_restricted_node[1]

    legal_blocks = []

    constraints = [None] * 12
    
    for x_offset in range(-1, 2):
        for y_offset in range(-1, 2):
            if x_offset == 0 and y_offset == 0:
                continue

            surrounding_x = x + x_offset
            surrounding_y = y + y_offset

            # Disallow wrapping around array
            if surrounding_x < 0 or surrounding_y < 0 or surrounding_x > size - 1 or surrounding_y > size - 1:
                continue

            if field[surrounding_x][surrounding_y] == BLANK:
                continue

            surrounding_node = field[surrounding_x][surrounding_y]
            type = surrounding_node['type']
            times_rotated = surrounding_node['timesRotated']

            surrounding_node_constraints = constraints_json[type]['tags']

            # Adjust constraints based on node rotation
            adj_constraints = rotate_block_constraints(surrounding_node_constraints, times_rotated)

            # Get the indexes to check from the constraints
            host_index = get_host_index_from_coords(x_offset, y_offset)

            for index in host_index:
                constraints_index_to_check = index_map(index)
                constraint_applied = adj_constraints[constraints_index_to_check]
                constraints[index] = constraint_applied
    
    legal_blocks = get_legal_nodes_list(constraints)
    weighted_blocks_list = []

    node_to_place = DEBUGGING
    
    if len(legal_blocks) != 0:
        for node in legal_blocks:
            for _ in range(0, constraints_json[node['type']]['weight']):
                weighted_blocks_list.append(node)
        node_to_place = random.choice(weighted_blocks_list)
            

    field[x][y] = node_to_place

    output_field(field)

def index_map(index):
    if index == 0:
        return 6
    elif index == 1:
        return 8
    elif index == 2:
        return 7
    elif index == 3:
        return 9
    elif index == 4:
        return 11
    elif index == 5:
        return 10
    elif index == 6:
        return 0
    elif index == 7:
        return 2
    elif index == 8:
        return 1
    elif index == 9:
        return 3
    elif index == 10:
        return 5
    elif index == 11:
        return 4
    
def get_host_index_from_coords(x, y):
    if x == -1 and y == -1:
        return [0]
    elif x == 0 and y == -1:
        return [1, 2]
    elif x == 1 and y == -1:
        return [3]
    elif x == 1 and y == 0:
        return [4, 5]
    elif x == 1 and y == 1:
        return [6]
    elif x == 0 and y == 1:
        return [7, 8]
    elif x == -1 and y == 1:
        return [9]
    elif x == -1 and y == 0:
        return [10, 11]

def get_legal_nodes_list(constraints):
    block_types = ['Ocean', 'Land', 'SideBeach', 'CornerBeach', 'DiagonalSplit', 'CornerLand']
    blocks = []

    for block in block_types:
        for i in range(0, 4):
            blocks.append({
                "type": block,
                "timesRotated": i
            })

    legal_blocks = []

    for block in blocks:
        if check_block_legality(constraints, block):
            legal_blocks.append(block)

    return legal_blocks


def check_block_legality(constraints, node):
    node_constraints = constraints_json[node['type']]['tags']
    node_constraints = rotate_block_constraints(node_constraints, node['timesRotated'])

    for i in range(0, 12):
        constraint_passed = constraints[i]
        node_constraint = node_constraints[i]

        if node_constraint == 'all' or constraint_passed == None:
            continue

        if constraint_passed != node_constraint:
            return False
       
    return True

def rotate_block_constraints(constraints, times_rotated):
    removed_segment = constraints[0:times_rotated * 3]

    adj_constraints = constraints[times_rotated * 3:] + removed_segment

    return adj_constraints

def output_field(field):
    grid_size = 8 * size
    combined_image = np.zeros((grid_size, grid_size, 4), dtype=np.uint8)

    # Paste images into the combined image grid
    for x in range(0, size):
        for y in range(0, size):
            image = name_to_image[field[x][y]['type']]
            image_arr = np.array(image)
            for _ in range(0, field[x][y]['timesRotated']):
                image_arr = np.rot90(image_arr)
            x_offset = x * 8
            y_offset = y * 8
            combined_image[y_offset:y_offset+image.height, x_offset:x_offset+image.width, :] = image_arr

    combined_image = Image.fromarray(combined_image)
    combined_image.save('./out/map.png')

def wfc():
    while has_empty_nodes(field):
        wfc_cycle()

wfc()

output_field(field)