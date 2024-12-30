import subprocess

# Define your parameters
parameter_sets = [
    {"param1": "GRN", "param2": "evolution", "param3": "testo1.sqlite", "param4": "False", "param5": "False", "param6": "False"},
    {"param1": "GRN_system", "param2": "evolution", "param3": "testo2.sqlite", "param4": "False", "param5": "False", "param6": "False"},
    {"param1": "GRN_system_adv", "param2": "evolution", "param3": "testo3.sqlite", "param4": "False", "param5": "False", "param6": "False"}
]

# Call the script with different parameters
for params in parameter_sets:
    command = ["python", "examples/robot_bodybrain_ea_database/main.py"]
    for key, value in params.items():
        #command.append(f"--{key}")
        command.append(value)
    subprocess.run(command)