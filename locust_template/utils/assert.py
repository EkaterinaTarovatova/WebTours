import random

list_ids = ['210297424-100296-JB', '0-1-92', '0-2-1', '0-3-', '0-3-', '1-4-', '0-5-J', '16-6-0', '0-6-1', '8320-804-JB', '0-8-', '0-930-J', '0-10-JB']
list_nums = ['6', '11', '3', '7', '9', '12', '2', '8', '1', '4', '13', '10', '5']

flight_ids = 'flightID=' + '&flightID='.join(list_ids)

numbers = '.cgifields=' + '&cgifields='.join(list_nums)

random_index = random.randrange(len(list_nums))

print(flight_ids)
print(numbers)
print(random_index)