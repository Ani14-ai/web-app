from flask import Flask, request, jsonify, send_file
from sklearn.cluster import KMeans
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

app = Flask(__name__)

# Load and preprocess the dataset
data = pd.read_csv("Mall_Customers.csv")
x = data["Annual Income (k$)"]
y = data["Spending Score (1-100)"]
X = np.array(list(zip(x, y)))

# Fit K-Means model
num_clusters = 5
kmeans = KMeans(n_clusters=num_clusters)
kmeans.fit(X)

@app.route('/cluster', methods=['POST'])
def cluster_data():
    try:
        # Get input data as JSON
        input_data = request.get_json()
        new_data = input_data['data']
        
        # Predict cluster labels for new data
        labels = kmeans.predict(new_data)
        
        return jsonify({'cluster_labels': labels.tolist()})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/plot', methods=['GET'])
def generate_plots():
    try:
        # Generate and return the clustering plot
        plt.scatter(X[:, 0], X[:, 1], c=kmeans.labels_)
        plt.title('K-Means Clustering')
        plt.xlabel('Annual Income (k$)')
        plt.ylabel('Spending Score (1-100)')

        # Save the plot as an image
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png')
        img_buffer.seek(0)
        
        # Clear the plot to prevent multiple plots on subsequent requests
        plt.clf()

        # Return the image as a response
        return send_file(img_buffer, mimetype='image/png')
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=False)
