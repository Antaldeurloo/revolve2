from __future__ import annotations

from copy import deepcopy
import multineat
import numpy as np
import sqlalchemy.orm as orm
from sqlalchemy import event
from sqlalchemy.engine import Connection
from typing_extensions import Self

from revolve2.modular_robot.revolve2.modular_robot.body.v2 import BodyV2
from ._body_develop_grn_system_adv import DevelopGRN

class BodyGenotypeOrmV2GRN_system_adv(orm.MappedAsDataclass, kw_only=True):
    """Goal:
        SQLAlchemy model for a CPPNWIN body genotype."""

    # Body genotype
    body: multineat.Genome

    # Serialized body
    _serialized_body: orm.Mapped[str] = orm.mapped_column(
        "serialized_body", init=False, nullable=False
    )

    @classmethod
    def random_body(self: object, rng: np.random.Generator) -> BodyGenotypeOrmV2GRN_system_adv:
        # Set genome size
        genome_size = 150 + 1 + 6
        # Set random genotype
        genotype = [round(rng.uniform(0, 1), 2) for _ in range(genome_size)]

        return BodyGenotypeOrmV2GRN_system_adv(body = genotype)
    
    def mutate_body(
        self,
        rng: np.random.Generator,
    ) -> BodyGenotypeOrmV2GRN_system_adv: # Ask whether a copy should be provided or not!
        
        # Make deepcopy of the genotype
        genotype = deepcopy(self.body)
        # Get a random mutation position
        position = rng.choice(range(0, len(genotype)), 1)[0]

        # Get a random mutation type
        type = rng.choice(['perturbation', 'deletion', 'addition', 'swap'], 1)[0]

        # Mutate the genotype
        if type == 'perturbation':
            # Add or subtract a random value from the genotype
            newv = round(genotype[position] + rng.normal(0, 0.1), 2)
            # Protect the boundaries
            if newv > 1:
                genotype[position] = 1
            elif newv < 0:
                genotype[position] = 0
            else:
                genotype[position] = newv
        elif type == 'deletion':
            # Delete a value from the genotype
            genotype.pop(position)
        elif type == 'addition':
            # Add a value to the genotype
            genotype.insert(position, round(rng.uniform(0, 1), 2))
        elif type == 'swap':
            # Sample random second position
            position2 = rng.choice(range(0, len(genotype)), 1)[0]
            while position == position2:
                position2 = rng.choice(range(0, len(genotype)), 1)[0]
            # Get values
            position_v = genotype[position]
            position2_v = genotype[position2]
            # Swap values
            genotype[position] = position2_v
            genotype[position2] = position_v
        else:
            raise ValueError(f'Unknown mutation type {type}')
        
        return BodyGenotypeOrmV2GRN_system_adv(body = genotype)

    @classmethod
    def crossover_body(
        cls,
        parent1: Self,
        parent2: Self,
        rng: np.random.Generator,
    ) -> BodyGenotypeOrmV2GRN_system_adv:
        # Get genotypes
        genotype1 = parent1.body
        genotype2 = parent2.body

        # Set promoter threshold and number of nucleotypes 
        promoter_threshold = 0.8
        types_nucleotypes = 6

        # The first nucleotide is the concentration --> average of the parents
        new_genotype = []
        for ig in range(0, 7):
            new_genotype.append((genotype1[ig] + genotype2[ig])/2)

        # Get remaining nucleotides from parents
        p1 = genotype1[7:]
        p2 = genotype2[7:]

        # Get new genotype

        # Initialize nucleotide index and promotor sites
        nucleotide_idx = 0
        promotor_sites1 = []
        while nucleotide_idx < len(p1):
            # If the nucleotide value is less than the promoter threshold
            if p1[nucleotide_idx] < promoter_threshold:
                # If there are nucleotides enough to compose a gene
                if (len(p1) - 1 - nucleotide_idx) >= types_nucleotypes:
                    promotor_sites1.append(nucleotide_idx)
                    nucleotide_idx += types_nucleotypes
            nucleotide_idx += 1
        nucleotide_idx = 0
        promotor_sites2 = []
        while nucleotide_idx < len(p2):
            # If the nucleotide value is less than the promoter threshold
            if p2[nucleotide_idx] < promoter_threshold:
                # If there are nucleotides enough to compose a gene
                if (len(p2) - 1 - nucleotide_idx) >= types_nucleotypes:
                    promotor_sites2.append(nucleotide_idx)
                    nucleotide_idx += types_nucleotypes
            nucleotide_idx += 1
        # Sample a promotor site
        #print('starting test')
        cutpoint1 = rng.choice(promotor_sites1, 1)[0]
        #print('cutpoint1: ' + str(cutpoint1))
        #print(promotor_sites1) 
        cutpoint_ratio = cutpoint1 / len(p1) 
        #print('cutpoint ratio: '+str(cutpoint_ratio))
        if cutpoint_ratio < 0.5:
            cutpoint1 = min(promotor_sites1, key=lambda x: abs(x - ((1 - cutpoint_ratio) * len(p1))))
        #print('cutpoint revised: ' + str(cutpoint1))
        cutpoint2_rough = (1 - (cutpoint1 / len(p1))) * len(p2)
        # Get a subset of the parent genotype
        subset1 = p1[0:cutpoint1+types_nucleotypes+1]
        # Append the subset to the new genotype


        cutpoint2 = min(promotor_sites2, key=lambda x: abs(x - cutpoint2_rough))
        #print('p2:'+ str(promotor_sites2))
        #print('cutpoint2: '+str(cutpoint2))
        #print('lenght 2:'+ str(len(p2)))
        subset2 = p2[0:cutpoint2+types_nucleotypes+1]

        new_genotype += subset1 + subset2
    #    print('\n')
     #   print('parent1 ' + str(len(genotype1)))
      #  print('parent2 ' + str(len(genotype2)))
       # print('child ' + str(len(new_genotype)))
        #print('\n')

        return BodyGenotypeOrmV2GRN_system_adv(body = new_genotype)
    
    def develop_body(self: object, max_parts: int, mode_core_mult: bool) -> BodyV2:
        """
        Goal:
            Develop the genotype into a modular robot.
        -------------------------------------------------------------------------------------------
        Output:
            The created robot.
        """
        return DevelopGRN(max_parts, mode_core_mult, self.body).develop()




@event.listens_for(BodyGenotypeOrmV2GRN_system_adv, "before_update", propagate=True)
@event.listens_for(BodyGenotypeOrmV2GRN_system_adv, "before_insert", propagate=True)
def _update_serialized_body(
    mapper: orm.Mapper[BodyGenotypeOrmV2GRN_system_adv],
    connection: Connection,
    target: BodyGenotypeOrmV2GRN_system_adv,
) -> None:
    target._serialized_body = ','.join([str(gen) for gen in target.body])
    pass

@event.listens_for(BodyGenotypeOrmV2GRN_system_adv, "load", propagate=True)
def _deserialize_body(target: BodyGenotypeOrmV2GRN_system_adv, context: orm.QueryContext) -> None:
    body = [float(gen) for gen in target._serialized_body.split(",")]
    target.body = body