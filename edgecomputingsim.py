# -*- coding: utf-8 -*-
"""EdgeComputingSim.ipynb

!pip install simpy

"""# Imports and Data generation"""

import torch
from torchvision.models import resnet18, ResNet18_Weights
import pandas as pd
import numpy as np
from google.colab import drive
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error, mean_squared_error
from sklearn.preprocessing import MinMaxScaler
np.random.seed(11)
# mount drive
drive.mount('/content/drive')
# print(torch.__version__)

# Generate random outputs for training
outputs = np.random.randint(1, 5, 8619)
print(outputs)

count1 = 0
count2 = 0
count3 = 0
count4 = 0
for num in outputs:
  if num == 1:
    count1 += 1
  elif num == 2:
    count2 += 1
  elif num == 3:
    count3 += 1
  else:
    count4 += 1

print(count1)
print(count2)
print(count3)
print(count4)

outputs = pd.Series(outputs)
outputs



"""# Edge Server 1 Dataset"""

edge1 = pd.read_csv("/content/drive/Shareddrives/CSI 5240 - Cloud Computing/ML Model/1.csv", delimiter=";\t")
edge1 = edge1.loc[:, ~edge1.columns.isin(['Timestamp [ms]', 'CPU cores', 'CPU capacity provisioned [MHZ]', 'Memory capacity provisioned [KB]',
                                          'Disk read throughput [KB/s]', 'Disk write throughput [KB/s]',
                                          'Network received throughput [KB/s]', 'Network transmitted throughput [KB/s]'])]
# edge1.sort_values(by=['CPU usage [MHZ]', 'CPU usage [%]', 'Memory usage [KB]'])

# Remove rows at random so that all datasets have equal number of rows
remove_n = 15
drop_indices = np.random.choice(edge1.index, remove_n, replace=False)
edge1 = edge1.drop(drop_indices)
edge1.reset_index(drop=True, inplace=True)

print("Number of Edge Server Rows: " + str(edge1.shape[0]))

# Rename Columns to match what they represent
edge1 = edge1.add_prefix('Edge 1 ')
print(edge1.columns)

# print(edge1.dtypes)
# edge1



"""# Edge Server 2 dataset"""

edge2 = pd.read_csv("/content/drive/Shareddrives/CSI 5240 - Cloud Computing/ML Model/1229.csv", delimiter=";\t")
edge2 = edge2.loc[:, ~edge2.columns.isin(['Timestamp [ms]', 'CPU cores', 'CPU capacity provisioned [MHZ]', 'Memory capacity provisioned [KB]',
                                          'Disk read throughput [KB/s]', 'Disk write throughput [KB/s]',
                                          'Network received throughput [KB/s]', 'Network transmitted throughput [KB/s]'])]
# edge2.sort_values(by=['CPU usage [MHZ]', 'CPU usage [%]', 'Memory usage [KB]'])


# Remove rows at random so that all datasets have equal number of rows
remove_n = 18
drop_indices = np.random.choice(edge2.index, remove_n, replace=False)
edge2 = edge2.drop(drop_indices)
edge2.reset_index(drop=True, inplace=True)

print("Number of Edge Server Rows: " + str(edge2.shape[0]))

# Rename Columns to match what they represent
edge2 = edge2.add_prefix('Edge 2 ')
print(edge2.columns)

# print(edge2.dtypes)
# edge2



"""# Edge Server 3 Dataset"""

edge3 = pd.read_csv("/content/drive/Shareddrives/CSI 5240 - Cloud Computing/ML Model/980.csv", delimiter=";\t")
edge3 = edge3.loc[:, ~edge3.columns.isin(['Timestamp [ms]', 'CPU cores', 'CPU capacity provisioned [MHZ]', 'Memory capacity provisioned [KB]',
                                          'Disk read throughput [KB/s]', 'Disk write throughput [KB/s]',
                                          'Network received throughput [KB/s]', 'Network transmitted throughput [KB/s]'])]
# edge3.sort_values(by=['CPU usage [MHZ]', 'CPU usage [%]', 'Memory usage [KB]'])

# Remove rows at random so that all datasets have equal number of rows
remove_n = 21
drop_indices = np.random.choice(edge3.index, remove_n, replace=False)
edge3 = edge3.drop(drop_indices)
edge3.reset_index(drop=True, inplace=True)

print("Number of Edge Server Rows: " + str(edge3.shape[0]))

# Rename Columns to match what they represent
edge3 = edge3.add_prefix('Edge 3 ')
print(edge3.columns)



"""# Cloud Server Dataset"""

cloud = pd.read_csv("/content/drive/Shareddrives/CSI 5240 - Cloud Computing/ML Model/1226.csv", delimiter=";\t")
cloud = cloud.loc[:, ~cloud.columns.isin(['Timestamp [ms]', 'CPU cores', 'CPU capacity provisioned [MHZ]', 'Memory capacity provisioned [KB]',
                                          'Disk read throughput [KB/s]', 'Disk write throughput [KB/s]',
                                          'Network received throughput [KB/s]', 'Network transmitted throughput [KB/s]'])]
# cloud.sort_values(by=['CPU usage [MHZ]', 'CPU usage [%]', 'Memory usage [KB]'])


# Remove rows at random so that all datasets have equal number of rows
remove_n = 18
drop_indices = np.random.choice(cloud.index, remove_n, replace=False)
cloud = cloud.drop(drop_indices)
cloud.reset_index(drop=True, inplace=True)

print("Number of Cloud Server Rows: " + str(cloud.shape[0]))

# Rename Columns to match what they represent
cloud = cloud.add_prefix('Cloud ')
print(cloud.columns)



"""# Task Dataset"""

tasks = pd.read_csv("/content/drive/Shareddrives/CSI 5240 - Cloud Computing/ML Model/63.csv", delimiter=";\t")
tasks = tasks.loc[:, ~tasks.columns.isin(['Timestamp [ms]', 'CPU cores', 'CPU capacity provisioned [MHZ]', 'Memory capacity provisioned [KB]',
                                          'Disk read throughput [KB/s]', 'Disk write throughput [KB/s]',
                                          'Network received throughput [KB/s]', 'Network transmitted throughput [KB/s]', 'CPU usage [%]'])]
# tasks.sort_values(by=['CPU usage [MHZ]', 'CPU usage [%]', 'Memory usage [KB]'])


print("Number of Task Rows: " + str(tasks.shape[0]))

# Rename Columns to match what they represent
tasks.rename(columns={"CPU usage [MHZ]": "Task CPU Need", "Memory usage [KB]": "Task Memory Need"}, inplace=True)
print(tasks.columns)



"""# Concatenate all data sets to create input and outputs feature"""

combinedDataset = pd.concat([edge1, edge2, edge3, cloud, tasks, outputs], axis=1)
combinedDataset.rename(columns={0: "Outputs"}, inplace=True)
print(combinedDataset.columns)
combinedDataset

"""# ML Model"""

import numpy as np
from keras.models import Sequential
from keras.layers import LSTM, Dense
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

# Dataset name is combinedDataset, containing features and target data
# Feature names
features = [
    'Edge 1 CPU usage [MHZ]', 'Edge 1 CPU usage [%]', 'Edge 1 Memory usage [KB]',
    'Edge 2 CPU usage [MHZ]', 'Edge 2 CPU usage [%]', 'Edge 2 Memory usage [KB]',
    'Edge 3 CPU usage [MHZ]', 'Edge 3 CPU usage [%]', 'Edge 3 Memory usage [KB]',
    'Cloud CPU usage [MHZ]', 'Cloud CPU usage [%]', 'Cloud Memory usage [KB]',
    'Task CPU Need', 'Task Memory Need'
]

# Get the feature data and target data
X = combinedDataset.iloc[:, :-1]  # All rows, all columns except the last one as features
y = combinedDataset.iloc[:, -1:]  # All rows, last one columns as target

# Data preprocessing
scaler = MinMaxScaler(feature_range=(0, 1))
X_scaled = scaler.fit_transform(X)
y_scaled = scaler.fit_transform(y)

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_scaled, test_size=0.2, random_state=42)

# Get the input shape
input_shape = (X_train.shape[1], 1)  # Input shape should be (number of features, time steps)

# Define the LSTM model
model = Sequential()
model.add(LSTM(units=50, return_sequences=True, input_shape=input_shape))
model.add(LSTM(units=50, return_sequences=False))
model.add(Dense(units=1))  # One output nodes, corresponding to the one columns of target data

# Compile the model
model.compile(optimizer='adam', loss='mean_squared_error')

# Train the model
model.fit(X_train, y_train, epochs=10, batch_size=32, verbose=1, validation_data=(X_test, y_test))

# Use the trained model for prediction
predictions = model.predict(X_test)

# Inverse scaling the predicted results
predictions_rescaled = scaler.inverse_transform(predictions)



"""# Simulation

# Simulation Setup
"""

import simpy
import math

# Define a Virtual Machine class
class VirtualMachine:
    def __init__(self, env, cpu_capacity, mem_capacity):
        self.env = env
        # SimPy resources to simulate CPU and memory
        self.cpu = simpy.Container(env, cpu_capacity, init=cpu_capacity)  # CPU resource container
        self.mem = simpy.Container(env, mem_capacity, init=mem_capacity)  # Memory resource container

# Define a function to run tasks
def run_task(env, vm, cpu_needed, mem_needed, duration):
    # Request CPU resources
    cpu_amount = min(cpu_needed, vm.cpu.level)  # Ensure not to request more than available
    yield vm.cpu.get(cpu_amount)
    print(f'Time {env.now}: CPU resources requested {cpu_amount}MHz')

    # Request memory resources
    mem_amount = min(mem_needed, vm.mem.level)  # Ensure not to request more than available
    yield vm.mem.get(mem_amount)
    print(f'Time {env.now}: Memory resources requested {mem_amount}MB')

    # Simulate the task running for a certain duration
    yield env.timeout(duration)

    # Release resources
    yield vm.cpu.put(cpu_amount)
    print(f'Time {env.now}: Released CPU resources {cpu_amount}MHz')
    yield vm.mem.put(mem_amount)
    print(f'Time {env.now}: Released memory resources {mem_amount}MB')

# Create simulation environment and a virtual machines
env = simpy.Environment()
edge1_VM = VirtualMachine(env, cpu_capacity=9599, mem_capacity=3141)  # Based on your dataset format
edge2_VM = VirtualMachine(env, cpu_capacity=9599, mem_capacity=3141)  # Based on your dataset format
edge3_VM = VirtualMachine(env, cpu_capacity=9599, mem_capacity=3141)  # Based on your dataset format
cloud_VM = VirtualMachine(env, cpu_capacity=23407, mem_capacity=25165)  # Based on your dataset format

# Generate Tasks for simulation
print("Min Values for Tasks: ")
print(tasks.min())
print("Max Values for Tasks: ")
print(tasks.max())

simTasksCPU = np.random.uniform(low=tasks.min()[0], high=tasks.max()[0], size=(50,))

simTasksMemory = np.random.uniform(low=tasks.min()[1], high=tasks.max()[1], size=(50,))
temp = []
for memoryval in simTasksMemory:
  temp.append(memoryval/1000)

simTasksMemory = np.array(temp)

taskDurration = []
for cpuVal in simTasksCPU:
  taskDurration.append(math.ceil((cpuVal/tasks[['Task CPU Need']].max()) * 20))

print("Simulated Tasks CPU Values [MHZ]: ")
print(simTasksCPU)
print("Simulated Tasks Memory Values [MB]: ")
print(simTasksMemory)
print("Simulated Tasks Durration [S]: ")
print(taskDurration)

"""# Run Simulation"""

# env.process(run_task(env, edge1_VM, cpu_needed=1000, mem_needed=2048, duration=10))
# env.process(run_task(env, edge1_VM, cpu_needed=2000, mem_needed=4096, duration=20))


while(true):
  for task in tasks:
    vmResources = getCurrentUtilizationOfVMs()
    taskResources = getTaskCPUAndMemNeed()
    inputFeature = createInputFeature(vmResources, taskResources)
    prediction = model.predict(inputFeature)
    getLoss(prediction, vmResources)
    modelUpdate()
    assignTaskToHost(prediction)

  wait(20s)
  status = getStatusOfTasks()
  migratedTasks = getTasksToMigrate(status)

  tasks.append(migratedTasks)
  tasks.append(newTaskBatch)
