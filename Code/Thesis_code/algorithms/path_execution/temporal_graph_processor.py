import time

import numpy as np
from flatland.envs.agent_utils import RailAgentStatus
from flatland.utils.rendertools import RenderTool
from flatland.utils.rendertools import RenderTool, AgentRenderVariant

import Thesis_code.algorithms.path_to_action_convertors.temporal_graph as tpg_utils


class Temporal_Graph_Path_Processor:
    """"Processor meant for processing of the temporal plan graph"""

    def __init__(self, env, render_tool = None):
        self.env = env
        if render_tool is None:
            self.render_tool = RenderTool(env, gl="PILSVG", agent_render_variant=AgentRenderVariant.ONE_STEP_BEHIND,
                                          show_debug=False,
                                          screen_height=1500,  # Adjust these parameters to fit your resolution
                                          screen_width=1500)  # Adjust these parameters to fit your resolution
        else:
            self.render_tool = render_tool
        self.observations = self.env.obs_builder.get_many()
        self.step_max = int(8 * (env.width + env.height))

        self.graph_representation = self.observations[0]
        self.agent_states = self.observations[1]

    def copy_dict(self, old_dict):
        new_dict = {}
        for segment in old_dict.keys():
            new_dict[segment] = old_dict[segment]

        return new_dict

    def run_basic_simulation(self, vertex_paths, converted_path, step_info, selected_agents=None, render=False, animation_sleep=0, malf_counter=False, copy_dct=True):
        """"Primitive for the first round where the unexpected behaviour cannot happen"""

        temporal_graph = converted_path[1]
        if copy_dct:
            agent_current_temp_location = self.copy_dict(converted_path[2])
        else:
            agent_current_temp_location = converted_path[2]
        agent_next_temp_location = {}
        agent_next_action = {}
        done_agents = []
        old_agent_state = {}
        agent_number_of_malf_at_placement = [0 for i in range(len(self.env.agents))]

        steps_elapsed = 0
        cumulative_reward = 0
        normalized_reward = 0
        done = {}
        status = 0.0
        total_malf_duration = 0
        malfunction_occurence = 0  # MUST BE CALCULATED AFTER AGENT FINISHES TO PREVENT MISCOUNTING!

        # if selected_agents is None: # this is used if only subset of agents is planned for debugging purposes
        #     agent_shortlist = [i for i in range(len(agent_current_temp_location))]
        # else:
        #     agent_shortlist = selected_agents

        agent_shortlist = []
        for agent_id in range(len(vertex_paths)):
            if len(vertex_paths[agent_id]) == 0:
                continue
            agent_shortlist.append(agent_id)

        # first round of preparation, send messages, identify actions etc ...
        for agent_id in agent_shortlist:
            temporal_graph = tpg_utils.send_message_to_agents(temporal_graph, agent_current_temp_location[agent_id])  # increment related nodes for other agents
            agent_next_temp_location[agent_id], agent_next_action[agent_id] = tpg_utils.identify_next_node_and_action(temporal_graph, agent_current_temp_location[agent_id])

        while self.env.dones['__all__'] != True:
            step_action_dict = {}

            for agent_id in agent_shortlist:  # execute all or shortlisted agents, the engine does nothing for all other
                if step_info['action_required'][agent_id]:  # the engine says it needs an action for the agents
                    local_agent = self.env.agents[agent_id]  # get the current agent state
                    if local_agent.malfunction_data[
                        'malfunction'] == 0 or local_agent.status == RailAgentStatus.READY_TO_DEPART:  # the agent is not broken OR not yet placed and malfunction does not affect it
                        if tpg_utils.check_movement_validity(temporal_graph, agent_next_temp_location[agent_id]):  # check if agent has received enough messages to enter the location
                            step_action_dict[agent_id] = agent_next_action[agent_id]
                        else:
                            step_action_dict[agent_id] = 4
                    elif local_agent.malfunction_data[
                        'malfunction'] > 0 and local_agent.status == RailAgentStatus.ACTIVE:  # agent just broke, was already broken - either travelling or one move after being placed on the railway
                        pass
                    else:
                        print("ERROR: Agent reached and unidentified state, where action is required!")
                        raise ValueError

            old_step_info = step_info
            obs, all_rewards, done, step_info = self.env.step(step_action_dict)  # execute steps in the environment
            cum, norm = self.count_rewards(all_rewards, len(self.agent_states), self.step_max)  # run our reward TODO: fix this
            cumulative_reward += cum
            normalized_reward += norm

            for agent_id in self.env.active_agents:
                if self.env.agents[agent_id].status == RailAgentStatus.ACTIVE:
                    if old_agent_state == RailAgentStatus.READY_TO_DEPART:
                        agent_number_of_malf_at_placement[agent_id] = self.env.agents[agent_id].malfunction_data['nr_malfunctions']
                    old_malf_ct = old_step_info['malfunction'][agent_id]
                    new_malf_ct = step_info['malfunction'][agent_id]
                    if new_malf_ct > old_malf_ct:
                        total_malf_duration += new_malf_ct - 1  # the info given is one larger
                old_agent_state = {}
                old_agent_state[agent_id] = self.env.agents[agent_id].status

            for agent_id in agent_shortlist:
                local_agent = self.env.agents[agent_id]  # get the agent
                if step_info['action_required'][agent_id]:  # action is required, agent MIGHT have moved, check if location corresponds to the next node
                    if local_agent.position == agent_next_temp_location[agent_id][0]:
                        agent_current_temp_location[agent_id] = agent_next_temp_location[agent_id]
                        tpg_utils.send_message_to_agents(temporal_graph, agent_current_temp_location[agent_id])
                        agent_next_temp_location[agent_id], agent_next_action[agent_id] = tpg_utils.identify_next_node_and_action(temporal_graph, agent_current_temp_location[agent_id])
                    else:
                        pass
                elif local_agent.status == RailAgentStatus.DONE_REMOVED and agent_id not in done_agents:  # agent finished
                    # todo: perform messaging on last node entry and virtual exit
                    agent_current_temp_location[agent_id] = agent_next_temp_location[agent_id]
                    tpg_utils.send_message_to_agents(temporal_graph, agent_current_temp_location[agent_id])
                    agent_next_temp_location[agent_id], agent_next_action[agent_id] = tpg_utils.identify_next_node_and_action(temporal_graph, agent_current_temp_location[agent_id])
                    agent_current_temp_location[agent_id] = agent_next_temp_location[agent_id]
                    tpg_utils.send_message_to_agents(temporal_graph, agent_current_temp_location[agent_id])
                    agent_next_temp_location[agent_id], agent_next_action[agent_id] = tpg_utils.identify_next_node_and_action(temporal_graph, agent_current_temp_location[agent_id])
                    done_agents.append(agent_id)
                    malfunction_occurence += (local_agent.malfunction_data['nr_malfunctions'] - agent_number_of_malf_at_placement[agent_id])  # correct for previous ones
            if render:
                time.sleep(animation_sleep)  # use this to slow down the animation
                self.render_tool.render_env(show=True, frames=False, show_observations=False, show_predictions=False)

            steps_elapsed += 1  # total code steps

            if done['__all__']:
                break

        if len(done) != 0:
            status = self.calculate_success_rate(done)

        for agent_id in self.env.active_agents:
            malfunction_occurence += self.env.agents[agent_id].malfunction_data['nr_malfunctions']

        if malf_counter:
            return status, steps_elapsed, cumulative_reward, normalized_reward, malfunction_occurence, total_malf_duration
        else:
            return status, steps_elapsed, cumulative_reward, normalized_reward

    def calculate_success_rate(self, done_dict):
        """"Calculates the percentage completion of the game"""
        if self.env.active_agents == []:
            return 1.0

        ratio = 1 - len(self.env.active_agents) / len(self.env.agents)

        return ratio

    def count_rewards(self, rewards, agent_cnt, max_step):
        """"Count rewards per move"""
        cummulative = np.sum(list(rewards.values()))
        normalized = cummulative / (max_step + agent_cnt)

        return cummulative, normalized

    def sum_malfunction(self):
        occurences = 0
        for agent in self.env.agents:
            occurences += agent.malfunction_data['nr_malfunctions']

        return occurences
