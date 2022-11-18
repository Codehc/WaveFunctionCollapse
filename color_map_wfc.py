from PIL import Image
import numpy as np
import json
import random
import util
import time

RESTRICTION_RANGE = 20

FILE_NAME = 'field'

def fill_field(field, seeds, size, field_json):
    for y in range(0, size):
        row_local = []
        for x in range(0, size):
            seed_found = False
            for seed in seeds:
                if x == seed["x"] and y == seed["y"]:
                    seed_found = True
                    row_local.append((seed["red"], seed["green"], seed["blue"]))
            if seed_found == False:
                row_local.append((-1, -1, -1))
        field.append(row_local)
    
def get_most_restricted_pixel(field):
    max_restrictions = 0
    pixel_restriction_count = {}
    restriction_count = {'1': [], '2': [], '3': [], '4': [], '5': [], '6': [], '7': [], '8': []}

    # Iterate through pixels to find collapsed pixels
    for x in range(0, size):
        for y in range(0, size):
            if field[x][y] == (-1, -1, -1):
                continue

            # Collapsed pixel found
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
                    if field[target_x][target_y] != (-1, -1, -1):
                        continue

                    # If it's a non-collapsed pixel, store it

                    # Add to it's restriction count
                    pixel_key = f'{target_x},{target_y}'
                    if pixel_restriction_count.get(pixel_key) == None:
                        pixel_restriction_count[pixel_key] = 1
                    else:
                        pixel_restriction_count[pixel_key] += 1


                    target_pixel_restriction_count = pixel_restriction_count[pixel_key]
                    if target_pixel_restriction_count > max_restrictions:
                        max_restrictions = target_pixel_restriction_count

                    # Add the pixel to it's new restriction count bracket
                    restriction_count[str(target_pixel_restriction_count)].append((target_x, target_y))

    most_restricted_pixels = restriction_count[str(max_restrictions)]

    # Return a random one of the most restricted pixels
    random_most_restricted_pixel = random.choice(most_restricted_pixels)

    return random_most_restricted_pixel

def get_most_restricted_pixel_slow(field):
    max_restrictions = 0
    pixels = {}

    # Iterate through pixels to find the one with the most number of restrictions
    for x in range(0, size):
        for y in range(0, size):
            if field[x][y] != (-1, -1, -1):
                continue

            # Operate on individual pixel
            restricted_slots = 0
            # Iterate through slots around pixel to find collapsed pixels
            for x_offset in range(-1, 2):
                for y_offset in range(-1, 2):
                    if x_offset == 0 and y_offset == 0:
                        continue
                    target_x = x + x_offset
                    target_y = y + y_offset

                    # Disallow wrapping around array
                    if target_x < 0 or target_y < 0 or target_x > size - 1 or target_y > size - 1:
                        continue

                    if field[target_x][target_y] != (-1, -1, -1):
                        restricted_slots += 1;

            # Add pixel to dict with key corresponding to # of restrictions
            util.add_to_array_in_dict(pixels, restricted_slots, (x, y))

            if restricted_slots > max_restrictions:
                max_restrictions = restricted_slots

    # Get the array of pixels that have the most restrictions
    most_restricted_pixels = pixels[str(max_restrictions)]

    # Return a random one of the most restricted pixels
    random_most_restricted_pixel = random.choice(most_restricted_pixels)

    return random_most_restricted_pixel

def has_empty_pixels(field):
    for column in field:
        for pixel in column:
            if pixel == (-1, -1, -1):
                return True
    return False

# Setup timing variables
hep_time = time.time()
hep_times = []

mrp_time = 0
mrp_times = []

cr_time = 0
cr_times = []

si_time = 0
si_times = []

# Setup field
field_json = open(f'{FILE_NAME}.json')
field_json = json.load(field_json)

field = []
seeds = field_json['seeds']
size = field_json['size']
fill_field(field, seeds, size, field_json)

# Run WFC
while has_empty_pixels(field):
    hep_times.append(time.time() - hep_time)

    mrp_time = time.time()
    # Pixel info
    most_restricted_pixel = get_most_restricted_pixel(field)
    mrp_times.append(time.time() - mrp_time)
    x = most_restricted_pixel[0]
    y = most_restricted_pixel[1]

    # Restriction info
    restriction_reds = []
    restriction_greens = []
    restriction_blues = []

    # Iterate through slots around pixel to find collapsed pixels and calculate restrictions
    cr_time = time.time()
    for x_offset in range(-1, 2):
        for y_offset in range(-1, 2):
            if x_offset == 0 and y_offset == 0:
                continue
            target_x = x + x_offset
            target_y = y + y_offset

            # Disallow wrapping around array
            if target_x < 0 or target_y < 0 or target_x > size - 1 or target_y > size - 1:
                continue

            target_pixel = field[target_x][target_y]
            if target_pixel != (-1, -1, -1):
                # Add restriction info to restriction arrays
                restriction_reds.append(target_pixel[0])
                restriction_greens.append(target_pixel[1])
                restriction_blues.append(target_pixel[2])
    cr_times.append(time.time() - cr_time)

    # Calculate restriction center
    average_restriction_red = sum(restriction_reds) / len (restriction_reds)
    average_restriction_green = sum(restriction_greens) / len(restriction_greens)
    average_restriction_blue = sum(restriction_blues) / len(restriction_blues)

    # Calculate restriction ranges
    red_restriction_range = range(int(average_restriction_red - RESTRICTION_RANGE / 2), int(average_restriction_red + RESTRICTION_RANGE / 2 + 1))
    green_restriction_range = range(int(average_restriction_green - RESTRICTION_RANGE / 2), int(average_restriction_green + RESTRICTION_RANGE / 2 + 1))
    blue_restriction_range = range(int(average_restriction_blue - RESTRICTION_RANGE / 2), int(average_restriction_blue + RESTRICTION_RANGE / 2 + 1))

    # Pick values within restriction ranges
    red_value = random.choice(red_restriction_range)
    green_value = random.choice(green_restriction_range)
    blue_value = random.choice(blue_restriction_range)
    util.clamp(red_value, 0, 255)
    util.clamp(green_value, 0, 255)
    util.clamp(blue_value, 0, 255)

    # Set pixel to use values
    field[x][y] = (red_value, green_value, blue_value)

    #print(f'Pixel at ({x}, {y}) ranges: {restriction_reds} {restriction_greens} {restriction_blues} set to ({red_value}, {green_value}, {blue_value})')

    # Use PIL to create an image from the new array of pixels

    #time.sleep(0.5)
    si_time = time.time()
    array = np.array(field, dtype=np.uint8)
    new_image = Image.fromarray(array)
    new_image.save(f'{FILE_NAME}.png')
    si_times.append(time.time() - si_time)

    hep_time = time.time()

hep_time = sum(hep_times) / len(hep_times)
mrp_time = sum(mrp_times) / len(mrp_times)
cr_time = sum(cr_times) / len(cr_times)
si_time = sum(si_times) / len(si_times)
print(f"Average HEP time: {(hep_time):.20f}")
print(f"Average MRP time: {(mrp_time):.20f}")
print(f"Average CR time: {(cr_time):.20f}")
print(f"Average SI time: {(si_time):.20f}")
