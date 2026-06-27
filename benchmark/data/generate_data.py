import json
import string
import secrets


def generate_signal(array_size: int, string_size: int):
    characters = string.ascii_letters + string.digits

    return [''.join(secrets.choice(characters) for _ in range(string_size)) for _ in range(array_size)]


small_signal = generate_signal(1000, 128)
with open("small.json", "w") as file:
    json.dump(small_signal, file)

medium_signal = generate_signal(1000, 4096)
with open("medium.json", "w") as file:
    json.dump(medium_signal, file)
