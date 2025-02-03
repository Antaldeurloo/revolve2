import sqlite3
import pandas as pd
#from ci_group.revolve2.ci_group.genotypes.cppnwin._body_genotype_v2_multineat_genotype_pickle_wrapper import MultineatGenotypePickleWrapper

# Connect to the SQLite database
conn = sqlite3.connect('controlled_cross_9more.sqlite')
cursor = conn.cursor()

# Run a query
query = """
    
    
    SELECT fitness  FROM individual i
    
    inner join genotype g on g.id = i.genotype_id
    order by fitness desc
    limit 10

;"""  # Replace with your actual table name

query2 = """

    select max(fitness) from experiment e
    join generation g on e.id = g.experiment_id
    join population p on p.id = g.population_id
    join individual i on i.population_id = p.id
    join genotype ge on ge.id = i.genotype_id
    group by g.experiment_id
    

"""

query3 = """

    select * from generation

"""



# Fetch all rows and column names

# Convert the results to a DataFrame
db_paths = [
        "adv_30_vertical_10runs.sqlite",
        "adv_30_vertical_10runs_2.sqlite",
        "adv_30_vertical_10runs_last2.sqlite",
        "adv_30_vertical_test.sqlite",
        "final_std_cross.sqlite"]
all_df_list = []
for db_path in db_paths:
    cursor.execute(query2)

# Fetch all rows and column names
    rows = cursor.fetchall()

    columns = [description[0] for description in cursor.description]
    df = pd.DataFrame(rows, columns=columns)
    all_df_list.append(df)
all_data = pd.concat(all_df_list, ignore_index=True)

print(all_data)
# Close the connection
conn.close()