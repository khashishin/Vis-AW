import datetime
import json


class Handler:

    def __init__(self, j):
        self.j = j  # Not named "json" to avoid messing with namespace.
        self.filename = ""

    def write_html(self):
        now = datetime.datetime.now()
        file1 = open('htmls/part1.txt', 'r')
        file2 = open('htmls/part2.txt', 'r')
        self.filename = str("htmls/"+now.strftime("%Y-%m-%d_%H-%M")+".html")
        with open(self.filename, "w") as out_file:
            out_file.write(file1.read())
            out_file.write(json.dumps(self.j))
            out_file.write(file2.read())

test_json = {"nodes": [{"node": 0}, {"node": 1}, {"node": 2}
                       , {"node": 3}, {"node": 4},
                       {"node": 5}, {"node": 6},
                       {"node": 7}],
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
# w.write_html() # This is where the magic happens. TODO: How will user open visualisation?
