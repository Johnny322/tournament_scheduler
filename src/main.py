#External Modules/libraries
import xml.etree.ElementTree as ET

#Selfwritten
import genetic_algorithm as ga

def gen_sport_dict(teams):
    sport_dict = {}
    for team in teams:
        #Info
        id = team.get('Id')
        group_id = team.get('Group_id')
        sport = team.get('Sport')
        if sport not in sport_dict:
            sport_dict[sport] = {}
        if group_id not in sport_dict[sport]:
            sport_dict[sport][group_id] = []

        sport_dict[sport][group_id].append(id)
    return sport_dict

def gen_timeslot_dicts(sport_dict):
    total_matches_dict = {}
    matches = {}
    index = 0
    for sport in sport_dict:
        total = 0
        for group_id in sport_dict[sport]:
            count = 0
            previous_teams = []
            for team in sport_dict[sport][group_id]:
                count +=1
                for team1 in sport_dict[sport][group_id]:
                    if(team != team1 and team1 not in previous_teams):
                        match = [team, team1, sport]
                        matches[index] = match
                        index+=1
                previous_teams.append(team)
            for i in range(count):
                total += i


        total_matches_dict[sport] = total

    largest_sport = max(total_matches_dict, key=total_matches_dict.get)
    time_slots = {}
    for i in range(total_matches_dict[largest_sport]):
        time_slots[i] = {}

    return time_slots, matches

def get_data(filename):
    tree = ET.parse(filename)
    root = tree.getroot()

    app = root.find('Sport')
    sport_dict = gen_sport_dict(app)

    time_slots, matches = gen_timeslot_dicts(sport_dict)

    return sport_dict, time_slots, matches



def run(amount_of_overlaps_allowed, filename, generations = 10):
    folder = "teams/"
    sport_dict, time_slots, matches = get_data(folder+filename)
    sport_list = list(sport_dict.keys())
    population = ga.gen_pop(10,matches,time_slots,sport_list)

    # times = ["16:20", "17:00", "17:40", "18:20"]
    # counter = 0
    # for time_slot in population[0]:
    #     if time_slot % 4 == 0:
    #         counter += 1
    #     print('Day ', counter, ', ', times[time_slot % 4])
    #     for sport in population[0][time_slot]:
    #         if (population[0][time_slot][sport] == "Buffer"):
    #             print("Buffer")
    #         elif (population[0][time_slot][sport] != None):
    #             i = population[0][time_slot][sport][0]
    #             print(matches[i])

    fitness_scores, overlaps = ga.fitness(population, matches)
    fittest_idx, second_fittest_idx = ga.select(fitness_scores)

    while(fitness_scores[fittest_idx] > amount_of_overlaps_allowed):
        fittest = population[fittest_idx]
        second_fittest = population[second_fittest_idx]
        print("fittest: ",fitness_scores[fittest_idx])

        #Create 2 new children from the 2 fittest parents
        child1, child2 = ga.crossover(fittest, second_fittest)
        child1 = ga.mutation(child1, sport_list, matches)
        child2 = ga.mutation(child2, sport_list, matches)
    
        #replace least fit with most fit's offspring
        least_fit1, least_fit2 = ga.find_least_fit(fitness_scores)
        population[least_fit1] = child1
        population[least_fit2] = child2
        for chromosome in range(len(population)):
            population[chromosome] = ga.mutation(population[chromosome], sport_list, matches)
        fitness_scores, overlaps = ga.fitness(population, matches)
        fittest_idx, second_fittest_idx = ga.select(fitness_scores)

    print("fittest: ", fitness_scores[fittest_idx])
    times = ["16:20", "17:00", "17:40", "18:20"]
    counter = 0
    for time_slot in population[fittest_idx]:
        if time_slot % 4 == 0: counter+=1
        print('Day ', counter, ', ', times[time_slot % 4])
        for sport in population[fittest_idx][time_slot]:
            if (population[fittest_idx][time_slot][sport] == "Buffer"):
                print("Buffer")
            elif (population[fittest_idx][time_slot][sport] != None):
                i = population[fittest_idx][time_slot][sport][0]
                print(matches[i])
    for entry in overlaps[fittest_idx].keys():
        print('Day ', int(entry / 4)+1, ', ', times[(entry-1) % 4], ' and ', times[entry % 4], ' contains conflict of team(s) ', overlaps[fittest_idx][entry])
           

run(9,"teams.xml", 100)
