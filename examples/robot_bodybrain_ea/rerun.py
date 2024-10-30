"""Rerun a robot with given body and parameters."""

import logging
import pickle

from evaluator import Evaluator
from individual import Individual

from revolve2.experimentation.revolve2.experimentation.logging import setup_logging

# This is a pickled genotype we optimized.
# You can copy your own parameters from the optimization output log.
PICKLED_GENOTYPE = b'\x80\x04\x95\xf6\x13\x00\x00\x00\x00\x00\x00\x8c\nindividual\x94\x8c\nIndividual\x94\x93\x94)\x81\x94}\x94(\x8c\x08genotype\x94h\x05\x8c\x08Genotype\x94\x93\x94)\x81\x94}\x94(\x8c\x05brain\x94\x8cXrevolve2.ci_group.revolve2.ci_group.genotypes.cppnwin._multineat_genotype_pickle_wrapper\x94\x8c\x1eMultineatGenotypePickleWrapper\x94\x93\x94)\x81\x94X\x17\t\x00\x00{\n"value0":{\n"value0":0,\n"value1":[\n{\n"value0":{\n"value0":[]\n},\n"value1":1,\n"value2":1,\n"value3":0.0,\n"value4":0.0,\n"value5":0.0,\n"value6":0.0,\n"value7":0,\n"value8":0,\n"value9":1,\n"value10":0.0\n},\n{\n"value0":{\n"value0":[]\n},\n"value1":2,\n"value2":1,\n"value3":0.0,\n"value4":0.0,\n"value5":0.0,\n"value6":0.0,\n"value7":0,\n"value8":0,\n"value9":1,\n"value10":0.0\n},\n{\n"value0":{\n"value0":[]\n},\n"value1":3,\n"value2":1,\n"value3":0.0,\n"value4":0.0,\n"value5":0.0,\n"value6":0.0,\n"value7":0,\n"value8":0,\n"value9":1,\n"value10":0.0\n},\n{\n"value0":{\n"value0":[]\n},\n"value1":4,\n"value2":1,\n"value3":0.0,\n"value4":0.0,\n"value5":0.0,\n"value6":0.0,\n"value7":0,\n"value8":0,\n"value9":1,\n"value10":0.0\n},\n{\n"value0":{\n"value0":[]\n},\n"value1":5,\n"value2":1,\n"value3":0.0,\n"value4":0.0,\n"value5":0.0,\n"value6":0.0,\n"value7":0,\n"value8":0,\n"value9":1,\n"value10":0.0\n},\n{\n"value0":{\n"value0":[]\n},\n"value1":6,\n"value2":1,\n"value3":0.0,\n"value4":0.0,\n"value5":0.0,\n"value6":0.0,\n"value7":0,\n"value8":0,\n"value9":1,\n"value10":0.0\n},\n{\n"value0":{\n"value0":[]\n},\n"value1":7,\n"value2":2,\n"value3":0.0,\n"value4":0.0,\n"value5":0.0,\n"value6":0.0,\n"value7":0,\n"value8":0,\n"value9":1,\n"value10":0.0\n},\n{\n"value0":{\n"value0":[]\n},\n"value1":8,\n"value2":4,\n"value3":3.025,\n"value4":0.0,\n"value5":0.0,\n"value6":0.0,\n"value7":0,\n"value8":0,\n"value9":9,\n"value10":1.0\n},\n{\n"value0":{\n"value0":[]\n},\n"value1":11,\n"value2":3,\n"value3":0.7233842593524689,\n"value4":0.0,\n"value5":0.0,\n"value6":0.0,\n"value7":0,\n"value8":0,\n"value9":9,\n"value10":0.5\n}\n],\n"value2":[\n{\n"value0":{\n"value0":[]\n},\n"value1":3,\n"value2":8,\n"value3":3,\n"value4":false,\n"value5":-0.3075913635403045\n},\n{\n"value0":{\n"value0":[]\n},\n"value1":4,\n"value2":8,\n"value3":4,\n"value4":false,\n"value5":-0.0907233318088479\n},\n{\n"value0":{\n"value0":[]\n},\n"value1":7,\n"value2":8,\n"value3":7,\n"value4":false,\n"value5":0.12446286668667917\n},\n{\n"value0":{\n"value0":[]\n},\n"value1":2,\n"value2":8,\n"value3":7,\n"value4":false,\n"value5":1.0\n},\n{\n"value0":{\n"value0":[]\n},\n"value1":6,\n"value2":11,\n"value3":36,\n"value4":false,\n"value5":1.0\n},\n{\n"value0":{\n"value0":[]\n},\n"value1":11,\n"value2":8,\n"value3":37,\n"value4":false,\n"value5":0.3194615515798602\n}\n],\n"value3":7,\n"value4":1,\n"value5":0.0,\n"value6":0.0,\n"value7":0,\n"value8":0.0,\n"value9":false,\n"value10":16384,\n"value11":{\n"value0":[]\n},\n"value12":8,\n"value13":7\n}\n}\x94b\x8c\x04body\x94h\r)\x81\x94X\xe2\t\x00\x00{\n"value0":{\n"value0":0,\n"value1":[\n{\n"value0":{\n"value0":[]\n},\n"value1":1,\n"value2":1,\n"value3":0.0,\n"value4":0.0,\n"value5":0.0,\n"value6":0.0,\n"value7":0,\n"value8":0,\n"value9":1,\n"value10":0.0\n},\n{\n"value0":{\n"value0":[]\n},\n"value1":2,\n"value2":1,\n"value3":0.0,\n"value4":0.0,\n"value5":0.0,\n"value6":0.0,\n"value7":0,\n"value8":0,\n"value9":1,\n"value10":0.0\n},\n{\n"value0":{\n"value0":[]\n},\n"value1":3,\n"value2":2,\n"value3":0.0,\n"value4":0.0,\n"value5":0.0,\n"value6":0.0,\n"value7":0,\n"value8":0,\n"value9":1,\n"value10":0.0\n},\n{\n"value0":{\n"value0":[]\n},\n"value1":4,\n"value2":4,\n"value3":3.025,\n"value4":0.0,\n"value5":0.0,\n"value6":0.0,\n"value7":0,\n"value8":0,\n"value9":2,\n"value10":1.0\n},\n{\n"value0":{\n"value0":[]\n},\n"value1":5,\n"value2":4,\n"value3":3.025,\n"value4":0.0,\n"value5":0.0,\n"value6":0.0,\n"value7":0,\n"value8":0,\n"value9":2,\n"value10":1.0\n},\n{\n"value0":{\n"value0":[]\n},\n"value1":6,\n"value2":4,\n"value3":3.025,\n"value4":0.0,\n"value5":0.0,\n"value6":0.0,\n"value7":0,\n"value8":0,\n"value9":2,\n"value10":1.0\n},\n{\n"value0":{\n"value0":[]\n},\n"value1":7,\n"value2":4,\n"value3":3.025,\n"value4":0.0,\n"value5":0.0,\n"value6":0.0,\n"value7":0,\n"value8":0,\n"value9":2,\n"value10":1.0\n},\n{\n"value0":{\n"value0":[]\n},\n"value1":17,\n"value2":3,\n"value3":3.5051739939488515,\n"value4":0.0,\n"value5":0.0,\n"value6":0.0,\n"value7":0,\n"value8":0,\n"value9":0,\n"value10":0.5\n}\n],\n"value2":[\n{\n"value0":{\n"value0":[]\n},\n"value1":2,\n"value2":4,\n"value3":2,\n"value4":false,\n"value5":-0.5458908552212669\n},\n{\n"value0":{\n"value0":[]\n},\n"value1":3,\n"value2":4,\n"value3":3,\n"value4":false,\n"value5":0.3315792927782888\n},\n{\n"value0":{\n"value0":[]\n},\n"value1":1,\n"value2":6,\n"value3":7,\n"value4":false,\n"value5":-0.09644513012560535\n},\n{\n"value0":{\n"value0":[]\n},\n"value1":1,\n"value2":7,\n"value3":10,\n"value4":false,\n"value5":-0.07955120534377169\n},\n{\n"value0":{\n"value0":[]\n},\n"value1":3,\n"value2":7,\n"value3":12,\n"value4":false,\n"value5":0.1409455423164866\n},\n{\n"value0":{\n"value0":[]\n},\n"value1":1,\n"value2":17,\n"value3":64,\n"value4":false,\n"value5":1.0\n},\n{\n"value0":{\n"value0":[]\n},\n"value1":17,\n"value2":4,\n"value3":65,\n"value4":false,\n"value5":0.35603410977535168\n},\n{\n"value0":{\n"value0":[]\n},\n"value1":17,\n"value2":6,\n"value3":94,\n"value4":false,\n"value5":0.7618254477087496\n},\n{\n"value0":{\n"value0":[]\n},\n"value1":2,\n"value2":6,\n"value3":62,\n"value4":false,\n"value5":0.07936778136430833\n}\n],\n"value3":3,\n"value4":4,\n"value5":0.0,\n"value6":0.0,\n"value7":0,\n"value8":0.0,\n"value9":false,\n"value10":16384,\n"value11":{\n"value0":[]\n},\n"value12":7,\n"value13":12\n}\n}\x94bub\x8c\x07fitness\x94G?\xf0\xa2F\xe5\x89\xa5Jub.'


def main() -> None:
    """Perform the rerun."""
    setup_logging()

    individual: Individual = pickle.loads(PICKLED_GENOTYPE)
    robot = individual.genotype.develop()

    logging.info(f"Fitness from pickle: {individual.fitness}")

    evaluator = Evaluator(
        headless=False,
        num_simulators=1,
    )
    fitness = evaluator.evaluate([robot])[0]
    logging.info(f"Rerun fitness: {fitness}")


if __name__ == "__main__":
    main()
