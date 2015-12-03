import json
import numpy as np
import itertools


N = 8
final_number_of_groups = 1
bigM = 9999999
nodes, links = [], []

groups = []
groups_maping = {}  # Maps groups into numbers 0,1,2... for easier indexing in algorithms.
distance_metric = "closest neighbour"
original_matrix = []
groups_to_join = []

def get_fixed_sample():
    return [[9999999, 8, 9, 6, 2],
            [8, 9999999, 5, 0, 1],
            [9, 5, 9999999, 4, 0],
            [6, 0, 4, 9999999, 5],
            [2, 1, 0, 5, 9999999]]

def get_3_level_sample():
    return [
[9999999,	1,	2,	9,	9,	9,	9,	9],
[1,	9999999,	9,	9,	9,	9,	9,	9],
[2,	9,	9999999,	1,	3,	9,	9,	9],
[9,	9,	1,	9999999,	9,	9,	9,	9],
[9,	9,	3,	9,	9999999,	1,	2,	9],
[9,	9,	9,	9,	1,	9999999,	9,	9],
[9,	9,	9,	9,	2,	9,	9999999,	1],
[9,	9,	9,	9,	9,	9,	1,	9999999]]


def get_sample_data():
    b = np.random.random_integers(0, 10, size=(N, N))
    b_symm = (b + b.T) / 2

    for row in range(N):
        for column in range(N):
            if row == column:
                b_symm[row][column] = bigM
    return b_symm


def calculate_closest_nodes(matrix, first_iteration):
    # points = [x for x in range(N)]
    neighbours_dict = {}
    print 'Calculating closest nodes... Current matrix:'
    for row in range(len(matrix)):
        print matrix[row]
        row_min = min(matrix[row])
        for col in range(len(matrix[row])):

            if matrix[row][col] == row_min:
                # print row, col, matrix[row][col], 'kek'

                neighbours_dict[row] = {"target": col, "bond": 1, "length": matrix[row][col]}
                add_point_to_group(row, col)

                if col in neighbours_dict.keys() and neighbours_dict[col]["target"] == row and neighbours_dict[row]["target"] == col:
                    neighbours_dict[col]["bond"] = 2
                    neighbours_dict[row]["bond"] = 2

                break

    # print matrix
    print "Found neighbours:"
    print neighbours_dict
    remove_duplicates_from_groups()


    if first_iteration:
        for key, value in neighbours_dict.iteritems():
            add_link(key, value["target"], value["bond"], value["length"])

    else:  # If we join groups with groups/nodes:
        new_groups = groups
        for key, value in neighbours_dict.iteritems():
            if len(groups[key]) > 1:

                print "Want to join", groups[key], "with", groups[value["target"]]
                mini = (0, 0, bigM)
                for node in groups[key]:
                    for node2 in groups[value["target"]]:
                        if original_matrix[node][node2] < mini[2]:
                            mini = (node, node2,  original_matrix[node][node2])
                        # print node, node2, "distance:", original_matrix[node][node2]
                # print "Joining by", mini
                add_link(mini[0], mini[1], 1, mini[2])
                add_to_groups_joining(key, value["target"])

        join_groups()

def add_to_groups_joining(group1_id, group2_id):
    groups_to_join.append(sorted((group1_id, group2_id)))

def join_groups():
    groups_to_join.sort()
    final_joining = list(k for k,_ in itertools.groupby(groups_to_join))  # Deleting BA if (AB and BA) - duplicates
    # print groups
    new_groups = []
    for joining in final_joining:
        new_groups.append(groups[joining[0]] + groups[joining[1]])

    set_as_new_groups(new_groups)

def set_as_new_groups(new_groups):
    del groups[:]
    for group in new_groups:
        groups.append(group)
    # TODO od tad: mam nowe grupy, juz polaczone, teraz caly proces dalej zapetlic. Zaczac od przeliczenia groups_maping



def add_point_to_group(point, point2):
    for group in groups:
        if point2 in group:
            group.append(point)
            return

    groups.append([point, point2])

def remove_duplicates_from_groups():
    for group in range(len(groups)):
        groups[group] = list(set(groups[group]))

def rebuild_matrix(links):
    c = 0
    for group in groups:
        groups_maping[c] = group
        c += 1
    print "Rebuilding matrix... New group maping:"
    print groups_maping

    return get_distance_between_groups()


def get_distance_between_groups():
    if distance_metric == "closest neighbour":
        return get_closest_neighbour_distance()
    # TODO: dodac wiecej opcji liczenia dystansu

def get_closest_neighbour_distance():
    n = len(groups)
    result_matrix = [[bigM for _ in range(n)] for _ in range(n)]
    for row in range(n):
        for col in range(n):
            if row == col:  # TODO zrobic tak zeby tylko jedna polowa macierzy sie przeliczala i kopiowala, a nie ze obie robia to samo 2 razy
                pass
            else:
                distance = min(get_all_distances(groups_maping[row], groups_maping[col]))
                # print "dist", distance
                result_matrix[row][col] = distance
    return result_matrix

def get_all_distances(group1, group2):
    # print "-",group1, group2
    result = []
    for x in group1:
        for y in group2:
            # print x,y, matrix[x][y]
            result.append(matrix[x][y])
    return result

def add_link(node1, node2, bond, length):
    links.append({"source": node1, "target": node2, "bond": bond, "length": length})


def add_nodes():
    for x in range(N):
        nodes.append({"node": x})


def get_json():
    result = {"nodes": nodes,
              "links": links}
    return json.dumps(result)


add_nodes()
# matrix = get_fixed_sample()
matrix= get_3_level_sample()
original_matrix = matrix

calculate_closest_nodes(matrix, True)
if len(groups) == final_number_of_groups:
    # "Jego glowna zaleta jest mozliwosc okreslenia liczby wynikowych grup."
    # https://pl.wikipedia.org/wiki/Dendryt_wroc%C5%82awski
     # End of the work.
    print get_json()
else:
    remove_duplicates_from_groups()
    matrix = rebuild_matrix(links)
    calculate_closest_nodes(matrix, False)  # TODO: od tad - a konkretrnie False przy first_iteration. Polaczyc odpowiednie krawedzie pomiedzy grupami

# remove_duplicates_from_groups()
# matrix = rebuild_matrix(links)
# calculate_closest_nodes(matrix, False)

print "Links:"
for link in links:
    print link
print groups
# print get_json()