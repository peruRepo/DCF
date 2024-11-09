import statistics


def find_average_each_element(statement):
    averages = {}
    statementObj = {};
    # Iterate over the object array
    for obj in statement:
        # Iterate over the keys and values in each object
        for key, value in obj.items():
            # If the key is not already in the averages dictionary, add it
            if key not in averages:
                averages[key] = []
            # Append the value to the list for the key
            if not (str(key) == "date"):
                if(str(value) == ""):
                    value = 0;
                averages[key].append(float(value))

    # Find the average for each key
    for key, values in averages.items():
        if not (str(key) == "date"):
            statementObj[key] = sum(values) / len(values)

    statement.append(statementObj)

    return statement

