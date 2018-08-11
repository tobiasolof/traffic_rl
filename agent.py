import time
import random
from collections import deque
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Reshape
import tensorflow as tf
from city import City


NR_EPISODES = 20000
REPLAY_SIZE = 16
TERMINATE_FREQ = 2
ACTION_FREQ = 50
DRAW_FREQ = 5
DRAW_FREQ_EPOCH = 10
NR_CARS = 10
DIMENSIONS = (4, 3)


# Inspired by https://keon.io/deep-q-learning/
class TrafficQNAgent:

    def __init__(self):
        self.env = City(stepsize=0.01, dimensions=DIMENSIONS)
        self.state_size = 1 + len(self.env.intersections) * 4 * 3
        self.action_size = len(self.env.intersections) * 4
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95  # discount rate
        self.epsilon = 1.0  # initial exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = (self.epsilon_min / self.epsilon) ** (1.25 / NR_EPISODES)
        self.timestamp = time.strftime('%Y%m%d-%H%M', time.localtime())
        self.model = self._build_model()

    # Define neural network
    def _build_model(self):
        model = Sequential()
        model.add(Dense(16, input_dim=self.state_size, activation='relu'))
        model.add(Dense(self.action_size, activation='linear'))
        model.add(Reshape((len(self.env.intersections), -1)))
        model.compile(loss='mse', optimizer='nadam')
        return model

    # Add frame to memory
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    # Decide action
    def act(self, state):
        # Explore randomly
        if np.random.rand() <= self.epsilon:
            return np.array([random.randrange(4) for _ in range(len(self.env.intersections))])
        # Act according to policy
        else:
            return np.argmax(self.model.predict(state)[0], axis=1)

    # Train based on experience replay
    def replay(self, batch_size):
        # Draw from memory
        try:
            minibatch = random.sample(self.memory, batch_size)
        # If not enough memories, draw with replacement
        except ValueError:
            minibatch = random.choices(self.memory, k=batch_size)

        # Loop over batch
        for state, action, reward, next_state, done in minibatch:

            # Calculate the reward (discounted if not end state)
            if done:
                target = reward
            else:
                target = reward + self.gamma * np.max(self.model.predict(next_state)[0])
            # Predict the direct rewards from the current state
            target_f = self.model.predict(state)
            # Set the reward for the chosen state
            for i in range(len(self.env.intersections)):
                target_f[0][i][action[i]] = target
            # Train model to predict rewards for all actions
            self.model.fit(state, target_f, epochs=1, verbose=0)

        # Decay exploration rate
        self.epsilon *= self.epsilon_decay

    # Run agent
    def run(self, train=False, nr_cars=NR_CARS, nr_episodes=NR_EPISODES,
            terminate_freq=TERMINATE_FREQ, visualize=False, write=True):

        # Define writer
        writer = tf.summary.FileWriter(f'./logs/{self.timestamp}/')

        # Create window
        if visualize:
            self.env.build_window()

        # Iterate over episodes
        for epoch in range(nr_episodes):

            # Reset state in the beginning of each episode
            self.env.place_cars(n=nr_cars, clear=True)  # TODO: Add more cars after a while
            state = [-self.env.sum_wait_time()] + self.env.get_predictors()
            state = np.reshape(state, [1, -1])

            # Iterate over time frames
            for t in range(terminate_freq):

                # Decide action
                action = self.act(state)

                # Advance the game
                for i, intersection in enumerate(self.env.intersections):
                    intersection.change_state(action[i])
                # Move multiple steps in one iteration
                for i in range(ACTION_FREQ):
                    self.env.update_positions(visualize=visualize)
                    # Update visualization
                    if visualize & (i % DRAW_FREQ == 0) & (epoch % DRAW_FREQ_EPOCH == 0):
                        self.env.tk.update_idletasks()
                        self.env.tk.update()
                next_state = [-self.env.sum_wait_time()] + self.env.get_predictors()
                next_state = np.reshape(next_state, [1, -1])
                reward = -self.env.sum_wait_time()
                if train:
                    done = (t == (TERMINATE_FREQ - 1))

                    # Add to memory
                    self.remember(state, action, reward, next_state, done)

                # Update current state
                state = next_state

            # Train with experience replay
            if train:
                self.replay(REPLAY_SIZE)

            # Write to TensorBoard
            if write:
                tag_prefix = '' if train else 'test_'
                writer.add_summary(
                    tf.Summary(
                        value=[tf.Summary.Value(tag=tag_prefix + 'wait', simple_value=-reward)]
                    ),
                    epoch
                )
                writer.add_summary(tf.Summary(value=[
                    tf.Summary.Value(tag=tag_prefix + 'nr_cars', simple_value=len(self.env.cars))]),
                                        epoch)
                writer.flush()

            # Print progress
            print(round(100 * epoch / NR_EPISODES), '%', sep='', end='\r', flush=True)

        # Close Tkinter window
        if visualize:
            self.env.tk.destroy()

    # Train agent
    def train(self, nr_cars=NR_CARS, nr_episodes=NR_EPISODES,
              terminate_freq=TERMINATE_FREQ, visualize=False):
        # Just wrap run finction
        self.run(train=True, nr_cars=nr_cars, nr_episodes=nr_episodes,
                 terminate_freq=terminate_freq, visualize=visualize)


if __name__ == '__main__':
    agent = TrafficQNAgent()
    agent.run(train=True, visualize=False, write=True)
    agent.run()
