import sqlite3
import pandas as pd
#from ci_group.revolve2.ci_group.genotypes.cppnwin._body_genotype_v2_multineat_genotype_pickle_wrapper import MultineatGenotypePickleWrapper

# Connect to the SQLite database
conn = sqlite3.connect('adv_30_vertical_nocross_10runs.sqlite')
cursor = conn.cursor()

# Run a query
query = """
    
    
    SELECT * from experiment e
    limit 100

;"""  # Replace with your actual table name

query2 = """

    select g.id, fitness, serialized_body from experiment e
    join generation g on e.id = g.experiment_id
    join population p on p.id = g.population_id
    join individual i on i.population_id = p.id
    join genotype ge on ge.id = i.genotype_id
    where e.id = 1
    order by g.id desc
    

"""

query3 = """

    select * from population

"""

cursor.execute(query)

# Fetch all rows and column names
rows = cursor.fetchall()

columns = [description[0] for description in cursor.description]
print(rows[0])
# Convert the results to a DataFrame
df = pd.DataFrame(rows, columns=columns)
print(df)
# Close the connection
conn.close()