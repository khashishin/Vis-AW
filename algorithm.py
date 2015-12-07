# coding=utf-8
import json
import numpy as np
import itertools
import html_handler

big_m = 9999999


class Dendrite:
    def __init__(self, data, metric, objects_maping):

        self.final_number_of_groups = 1
        self.data = data
        self.nodes, self.links = [], []
        self.matrix = []

        self.groups = []
        self.groups_maping = {}  # Maps groups into numbers 0,1,2... for easier indexing in algorithms.
        self.objects_maping = objects_maping
        self.metrics_dict ={"Najblizszy sasiad": "closest neighbour",
                            "Najdalszy sasiad": "farthest neighbour"}
        self.distance_metric = self.metrics_dict[metric]
        self.original_matrix = []
        self.groups_to_join = []

    def calculate_closest_nodes(self,matrix, first_iteration):
        neighbours_dict = {}
        print 'Calculating closest nodes... Current matrix:'
        for row in range(len(matrix)):
            print matrix[row]
            row_min = min(matrix[row])
            for col in range(len(matrix[row])):
                if matrix[row][col] == row_min:
                    neighbours_dict[row] = {"target": col, "bond": 1, "length": matrix[row][col]}
                    self.add_point_to_group(row, col)
                    if col in neighbours_dict.keys() and neighbours_dict[col]["target"] == row and neighbours_dict[row]["target"] == col:
                        neighbours_dict[col]["bond"] = 2
                        neighbours_dict[row]["bond"] = 2
                    break
        print "Found neighbours:"
        print neighbours_dict
        self.remove_duplicates_from_groups()
        if first_iteration:
            for key, value in neighbours_dict.iteritems():
                self.add_link(key, value["target"], value["bond"], value["length"])

        else:  # If we join groups with groups/nodes:
            for key, value in neighbours_dict.iteritems():
                if len(self.groups[key]) > 1:

                    print "Want to join", self.groups[key], "with", self.groups[value["target"]]
                    mini = (0, 0, big_m) # Minimal distance and it's nodes
                    for node in self.groups[key]:
                        for node2 in self.groups[value["target"]]:
                            if self.original_matrix[node][node2] < mini[2]:
                                mini = (node, node2,  self.original_matrix[node][node2])
                            # print node, node2, "distance:", original_matrix[node][node2]
                    # print "Joining by", mini
                    self.add_link(mini[0], mini[1], 1, mini[2])
                    self.add_to_groups_joining(key, value["target"])

            self.join_groups()

    def add_to_groups_joining(self,group1_id, group2_id):
        self.groups_to_join.append(sorted((group1_id, group2_id)))

    def join_groups(self):
        self.groups_to_join.sort()
        final_joining = list(k for k,_ in itertools.groupby(self.groups_to_join))  # Deleting BA if (AB and BA) - duplicates
        # print groups
        new_groups = []
        for joining in final_joining:
            new_groups.append(self.groups[joining[0]] + self.groups[joining[1]])

        self.set_as_new_groups(new_groups)

    def set_as_new_groups(self, new_groups):
        del self.groups[:]
        for group in new_groups:
            self.groups.append(group)
        # TODO od tad: mam nowe grupy, juz polaczone, teraz caly proces dalej zapetlic. Zaczac od przeliczenia groups_maping

    def add_point_to_group(self, point, point2):
        for group in self.groups:
            if point2 in group:
                group.append(point)
                return
        self.groups.append([point, point2])

    def remove_duplicates_from_groups(self,):
        for group in range(len(self.groups)):
            self.groups[group] = list(set(self.groups[group]))

    def rebuild_matrix(self,links):
        c = 0
        for group in self.groups:
            self.groups_maping[c] = group
            c += 1
        print "Rebuilding matrix... New group maping:"
        print self.groups_maping
        return self.get_distance_between_groups()

    def get_distance_between_groups(self):
        if self.distance_metric == "closest neighbour":
            return self.get_closest_neighbour_distance("closest")
        if self.distance_metric == "farthest neighbour":
            return self.get_closest_neighbour_distance("farthest")
        # TODO: dodac wiecej opcji liczenia dystansu
        # Mozliwe opcje:
        # najblizszy sasiad - jest
        # najdalszy sasiad  - wystarczy zmienic z min na max
        # formula srednich grupowych - bez sensu
        # uogolniona odleglosc Mahalanobisa - potrzebna metoda liczenia centroidow oraz
        # macierzy wariancji i kowariancji zmiennych (zawsze przy porownywaniu 2 grup)
        # moge sie tego podjac - Hinc

    def get_closest_neighbour_distance(self, type):
        n = len(self.groups)
        result_matrix = [[big_m for _ in range(n)] for _ in range(n)]
        for row in range(n):
            for col in range(n):
                if row == col:  # TODO zrobic tak zeby tylko jedna polowa macierzy sie przeliczala i kopiowala, a nie ze obie robia to samo 2 razy
                    pass
                else:
                    if type == "closest":
                        distance = min(self.get_all_distances(self.groups_maping[row], self.groups_maping[col]))
                    else: # if type == "farthest":
                        distance = max(self.get_all_distances(self.groups_maping[row], self.groups_maping[col]))
                    result_matrix[row][col] = distance
        return result_matrix

    def get_all_distances(self, group1, group2):
        return [self.matrix[x][y] for x in group1 for y in group2]

    def add_link(self,node1, node2, bond, length):
        self.links.append({"source": node1, "target": node2, "bond": bond, "length": length})

    def add_nodes(self):
        for x in range(len(self.objects_maping)):
            self.nodes.append({"node": self.objects_maping[x]})

    def get_json(self):
        critical_value = self.get_critical_value()
        result = {"nodes": self.nodes,
                  "links": self.links,
                  "mean": critical_value[0],
                  "std_dev":critical_value[1]}
        return json.dumps(result)

    def calculate(self):

        if self.data == 0:
            self.matrix = get_3_level_sample()
        else:
            self.matrix = self.data
        self.original_matrix = self.matrix
        self.add_nodes()
        self.calculate_closest_nodes(self.matrix, True)
        if len(self.groups) == self.final_number_of_groups:
             # End of the work.
            print self.get_json()
        else:
            self.remove_duplicates_from_groups()
            self.matrix = self.rebuild_matrix(self.links)
            self.calculate_closest_nodes(self.matrix, False)  # TODO: od tad - a konkretrnie False przy first_iteration. Polaczyc odpowiednie krawedzie pomiedzy grupami

        # self.remove_duplicates_from_groups()
        # self.matrix = self.rebuild_matrix(self.links)
        # self.calculate_closest_nodes(self.matrix, False)

        print "Links:"
        for link in self.links:
            print link
        print self.groups
        # print self.get_json()
        self.process_visualisation() TODO: odkomentowac

    def process_visualisation(self):

        w = html_handler.Handler(self.get_json())
        w.write_html()
        w.open_visualisation()

    def get_critical_value(self):
        values = []
        for value in self.links:
            values.append(value["bond"])
        np_array = np.array(values)
        # print 'srednia', np_array.mean(), "odch", np_array.std()
        return np_array.mean(),np_array.std()


def get_3_level_sample():
        # TODO: remove in production
        return [[9999999,	1,	2,	9,	9,	9,	9,	9],
    [1,	9999999,	9,	9,	9,	9,	9,	9],
    [2,	9,	9999999,	1,	3,	9,	9,	9],
    [9,	9,	1,	9999999,	9,	9,	9,	9],
    [9,	9,	3,	9,	9999999,	1,	2,	9],
    [9,	9,	9,	9,	1,	9999999,	9,	9],
    [9,	9,	9,	9,	2,	9,	9999999,	1],
    [9,	9,	9,	9,	9,	9,	1,	9999999]]


def prepare_data(data):
    n = len(data[0])
    data[0][0] = ""
    for x in range(n):
        for y in range(n):
            if x == y:
                data[x][y] = big_m
    return data


def run(data, metric, objects_maping):
    data = prepare_data(data)
    d = Dendrite(data, metric, objects_maping)
    d.calculate()

if __name__ == '__main__':
    maping = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h'}

    d = Dendrite(0, "Najblizszy sasiad", maping)
    d.calculate()
