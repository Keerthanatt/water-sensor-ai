
import csv
import random

sensors = ["S1", "S2", "S3", "S4", "S5"]

with open("sensor_data.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Reading", "Sensor", "Depth_m"])

    for reading in range(1, 11):
        for sensor in sensors:
            depth = round(random.uniform(10, 20), 2)
            writer.writerow([reading, sensor, depth])

print("Sensor data created successfully!")
