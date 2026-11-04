import json

with open("data/skills.json", "r") as file:

    skills = json.load(file)

print("Total skills:", len(skills))

print("First skill:", skills[0])

print("Second skill:", skills[1])