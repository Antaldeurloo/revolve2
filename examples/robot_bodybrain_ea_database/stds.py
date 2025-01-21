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


def process_database(db_path):

    dbengine = open_database_sqlite(
        config.DATABASE_FILE, open_method=OpenMethod.OPEN_IF_EXISTS
    )

    with Session(dbengine) as ses:
        rows = ses.execute(
            select(Genotype, Individual.fitness, Generation.experiment_id,
                   Generation.generation_index)

            .join_from(Experiment, Generation, Experiment.id == Generation.experiment_id)
            .join_from(Generation, Population, Generation.population_id == Population.id)
            .join_from(Population, Individual, Population.id == Individual.population_id)
            .join_from(Individual, Genotype, Individual.genotype_id == Genotype.id)

            .where(Generation.generation_index < 401)

            #.order_by(Individual.fitness.desc())
        ).all() # Individual.body_id where(Experiment.id.label("experiment_id") == int(sys.argv[7]))
    data = [
    {
        "genotype": genotype,  # Store the Genotype object directly
        "fitness": fitness,
        "experiment_id": experiment_id,
        "generation_index": generation_index,

    }
    for genotype, fitness, experiment_id, generation_index in rows
    ]
    df = pd.DataFrame(data)
    return df


def main() -> None:
    """Perform the rerun."""
    setup_logging()

    # Load the best individual from the database.
    
    all_data = pd.DataFrame()
    all_df_list = []
    db_paths = ['adv_30_vertical_10runs_2.sqlite']
    for db_path in db_paths:
        all_df_list.append(process_database(db_path))
    all_data = pd.concat(all_df_list, ignore_index=True)
    #print(df.genotype[0])

    #fitness = evaluator.evaluate([df.genotype[0].develop(include_bias = config.CPPNBIAS,
    #            
    #            max_parts = config.MAX_PARTS, 
    #            mode_core_mult = config.MODE_CORE_MULT, 
    #            )])[0]
    #print(fitness)
    #print(df)
    # Extract the length of the 'body' values
    all_data['body_length'] = all_data['genotype'].apply(lambda x: len(x.body))
    all_data = all_data[all_data['generation_index'] % 2 == 0]
    all_data['generation_index'] = all_data['generation_index'].apply(lambda x: x / 2)

    #all_data['max_fitness'] = all_data.groupby(['generation_index', 'experiment_id']).agg(max_fitness=('fitness', 'max')).reset_index()
    #all_data['max_fitness_per_group'] = all_data.groupby(['generation_index', 'experiment_id'])['fitness'].transform('max')
    print(all_data)
# Group by 'generation' and compute the average length
    # result = all_data.groupby('generation_index').agg(
    # avg_body_length=('body_length', 'mean'),
    # avg_fitness=('fitness', 'mean'),
    # avg_highest_fitness=('max_fitness_per_group','mean'),
    # total_highest_fitness=('max_fitness_per_group','max')
    # std_fitness=('fitness', 'std')
    # ).reset_index()
    all_data['std_per_group'] = all_data.groupby(['generation_index', 'experiment_id'])['fitness'].transform('std')

    result = all_data.groupby('generation_index').agg(
    std_fitness=('std_per_group', 'mean')
    ).reset_index()
    plt.figure(figsize=(10, 6))
    plt.plot(result['generation_index'], result['std_fitness'], linestyle='-', label='Standard Deviation of Fitness')
    plt.title('Standard Deviation of Fitness Over Generations')
    plt.xlabel('Generation Index')
    plt.ylabel('Standard Deviation of Fitness')
    plt.grid(True)
    plt.legend()
    plt.show()
# Line graph
#     fig, ax1 = plt.subplots(figsize=(10, 6))

# # Primary axis for body length
#     ax1.set_xlabel('Generation Index', fontsize=12)
#     ax1.set_ylabel('Genome Length', fontsize=12, color='blue')
#     ax1.plot(result['generation_index'], result['avg_body_length'], linestyle='-', linewidth=2, color='blue', label='Average Genome Length')
#     ax1.tick_params(axis='y', labelcolor='blue')
#     ax1.grid(True, linestyle='--', alpha=0.6)
#     ax1.set_xlim(left=0)
# # Secondary axis for fitness
#     ax2 = ax1.twinx()
#     ax2.set_ylabel('Fitness', fontsize=12, color='green')
#     ax2.plot(result['generation_index'], result['avg_fitness'], linestyle='-', linewidth=2, color='green', label='Average Fitness')
#     ax2.plot(result['generation_index'], result['avg_highest_fitness'], linestyle='-', linewidth=2, color='orange', label='Average Highest Fitness')
#     ax2.plot(result['generation_index'], result['total_highest_fitness'], linestyle='--', linewidth=2, color='red', label='Total Highest Fitness')  # New line for highest fitness
#     ax2.tick_params(axis='y', labelcolor='green')
#     if config.DATABASE_FILE != 'adv_30_vertical_nocross_10runs.sqlite':
#         ax1.set_ylim(bottom=0)
# # Add title and legends
#     fig.suptitle('Genome Length and Fitness Metrics of Experiment 2', fontsize=14)
#     ax1.legend(loc='upper left', fontsize=10)
#     ax2.legend(loc='lower right', fontsize=10)
#     ax2.set_ylim(bottom=0)

#     plt.show()


if __name__ == "__main__":
    main()