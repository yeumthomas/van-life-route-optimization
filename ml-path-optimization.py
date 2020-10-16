import googlemaps
from itertools import combinations
import config
import random

maps = googlemaps.Client(key=config.API_KEY)

trip_waypoints = [
    # TEXAS
    "Mary's, 3853 N St Mary's St, San Antonio, TX 78212",  # San Antonio Japanese Tea Garden
    "Austin, TX 78712",  # UT Austin
    "1311 S 5th St, Waco, TX 76706",  # Baylor Uni
    "800 W Campbell Rd, Richardson, TX 75080",  # UTD
    "Katy, TX", # Katy

    # OKLAHOMA
    "Davis, OK 73030",  # Turner Falls

    # KANSAS,
    "Wichita, KA",

    # COLORADO
    "1805 N 30th St, Colorado Springs, CO 80904", # Garden of the Gods
    "Mesa Verde, CO",

    # NEBRASKA
    "Unnamed Road, Gering, NE 69341",  # Scotts Bluff National Monument (oregon trail stuff)

    # SOUTH DAKOTA
    "13000 SD-244, Keystone, SD 57751",  # Mt. Rushmore

    # NORTH DAKOTA
    "203 14th St W, Dickinson, ND 58601",  # Pho bc there's nothing else to do in this state

    # WYOMING
    "Yellowstone National Park, WY 82190",  # Old Faithful
    "Cheyenne, WY",

    # WASHINGTON
    "16272 Cleveland St, Redmond, WA 98052",  # Redmond, near Mt. Rainier National Park

    # IDAHO
    "Idaho Falls, ID",

    # OREGON
    "Oregon 97604",  # Crater Lake

    # UTAH
    "Corinne, UT 84307",  # Pink Lake

    # NEVADA
    "120 NV-28, Crystal Bay, NV 89402",  # Lake Tahoe
    "3900 S Las Vegas Blvd, Las Vegas, NV 89119",  # Las Vegas

    # NORTHERN CALIFORNIA
    "Bay Area, CA",  # Bay Area
    "Yosemite Village, CA 95389",  # Yosemite
    "Sacramento, CA",  # Sacramento
    "San Jose",

    # SOUTHERN CALIFORNIA
    "909 W Valencia Dr #2106, Fullerton, CA 92832",  # Fullerton

    # ARIZONA
    "Grand Canyon Village, AZ 86023",  # Grand Canyon

    # NEW MEXICO
    "albuquerque, NM 87413"  # Bisti/De-Na-Zin Wildernes
]

def get_distances_times(waypoints):
    """
    Finds distances and the duration of travel by car bt each 2 locations
    :param waypoints: dictionary of all locations to travel to
    :return: distance and time matrices between each 2 locations
    """
    distances, times = {}, {}
    all_waypoints = set()

    print("BEGINNING CALCULATION OF DISTANCES AND DURATIONS...")
    for (waypoint1, waypoint2) in combinations(waypoints, 2):
        try:
            routes = maps.distance_matrix(origins=[waypoint1],
                                          destinations=[waypoint2],
                                          mode="driving",
                                          language="English",
                                          units="metric")

            distance = routes["rows"][0]["elements"][0]["distance"]["value"]
            duration = routes["rows"][0]["elements"][0]["duration"]["value"]  # in seconds

            distances[frozenset([waypoint1, waypoint2])] = distance
            times[frozenset([waypoint1, waypoint2])] = duration
            all_waypoints.update([waypoint1, waypoint2])

        except Exception:
            print("rip: " + waypoint1 + " ++ " + waypoint2)

    print("FINISHED CALCULATING ALL DISTANCES AND TIMES")
    return distances, times, all_waypoints


def calculate_fitness(path, distances):
    """
    Gets the fitness of a current solution.
    :param path: lst of waypoints in order of path
    :return: single value of fitness
    """
    fitness = 0.0

    for ind, location in enumerate(path):
        waypoint1 = path[ind - 1]
        waypoint2 = path[ind]
        fitness += distances[frozenset([waypoint1, waypoint2])]

    return fitness


def create_random_path():
    """
    Creates a random path for road trip.
    :param all_waypoints: set of all waypoints
    :return: random path
    """
    random_path = list(trip_waypoints)
    random.shuffle(random_path)
    return tuple(random_path)


def mutate_path(path_genome, max_mutations=2):
    """
    makes somewhere bt 1 and max_mutations point mutations to the path
    :param path_genome: set of possible locations
    :param max_mutations: max number of point mutations made
    :return: randomized path with point mutations done
    """
    path_genome = list(path_genome)
    total_mutations = random.randint(1, max_mutations)

    for mutation in range(total_mutations):
        swap_ind1 = random.randint(0, len(path_genome) - 1)
        swap_ind2 = swap_ind1

        while swap_ind1 == swap_ind2:
            swap_ind2 = random.randint(0, len(path_genome) - 1)

        path_genome[swap_ind1], path_genome[swap_ind2] = path_genome[swap_ind2], path_genome[swap_ind1]

    return tuple(path_genome)


def shuffle_mutation(path_genome):
    """
    Applies one shuffle mutation, where section of entire path is uprooted and placed somewhere else
    :param path_genome: set of locations on path
    :return: path of locations in mutated order
    """
    path_genome = list(path_genome)

    ind_beginning_of_swap = random.randint(0, len(path_genome) - 1)
    length = random.randint(2, 15)
    clipped_genome = path_genome[ind_beginning_of_swap: ind_beginning_of_swap + length]
    path_genome = path_genome[:ind_beginning_of_swap] + path_genome[ind_beginning_of_swap + length:]
    insert_ind = random.randint(0, (len(path_genome) + len(clipped_genome)))

    return tuple(path_genome[:insert_ind] + clipped_genome + path_genome[insert_ind:])


def generate_rando_pop(pop_size, all_waypoints):
    """
    creates pop_size number of random paths
    :param pop_size: number of paths
    :param all_waypoints: set of all waypoints
    :return: lst of randomly generated paths
    """
    random_pop = []
    for ind in range(pop_size):
        random_pop.append(create_random_path())
    return random_pop


def run(waypoints, generations=5000, population_size=100):
    """
    runs the entire script
    :param generations: total generations/iterations of script
    :param population_size: number of paths
    :return: optimal path
    """
    current_best_distance = -1
    population_subset_size = int(population_size / 10.)
    generations_tenth = int(generations / 10.)

    # calculate all distances and times
    distances, times, all_waypoints = get_distances_times(waypoints)

    print(all_waypoints)
    # initial population
    population = generate_rando_pop(population_size, waypoints)

    for generation in range(generations):

        # get fitness of each path
        pop_fitness = {}

        for path_genome in population:
            if path_genome in pop_fitness:
                continue
            pop_fitness[path_genome] = calculate_fitness(path_genome, distances)

        # get 10% best
        new_population = []
        for rank, path_genome in enumerate(sorted(pop_fitness, key=pop_fitness.get)[:population_subset_size]):

            if (generation % generations_tenth == 0 or generation == generations - 1) and rank == 0:
                print("Generation %d best: %d | Unique genomes: %d" % (generation + 1,
                                                                       pop_fitness[path_genome],
                                                                       len(pop_fitness)))
                print(path_genome)
                print("")

                if pop_fitness[path_genome] < current_best_distance or current_best_distance < 0:
                    print("THIS IS THE BEST PATH YET: ")
                    print(path_genome)
                    print("DISTANCE OF: ", pop_fitness[path_genome])
                    print(" ")

            new_population.append(path_genome)

            # 2 offspring will get point mutation
            for offspring in range(2):
                new_population.append(mutate_path(path_genome, 3))

            # 7 offspring will get shuffle mutation
            for offspring in range(7):
                new_population.append(shuffle_mutation(path_genome))

        # Replace the old population with the new population of offspring
        for i in range(len(population))[::-1]:
            del population[i]

        population = new_population

    return population[0]

print("RUNNING AI")
run(trip_waypoints)