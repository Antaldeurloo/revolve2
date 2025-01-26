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


def process_database(db_path):

    dbengine = open_database_sqlite(
        db_path, open_method=OpenMethod.OPEN_IF_EXISTS
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
            #.where(Experiment.id == 2)
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
    if config.DATABASE_FILE == 'standard':
        db_paths = [
        # "adv_30_vertical_10runs.sqlite",
        # "adv_30_vertical_10runs_2.sqlite",
        # "adv_30_vertical_10runs_last2.sqlite",
        # "adv_30_vertical_test.sqlite",
        "final_std_cross.sqlite"]
    elif str(config.DATABASE_FILE) == 'nocross':
        db_paths = ['adv_30_vertical_nocross_10runs.sqlite']
    elif config.DATABASE_FILE == 'controlled':
        db_paths = ['controlled_cross_9more.sqlite']
    else:
        db_paths = [config.DATABASE_FILE]
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
    all_data['max_fitness_per_group'] = all_data.groupby(['generation_index', 'experiment_id'])['fitness'].transform('max')
    print(all_data)
# Group by 'generation' and compute the average length
    avg_fitness_df = (
    all_data.groupby(['experiment_id', 'generation_index'])
    .agg(avg_fitness=('fitness', 'mean'),
         avg_genome_length=('body_length','mean')
         )

    .reset_index()
    )
    # Group by experiment_id and generation_index for individual runs
    print(avg_fitness_df)



# Line graph
    fig, ax1 = plt.subplots(figsize=(11, 7))

# Primary axis for body length


# Plot the data
    for experiment_id, run_data in avg_fitness_df.groupby('experiment_id'):
        print(run_data)
        ax1.plot(
            run_data['generation_index'], 
            run_data['avg_genome_length'], 
            label=f'Run {experiment_id}',
            linewidth=2
        )

    # Apply the settings
    ax1.set_xlabel('Generation', fontsize=26)
    ax1.set_ylabel('Genome Length', fontsize=26, color='blue')
    ax1.tick_params(axis='y', labelcolor='blue', labelsize=24)
    ax1.tick_params(axis='x', labelsize=24)
    ax1.yaxis.set_major_locator(MaxNLocator(nbins=5))
    ax1.xaxis.set_major_locator(MaxNLocator(nbins=5))
    ax1.grid(True, linestyle='--', alpha=0.6)
    ax1.set_xlim(left=0)
    ax1.set_ylim(bottom=0, top=1650)

    # Add a legend and show the plot

    plt.tight_layout()
    plt.savefig(config.DATABASE_FILE + "_all_10.pdf", format="pdf")
    plt.show()

    for spine in ax1.spines.values():
        spine.set_linewidth(0.6)

    # if config.DATABASE_FILE != 'adv_30_vertical_nocross_10runs.sqlite':
        # ax1.set_ylim(bottom=0)
# Add title and legends

    # lines_1, labels_1 = ax1.get_legend_handles_labels()
    # lines_2, labels_2 = ax2.get_legend_handles_labels()
    # legend = ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='lower right',fontsize=16)
    # legend.remove()
    # fig_legend = plt.figure(figsize=(4, 2))  # Adjust size as needed
    # ax_legend = fig_legend.add_subplot(111)
    # ax_legend.axis('off')  # Turn off axes for a clean legend
    # # Reuse the handles and labels from the original legend
    # ax_legend.legend(handles=legend.legend_handles, labels=[text.get_text() for text in legend.get_texts()],
    #                 loc='center', fontsize=16)
    # fig_legend.show()
    # # Save the legend as a standalone PDF
    # fig_legend.savefig("custom_legend.pdf", bbox_inches='tight', dpi=300)
    plt.savefig(config.DATABASE_FILE + "_all_10.pdf", format="pdf")
   




if __name__ == "__main__":
    main()