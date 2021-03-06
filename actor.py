import random
import zmq
from collections import deque

import gym
import numpy as np
from tensorflow.keras.layers import Dense
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam


class DQNAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.replay_buffer = deque(maxlen=2000)#创建最大长度为2000的双向队列
        self.gamma = 0.95  # Discount Rate
        self.epsilon = 1.0  # Exploration Rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.model = self._build_model()


    def _build_model(self):#创建一个三层的神经网络
        """Build Neural Net for Deep Q-learning Model"""

        model = Sequential()
        model.add(Dense(24, input_dim=self.state_size, activation='relu'))
        model.add(Dense(24, activation='relu'))
        model.add(Dense(self.action_size, activation='linear'))
        model.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))
        return model


    def act(self, state):
        if np.random.rand() <= self.epsilon:#以概率epsilon随机决策
            return random.randrange(self.action_size)
        act_values = self.model.predict(state)#经过神经网络给出一个决策
        return np.argmax(act_values[0])  # returns action
    


    def load(self, name):
        self.model.load_weights(name)

    


if __name__ == '__main__':
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://172.17.0.06:6566")
    env = gym.make('CartPole-v1')
    state_size = env.observation_space.shape[0]
    action_size = env.action_space.n

    agent = DQNAgent(state_size, action_size)
    # agent.load('./save/cartpole-dqn.h5')
    
    

    done = False#游戏结束
    batch_size = 32
    num_episodes = 1000
    version = 1
    for e in range(num_episodes):
        state = env.reset()
        state = np.reshape(state, [1, state_size]) 
        for time in range(500):
            action = agent.act(state) 
            next_state, reward, done, _ = env.step(action)
            reward = reward if not done else -10 
            next_state = np.reshape(next_state, [1, state_size])
            wjt = []
            wjt.append(state.tolist())
            wjt.append(action)
            wjt.append(reward)
            wjt.append(next_state.tolist())
            wjt.append(done)
            socket.send(bytes(str(wjt), encoding = "utf8"))
            print("Sending data : ",wjt)
            model = socket.recv()
            state = next_state 
            if len(model):
                fm = open('ver_pra{}.h5'.format(version),'wb')
                fm.write(model)
                fm.close()
                agent.load('ver_pra{}.h5'.format(version))
                print("load new model!")
                version += 1
                if agent.epsilon > agent.epsilon_min:
                    agent.epsilon *= agent.epsilon_decay
            if done:
                print('episode: {}/{}, score: {}, e: {:.2}'.format(e, num_episodes, time, agent.epsilon))
                break
            
            
            
