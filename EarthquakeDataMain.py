import os
import webbrowser
from EarthquakeDataFunctions import read_data_from_csv,read_live_data,extract_data
from EarthquakeDataFunctions import calculate_statistics, frequency_table, pearson_correlation
from EarthquakeDataFunctions import interpret_correlation, printing_result
from EarthquakeDataFunctions import plot_earthquakes_on_map


# Main function to orchestrate the program flow
def main():
    print("Welcome to the Earthquake Data Analysis Program!")
    print()
    print("This program allows you to explore earthquake data collected from various sources and analyze it to gain insights into seismic activity around the world. Whether you're interested in recent seismic events or historical data, this program provides you with tools to visualize earthquake magnitudes, depths, and locations.")
    print()
    print("Please select the data source:")
    print("1. CSV file")
    print("2. Live data from USGS API")
    print("Or type 'q' to Quit")

    while True:
        # Prompt user to select data source
        choice = input("Choice: ")

        if choice == '1':
            # Read earthquake data from CSV file
            filename = 'earthquakes.csv'
            data = read_data_from_csv(filename)
            break  # Exit the loop if a valid choice is made
        elif choice == '2':
            # Read live earthquake data from USGS API
            url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_month.geojson"
            data = read_live_data(url)
            break  # Exit the loop if a valid choice is made
        elif choice.lower() == 'q':
            print("Exiting program...")
            exit()  # Exit the program if the user chooses to quit
        else:
            print("Invalid choice. Please enter 1, 2, or 'q'.")

    # Extract earthquake data
    magnitudes, depths, coordinates = extract_data(choice,data)
    
    if magnitudes is None or depths is None or coordinates is None:
        return

    # Calculate and display statistics
    statistics_dict = calculate_statistics(magnitudes, depths)
    correlation = pearson_correlation(magnitudes, depths)
    correlation_interpretation = interpret_correlation(correlation)
    mag_f_df, dp_f_df = frequency_table(magnitudes,depths,coordinates)

    printing_result(statistics_dict,correlation,correlation_interpretation,mag_f_df,dp_f_df)

    # Plot earthquakes on map
    plot_earthquakes_on_map(coordinates, magnitudes)
    #open the link with default
    # Get the absolute path to the HTML file
    html_file_path = os.path.abspath('earthquakes_map.html')

    # Open the HTML file in the default web browser
    webbrowser.open(f'file://{html_file_path}', new=2)
    #webbrowser.open('earthquakes_map.html', new=2)

# Execute the main function if the script is run directly
if __name__ == "__main__":
    main()

