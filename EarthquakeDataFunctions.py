import folium               #For map result
import requests             # For making HTTP requests
import statistics           # For statistical calculations
import numpy as np          # For numerical computations
import pandas as pd         # For data manipulation and analysis
import scipy.stats as stats


# Function to read data from CSV file
def read_data_from_csv(filename):
    
    try:
        data = pd.read_csv(filename) #read data from file
        return data
    except FileNotFoundError as fe:
        print(f"File {filename} not found. Error msg: {fe}") #handle error when the file is not found
        quit()
    except Exception as e:
        print(f"Opps something went wrong Error msg: {e}") #indicates to user that something went wrong instead of showing an error
        quit()
        
# Function to read live data from the given URL
def read_live_data(url):

    response = requests.get(url) #make GET request to the URL to fetch data
    data = response.json() #assigns the response
    return data 

# Function to extract data
def extract_data(choice,data): 

    magnitudes = []
    depths = []
    coordinates = []

    try:
        if choice == '1':
            for index, row in data.iterrows():
                magnitudes.append(row['mag'])
                depths.append(row['depth'])
                coordinates.append([row['latitude'], row['longitude']])
        elif choice == '2':
            for feature in data['features']:
                magnitudes.append(feature['properties']['mag'])
                depths.append(feature['geometry']['coordinates'][2])
                coordinates.append([feature['geometry']['coordinates'][1], feature['geometry']['coordinates'][0]])
        else:
            print("Invalid data source.")
            return None, None, None
    except KeyError as e:
        print(f"Error: {e}\nInvalid data format, try again.")
        return None, None, None

    return magnitudes, depths, coordinates


# Function to calculate statistical values
def calculate_statistics(magnitudes, depths):
    corr, _ = stats.pearsonr(magnitudes, depths)
    statistics_dict = {
        'Maximum Magnitude': max(magnitudes),
        'Minimum Magnitude': min(magnitudes),
        'Mean Magnitude': statistics.mean(magnitudes),
        'Median Magnitude': statistics.median(magnitudes),
        'Mode Magnitude': statistics.mode(magnitudes),
        'Standard Deviation Magnitude': statistics.stdev(magnitudes),
        'Maximum Depth': max(depths),
        'Minimum Depth': min(depths),
        'Mean Depth': statistics.mean(depths),
        'Median Depth': statistics.median(depths),
        'Mode Depth': statistics.mode(depths),
        'Standard Deviation Depth': statistics.stdev(depths),
        'Automated Pearson Correlation': corr
    }

    return statistics_dict

# Function to display frequency table
def frequency_table(magnitudes,depths,coordinates):

    eq_df = pd.DataFrame({     #create a dataframe for extracting data
            'Magnitude': magnitudes,
            'Depth': depths,
            'Longitude': [coord[0] for coord in coordinates],
            'Latitude': [coord[1] for coord in coordinates]
        })

    #create a frequency table for magnitudes
    mag_frequency_table = eq_df.Magnitude.value_counts().sort_index()

    mag_f_df = pd.DataFrame({
            'Maginitude': mag_frequency_table.index,
            'Mag_Counts': mag_frequency_table.values
        })

    #create a frequency table for depths
    dp_frequency_table = eq_df.Depth.value_counts().sort_index()

    dp_f_df = pd.DataFrame({
            'Depth': dp_frequency_table.index,
            'Dep_Counts': dp_frequency_table.values
        })

    #check if extract_data returned None
    if magnitudes is None or depths is None or coordinates is None:
        print("Error extracting data. Exiting")
        quit()
    
    return mag_f_df,dp_f_df

#correlation fomula
def pearson_correlation(magnitudes, depths):
    
    # Extract x and y coordinates
    x = np.array(magnitudes)
    y = np.array(depths)
    
    # Check if the lengths of x and y are equal
    if len(x) != len(y):
        raise ValueError("Arrays must have the same length")

    n = len(x)

    # Calculate the mean of x and y
    mean_x = sum(x) / n
    mean_y = sum(y) / n

    # Calculate the numerator and denominators for Pearson correlation
    numerator = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
    denominator_x = sum((xi - mean_x) ** 2 for xi in x)
    denominator_y = sum((yi - mean_y) ** 2 for yi in y)

    # Avoid division by zero error
    if denominator_x == 0 or denominator_y == 0:
        return 0

    # Calculate Pearson correlation coefficient
    correlation = numerator / (denominator_x ** 0.5 * denominator_y ** 0.5)

    return correlation


#showing the results
def interpret_correlation(correlation):
    if correlation == 1:
        return "Perfectly positive"
    elif correlation > 0.8:
        return "Strongly positive"
    elif correlation > 0.5:
        return "Moderately positive"
    elif correlation > 0:
        return "Weakly positive"
    elif correlation == 0:
        return "No correlation"
    elif correlation < -0.8:
        return "Strongly negative"
    elif correlation < -0.5:
        return "Moderately negative"
    elif correlation < 0:
        return "Weakly negative"
    elif correlation == -1:
        return "Perfectly negative"

#Print the result that user needs
def printing_result(statistics_dict, correlation,correlation_interpretation,mag_f_df,dp_f_df):
    
    #print all the info
    print("\nStatistics:")

    for key, value in statistics_dict.items():
        print(f"{key}: {value}")

    print(f"\nPearson correlation between magnitudes and depths: {correlation}")
    print(f"Direction & Strength: {correlation_interpretation}")
    print()
    print(f"Magnitude frequency table: \n{mag_f_df}")
    print("="*20)
    print(f"Depth frequency table: \n{dp_f_df}")

# Function to map magnitudes to colors based on the Richter scale
def magnitude_to_color(magnitude):
    if 1.0 <= magnitude < 5.0:
        return 'green' 
    elif 5.0 <= magnitude < 6.0:
        return 'orange'   
    elif 6.0 <= magnitude < 7.0:
        return 'red'  
    elif 7.0 <= magnitude < 8.0:
        return 'black' 
    else:
        return 'gray'  # Default color for values outside the defined range
    

#putting data on the map
def plot_earthquakes_on_map(coordinates, magnitudes):
    # Create a Folium map centered at the mean latitude and longitude of the earthquake data
    map_center = [np.mean([coord[0] for coord in coordinates]), np.mean([coord[1] for coord in coordinates])]
    world_map = folium.Map(location=map_center, zoom_start=2)

    # Add a title to the map
    title_html = '<h3 align="center" style="font-size:20px"><b>Earthquake Distribution Map</b></h3>'
    world_map.get_root().html.add_child(folium.Element(title_html))

    # Add markers for each earthquake with popup information and color coding based on magnitude
    for i in range(len(coordinates)):
        magnitude = magnitudes[i]
        if 1.0 <= magnitude < 5.0:
            strength = 'Light'  
        elif 5.0 <= magnitude < 6.0:
            strength = 'Moderate'  
        elif 6.0 <= magnitude < 7.0:
            strength = 'Strong'  
        elif 7.0 <= magnitude < 8.0:
            strength = 'Major'

        popup_text = f"Magnitude: {magnitude}"
        tooltip_text = f"Coordinates: {coordinates[i]}, Magnitude: {magnitude}, Strength: {strength}"
        color = magnitude_to_color(magnitude)
        folium.Marker(location=coordinates[i], popup=popup_text, tooltip=tooltip_text, icon=folium.Icon(color=color)).add_to(world_map)

    # Display the map
    world_map.save('earthquakes_map.html')

   