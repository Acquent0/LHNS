import pickle as pkl

# read TSP20.pkl

# Open the pickle file in read mode
with open('TSP100.pkl', 'rb') as file:
    # Load the data from the pickle file
    data = pkl.load(file)

# Access the individual data elements
coords = data['coordinate']