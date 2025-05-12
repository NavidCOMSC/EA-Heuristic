from typing import List, Tuple, Dict, Any
import random
import datetime


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
    """
    Evaluate the solution and return the number of unallocated jobs, delayed and overallocated jobs.
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


def timeMutate(genome, instance):
    """
    Mutate the genome by moving the job with the longest duration to the front of the genome.
    """
    tl = datetime.timedelta(minutes=0)
    gene = None

    for _ in range(10):
        x = random.randint(0, len(genome) - 1)
        g = genome[x]
        jb = g[1].split(":")[0]
        if instance.jobs[jb].duration > tl:
            tl = instance.jobs[jb].duration
            gene = x

    t = genome[gene]
    genome.pop(gene)
    genome.insert(0, t)
    return genome


def mutate(genome, instance):  # TODO: comment this function
    """
    Mutate the genome by changing a random job to a random staff member or moving a job to a different position.
    """
    ch = random.randint(0, 3)
    if ch == 1:
        n = random.randint(0, len(genome) - 1)
        availStaff = instance.getListStaff()

        j = genome[n][1].split(":")[0]
        theJob = instance.jobs[j]
        rStaff = random.choice(availStaff)
        while not theJob.check(instance.staff[rStaff]):
            rStaff = random.choice(availStaff)
        genome[n][0] = rStaff

    if ch == 2:
        x = random.randint(0, len(genome) - 1)
        y = random.randint(0, len(genome) - 1)
        t = genome[x]
        genome.pop(x)
        genome.insert(y, t)
    if ch == 3:
        genome = timeMutate(genome, instance)
    return genome


def copyG(genome):
    """
    copy method for the genome
    Args:
        genome (_type_): _description_
    """
    n = []
    for g in genome:
        n.append(g.copy())

    return n


def contains(genome, jCode):
    """
    Check if the genome contains a job code.
    Args:
        genome (_type_): _description_
        jCode (_type_): _description_
    """
    for j in genome:
        if j[1] == jCode:
            return True
    return False


def xo(pA, pB):
    """
    Crossover function for the EA model.
    Args:
        pA (_type_): _description_
        pB (_type_): _description_
    """
    if len(pA) != len(pB):
        print("Parent len mismatch")

    child = []
    for c in range(len(pA)):
        if not contains(child, pA[c][1]):
            child.append(pA[c].copy())
        if not contains(child, pB[c][1]):
            child.append(pB[c].copy())

    return child


def tour(pop):
    """
    Tournament selection function for the EA model.
    Args:
        pop (_type_): _description_
    """
    p1 = random.choice(pop)
    p2 = random.choice(pop)

    if p1[0] < p2[0]:
        return p1
    else:
        return p2


def rip(pop):
    """
    Roulette selection function for the EA model.
    """
    p1 = random.choice(pop)
    p2 = random.choice(pop)

    if p1[0] > p2[0]:
        return p1
    else:
        return p2
