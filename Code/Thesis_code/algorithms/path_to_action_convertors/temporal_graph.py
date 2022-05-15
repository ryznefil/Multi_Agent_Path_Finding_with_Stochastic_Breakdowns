import time as t

import networkx as nx
import numpy as np

from Thesis_code.algorithms.path_to_action_convertors.conversion_types import ConversionType


def create_temporal_plan_graph(agent_vertex_paths, env_graph, reservation_table):
    a = t.time()
    agent_shortlist = []
    for key in agent_vertex_paths.keys():
        if len(agent_vertex_paths[key]) != 0:
            agent_shortlist.append(key)

    agent_starting_tpg_node = {}
    agent_ending_tpg_node = {}
    shortlist_paths = {}
    env_graph = env_graph
    tpg = nx.DiGraph()

    # add edge type 1 and create vertices, node format (((coordinates
    for agent_id in agent_shortlist:
        agent_plan = agent_vertex_paths[agent_id]
        start_node = vertex_to_node(agent_plan[0], agent_id)
        agent_starting_tpg_node[agent_id] = start_node
        tpg.add_node(start_node, m_received=0, m_sent=False)  # add the starting node to the graph
        last_transferred_vertex = agent_plan[0]
        shortlist_paths[agent_id] = [start_node]

        for plan_step in range(1, len(agent_plan)):  # iterate over all next steps
            if agent_plan[plan_step][0] != agent_plan[plan_step - 1][0]:  # agent changed position (or orientation at deadend)
                new_node = vertex_to_node(agent_plan[plan_step],agent_id)
                tpg.add_node(new_node, m_received=0, m_sent=False)
                shortlist_paths[agent_id].append(new_node)
                edge = env_graph[node_graph_vertex(last_transferred_vertex)][node_graph_vertex(agent_plan[plan_step])]  # edge representing the step from the current node to the next node
                tpg.add_edge(vertex_to_node(last_transferred_vertex, agent_id), vertex_to_node(agent_plan[plan_step], agent_id), action=edge['action'])
                last_transferred_vertex = agent_plan[plan_step]

        agent_ending_tpg_node[agent_id] = vertex_to_node(last_transferred_vertex, agent_id)

    for agent_id in agent_shortlist:
        for step_i in range(1, len(shortlist_paths[agent_id]) - 1):  # leave out the first node and iterate over all agents nodes; ignore virtual sink node
            agent_step = shortlist_paths[agent_id][step_i] # get the next step
            entered_coordinates = agent_step[0]
            entry_time = agent_step[1]
            other_entering_agents = np.unique(reservation_table[entered_coordinates][entry_time+1:]).astype(int)
            other_entering_agents = (other_entering_agents[(other_entering_agents != 0) & (other_entering_agents != agent_id + 1)]) - 1

            for later_agent in other_entering_agents: # TODO: Try the has node alternative too
                for step_j in range(1, len(shortlist_paths[later_agent]) - 1): # the other agent can never have less steps to get to the tile than this one (we are looking for later agents)! Either can have one more if closely following or more
                    other_step = shortlist_paths[later_agent][step_j] # get the move
                    if same_tile_later(agent_step, other_step):
                        tpg.add_edge(shortlist_paths[agent_id][step_i+1], other_step)
                        break

    # a = t.time()
    # for agent_id in agent_shortlist:
    #     for i in range(1, len(shortlist_paths[agent_id]) - 1):  # leave out the first node and iterate over all agents nodes; ignore virtual sink node
    #         agent_step = shortlist_paths[agent_id][i] # get the next step
    #         for other_agent in agent_shortlist: # iterate over other agents
    #             if agent_id == other_agent: # ignore the first agent
    #                 continue
    #
    #             for j in range(1, len(shortlist_paths[other_agent]) - 1): # iterate over all their path, ignore the very last virtual sink node, TODO: start at the latter timestep (add BS in between?)
    #                 other_step = shortlist_paths[other_agent][j] # get the move
    #                 if same_tile_later(agent_step, other_step):
    #                     tpg.add_edge(shortlist_paths[agent_id][i+1], other_step)
    #                     break
    #
    # b = t.time()
    # total = b - a
    # print(total)

    # SAVE OLD VERSION
    # a = t.time()
    # for agent_id in agent_shortlist:
    #     agent_plan = agent_vertex_paths[agent_id]
    #     for plan_step in range(1, len(agent_plan)):  # leave out the first node
    #         if agent_plan[plan_step][0] != agent_plan[plan_step - 1][0]:  # agent moved
    #             coordinates = node_coordinates(agent_plan[plan_step - 1])
    #             for other_agent in agent_shortlist:
    #                 if agent_id != other_agent:
    #                     for time_step in range(agent_plan[plan_step - 1][1], agent_vertex_paths[other_agent][-1][1] + 1):
    #                         a = t.time()
    #                         node = (coordinates, time_step, other_agent)
    #                         if tpg.has_node(node):  # TODO CHECK
    #                             tpg.add_edge(vertex_to_node(agent_plan[plan_step], agent_id), node)
    #                             break
    #         else:
    #             continue
    return ConversionType.TEMPORAL_PLAN_GRAPH, tpg, agent_starting_tpg_node, agent_ending_tpg_node

def same_tile_later(pos1, pos2):
    if pos1[0] == pos2[0] and pos1[1] < pos2[1]:
        return True
    return False

def reset_TPG(tpg):
    tpg_g = tpg[1]
    for node in tpg_g.nodes(data=True):
        node[1]['m_sent'] = False
        node[1]['m_received'] = 0
    return tpg


def transitive_reduction_of_the_plan(tpg):
    """"Performs a transitive reduction of the plan graph"""
    # return nx.transitive_reduction(tpg)
    # EDIT TODO: FIX THE TRANSITIVE REDUCTION SO THAT IT KEEPS THE ATTRIBUTES!
    return tpg


def send_message_to_agents(tpg, entered_node):
    """"Sends +1 increment to all agents waiting for this agent to leave some node"""
    if tpg.nodes[entered_node]['m_sent']:  # safe check that we do not increment multiple times from one node
        return tpg

    adj_nodes = tpg.neighbors(entered_node)
    for adj_node in adj_nodes:
        tpg.nodes[adj_node]['m_received'] += 1
    tpg.nodes[entered_node]['m_sent'] = True  # mark that messages from this node have been sent

    return tpg


def identify_next_node_and_action(tpg, entered_node):
    """"Identifies the next node for this agent and action required to be performed in the future"""
    # TODO: merge with the previous
    agent_id = entered_node[2]  # get the agent id from the node
    next_node = None
    next_action = None

    e = tpg.out_edges(entered_node)
    for edge in e:
        if edge[1][2] == agent_id:  # this is a check to make sure that we are getting a relevant node
            next_node = edge[1]
            next_action = tpg[entered_node][edge[1]]['action']

    return next_node, next_action


def check_movement_validity(tpg, target_node):
    required_messages_count = len(tpg.in_edges(target_node))
    received_messages = tpg.nodes[target_node]['m_received']
    return received_messages == required_messages_count


# TODO: sort helper functions
def vertex_to_node(vertex, agent_id):
    return vertex[0][0], vertex[1], agent_id


# Helper functions for cleaner code
def node_graph_vertex(node):
    return node[0]


def node_coordinates(node):
    return node[0][0]


def node_timestep(node):
    return node[1]


def node_orientation(node):
    return node[0][1]
