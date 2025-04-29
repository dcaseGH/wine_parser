from Wine import Wine

def split_year(my_string):
    """
    Splits a string into name and year.
    
    Args:
        my_string (str): The string to split.
        
    Returns:
        tuple: A tuple containing the name and year.
    """
    parts = my_string.split()
    if len(parts) > 1 and parts[-1].isdigit():
        year = parts[-1]
        name = ' '.join(parts[:-1])
        return name, year
    else:
        return my_string, None

with open('grapeandgrind.co.uk.txt', 'r') as f:
    wine_list = []
    lines = f.readlines()
    for il, l in enumerate(lines):
#        print(l.strip())
        # Look for the pound sign
        if (ord(l[0]) == 163):
            name, year = split_year(lines[il-1].strip())
            wine = Wine(name)
            wine.year = year
            wine.cost = lines[il+1].strip()
            wine_list.append(wine)

print([w.__str__() for w in wine_list])
