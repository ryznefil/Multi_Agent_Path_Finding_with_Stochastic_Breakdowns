import numpy as np
from flatland.envs.agent_utils import RailAgentStatus
from flatland.utils.rendertools import RenderTool


class K_Robust_Path_Processor:
    """"Processor meant for processing of k-robust plans"""

    def __init__(self, env):
        self.env = env
        self.render_tool = RenderTool(self.env)
        self.observations = self.env.obs_builder.get_many()
        self.step_max = int(8 * (env.width + env.height))

        self.graph_representation = self.observations[0]
        self.agent_states = self.observations[1]

    def run_basic_simulation(self, agent_given_actions, agent_vertex_debug, step_info, selected_agents=None, render=False, animation_sleep=0):
        """"Primitive for the first round where the unexpected behaviour cannot happen"""
        agent_action_dict = agent_given_actions
        if selected_agents is None:  # this is used if only subset of agents is planned for debugging purposes
            agent_shortlist = []
            for agent_id in range(len(self.agent_states)):
                if len(agent_vertex_debug[agent_id]) != 0:
                    agent_shortlist.append(agent_id)
        else:
            agent_shortlist = []
            for agent_id in range(len(self.agent_states)):
                if len(agent_vertex_debug[agent_id]) != 0 and agent_id in selected_agents:
                    agent_shortlist.append(agent_id)

        steps_elapsed = 0
        cumulative_reward = 0
        normalized_reward = 0
        done = {}
        status = 0.0
        agent_executed_step = [0 for i in range(len(self.env.agents))]

        while self.env.dones['__all__'] != True:
            # print(step_info)
            step_action_dict = {}

            for agent_id in agent_shortlist:  # execute all or shortlisted agents, the engine does nothing for all other
                if step_info['action_required'][agent_id] == True:  # the engine says it needs an action for the agents
                    local_agent = self.env.agents[agent_id]
                    if len(agent_action_dict[agent_id]) > agent_executed_step[agent_id]:
                        if local_agent.malfunction_data['malfunction'] == 0:  # the agent is not broken
                            step_action_dict[agent_id] = agent_action_dict[agent_id][agent_executed_step[agent_id]][0]  # assign the action according to the current step execution
                        elif local_agent.malfunction_data[
                            'malfunction'] > 0 and local_agent.status == RailAgentStatus.READY_TO_DEPART:  # agent is broken, but has not yet been placed on the playing field, can only happen while waiting for placement or in the placement move
                            step_action_dict[agent_id] = agent_action_dict[agent_id][agent_executed_step[agent_id]][0]  # assign the action according to the current step execution
                        elif local_agent.malfunction_data[
                            'malfunction'] > 0 and local_agent.status == RailAgentStatus.ACTIVE:  # agent just broke/was already broken - either travelling or one move after being placed on the railway
                            pass
                            # step_action_dict[agent_id] = agent_action_dict[agent_id][agent_executed_step[agent_id]][0]  # assign the action according to the current step execution
                        else:
                            print("ERROR: Agent reached and unidentified state, where action is required!")
                            raise ValueError
                    else:
                        print("ERROR: Agent ", agent_id, " is out of moves")
                        raise ValueError

            old_step_info = step_info
            obs, all_rewards, done, step_info = self.env.step(step_action_dict)  # execute steps in the environment
            cum, norm = self.count_rewards(all_rewards, len(self.agent_states), self.step_max)  # run our reward TODO: fix this
            cumulative_reward += cum
            normalized_reward += norm

            for agent_id in agent_shortlist:
                local_agent = self.env.agents[agent_id]
                if local_agent.status == RailAgentStatus.READY_TO_DEPART:
                    agent_executed_step[agent_id] = agent_executed_step[agent_id] + 1  # wait actions carried out when not on the board (placement handled below)
                elif old_step_info['status'][agent_id] == RailAgentStatus.READY_TO_DEPART and step_info['status'][
                    agent_id] == RailAgentStatus.ACTIVE:  # if agent broken it can still be placed and the action pointer must be moved
                    agent_executed_step[agent_id] = agent_executed_step[agent_id] + 1  # shift the pointer to agent action
                elif old_step_info['action_required'][agent_id] == True and step_info['malfunction'][
                    agent_id] == 0:  # if agent needed action assignment and did not broke during the assignment, then advance the pointer
                    agent_executed_step[agent_id] = agent_executed_step[agent_id] + 1  # shift the pointer to agent action

            if render:
                # time.sleep(animation_sleep)  # use this to slow down the animation
                self.render_tool.render_env(show=True, frames=True, show_observations=False)

            if done['__all__']:
                break

            steps_elapsed += 1  # total code steps

        if len(done) != 0:
            status = self.calculate_success_rate(done)

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
