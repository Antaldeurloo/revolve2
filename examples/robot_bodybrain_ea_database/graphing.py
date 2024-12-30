import graphviz

dot = graphviz.Digraph('genes-graph', comment='Genes Relationships')



dot.node('new_module', 'New Module', shape='box')  # New Module as a rectangular node

# Define TF nodes in a row
with dot.subgraph() as tf_nodes:
    tf_nodes.attr(rank='same')  # Place TF nodes in the same rank (row)
    tf_nodes.node('TF1', 'TF1')
    tf_nodes.node('TF2', 'TF2')
    tf_nodes.node('TF3', 'TF3')
    tf_nodes.node('TF4', 'TF4')
    tf_nodes.node('TF5', 'TF5')

# Define gene nodes
dot.node('gene1', "['TF1', 0.12, 0.97, 'TF2', 0.37, 2]")
dot.node('gene2', "['TF1', 0.7, 0.95, 'TF1', 0.06, 3]")
dot.node('gene3', "['TF3', 0.3, 0.94, 'TF3', 0.33, 0]")
dot.node('gene4', "['TF4', 0.09, 0.09, 'TF3', 0.4, 1]")
dot.node('gene5', "['TF3', 0.01, 0.48, 'TF4', 0.3, 1]")
dot.node('gene6', "['TF4', 0.04, 0.81, 'TF1', 0.04, 0]")
dot.node('gene7', "['TF1', 0.35, 0.81, 'TF3', 0.05, 1]")
dot.node('gene8', "['TF4', 0.7, 0.97, 'TF3', 0.67, 1]")
dot.node('gene9', "['TF2', 0.14, 0.54, 'TF3', 0.86, 2]")
dot.node('gene10', "['TF1', 0.05, 0.12, 'TF1', 0.89, 2]")

# Define additional nodes (0, 1, 2, 3)
dot.node('node0', 'side 1', shape='circle')
dot.node('node1', 'side 2', shape='circle')
dot.node('node2', 'side 3', shape='circle')
dot.node('node3', 'side 4', shape='circle')

# Add the "Module Placement" node underneath the new nodes
dot.node('module_placement', 'Module Placement', shape='box')

dot.node('maternal_injection', 'Maternal Injection', shape='box')

# Add an edge from "Maternal Injection" to the first gene
dot.edge('maternal_injection', 'gene1')

# Define edges to the "New Module"
dot.edge('TF3', 'new_module')
dot.edge('TF4', 'new_module')
dot.edge('TF5', 'new_module')

# Define edges (connections between TF nodes and genes)
dot.edge('TF1', 'gene1')  # Incoming to gene1 from TF1
dot.edge('gene1', 'TF2')  # Outgoing from gene1 to TF2
dot.edge('gene1', 'node2')  # Gene1 to node 2

dot.edge('TF1', 'gene2')
dot.edge('gene2', 'TF1')
dot.edge('gene2', 'node3')  # Gene2 to node 3

dot.edge('TF3', 'gene3')
dot.edge('gene3', 'TF3')
dot.edge('gene3', 'node0')  # Gene3 to node 0

dot.edge('TF4', 'gene4')
dot.edge('gene4', 'TF3')
dot.edge('gene4', 'node1')  # Gene4 to node 1

dot.edge('TF3', 'gene5')
dot.edge('gene5', 'TF4')
dot.edge('gene5', 'node1')  # Gene5 to node 1

dot.edge('TF4', 'gene6')
dot.edge('gene6', 'TF1')
dot.edge('gene6', 'node0')  # Gene6 to node 0

dot.edge('TF1', 'gene7')
dot.edge('gene7', 'TF3')
dot.edge('gene7', 'node1')  # Gene7 to node 1

dot.edge('TF4', 'gene8')
dot.edge('gene8', 'TF3')
dot.edge('gene8', 'node1')  # Gene8 to node 1

dot.edge('TF2', 'gene9')
dot.edge('gene9', 'TF3')
dot.edge('gene9', 'node2')  # Gene9 to node 2

dot.edge('TF1', 'gene10')
dot.edge('gene10', 'TF1')
dot.edge('gene10', 'node2')  # Gene10 to node 2

# Define edges from new nodes to "Module Placement"
dot.edge('node0', 'module_placement')
dot.edge('node1', 'module_placement')
dot.edge('node2', 'module_placement')
dot.edge('node3', 'module_placement')

# Add invisible edges to place "New Module" above TF nodes
dot.edge('new_module', 'TF1', style='invis')
dot.edge('new_module', 'TF2', style='invis')
dot.edge('new_module', 'TF3', style='invis')
dot.edge('new_module', 'TF4', style='invis')
dot.edge('new_module', 'TF5', style='invis')

# Add invisible edges to align genes under TF nodes
dot.edge('TF1', 'gene1', style='invis')
dot.edge('TF2', 'gene2', style='invis')
dot.edge('TF3', 'gene3', style='invis')
dot.edge('TF4', 'gene4', style='invis')
dot.edge('TF5', 'gene5', style='invis')

# Add invisible edges to align nodes (0, 1, 2, 3) under gene nodes
dot.edge('gene1', 'node0', style='invis')
dot.edge('gene2', 'node1', style='invis')
dot.edge('gene3', 'node2', style='invis')
dot.edge('gene4', 'node3', style='invis')


# Render the graph (optional step for visualization)
dot.render('genes-graph', format='png', cleanup=True, view=True)