import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from sklearn.tree import export_graphviz
import pydot

din_data = pd.read_csv('/Users/tylerkim/Desktop/SquarePanda/Machine Learning project/din_train_data.csv')

data = pd.read_csv('/Users/tylerkim/Desktop/SquarePanda/Machine Learning project/green_train_data.csv')
data.describe()

feature_list = list(data.columns)[1:-1]
# feature_list = ['Phonological Awareness Duration', 'Spelling Writing Duration', 'Phonics Duration']
#
x = np.array(data[['Phonological Awareness Duration', 'Phonics Duration', 'Spelling Writing Duration', 'Lagoon Duration', 'Word Reading Duration']])
# x = np.array(data[['Phonological Awareness Duration', 'Spelling Writing Duration', 'Phonics Duration']])
y = np.array(data[['mean']])
#
train_features, test_features, train_labels, test_labels = train_test_split(x, y, test_size=.20, random_state=69)

model = RandomForestRegressor(random_state=69)
model.fit(train_features, train_labels)
predictions = model.predict(test_features)
errors = abs(predictions - test_labels)
mape = 100 * (errors/test_labels)
accuracy = 100 - np.mean(mape)
print(f'Model accuracy is {round(accuracy, 2)}%')
#
# importances = list(model.feature_importances_)
# feature_importances = [(feature, round(importance, 2)) for feature, importance in zip(feature_list, importances)]
# # Sort the feature importances by most important first
# feature_importances = sorted(feature_importances, key = lambda x: x[1], reverse = True)
# # Print out the feature and importances
# [print('Variable: {:20} | Importance: {}'.format(*pair)) for pair in feature_importances];
#
#
# Set the style
# plt.style.use('fivethirtyeight')
# # list of x locations for plotting
# x_values = list(range(len(importances)))
# # Make a bar chart
# plt.bar(x_values, importances, orientation = 'vertical')
# # Tick labels for x axis
# plt.xticks(x_values, feature_list, rotation=0)
# # Axis labels and title
# plt.ylabel('Importance'); plt.xlabel('Variable'); plt.title('Variable Importances')
# plt.show()
# print('Accuracy:', round(accuracy, 2), '%.')
#
# tree = model.estimators_[5]
# # Export the image to a dot file
# export_graphviz(tree, out_file = 'tree.dot', feature_names = feature_list, rounded = True, precision = 1)
# # Use dot file to create a graph
# (graph, ) = pydot.graph_from_dot_file('tree.dot')
# # Write graph to a png file
# graph.write_png('/Users/tylerkim/Desktop/SquarePanda/Machine Learning project/important_tree.png')

# din_x = np.array(din_data[['Phonological Awareness Duration', 'Phonics Duration', 'Spelling Writing Duration', 'Lagoon Duration', 'Word Reading Duration']])
# # din_x = np.array(din_data[['Phonological Awareness Duration', 'Phonics Duration', 'Spelling Writing Duration']])
# din_y = np.array(din_data['mean'])
# din_pred = model.predict(test_features)
# errors = abs(din_pred - test_labels)
# mape = 100 * (errors/test_labels)
# accuracy = 100 - np.mean(mape)
# print(f'Model accuracy on Dinwiddie data is {round(accuracy, 2)}%')



