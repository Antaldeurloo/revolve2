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
import numpy as np

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
types_nucleotypes = 6 # Number of types of nucleotypes
regulatory_tfs = 2
structural_trs = len(['brick', 'joint', 'rotation'])
 # Number of diffusion sites (probably front, back, left, right)?

regulatory_transcription_factor_idx = 0 # Index of the regulatory transcription factor label
regulatory_min_idx = 1 # Index of the minimum regulatory value to which gene is responsive
regulatory_max_idx = 2 # Index of the maximum regulatory value to which gene is responsive
transcription_factor_idx = 3 # Index of the transcription factor label
transcription_factor_amount_idx = 4 # Index of the transcription factor amount upon expression
diffusion_site_idx = 5 # Index of release site of the transcription factor
promoter_threshold = 0.8

def parsing(genotype):
    genes = []
    nucleotide_idx = 0
        #genotype = [0.5725732843577864,0.6646651017665862,0.550558058321476,0.5535269796848297,0.6043629667907954,0.37288902074098584,0.5954864632338286,0.56,0.51,0.01,0.63,0.85,0.41,0.16,0.56,0.84,0.01,0.63,0.85,0.41,0.16,0.56,0.84,0.01,0.63,0.85,0.41,0.16,0.49,0.74,0.04,0.18,0.84,0.2,0.32,0.56,0.84,0.01,0.63,0.85,0.41,0.16,0.49,0.74,0.04,0.18,0.84,0.2,0.32,0.57,0.02,0.98,0.9,0.73,0.71,0.49,0.02,0.99,0.31,0.73,0.61,0.94,0.5,0.69,0.43,0.29,0.63,0.77,0.87,0.16,0.1,0.07,0.31,0.98,0.14,0.02,0.75,0.95,0.95,0.91,1.0,0.74,0.51,0.44,0.61,0.81,0.68,0.9,0.92,0.78,0.8,0.46,0.98,0.12,0.14,0.21,0.83,0.5,0.79,0.57,0.97,0.39,0.55,0.84,0.48,0.21,0.28,0.16,0.9,0.41,0.61,0.58,0.2,0.03,0.89,0.41,0.19,0.12,0.31,0.73,0.92,0.34,0.61,0.17,0.96,0.51,0.98,0.02,0.02,0.29,0.68,0.96,0.32,0.56,0.84,0.01,0.63,0.85,0.41,0.4,0.49,0.74,0.04,0.18,0.84,0.2,0.32,0.57,0.02,0.98,0.9,0.85,0.71,0.49,0.02,0.99,0.31,0.73,0.61,0.94,0.5,0.48,0.78,0.39,0.37,0.65,0.79,0.68,0.58,0.15,0.82,0.76,0.31,0.36,0.56,0.51,0.01,0.63,0.85,0.41,0.16,0.56,0.84,0.01,0.63,0.85,0.41,0.16,0.56,0.84,0.01,0.63,0.85,0.41,0.16,0.49,0.74,0.04,0.18,0.84,0.2,0.32,0.56,0.84,0.01,0.63,0.85,0.41,0.16,0.49,0.74,0.04,0.18,0.84,0.2,0.32,0.57,0.02,0.98,0.9,0.85,0.71,0.49,0.02,0.99,0.31,0.73,0.61,0.94,0.5,0.69,0.43,0.29,0.63,0.77,0.87,0.16,0.1,0.07,0.31,0.98,0.14,0.02,0.75,0.95,0.95,0.91,1.0,0.74,0.51,0.44,0.61,0.81,0.68,0.9,0.92,0.78,0.8,0.46,0.98,0.12,0.14,0.21,0.83,0.5,0.79,0.57,0.97,0.39,0.55,0.84,0.48,0.21,0.28,0.16,0.9,0.41,0.61,0.58,0.2,0.03,0.89,0.41,0.19,0.12,0.31,0.73,0.92,0.34,0.61,0.17,0.96,0.51,0.98,0.02,0.02,0.29,0.68,0.96,0.32,0.56,0.84,0.01,0.63,0.85,0.41,0.4,0.49,0.74,0.04,0.18,0.84,0.2,0.32,0.57,0.02,0.98,0.9,0.85,0.71,0.49,0.02,0.99,0.31,0.73,0.61,0.94,0.5,0.48,0.78,0.39,0.37,0.65,0.79,0.68,0.58,0.15,0.82,0.76,0.31,0.36,0.56,0.84,0.01,0.53,0.85,0.41,0.4,0.49,0.74,0.04,0.18,0.84,0.2,0.32,0.57,0.02,0.98,0.9,0.85,0.71,0.49,0.56,0.84,0.01,0.63,0.85,0.41,0.16,0.49,0.74,0.04,0.18,0.84,0.2,0.32,0.57,0.84,0.01,0.63,0.85,0.41,0.16,0.49,0.74,0.04,0.18,0.84,0.2,0.32]
        #genotype = genotype[7:]
        #print(genotype)
        # Repeat as long as index is smaller than gene length
    while nucleotide_idx < len(genotype):
        # If the associated value is smaller than the promoter threshold
        #print(genotype[nucleotide_idx])
        if genotype[nucleotide_idx] < promoter_threshold:
            # If there are nucleotypes enough to compose a gene
            if (len(genotype) - 1 - nucleotide_idx) >= types_nucleotypes:
                
                # Get regulatory transcription factor(s)
                regulatory_transcription_factor = genotype[nucleotide_idx + regulatory_transcription_factor_idx + 1] # Which regulatory tf is expressed?
                regulatory_min = np.float64(genotype[nucleotide_idx + regulatory_min_idx + 1]) # Between those two values regulatory tf expresses gene
                regulatory_max = np.float64(genotype[nucleotide_idx + regulatory_max_idx + 1])
                # Get transcription factor, -amount and diffusion site
                transcription_factor = genotype[nucleotide_idx + transcription_factor_idx + 1] # Which tf is expressed?
                transcription_factor_amount = genotype[nucleotide_idx + transcription_factor_amount_idx + 1] # Amount of increase of the tf at the diffusion site
                diffusion_site = genotype[nucleotide_idx + diffusion_site_idx + 1] # Where the tf is expressed
                
                # Converts rtfs and tfs values into labels
                range_size = 1 / (structural_trs + regulatory_tfs)
                limits = [round(limit / 100, 2) for limit in range(0, 1 * 100, int(range_size * 100))]
                for idx in range(0, len(limits) - 1):
                    # Set label for regulatory transcription factor
                    if (regulatory_transcription_factor >= limits[idx]) and (regulatory_transcription_factor < limits[idx + 1]):
                        regulatory_transcription_factor_label = 'TF' + str(idx + 1)
                    elif regulatory_transcription_factor >= limits[idx + 1]:
                        regulatory_transcription_factor_label = 'TF' + str(len(limits))
                    # Set label for transcription factor
                    if (transcription_factor >= limits[idx]) and (transcription_factor < limits[idx + 1]):
                        transcription_factor_label = 'TF' + str(idx + 1)
                    elif transcription_factor >= limits[idx + 1]:
                        transcription_factor_label = 'TF' + str(len(limits))
        
                # Converts diffusion sites values into labels
                range_size = 1 / 4
                limits = [round(limit / 100, 2) for limit in range(0, 1 * 100, int(range_size * 100))]
                for idx in range(0, len(limits) - 1):
                    if limits[idx+1] > diffusion_site >= limits[idx]:
                        diffusion_site_label = idx
                    elif diffusion_site >= limits[idx + 1]:
                        diffusion_site_label = len(limits) - 1
                
                # Translate gene to interpretable format
                min_rTF = min([regulatory_min, regulatory_max])
                max_rTF = max([regulatory_min, regulatory_max])
                gene = [regulatory_transcription_factor_label, min_rTF, max_rTF,
                            transcription_factor_label, float(transcription_factor_amount), int(diffusion_site_label)]
                #print('\n')
                #print([regulatory_transcription_factor, regulatory_min, regulatory_max, transcription_factor,transcription_factor_amount, diffusion_site])
                #print(gene)
                #print('\n')
                # Append gene to promoters
                genes.append(gene)

                # Increase nucleotide index
                nucleotide_idx += types_nucleotypes
        
        # Increase nucleotide index
        nucleotide_idx += 1
    #print(promotors)
    return len(genes) * 7


def process_database(db_path):

    dbengine = open_database_sqlite(
        db_path, open_method=OpenMethod.OPEN_IF_EXISTS
    )
    db_path_to_variable = {
    "adv_30_vertical_10runs.sqlite": {"runs": 2, "start_run_number": 1},
    "adv_30_vertical_10runs_2.sqlite": {"runs": 2, "start_run_number": 3},
    "adv_30_vertical_10runs_last2.sqlite": {"runs": 3, "start_run_number": 5},
    "adv_30_vertical_test.sqlite": {"runs": 2, "start_run_number": 8},
    "final_std_cross.sqlite": {"runs": 1, "start_run_number": 10},
}
    db_info = db_path_to_variable.get(db_path, None)
    if not db_info:
        raise ValueError(f"No configuration found for db_path: {db_path}")

    number_of_runs = db_info["runs"]
    current_run_number = db_info["start_run_number"]
    all_df_list = []
    for run in range(1,number_of_runs+1):
        print(run)
        if db_path == 'final_std_cross.sqlite':
            run = 2
        with Session(dbengine) as ses:
            rows = ses.execute(
                select(Genotype, Individual.fitness, Generation.experiment_id,
                    Generation.generation_index)

                .join_from(Experiment, Generation, Experiment.id == Generation.experiment_id)
                .join_from(Generation, Population, Generation.population_id == Population.id)
                .join_from(Population, Individual, Population.id == Individual.population_id)
                .join_from(Individual, Genotype, Individual.genotype_id == Genotype.id)
                .where(Generation.generation_index == 400)
                .where(Generation.experiment_id == run)


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
        print(df)
        print('current_run_number:' + str(current_run_number) + ', run:' + str(run))
        df['experiment_id'] = (current_run_number + run - 1)
        df['body_length'] = df['genotype'].apply(lambda x: len(x.body))
        df = df[df['generation_index'] % 2 == 0]
        df['generation_index'] = df['generation_index'].apply(lambda x: x / 2)
        df['used_genes'] = df['genotype'].apply(lambda x: parsing(x.body))
        all_df_list.append(df)

        
    all_data = pd.concat(all_df_list, ignore_index=True)
    return all_data



def main() -> None:
    """Perform the rerun."""
    setup_logging()

    
    all_data = pd.DataFrame()
    all_df_list = []
    db_paths = ["adv_30_vertical_10runs.sqlite",
        "adv_30_vertical_10runs_2.sqlite",
        "adv_30_vertical_10runs_last2.sqlite",
        "adv_30_vertical_test.sqlite",
        "final_std_cross.sqlite"]
    for db_path in db_paths:
        all_df_list.append(process_database(db_path))
    all_data = pd.concat(all_df_list, ignore_index=True)


    #fitness = evaluator.evaluate([df.genotype[0].develop(include_bias = config.CPPNBIAS,
    #            
    #            max_parts = config.MAX_PARTS, 
    #            mode_core_mult = config.MODE_CORE_MULT, 
    #            )])[0]
    #print(fitness)
    #print(df)
    # Extract the length of the 'body' values

    


    all_data['usage_ratio'] = all_data['used_genes'] / all_data['body_length']

    print(all_data)

# Group by 'generation' and compute the average length
    result = all_data.groupby('generation_index').agg(
    avg_body_length=('body_length', 'mean'),
    avg_fitness=('fitness', 'mean'),
    avg_usage_ratio=('usage_ratio', 'mean'),
    avg_used_genes=('used_genes', 'mean'),

    ).reset_index()

    result['max_fitness'] = all_data.groupby('generation_index')['fitness'].max().reset_index(drop=True)
    print(result)
# Line graph
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Primary axis for body length
    ax1.set_xlabel('Generation Index', fontsize=12)
    ax1.set_ylabel('Average Genome Length', fontsize=12, color='blue')
    ax1.plot(result['generation_index'], result['avg_body_length'], linestyle='-', linewidth=2, color='blue', label='Average Genome Length')
    ax1.plot(result['generation_index'], result['avg_used_genes'], linestyle='--', linewidth=2, color='green', label='Genes used')  # Add another column on the same axis
    ax1.tick_params(axis='y', labelcolor='blue')
    ax1.grid(True, linestyle='--', alpha=0.6)



# Secondary axis for fitness
    ax2 = ax1.twinx()
    ax2.set_ylabel('Fitness', fontsize=12, color='green')
    ax2.plot(result['generation_index'], result['avg_fitness'], linestyle='-', linewidth=2, color='green', label='Average Fitness')
    ax2.plot(result['generation_index'], result['max_fitness'], linestyle='--', linewidth=2, color='red', label='Highest Fitness')  # New line for highest fitness
    ax2.tick_params(axis='y', labelcolor='green')

# Add title and legends
    fig.suptitle('Genome Length and Fitness by Generation Index', fontsize=14)
    ax1.legend(loc='upper left', fontsize=10)
    ax2.legend(loc='upper right', fontsize=10)

    #plt.show()


if __name__ == "__main__":
    main()