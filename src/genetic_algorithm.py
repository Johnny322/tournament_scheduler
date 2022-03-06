#import xml.etree.ElementTree as ET
import random, sys, math

def gen_chromosome(matches, time_slots, sport_list):
    chromosome = {}
    toast = list(time_slots.keys())
    already_used = []
    buffer = len(toast) - 12
    for time_slot in range(len(toast)):
        chromosome[toast[time_slot]] = {}
        for sport in sport_list:

            gene = random.choices(range(len(matches.keys())))

            if len(already_used) >= len(matches.keys()):
                if time_slot > buffer:
                    chromosome[toast[time_slot]][sport] = "Buffer"
                else:
                    chromosome[toast[time_slot]][sport] = None
            else:
                already_tried = already_used.copy()
                while ((gene in already_tried) or (matches[gene[0]][2] != sport)) and (len(already_tried)<len(matches.keys())):
                    # print(matches[gene[0]])
                    if gene not in already_tried:
                        already_tried.append(gene)
                    gene = random.choices(range(len(matches.keys())))
                if(len(already_tried)>=len(matches.keys())):
                    if time_slot > buffer:
                        chromosome[toast[time_slot]][sport] = "Buffer"
                    else:
                        chromosome[toast[time_slot]][sport] = None
                else:
                    # print(matches[gene[0]][2], ' == ', sport)
                    # print('Appending ', gene[0], ' to already used, which is ', matches[gene[0]])
                    already_used.append(gene)
                    # print('Already used = ', already_used)
                    # print(time_slot, ', ', sport, ' now contains ', matches[gene[0]])
                    chromosome[toast[time_slot]][sport] = gene
    # print('done')
    return chromosome

def gen_pop(pop_size,matches,time_slots, sport_list):
    return [gen_chromosome(matches, time_slots, sport_list) for _ in range(pop_size)]

def pretty_print_dict(dic):
    for d in dic.items():
        print(d)
    print("\n")

def find_least_fit(fitness_scores):
    fitness_scores_values = list(fitness_scores.values())
    fitness_scores_values_copy = list(fitness_scores_values)

    least_fittest_value = min(fitness_scores_values)
    least_fittest = fitness_scores_values.index(least_fittest_value)
    fitness_scores_values.remove(least_fittest_value)

    second_least_fittest_value = min(fitness_scores_values)
    second_least_fittest = fitness_scores_values_copy.index(second_least_fittest_value)
    return least_fittest, second_least_fittest

def select(fitness_scores):
    fitness_scores_values = list(fitness_scores.values())
    fitness_scores_values_copy = list(fitness_scores_values)
    fittest_value = min(fitness_scores_values)
    fittest = fitness_scores_values.index(fittest_value)
    fitness_scores_values.remove(fittest_value)
    second_fittest_value = min(fitness_scores_values)
    second_fittest = fitness_scores_values_copy.index(second_fittest_value)
    return fittest,second_fittest

def crossover(parent1, parent2):
    if len(parent1) != len(parent2):
        raise ValueError("Genomes did not have same length")
    length = 3
    crossover_integer = random.randint(0, length - 1)
    child1 = {}
    child2 = {}
    sports_list = list(parent1[0].keys())
    for i in range(len(parent1)):
        child1[i] = parent1[i]
        child1[i][sports_list[crossover_integer]] = parent2[i][sports_list[crossover_integer]]
        child2[i] = parent2[i]
        child2[i][sports_list[crossover_integer]] = parent1[i][sports_list[crossover_integer]]

    return child1, child2

def mutation(chromosome,sport_list, mutate_probability = 0.5):
    for i in range(75):
        index1 = random.randrange(len(chromosome))
        index2 = random.randrange(len(chromosome))
        index_list = random.randrange(len(sport_list))
        if not(random.random() > mutate_probability):
            while (chromosome[index1][sport_list[index_list]] == "Buffer" or chromosome[index2][sport_list[index_list]] == "Buffer"):
                index1 = random.randrange(len(chromosome))
                index2 = random.randrange(len(chromosome))
            temp = chromosome[index1][sport_list[index_list]]
            chromosome[index1][sport_list[index_list]] = chromosome[index2][sport_list[index_list]]
            chromosome[index2][sport_list[index_list]] = temp
    return chromosome

def calculate_interference(task, sorted_task_dict, prev_task_list, wcet_factor):
    D_deadline, T_period, T_wcet, cpu_id, core_id, wcrt = task
    if prev_task_list == []:
        return T_wcet*wcet_factor, T_period, T_wcet
    last_task = prev_task_list[len(prev_task_list)-1]
    prev_task_list.remove(last_task)
    P_interference, P_period, P_wcet = calculate_interference(sorted_task_dict[last_task], sorted_task_dict, prev_task_list, wcet_factor)
    interference = T_wcet*wcet_factor + math.ceil(P_interference/P_period)*P_wcet*wcet_factor #computes interferencecalculate_interference()
    return interference, T_period, T_wcet

def create_sorted_task_dict(tasks_for_core, tasks, wcet_factor, cpu_id, core_id):
    task_dict = {}
    for gene_id in tasks_for_core:
        task = tasks[gene_id]
        deadline, period, wcet, task_id = int(task["Deadline"]), int(task["Period"]), int(task["WCET"]), int(task["Id"])
        task_dict[gene_id] = [deadline, period, wcet, cpu_id, core_id, 0]
    sorted_task_list = sorted(task_dict.items(), key = lambda x : x[1][0])
    sorted_task_dict = {i : l for i,l in sorted_task_list}
    return sorted_task_dict

#compute fitness values to optimize solution to problem
def fitness(population, matches):
    fitness_scores = {}
    # gene_ids = list(map(int,list(tasks.keys())))
    fitness_chromo_dict = {}
    overlaps = {}
    for i in range(len(population)): #chromosome encodes a solution (list of core id's)
        overlaps[i] = {}
        counter = 0
        total_fitness = 0
        prev_slot = []
        for time_slot in population[i]:
            # print('timeslot = ',chromosome[time_slot])
            team_list = []
            for entry in population[i][time_slot]:
                if(population[i][time_slot][entry] != None and population[i][time_slot][entry] != "Buffer"):
                    a = population[i][time_slot][entry][0]
                    # print('match_id = ',i)
                    # print('added ', matches[i])
                    team_list.append(matches[a][0])
                    team_list.append(matches[a][1])
                    # print('added ', matches[i][1])
            # print('team_list = ',team_list)
            # print('len of team_list = ',len(team_list))
            # print('len of team_set = ',len(set(team_list)))
            if(len(team_list)>len(set(team_list))):
                # print("This not good")
                total_fitness += 10000
            if counter % 4 != 0:
                if(len(prev_slot)>0):
                    # print("prev_slot = ",prev_slot)
                    # print("team_list = ",team_list)
                    for team in team_list:
                        if team in prev_slot:
                            # print("team ",team, " is in prevlist and is added to overlaps")
                            if time_slot in overlaps[i].keys():
                                overlaps[i][time_slot].append(team)
                            else:
                                overlaps[i][time_slot] = [team]
                            total_fitness += 1
            counter+=1
            prev_slot = team_list
        # print("")
        fitness_scores[i] = total_fitness
    return fitness_scores, overlaps
