import numpy as np
import time
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from flask import Flask, render_template, Response

app = Flask(__name__)

# Global variables to store data
time_data = []
voltage_data = []
start_time = time.time()  # Store the initial start time
MAX_DATA_POINTS = 60  # Maximum number of data points to keep

def generate_potentiometer_data():
    """
    Generates realistic dummy data for an ESP32 reading a potentiometer
    in a car, simulating voltage in millivolts.

    Assumptions:
    - 16-bit ADC resolution (0-65535)
    - Voltage range: 0-3.3V (ESP32's typical ADC range)
    - Potentiometer simulates throttle position
    - Car is starting, idling, accelerating, decelerating, and cruising.
    """
    # Simulate time passing (in seconds)
    t = time.time() - start_time  # Time since the script started

    # Base voltage (idling, let's say between 0.7V and 1.1V)
    base_voltage = np.random.uniform(0.7, 1.1)

    # Simulate throttle position changes
    if t < 5:  # Starting - quick ramp up
        throttle = t / 5
    elif 5 <= t < 15:  # Accelerating
        throttle = 0.2 + (t - 5) / 10 * 0.8  # Goes from 0.2 to 1.0
    elif 15 <= t < 30:  # Cruising
        throttle = np.random.normal(0.8, 0.1)  # Around 0.8 with some noise
        throttle = np.clip(throttle, 0.6, 1.0)  # Limit the noise
    elif 30 <= t < 40:  # Decelerating
        throttle = 0.8 - (t - 30) / 10 * 0.6
    elif 40 <= t < 50:  # More Decelerating
        throttle = 0.2 - (t - 40) / 10 * 0.2
    else:  # Idling
        throttle = np.random.normal(0.1, 0.05)
        throttle = np.clip(throttle, 0.05, 0.2)

    # Calculate voltage
    voltage = base_voltage + throttle * (3.3 - base_voltage)

    # Convert voltage to millivolts
    millivolts = voltage * 1000

    # Convert millivolts to 16-bit ADC value (0-65535)
    adc_value = int((millivolts / 3300) * 65535)

    # Add some noise to simulate real-world fluctuations (optional, but makes it more realistic)
    noise = np.random.normal(0, 10)  # Standard deviation of 10 mV
    millivolts_with_noise = millivolts + noise
    adc_value_with_noise = int((millivolts_with_noise / 3300) * 65535)

    # Clamp the values to the valid range for 16-bit
    millivolts_with_noise = np.clip(millivolts_with_noise, 0, 3300)
    adc_value_with_noise = np.clip(adc_value_with_noise, 0, 65535)

    return t, int(millivolts_with_noise), int(adc_value_with_noise)  # Return time, millivolts, and adc

def generate_graph():
    """
    Generates the voltage vs. time graph as a PNG image in base64 format.
    This version updates the global data lists and uses them to plot.

    Returns:
        str: The base64 encoded PNG image of the graph.
    """
    global time_data, voltage_data, start_time, MAX_DATA_POINTS

    # Get new data
    time_val, mv, _ = generate_potentiometer_data()
    time_data.append(time_val)
    voltage_data.append(mv)

    # Keep only the last MAX_DATA_POINTS
    if len(time_data) > MAX_DATA_POINTS:
        time_data = time_data[-MAX_DATA_POINTS:]
        voltage_data = voltage_data[-MAX_DATA_POINTS:]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(time_data, voltage_data)
    plt.title('Voltage vs. Time (Last {} Seconds)'.format(MAX_DATA_POINTS))
    plt.xlabel('Time (s)')
    plt.ylabel('Voltage (mV)')
    plt.grid(True)

    # Save the plot to a BytesIO object (in memory)
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()  # Close the plot to free memory

    # Encode the image to base64
    image_png = buffer.getvalue()
    encoded_image = base64.b64encode(image_png).decode('utf-8')
    return encoded_image

@app.route('/plot.png')
def plot_png():
    """
    Flask route to serve the graph as a PNG image.  This is used for the img tag.
    """
    graph_data = generate_graph()  # Get the new graph data
    return Response(base64.b64decode(graph_data), mimetype='image/png')

@app.route('/')
def index():
    """
    Flask route to render the HTML page with the embedded image.
    The page will refresh every second to update the graph.
    """
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
