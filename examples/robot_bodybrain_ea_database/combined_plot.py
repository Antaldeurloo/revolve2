import logging
import os
import sys
import pandas as pd
import numpy as np
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
# assert file_name.endswith(".sqlite"), "FILE_NAME must end with sqlite"
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
from matplotlib.ticker import MaxNLocator

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
    
    all_data = pd.read_csv('combined_results.csv')
    standard_data = all_data[all_data['crossover'] == 'standard']
    nocross_data = all_data[all_data['crossover'] == 'nocross']
    controlled_data = all_data[all_data['crossover'] == 'controlled']
    print('avg std standard: ' + str(standard_data['std'].mean()))
    print('avg std nocross: ' + str(nocross_data['std'].mean()))
    print('avg std controlled: ' + str(controlled_data['std'].mean()))
# Line graph
    fig, ax2 = plt.subplots(figsize=(11, 7))

# Primary axis for body length
    selected_x = 21
    selected_y = 5.8

    # Draw dashed lines to the right axis and bottom axis

    ax2.plot([20.5, 200], [5.85, 5.85], linestyle='--', color='gray', linewidth=2)
    ax2.plot([20.5, 20.5], [5.85, 0], linestyle='--', color='gray', linewidth=2)
    ax2.plot([95, 95], [5.85, 0], linestyle='--', color='gray', linewidth=2)

    ax2.plot([51.5, 200], [6.76, 6.76], linestyle='--', color='gray', linewidth=2)
    ax2.plot([51.5, 51.5], [6.76, 0], linestyle='--', color='gray', linewidth=2)

# Secondary axis for fitness
    ax2.set_ylabel('Fitness', fontsize=26, color='black')
    ax2.set_xlabel('Generation', fontsize=26, color='black')
    ax2.plot(standard_data['generation_index'], standard_data['avg_highest_fitness'], linestyle='-', linewidth=4, color='red', label='Standard')
    ax2.plot(nocross_data['generation_index'], nocross_data['avg_highest_fitness'], linestyle='-', linewidth=4, color='green', label='Nocross')
    ax2.plot(controlled_data['generation_index'], controlled_data['avg_highest_fitness'], linestyle='-', linewidth=4, color='blue', label='Controlled')
  # New line for highest fitness
    ax2.tick_params(axis='y', labelcolor='black', labelsize=20)
    ax2.tick_params(axis='x', labelcolor='black', labelsize=20)
    ax2.yaxis.set_major_locator(MaxNLocator(nbins=7))
    ax2.xaxis.set_major_locator(MaxNLocator(nbins=9))
    ax2.set_ylim(bottom=0, top=13)
    ax2.set_xlim(left=0)

    for spine in ax2.spines.values():
        spine.set_linewidth(0.6)
    # if config.DATABASE_FILE != 'adv_30_vertical_nocross_10runs.sqlite':
        # ax1.set_ylim(bottom=0)
# Add title and legends
    ax2.legend(fontsize=18, loc='upper left')
    plt.grid(True, linestyle='--', alpha=0.6)


    # legend.remove()
    # fig_legend = plt.figure(figsize=(4, 2))  # Adjust size as needed


    # # Save the legend as a standalone PDF
    plt.savefig("pojection_graph.pdf", bbox_inches='tight', dpi=300)

   
    plt.show()



if __name__ == "__main__":
    main()