import logging
import os
import sys
import pandas as pd

import matplotlib.pyplot as plt


# Set algorithm, mode and file name from command line arguments.
algo = sys.argv[1]
mode = sys.argv[2]
file_name = sys.argv[3]
headless = sys.argv[4]
writefiles = sys.argv[5]
writevideos = sys.argv[6]

assert headless in ["True", "False"], "HEADLESS must be either True or False"
if (writefiles == "True"):
    assert (writevideos == "False"), "WRITEVIDEOS must be False if WRITEFILES is True"
    assert (headless == "True"), "HEADLESS must be True if WRITEFILES is True"
assert writefiles in ["True", "False"], "WRITEFILES must be either True or False"
assert writevideos in ["True", "False"], "WRITEVIDEOS must be either True or False"
assert algo in ["GRN", "GRN_system", "GRN_system_adv", "CPPN"], "ALGORITHM must be either GRN, 'GRN_system' or CPPN"
assert mode in ["random search", "evolution"], "MODE must be either random search or evolution"
assert type(file_name) == str, "FILE_NAME must be a string"
assert file_name.endswith(".sqlite"), "FILE_NAME must end with sqlite"
os.environ["ALGORITHM"] = algo
os.environ["MODE"] = mode
os.environ["DATABASE_FILE"] = file_name
os.environ["HEADLESS"] = headless
os.environ["WRITEFILES"] = writefiles
os.environ["WRITEVIDEOS"] = writevideos

if os.environ["WRITEFILES"] == "True":
    os.environ["RERUN"] = "True"
else:
    os.environ["RERUN"] = "False"


from evaluator import Evaluator
from experiment import Experiment
from generation import Generation
from individual import Individual
from population import Population

import shutil
from sqlalchemy import select
from sqlalchemy.orm import Session

from revolve2.experimentation.revolve2.experimentation.database import OpenMethod, open_database_sqlite
from revolve2.experimentation.revolve2.experimentation.logging import setup_logging

from revolve2.ci_group.revolve2.ci_group.simulation_parameters import make_standard_batch_parameters
from revolve2.simulators.mujoco_simulator.revolve2.simulators.mujoco_simulator import LocalSimulator
from revolve2.modular_robot_simulation.revolve2.modular_robot_simulation import (
    ModularRobotScene,
    Terrain,
    simulate_scenes,
)

from genotype_grn import Genotype
import config






def main() -> None:
    """Perform the rerun."""
    setup_logging()

    # Load the best individual from the database.
    dbengine = open_database_sqlite(
        config.DATABASE_FILE, open_method=OpenMethod.OPEN_IF_EXISTS
    )

    with Session(dbengine) as ses:
        rows = ses.execute(
            select(Genotype, Individual.fitness, Individual.energy_used, Individual.efficiency,
                   Individual.x_distance, Individual.y_distance, Generation.experiment_id,
                   Generation.generation_index, Individual.body_id)
            .where(Generation.generation_index == 280)

            .join_from(Experiment, Generation, Experiment.id == Generation.experiment_id)
            .join_from(Generation, Population, Generation.population_id == Population.id)
            .join_from(Population, Individual, Population.id == Individual.population_id)
            .join_from(Individual, Genotype, Individual.genotype_id == Genotype.id)
            .order_by(Individual.fitness.desc())
        ).all() # Individual.body_id where(Experiment.id.label("experiment_id") == int(sys.argv[7]))
    data = [
    {
        "genotype": genotype,  # Store the Genotype object directly
        "fitness": fitness,
        "energy_used": energy_used,
        "efficiency": efficiency,
        "x_distance": x_distance,
        "y_distance": y_distance,
        "experiment_id": experiment_id,
        "generation_index": generation_index,
        "body_id": body_id,
    }
    for genotype, fitness, energy_used, efficiency, x_distance, y_distance, experiment_id, generation_index, body_id in rows
    ]
    df = pd.DataFrame(data)
    print(df["fitness"])
    #print(df.genotype[0])
    evaluator = Evaluator(
        headless = False, num_simulators = 1,
                          terrain = config.TERRAIN, fitness_function = config.FITNESS_FUNCTION,
                          simulation_time = config.SIMULATION_TIME, sampling_frequency = config.SAMPLING_FREQUENCY, 
                          simulation_timestep = config.SIMULATION_TIMESTEP, control_frequency = config.CONTROL_FREQUENCY
    )
    #fitness = evaluator.evaluate([df.genotype[0].develop(include_bias = config.CPPNBIAS,
    #            
    #            max_parts = config.MAX_PARTS, 
    #            mode_core_mult = config.MODE_CORE_MULT, 
    #            )])[0]
    #print(fitness)
    #print(df)
    # Extract the length of the 'body' values
    # Extract the first element of the tuples in Column1
    df['gen_length'] = df['genotype'].apply(lambda x: len(x.body))

# Scatterplot using the first element of the tuples
    plt.figure(figsize=(8, 6))
    plt.scatter(df['gen_length'], df['fitness'], alpha=0.7, edgecolors='k')
    plt.title('Generation 160', fontsize=14)
    plt.xlabel('genome length', fontsize=12)
    plt.ylabel('fitness', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.show()

if __name__ == "__main__":
    main()