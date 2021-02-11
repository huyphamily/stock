def convert_to_csv_format(array_data):
    output = ''

    for data in array_data:
        output += ",".join(str(data) for data in data.values())
        output += '\n'

    return output
