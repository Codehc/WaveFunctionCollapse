# TODO Improve rng_world_constraints.json, constraints aren't 100% accurate. I think I missed some possible valid states for slots

from PIL import Image
import numpy as np
import json
import random
import time

BLANK = {
    "type": "BLANK",
    "timesRotated": 0
}

'''
"Ocean": {
        "tags": [
            [], // top
            [], // top right
            [], // right
            [], // bottom right
            [], // bottom
            [], // bottom left
            [], // left
            [] // top left
        ],
        "constraints": [
            [], // top
            [], // top right
            [], // right
            [], // bottom right
            [], // bottom
            [], // bottom left
            [], // left
            [] // top left
        ]
    }
'''

CORNER_BEACH_IMAGE = Image.open('./res/fewer_tiles/CornerBeach.png')
SIDE_BEACH_IMAGE = Image.open('./res/fewer_tiles/SideBeach.png')
OCEAN_IMAGE = Image.open('./res/fewer_tiles/Ocean.png')
CORNER_LAND_IMAGE = Image.open('./res/fewer_tiles/CornerLand.png')
LAND_IMAGE = Image.open('./res/fewer_tiles/Land.png')
DIAGONAL_SPLIT_IMAGE = Image.open('./res/fewer_tiles/DiagonalSplit.png')

BLANK_IMAGE = Image.open('./res/fewer_tiles/Blank.png')
DEBUGGING_IMAGE = Image.open('./res/fewer_tiles/DEBUGGING.png')

name_to_image = {'CornerBeach': CORNER_BEACH_IMAGE, 'SideBeach': SIDE_BEACH_IMAGE, 'Ocean': OCEAN_IMAGE, 
                 'CornerLand': CORNER_LAND_IMAGE, 'Land': LAND_IMAGE, 'DiagonalSplit': DIAGONAL_SPLIT_IMAGE,
                 'BLANK': BLANK_IMAGE, 'DEBUGGING': DEBUGGING_IMAGE}

random.seed(a=9, version=2)

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
constraints_json = open('./res/rng_world_fewer_blocks_constraints.json')
constraints_json = json.load(constraints_json)

field = []

seed_json = open('./res/world_seed_fewer_blocks.json')
seed_json = json.load(seed_json)

size = seed_json['size']

populate_field(field, size, seed_json)

def wfc_cycle():
    most_restricted_node = get_most_restricted_node()

    x = most_restricted_node[0]
    y = most_restricted_node[1]
    #print(f'  - Node: ({x}, {y})')

    legal_blocks = [{"type":"CornerBeach","timesRotated":0},{"type":"CornerBeach","timesRotated":1},{"type":"CornerBeach","timesRotated":2},{"type":"CornerBeach","timesRotated":3},{"type":"SideBeach","timesRotated":0},{"type":"SideBeach","timesRotated":1},{"type":"SideBeach","timesRotated":2},{"type":"SideBeach","timesRotated":3},{"type":"Land","timesRotated":0},{"type":"Ocean","timesRotated":0},{"type":"CornerLand","timesRotated":0},{"type":"CornerLand","timesRotated":1},{"type":"CornerLand","timesRotated":2},{"type":"CornerLand","timesRotated":3},{"type":"DiagonalSplit","timesRotated":0},{"type":"DiagonalSplit","timesRotated":1},{"type":"DiagonalSplit","timesRotated":2},{"type":"DiagonalSplit","timesRotated":3}]

    for x_offset in range(-1, 2):
        for y_offset in range(-1, 2):
            if x_offset == 0 and y_offset == 0:
                continue

            #print(f'  - Surrounding Offset: ({x_offset}, {y_offset})')

            surrounding_x = x + x_offset
            surrounding_y = y + y_offset

            #print(f'    - Surrounding Coords: ({surrounding_x}, {surrounding_y})')

            # Disallow wrapping around array
            if surrounding_x < 0 or surrounding_y < 0 or surrounding_x > size - 1 or surrounding_y > size - 1:
                #print(f'    - Skipped since Illegal Coords xxxxxxxxxxxxxxxxxxxx')
                continue

            #print(f'    - Surrounding Node Type: {field[surrounding_x][surrounding_y]}')

            if field[surrounding_x][surrounding_y] == BLANK:
                #print(f'    - Skipped since blank xxxxxxxxxxxxxxxxxxxx')
                continue

            surrounding_node = field[surrounding_x][surrounding_y]
            print(surrounding_node)
            surrounding_node_type = surrounding_node['type']
            surrounding_node_times_rotated = surrounding_node['timesRotated']

            surrounding_node_constraints = constraints_json[surrounding_node_type]

            legal_y_index = 1 - y_offset
            legal_x_index = 1 - x_offset
            
            surrounding_node_constraints_imposed = surrounding_node_constraints[legal_y_index][legal_x_index]
            imposed_constraints = []

            for constraint in surrounding_node_constraints_imposed:
                new_constraint = constraint
                new_constraint['timesRotated'] = (constraint['timesRotated'] + 1) % 3
                imposed_constraints.append(new_constraint)

            #print(f'    - Legal Blocks Before: {legal_blocks}')
            #print(f'    - Surrounding Node Constraints: {surrounding_node_constraints_imposed}')

            local_legal = []
            for legal_block in legal_blocks:
                if legal_block in imposed_constraints:
                    local_legal.append(legal_block)
            legal_blocks = local_legal

            #print(f'    - Legal Blocks After: {legal_blocks}')
    
    if len(legal_blocks) == 0:
        field[x][y] = {
            "type": "DEBUGGING",
            "timesRotated": 0
        }
    else:
        field[x][y] = random.choice(legal_blocks)
    
    #print(f'  - Final Block: {field[x][y]} out of {legal_blocks}')

def wfc():
    while has_empty_nodes(field):
        wfc_cycle()

starting_time = time.time()
for _ in range(0, 10): 
    wfc()

print(f'Average WFC time {(time.time() - starting_time) / 10}')

starting_time = time.time()

grid_size = 8 * size
combined_image = np.zeros((grid_size, grid_size, 4), dtype=np.uint8)

# Paste images into the combined image grid
for x in range(0, size):
    for y in range(0, size):
        image = name_to_image[field[x][y]]
        x_offset = x * 8
        y_offset = y * 8
        combined_image[y_offset:y_offset+image.height, x_offset:x_offset+image.width, :] = np.array(image)

combined_image = Image.fromarray(combined_image)
combined_image.save('generated_world_map.png')

print(f'Save time {(time.time() - starting_time)}')