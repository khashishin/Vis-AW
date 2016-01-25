# coding=utf-8
import json
import time

import numpy as np
import itertools
import html_handler
import graph_algorithms

big_m = 9999999  # Value on 


class Dendrite:
    def __init__(self, data, metric, objects_mapping):

        self.final_number_of_groups = 1  # Side-effect usability - program can stop after having n groups.
        self.data = data
        self.nodes, self.links = [], []
        self.matrix = []

        self.groups = []
        self.groups_mapping = {}  # Maps groups into numbers 0,1,2... for easier indexing in algorithms.
        self.objects_mapping = objects_mapping  # Maps outer names of objects into numbers.
        self.metrics_dict = {"Najblizszy sasiad": "closest neighbour",
                             "Najdalszy sasiad": "farthest neighbour"}
        self.distance_metric = self.metrics_dict[metric]
        self.original_matrix = []  # Original distance matrix.
        self.groups_to_join = []
        self.step_jsons = {}

    def calculate_closest_nodes(self, matrix, first_iteration):
        neighbours_dict = {}
        print 'Calculating closest nodes... Current matrix:'
        for row in range(len(matrix)):
            row_min = min(matrix[row])
            print matrix[row]
            for col in range(len(matrix[row])):
                if matrix[row][col] == row_min:
                    neighbours_dict[row] = {"target": col, "bond": 1, "length": matrix[row][col]}

                    if first_iteration:
                        self.add_point_to_group(row, col)
                    else:
                        self.add_to_groups_joining(row, col)


                    if col in neighbours_dict.keys() and neighbours_dict[col]["target"] == row and neighbours_dict[row][
                        "target"] == col:
                        # neighbours_dict[col]["bond"] = 2
                        neighbours_dict[row]["bond"] = 2
                        neighbours_dict.pop(col)
                    break
        print "Found neighbours:"
        print neighbours_dict
        self.remove_duplicates_from_groups()

        if first_iteration:
            for key, value in neighbours_dict.iteritems():
                self.add_link(key, value["target"], value["bond"], value["length"])

        else:  # If we join groups with groups/nodes:
            print "Groups:"
            print self.groups
            for key, value in neighbours_dict.iteritems():
                if len(self.groups[key]) >= 1:

                    print "Want to join", self.groups[key], "with", self.groups[value["target"]]
                    minimal_distance = (0, 0, big_m)  # Minimal distance and it's nodes
                    for node in self.groups[key]:
                        for node2 in self.groups[value["target"]]:
                            if self.original_matrix[node][node2] < minimal_distance[2]:
                                minimal_distance = (node, node2, self.original_matrix[node][node2])
                    self.add_link(minimal_distance[0], minimal_distance[1], 1, minimal_distance[2])
                    self.add_to_groups_joining(key, value["target"])

            self.join_groups()
            del self.groups_to_join[:]

    def add_to_groups_joining(self, group1_id, group2_id):
        self.groups_to_join.append(sorted((group1_id, group2_id)))

    def join_groups(self):
        new_groups = []

        def add_old_group_to_new_group(group, new_group):
            for new in new_groups:
                if new_group == new:
                    new.extend(group)
            for new in range(len(new_groups)):
                new_groups[new] = list(set(new_groups[new]))

        self.groups_to_join.sort()
        old_groups_without_ab_and_ba = list(
                k for k, _ in itertools.groupby(self.groups_to_join))  # Deleting BA if (AB and BA) - duplicates

        for old_group in old_groups_without_ab_and_ba:
            added = False
            for elem in old_group:
                for new_group in new_groups:
                    if elem in new_group:
                        add_old_group_to_new_group(old_group, new_group)
                        added = True
            if not added:
                new_groups.append(old_group)
        self.set_as_new_groups(new_groups)

    def set_as_new_groups(self, new_groups):
        del self.groups[:]
        for group in new_groups:
            self.groups.append(group)

    def add_point_to_group(self, point, point2):
        for group in self.groups:
            if point2 in group:
                group.append(point)
                return
        self.groups.append([point, point2])

    def remove_duplicates_from_groups(self):
        for group in range(len(self.groups)):
            self.groups[group] = list(set(self.groups[group]))

    def rebuild_matrix(self, links):
        self.groups_mapping.clear()
        print "Rebuilding matrix... New group maping:"
        for i, group in enumerate(self.groups):
            self.groups_mapping[i] = group


        print self.groups_mapping
        return self.get_distance_between_groups()

    def get_distance_between_groups(self):
        if "neighbour" in self.distance_metric:
            return self.get_closest_neighbour_distance(self.distance_metric)
            # TODO: dodac wiecej opcji liczenia dystansu

    def get_closest_neighbour_distance(self, type):
        n = len(self.groups)
        result_matrix = [[big_m for _ in range(n)] for _ in range(n)]
        for row in range(n):
            for col in range(n):
                if row == col:
                    pass
                else:
                    if type == "closest neighbour":
                        distance = min(self.get_all_distances(self.groups_mapping[row], self.groups_mapping[col]))
                    if type == "farthest neighbour":
                        distance_list = self.get_all_distances(self.groups_mapping[row], self.groups_mapping[col])
                        distance = 0
                        for dist in distance_list:  # Max distance excluding big_m
                            if distance < dist < big_m:
                                distance = dist
                    result_matrix[row][col] = distance
        return result_matrix

    def get_all_distances(self, group1, group2):
        return [self.original_matrix[x][y] for x in group1 for y in group2]

    def add_link(self, node1, node2, bond, length):
        self.links.append({"source": node1, "target": node2, "bond": bond, "length": length})

    def add_nodes(self):
        for x in range(len(self.objects_mapping)):
            self.nodes.append({"node": self.objects_mapping[x]})

    def get_json(self):
        critical_value = self.get_critical_value()
        result = {"nodes": self.nodes,
                  "links": self.links,
                  "mean": critical_value[0],
                  "std_dev": critical_value[1]}
        return json.dumps(result)

    def calculate(self):

        if self.data == 0:
            self.matrix = get_voivodeship_sample()
        else:
            self.matrix = self.data
        self.original_matrix = self.matrix
        self.add_nodes()
        self.calculate_closest_nodes(self.matrix, True)

        step = 1
        while len(self.groups) != self.final_number_of_groups:
            print "Next iteration"
            self.remove_duplicates_from_groups()
            self.matrix = self.rebuild_matrix(self.links)
            self.calculate_closest_nodes(self.matrix, False)
            self.add_step_json(self.get_json(), step)
            step += 1
        self.do_last_joining(step)
        print "Connected graph:", graph_algorithms.json_graph_is_connected(self.step_jsons[max(self.step_jsons.keys(), key=int)])

    def do_last_joining(self, step):
        minimal_distance = (0, 0, big_m)  # Minimal distance and it's nodes
        for node in self.groups_mapping[0]:
            for node2 in self.groups_mapping[1]:
                    minimal_distance = (node, node2, self.original_matrix[node][node2])
        self.add_link(minimal_distance[0], minimal_distance[1], 1, minimal_distance[2])
        self.add_step_json(self.get_json(), step)

    def add_step_json(self, current_json, step):
        self.step_jsons[step] = current_json

    def process_visualisation(self):
        vis_handler = html_handler.Handler(self.step_jsons)
        vis_handler.write_html()
        vis_handler.open_visualisation()

    def get_critical_value(self):
        values = []
        for value in self.links:
            values.append(value["length"])
        np_array = np.array(values)
        return np_array.mean(), np_array.std()


def get_3_level_sample():
    # TODO: remove in production
    return [[9999999, 1, 2, 9, 9, 9, 9, 9],
            [1, 9999999, 9, 9, 9, 9, 9, 9],
            [2, 9, 9999999, 1, 3, 9, 9, 9],
            [9, 9, 1, 9999999, 9, 9, 9, 9],
            [9, 9, 3, 9, 9999999, 1, 2, 9],
            [9, 9, 9, 9, 1, 9999999, 9, 9],
            [9, 9, 9, 9, 2, 9, 9999999, 1],
            [9, 9, 9, 9, 9, 9, 1, 9999999]]


def get_voivodeship_sample():
    return [[99999999, 1349.5032, 596.4995, 945.841, 1509.4647, 1323.5378, 3323.5855, 1355.9689, 1234.6159, 1591.1831,
             257.2359, 1470.4319, 1017.8954, 791.0219, 626.3177, 1694.7301],
            [1349.5032, 99999999, 1266.963, 1610.6614, 2559.1762, 1715.8729, 4329.1733, 2639.9604, 254.2415, 2184.2117,
             1254.2596, 2525.417, 1516.3567, 2098.04, 1460.4762, 2308.7833],
            [596.4995, 1266.963, 99999999, 1455.4412, 2031.6116, 1834.2801, 3883.1805, 1765.4951, 1061.7501, 1103.806,
             786.6984, 2033.3496, 455.7848, 1114.9852, 224.8652, 1226.1806],
            [945.841, 1610.6614, 1455.4412, 99999999, 993.9037, 488.9311, 2785.3655, 1348.0514, 1633.7799, 2486.0428,
             752.6785, 995.4215, 1906.4676, 1155.1549, 1539.5346, 2597.2796],
            [1509.4647, 2559.1762, 2031.6116, 993.9037, 99999999, 1184.9406, 1972.5175, 749.8211, 2541.3944, 2829.3315,
             1438.9059, 345.0821, 2419.5536, 1118.0816, 2024.7082, 2910.813],
            [1323.5378, 1715.8729, 1834.2801, 488.9311, 1184.9406, 99999999, 2727.2223, 1693.923, 1800.788, 2900.0589,
             1091.3674, 1136.5821, 2284.8036, 1591.3568, 1931.4451, 3009.6334],
            [3323.5855, 4329.1733, 3883.1805, 2785.3655, 1972.5175, 2727.2223, 99999999, 2320.8318, 4351.5057,
             4560.6832, 3240.4473, 1877.5371, 4240.471, 2907.3899, 3833.1802, 4611.5751],
            [1355.9689, 2639.9604, 1765.4951, 1348.0514, 749.8211, 1693.923, 2320.8318, 99999999, 2551.7556, 2315.281,
             1412.6633, 834.8674, 2055.2988, 658.5056, 1686.5401, 2373.3755],
            [1234.6159, 254.2415, 1061.7501, 1633.7799, 2541.3944, 1800.788, 4351.5057, 2551.7556, 99999999, 1938.9953,
             1183.4454, 2516.754, 1276.6655, 1975.543, 1255.8541, 2063.5917],
            [1591.1831, 2184.2117, 1103.806, 2486.0428, 2829.3315, 2900.0589, 4560.6832, 2315.281, 1938.9953, 99999999,
             1828.165, 2842.127, 698.9318, 1723.528, 976.4813, 147.8553],
            [257.2359, 1254.2596, 786.6984, 752.6785, 1438.9059, 1091.3674, 3240.4473, 1412.6633, 1183.4454, 1828.165,
             99999999, 1386.389, 1223.2073, 924.02, 854.6096, 1934.215],
            [1470.4319, 2525.417, 2033.3496, 995.4215, 345.0821, 1136.5821, 1877.5371, 834.8674, 2516.754, 2842.127,
             1386.389, 99999999, 2422.9308, 1169.6845, 2013.7772, 2918.7213],
            [1017.8954, 1516.3567, 455.7848, 1906.4676, 2419.5536, 2284.8036, 4240.471, 2055.2988, 1276.6655, 698.9318,
             1223.2073, 2422.9308, 99999999, 1404.4743, 414.6411, 821.291],
            [791.0219, 2098.04, 1114.9852, 1155.1549, 1118.0816, 1591.3568, 2907.3899, 658.5056, 1975.543, 1723.528,
             924.02, 1169.6845, 1404.4743, 99999999, 1037.3626, 1799.4491],
            [626.3177, 1460.4762, 224.8652, 1539.5346, 2024.7082, 1931.4451, 3833.1802, 1686.5401, 1255.8541, 976.4813,
             854.6096, 2013.7772, 414.6411, 1037.3626, 99999999, 1086.6398],
            [1694.7301, 2308.7833, 1226.1806, 2597.2796, 2910.813, 3009.6334, 4611.5751, 2373.3755, 2063.5917, 147.8553,
             1934.215, 2918.7213, 821.291, 1799.4491, 1086.6398, 99999999]]


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
    d.process_visualisation()


if __name__ == '__main__':
    maping = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h'}

    d = Dendrite(0, "Najblizszy sasiad", maping)
    d.calculate()
