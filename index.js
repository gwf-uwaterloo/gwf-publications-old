/**
   * Here is just a basic example on how to properly display a graph
   * exported from Gephi in the GEXF format.
   *
   * The plugin sigma.parsers.gexf can load and parse the GEXF graph file,
   * and instantiate sigma when the graph is received.
   *
   * The object given as the second parameter is the base of the instance
   * configuration object. The plugin will just add the "graph" key to it
   * before the instanciation.
   */

var selected = [];
var attr_color = {};
var selectedAffiliation = [];
var value_list = [];


sigma.classes.graph.addMethod('neighbors', function (nodeId) {
    var k,
        neighbors = {},
        index = this.allNeighborsIndex[nodeId] || {};

    for (k in index)
        neighbors[k] = this.nodesIndex[k];

    return neighbors;
});

var s = new sigma({
    renderers: [
        {
            type: 'canvas',
            container: document.getElementById('sigma-container'),
            freeStyle: true
        }
    ],
    settings: {
        autoRescale: true,
        borderSize: 6,
        defaultEdgeColor: '#B1B1B1',
        edgeColor: 'default',
        minNodeSize: 0.001,
        maxNodeSize: 25,
        labelThreshold: 12,
        labelSize: "fixed",
        scalingMode: 'inside',
        sideMargin: 1,
        batchEdgesDrawing: true,
        hideEdgesOnMove: true,
        animationsTime: 5000,
        labelHoverBGColor: '#E0E0E0',
        defaultHoverLabelBGColor: '#E0E0E0',
        defaultNodeBorderColor: '#E0E0E0',
        zoomingRatio: 2.0
    }
})

sigma.parsers.gexf('gwf_co_author_graph/file/data/force_atlas_new.gexf',
    s,
    function (s) {
        // We first need to save the original colors of our
        // nodes and edges, like this:
        s.graph.nodes().forEach(function (n) {
            n.originalColor = n.color;
            n.originalLabel = n.label;
        });

        s.graph.edges().forEach(function (e) {
            e.originalColor = e.color;
        });

        // When a node is clicked, we check for each node
        // if it is a neighbor of the clicked one. If not,
        // we set its color as grey, and else, it takes its
        // original color.
        // We do the same for the edges, and we only keep
        // edges that have both extremities colored.
        s.bind('clickNode', function (e) {

            s.graph.nodes().forEach(function (n) {
                delete n['nodeBorderColor']
                n.color = n.originalColor;
                n.label = n.originalLabel;
            });

            var selected = [];

            selected[e.data.node.id] = e.data.node;
            showSelectedNodes(selected);

            var nodeId = e.data.node.id,
                toKeep = s.graph.neighbors(nodeId);
            toKeep[nodeId] = e.data.node;

            s.graph.nodes().forEach(function (n) {
                if (toKeep[n.id]) {
                    n.color = n.originalColor;
                } else {
                    n.color = '#eee';
                    n.label = "";
                }
            });

            s.graph.edges().forEach(function (e) {
                if (toKeep[e.source] && toKeep[e.target]) {
                    e.color = e.originalColor;
                } else {
                    e.color = '#FFF';
                }
            });

            e.data.node.nodeBorderColor = '#000'
            e.data.node.color = e.data.node.originalColor

            // Since the data has been modified, we need to
            // call the refresh method to make the colors
            // update effective.
            s.refresh();
        });

        // When the stage is clicked, we just color each
        // node and edge with its original color.
        s.bind('clickStage', function (e) {
            s.graph.nodes().forEach(function (n) {
                delete n['nodeBorderColor'];
                n.color = n.originalColor;
                n.label = n.originalLabel;
            });

            s.graph.edges().forEach(function (e) {
                e.color = e.originalColor;
            });
            document.getElementById('search-input').value = "";
            // Same as in the previous event:
            s.refresh();

            document.querySelectorAll('.checkbox-round').forEach(function (a) {
                a.checked = false;
                a.style.cssText = "background-color: white; border: 4px solid " + attr_color[a.value];
            });

        });


        s.refresh();
        populateSearchList(s.graph.nodes());
        populateAffiliations(s.graph.nodes());

        // Add event listeners to buttons
        var inputBox = document.getElementById('search-input');
        inputBox.addEventListener("change", searchChange);

        var zoomInButton = document.getElementById('zoom-in-button');
        zoomInButton.addEventListener("click", zoomIn);
        var zoomOutButton = document.getElementById('zoom-out-button');
        zoomOutButton.addEventListener("click", zoomOut);

        // Configure the noverlap layout:
        var noverlapListener = s.configNoverlap({
            nodeMargin: 0.5,
            scaleNodes: 1.1,
            gridSize: 50,
            easing: 'cubicIn', // animation transition function
            duration: 100   // animation duration. Long here for the purposes of this example only
        });
        // Bind the events:
        noverlapListener.bind('start stop interpolate', function (e) {
            console.log(e.type);
            if (e.type === 'start') {
                console.time('noverlap');
            }
            if (e.type === 'interpolate') {
                console.timeEnd('noverlap');
            }
        });
        // Start the layout:
        s.startNoverlap();
    });

function searchChange(e) {
    s.graph.nodes().forEach(function (n) {
        delete n['nodeBorderColor'];
        n.color = n.originalColor;
        n.label = n.originalLabel;
    });
    var selected = [];
    var value = e.target.value;

    // Add node to selected
    s.graph.nodes().forEach(function (n) {
        if (n.label == value) {
            if (!selected[n.id]) {
                selected[n.id] = n;
                n.nodeBorderColor = '#000'
                var c = s.camera;
                sigma.misc.animation.camera(c, {
                    x: n['read_cam0:x'], y: n['read_cam0:y'],
                    ratio: c.ratio / c.settings('zoomingRatio')
                }, {
                    duration: 700
                });
            }
        }
    });
    nodeSelect(s, selected);
}

function refresh() {
    s.refresh();
}

function zoomIn() {
    var c = s.camera;
    sigma.misc.animation.camera(c, {
        ratio: c.ratio / c.settings('zoomingRatio')
    }, {
        duration: 700
    });
}

function zoomOut() {
    var c = s.camera;
    sigma.misc.animation.camera(c, {
        ratio: c.ratio * c.settings('zoomingRatio')
    }, {
        duration: 700
    });
}

function populateSearchList(nodes) {
    var container = document.getElementById('nodes-datalist');
    nodes.forEach(function (n) {
        var item = document.createElement('option');
        item.value = n.label;
        container.appendChild(item);
    });
}

function populateAffiliations(nodes) {
    var container = document.getElementById('checkbox-container');
    var attr = {};

    nodes.forEach(function (n) {
        if (n.attributes.affiliation in attr) {
            attr[n.attributes.affiliation] += 1;
        } else {
            attr_color[n.attributes.affiliation] = n.viz.color;
            attr[n.attributes.affiliation] = 1;
        }
    });

    // Create items array
    var items = Object.keys(attr).map(function (key) {
        return [key, attr[key]];
    });

    // Sort the array based on the second element
    items.sort(function (first, second) {
        return second[1] - first[1];
    });

    attr_new = {}
    for (i = 0; i < items.length; i++) {
        attr_new[items[i][0]] = items[i][0];
    }

    for (const [key, value] of Object.entries(attr_new)) {
        if (key != 'undefined') {
            var input = document.createElement("input");
            input.type = "checkbox";
            input.classList.add("checkbox-round");
            input.style.cssText = "border: 4px solid " + attr_color[key]
            input.checked = false;
            input.value = key;
            input.addEventListener("click", filterNodesAffl)
            container.appendChild(input);

            var label = document.createElement("label");
            label.classList.add("label-round");
            label.innerText = key;
            label.style.cssText = "border-bottom: 5px solid " + attr_color[key]
            container.appendChild(label);

            // Append a line break 
            container.appendChild(document.createElement("br"));
        }
    };
}


function filterNodesAffl(e) {
    if (!(selectedAffiliation.includes(e.target))) {
        selectedAffiliation.push(e.target);
    }

    for (var aff of selectedAffiliation) {

        var value = aff.value;

        if (aff.checked == false) {
            aff.style.cssText = "background-color: white; border: 4px solid " + attr_color[value];

            if (selectedAffiliation == 0) {
                s.graph.nodes().forEach(function (n) {
                    n.color = n.originalColor;
                });
            } else {
                selectedAffiliation.splice(selectedAffiliation.indexOf(aff), 1);
                value_list.splice(value_list.indexOf(value), 1);

                if (selectedAffiliation == 0) {
                    s.graph.nodes().forEach(function (n) {
                        n.color = n.originalColor;
                    });
                } else {
                    s.graph.nodes().forEach(function (n) {
                        if (value_list.includes(n.attributes.affiliation)) {
                            n.color = n.originalColor;
                        } else {
                            n.color = '#eee';
                            n.label = "";
                        }
                    });
                }

            }

        } else {
            if (!(value_list.includes(value))) {
                value_list.push(value);
            }
            aff.style.cssText += "background-color: " + attr_color[value];
            s.graph.nodes().forEach(function (n) {
                if (value_list.includes(n.attributes.affiliation)) {
                    n.color = n.originalColor;
                } else {
                    n.color = '#eee';
                    n.label = "";
                }
            });
        }
    }



    s.refresh();
}

getColor = {
    "0": "#F012BE",
    "1": "#85144b",
    "2": "#2ECC40",
    "3": "#a9a9a9",
    "4": "#33805d",
    "5": "#222a2a",
    "6": "#FF4136",
    "7": "#001F3F",
    "8": "#FFDC00",
    "9": "#FF851B ",
};

// Show all selected nodes next to the notes for quick reference
function showSelectedNodes(selected) {
    // Remove old selecteed nodes
    document.querySelectorAll('.selected-node').forEach(function (a) {
        a.remove()
    });

    if (Object.keys(selected).length > 0) {
        var selected_container = document.getElementById('selected-nodes');
        Object.keys(selected).forEach(function (key) {
            var selected_item = document.createElement("div");
            selected_item.classList.add('selected-node');
            if (selected[key].attributes.affiliation == undefined) {
                selected_item.innerHTML = selected[key].label
            } else {
                selected_item.innerHTML = selected[key].label +
                    "<br>" + selected[key].attributes.affiliation + "<br><a href='" + selected[key].attributes.url
                    + "' target='_blank' style='color:white;'>Google Scholar</a>"
            }
            selected_container.appendChild(selected_item);
        });
    }
}

// Toggle select a node
function nodeSelect(s, selected) {
    // Making sure we have at least one node selected
    if (Object.keys(selected).length > 0) {
        var toKeep = nodesToKeep(s, selected);

        setSelectedColor(s, selected, toKeep);
        // Grey out irrelevant edges 
        setEdgesToInactive(s, toKeep);
    } else { // If no nodes are selected after click we just reset the graph
        resetStates(s);
    }
    showSelectedNodes(selected);
    s.refresh();
}

// Highlight hovered node and relevant nodes by greying out all else
function nodeHover(s, node, selected) {
    var selectedAndHovered = [];
    // Make a copy of selected and add the hovered node
    Object.assign(selectedAndHovered, selected);
    selectedAndHovered[node.id] = node;
    var toKeep = nodesToKeep(s, selectedAndHovered);

    s.graph.nodes().forEach(function (n) {
        if (toKeep[n.id]) {
            n.color = n.originalColor;
        } else {
            n.color = '#eee';
        }
    });
    // Grey out irrelevant edges 
    setEdgesToInactive(s, toKeep);
    s.refresh();
}

// Return graph to pre-hover state
function nodeHoverOut() {
    // Start clean, and then figure out what needs to be greyed out according to selected nodes
    resetStates(s);

    if (Object.keys(selected).length > 0) {
        var toKeep = nodesToKeep(s, selected);

        setSelectedColor(s, selected, toKeep);
        setEdgesToInactive(s, toKeep);
    }
    s.refresh();
}

// Reset all selections
function resetStates(s) {
    s.graph.nodes().forEach(function (n) {
        n.color = n.originalColor;
    });
    s.graph.edges().forEach(function (e) {
        e.color = e.originalColor;
    });
}

// Return matching items from two arrays
function returnMatchingArrayItems(array1, array2) {
    retain = [];

    for (var i = 0; i < array1.length; i += 1) {
        if (array2.indexOf(array1[i]) > -1) {
            retain.push(array1[i]);
        }
    }
    return retain;
}

// Return matching nodes from two arrays - 
// for instance when two nodes are selected only common neighbors should be shown
function returnMatchingNodes(array1, array2) {
    var retainKeys = returnMatchingArrayItems(Object.keys(array1), Object.keys(array2)),
        retainNodes = [];

    for (let id of retainKeys) {
        retainNodes[id] = array1[id];
    }
    return retainNodes;
}

// Return all relevant nodes to be kept
function nodesToKeep(s, selected) {
    // Make sure selected is not empty when calling this
    var toKeep,
        i = 0;

    Object.keys(selected).forEach(function (key) {
        if (i == 0) {
            toKeep = s.graph.neighbors(key);
            toKeep[key] = selected[key];
        } else {
            var keep = s.graph.neighbors(key);
            keep[key] = selected[key];
            toKeep = returnMatchingNodes(toKeep, keep);
        }
        i++;
    });
    return toKeep;
}

// Set the color of all selected nodes
function setSelectedColor(s, selected, toKeep) {
    s.graph.nodes().forEach(function (n) {

        if (selected[n.id]) {
            n.color = n.originalColor;
        }
        else if (!toKeep[n.id]) {
            n.color = '#eee';
            n.label = "";
        }
    });
}

// Grey out all edges that are not bewteen active nodes
function setEdgesToInactive(s, nodesToKeep) {
    s.graph.edges().forEach(function (e) {
        if (nodesToKeep[e.source] && nodesToKeep[e.target]) {
            e.color = e.originalColor;
        } else {
            e.color = "#FFF" //e.inactiveColor;
        }
    });
}