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
    
    allWPs = instance.getListJobs()

    sol = []

    for w in allWPs:
        wp = instance.jobs[w]
        gene = []
        wpStaffPool = {}
        wo = wp.firstWorkOrder
        while wo != None:
            woStaffPool = []
            for skill in wo.notAllocated:
                skills = skill.split('|')
                sk = random.choice(skills)
                sk = sk.strip()
                # Try WP pool
                if sk in wpStaffPool:
                    rStaff = random.choice(wpStaffPool[sk])
                else:
                    rStaff = random.choice(instance.certifications[sk])
                while rStaff in woStaffPool:
                    rStaff = random.choice(instance.certifications[sk])
                    
                code= wo.id+"."+skill
                t = [rStaff,code]
                woStaffPool.append(rStaff)
                if sk not in wpStaffPool:
                    wpStaffPool[sk] = []
                wpStaffPool[sk].append(rStaff)
                gene.append(t)
            wo = wo.next
        sol.append((wp.aircraft.aircraftID+"."+ wp.id,gene))   

    random.shuffle(sol)
    return sol


def evaluate(sol, instance):
    """
    Evaluate the solution and return the number of unallocated jobs, delayed and overallocated jobs.
    """
    instance.reset()
    instance.allocate(sol)
    instance.validate()
    unalloc =instance.getUnallocated()
    over = 0
    countOver =0
    for ac in instance.aircraft:
        airc = instance.aircraft[ac]
        o = airc.over()
        over = over +o
        if o >0 :
            countOver = countOver + 1
        
    return (unalloc + over),unalloc,countOver,over

# def timeMutate(genome, instance):
#     """
#     Mutate the genome by moving the job with the longest duration to the front of the genome.
#     """
#     tl = datetime.timedelta(minutes=0)
#     gene = None

#     for _ in range(10):
#         x = random.randint(0, len(genome) - 1)
#         g = genome[x]
#         jb = g[1].split(":")[0]
#         if instance.jobs[jb].duration > tl:
#             tl = instance.jobs[jb].duration
#             gene = x

#     t = genome[gene]
#     genome.pop(gene)
#     genome.insert(0, t)
#     return genome


def mutate(genome, instance):  # TODO: comment this function
    """
    Mutate the genome by changing a random job to a random staff member or moving a job to a different position.
    """
    ch = random.randint(1,2)
    if ch ==1:
        n = random.randint(0,len(genome)-1)
        
        wp =  genome[n][1]
        gene = random.choice(wp)
        woID = gene[1].split('.')[0]
        wo = instance.WOs[woID]

        skills = gene[1].split('.')[1].split('|')
        sk = random.choice(skills)
        sk = sk.strip()
        rStaff = random.choice(instance.certifications[sk])
        
        gene[0]= rStaff
        

    if ch==2:#Move WP
        x = random.randint(0,len(genome)-1)
        y = random.randint(0,len(genome)-1)
        t = genome[x]
        genome.pop(x)
        genome.insert(y,t)
    return genome


def copyG(genome):
    """
    copy method for the genome
    Args:
        genome (_type_): _description_
    """
    n = []
    for g in genome:
        wos =[]
        for wo in g[1]:
            wos.append(wo.copy())
        nG = (g[0],wos)
        n.append(nG)
    
    return n


def contains(genome, jCode):
    """
    Check if the genome contains a job code.
    Args:
        genome (_type_): _description_
        jCode (_type_): _description_
    """
    for j in genome:
        if j[0] == jCode:
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
        raise UserWarning("Parent len mismatch")
  
    child = []
    for c in  range(len(pA)):
        if not contains(child,pA[c][0]):
                g = (pA[c][0],pA[c][1].copy())
                child.append(g)
        if not contains(child,pB[c][0]):
                g = (pB[c][0],pB[c][1].copy())
                child.append(g)
    
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
