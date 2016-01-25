import datetime
import json
import webbrowser
import os
import graph_algorithms


class Handler:

    def __init__(self, j):
        self.j = j  # Not named "json" to avoid messing with namespace.
        self.filename = ""
        print "handler json", self.j[1]
        print self.j[2]

    def write_html(self):
        now = datetime.datetime.now()
        filename = open('visualisation.html', 'r')
        self.filename = str("Wizualizacje/"+now.strftime("%Y-%m-%d_%H-%M")+".html")
        found = False

        with open(self.filename, "w") as out_file:
            for line in filename:
                if not found:
                    out_file.write(line)
                if "application/json" in line:
                    found = True
                    out_file.write(self.j[2])
                if found and "</script>" in line:
                    found = False
                    out_file.write(line)


    def open_visualisation(self):
        webbrowser.open('file://' + os.path.realpath(self.filename))
        graph_algorithms.json_graph_is_connected(self.j[max(self.j.keys(), key=int)])


if __name__ == '__main__':

    test_json = {"nodes": [{"node": 0}, {"node": 1}, {"node": 2}, {"node": 3},
                       {"node": 4}, {"node": 5}, {"node": 6}, {"node": 7}],
                 "links": [{"source": 0, "length": 1, "target": 1, "bond": 2},
                       {"source": 1, "length": 1, "target": 0, "bond": 2},
                       {"source": 2, "length": 1, "target": 3, "bond": 2},
                       {"source": 3, "length": 1, "target": 2, "bond": 2},
                       {"source": 4, "length": 1, "target": 5, "bond": 2},
                       {"source": 5, "length": 1, "target": 4, "bond": 2},
                       {"source": 6, "length": 1, "target": 7, "bond": 2},
                       {"source": 7, "length": 1, "target": 6, "bond": 2},
                       {"source": 0, "length": 2, "target": 2, "bond": 1},
                       {"source": 2, "length": 2, "target": 0, "bond": 1},
                       {"source": 4, "length": 2, "target": 6, "bond": 1},
                       {"source": 6, "length": 2, "target": 4, "bond": 1}]}
    w = Handler(test_json)
    w.write_html()
    w.open_visualisation()