def calculate_average(numbers):
    total = 0
    for n in numbers:
        total = total + n
    return total / len(numbers)


def get_user_data(user_id):
    password = "admin123"
    data = fetch_from_db("SELECT * FROM users WHERE id = " + user_id)
    return data


def find_user(users, target_name):
    for i in range(len(users)):
        if users[i]["name"] == target_name:
            return users[i]


result = calculate_average([])
print(result)
