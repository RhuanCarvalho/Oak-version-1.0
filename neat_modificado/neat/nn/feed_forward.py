from neat.graphs import feed_forward_layers
from neat.six_util import itervalues
import math
from numba import jit
import numpy as np

def sum_aggregation(x):
    return sum(x)

@jit(nopython=True, fastmath=True, cache=True)
def tanh_activation(z):
    z = max(-60.0, min(60.0, 2.5 * z))
    return np.tanh(z)

class FeedForwardNetwork(object):
    def __init__(self, inputs, outputs, node_evals):
        self.input_nodes = inputs
        self.output_nodes = outputs
        self.node_evals = node_evals
        self.values = dict((key, 0.0) for key in inputs + outputs)

    def activate(self, inputs):

        if len(self.input_nodes) != len(inputs):
            raise RuntimeError("Expected {0:n} inputs, got {1:n}".format(len(self.input_nodes), len(inputs)))

        for k, v in zip(self.input_nodes, inputs):
            self.values[k] = v

        for node, bias, response, links in self.node_evals:
            s = (np.array([(self.values[i] * w) for i, w in links],dtype=np.float64)).sum()
            self.values[node] = tanh_activation(bias + response * s)

        return [self.values[i] for i in self.output_nodes]

    @staticmethod
    def create(genome, config):
        """ Receives a genome and returns its phenotype (a FeedForwardNetwork). """

        # Gather expressed connections.
        connections = [cg.key for cg in itervalues(genome.connections) if cg.enabled]

        layers = feed_forward_layers(config.genome_config.input_keys, config.genome_config.output_keys, connections)

        node_evals = []
        for layer in layers:
            for node in layer:
                inputs = []
                node_expr = [] # currently unused
                for conn_key in connections:
                    inode, onode = conn_key
                    if onode == node:
                        cg = genome.connections[conn_key]
                        inputs.append((inode, cg.weight))
                        node_expr.append("v[{}] * {:.7e}".format(inode, cg.weight))

                ng = genome.nodes[node]
                # aggregation_function = config.genome_config.aggregation_function_defs.get(ng.aggregation)
                # activation_function = config.genome_config.activation_defs.get(ng.activation)
                # node_evals.append((node, activation_function, aggregation_function, ng.bias, ng.response, inputs))
                node_evals.append((node, ng.bias, ng.response, inputs))

        return FeedForwardNetwork(config.genome_config.input_keys, config.genome_config.output_keys, node_evals)
