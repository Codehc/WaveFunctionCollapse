def add_to_array_in_dict(dictionary, key, value_to_add):
    # Method will return None of key doesn't exist
    if dictionary.get(str(key)) == None:
        dictionary[str(key)] = [value_to_add]
    else:
        dictionary[str(key)].append(value_to_add)

def clamp(input, min, max):
    if input < min:
        input = min
    elif input > max:
        input = max
    return input