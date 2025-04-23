import typing
import random
from datetime import datetime, timedelta


"""
This module contains relevant functions for the EA model.
It includes the function to generate a random solution for the problem.
"""


#
def randSol(instance):
    """_summary_

    Args:
        instance (_type_): _description_

    Returns:
        _type_: _description_

    The function to generate a random genome for the problem.
    """
    instance.reset()
    availStaff = instance.getListStaff()

    allJobs = instance.getListJobs()
    sol = []
    for j in allJobs:
        theJob = instance.jobs[j]
        c = 1
        for c in range(len(theJob.notAllocated)):

            rStaff = random.choice(availStaff)
            while not theJob.check(instance.staff[rStaff]):
                rStaff = random.choice(availStaff)

            code = j + ":" + str(c)
            t = [rStaff, code]
            sol.append(t)
            c = c + 1
    random.shuffle(sol)
    return sol


def evaluate(sol, instance):
    """_summary_

    Args:
        sol (_type_): _description_
        instance (_type_): _description_

    Returns:
        _type_: _description_

    Evaluate the fitness values and return the number of unallocated jobs, delayed jobs and overallocated jobs.
    """
    instance.reset()
    for g in sol:
        j = g[1].split(":")[0]
        instance.allocate(instance.staff[g[0]], instance.jobs[j])

    instance.validate()
    unalloc = instance.getUnallocated()
    over = 0
    countOver = 0
    for ac in instance.aircraft:
        airc = instance.aircraft[ac]
        o = airc.over()
        over = over + o
        if o > 0:
            countOver = countOver + 1

    return (unalloc + over), unalloc, countOver, over
