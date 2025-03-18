# Importing pandas and matplotlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Read in the Netflix CSV as a DataFrame
netflix_df = pd.read_csv("/Users/armandovalle/Desktop/Datasets/netflix_data.csv")

# Start coding here! Use as many cells as you like

# Filtering movies from the 1990s
netflix_90s = netflix_df[(netflix_df['release_year'] >= 1990) & (netflix_df['release_year'] <= 1999)]

# Plot histogram of release years
plt.hist(netflix_90s['release_year'], bins=10, edgecolor='black')
plt.xlabel('Release Year')
plt.ylabel('Frequency')
plt.title('Distribution of Netflix Content Release Years 90 - 99')
plt.show()
# Most frequent movie duration
duration = netflix_90s['duration'].mode()[0]  # Get the most frequent duration

# Initialize counter
short_movie_count = 0  

# Loop through each row in the DataFrame
for index, row in netflix_90s.iterrows():
    if row['genre'] == 'Action' and row['duration'] < 90:
        short_movie_count += 1  # Increment counter

# Print the count
print("The most frequent movie duration is:", str(duration) + " Minutes")
print("Short Action Movies Count:", short_movie_count)
print("hello")