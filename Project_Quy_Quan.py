import pynmea2
import simplekml
import pandas as pd


def read_gps_data(file_path):
    with open(file_path, 'r') as file:
        return file.readlines()


def parse_gps_data(nmea_lines):

    data = {'Timestamp': [], 'Latitude': [], 'Longitude': [], 'Speed': [], 'Elevation': []}
    elevation = None  # Initialize elevation
    last_position = None  # Store the last position to check for duplicates
    start_new_path = True  # Flag to indicate whether a new path is starting

    for line in nmea_lines:
        try:
            # Parse NMEA sentence
            msg = pynmea2.parse(line)

            # Extract relevant information from GPRMC and GPGGA sentences
            if isinstance(msg, pynmea2.types.talker.GGA):
                elevation = msg.altitude
            elif isinstance(msg, pynmea2.types.talker.RMC):
                timestamp = msg.timestamp
                speed = msg.spd_over_grnd * 1.852  # Convert speed from knots to km/h
                latitude = msg.latitude
                longitude = msg.longitude

                # Check if a new path is starting or if the location is significantly different
                if start_new_path or (last_position is not None and (latitude, longitude) != last_position):
                    # Append data to the dictionary
                    data['Timestamp'].append(timestamp)
                    data['Latitude'].append(latitude)
                    data['Longitude'].append(longitude)
                    data['Speed'].append(speed)
                    data['Elevation'].append(elevation)
                    start_new_path = False  # Reset the flag after adding the starting point
                last_position = (latitude, longitude)

        except pynmea2.ParseError:
            # Ignore lines that can't be parsed
            pass

    # Create a Pandas DataFrame
    df = pd.DataFrame(data)

    return df


def convert_to_kml(gps_dataframe):
    kml = simplekml.Kml()

    current_path_color = '7f00ffff'  # Yellow by default
    current_path_coords = []
    current_speed_over_ground = 0

    for index, row in gps_dataframe.iterrows():
        current_speed_over_ground = row['Speed']

        latitude = row['Latitude']
        longitude = row['Longitude']
        altitude = row['Elevation']

        if True:  # Add your condition here if needed
            # Check if current_path_coords is not empty before accessing its last element
            if current_path_coords:
                # Compare altitudes to determine uphill or downhill
                if altitude > current_path_coords[-1][2] and current_speed_over_ground > 10:
                    new_path_color = 'ff0000ff'  # Red for uphill
                else:
                    new_path_color = '7f00ffff'  # Yellow for flat or downhill

                if new_path_color != current_path_color:
                    linestring = kml.newlinestring(name="Path", description="GPS Path")
                    linestring.style.linestyle.color = current_path_color
                    linestring.coords.addcoordinates(current_path_coords)

                    linestring.altitudemode = simplekml.AltitudeMode.relativetoground
                    linestring.extrude = 1

                    current_path_coords = [(longitude, latitude, altitude)]
                    current_path_color = new_path_color
                else:
                    current_path_coords.append((longitude, latitude, altitude))
            else:
                current_path_coords.append((longitude, latitude, altitude))

    if current_path_coords:
        linestring = kml.newlinestring(name="Path", description="GPS Path")
        linestring.style.linestyle.color = current_path_color
        linestring.coords.addcoordinates(current_path_coords)

    kml.save("output.kml")

def main():
    file_path = '2023_August_Sept_Oct_GPS_FILES/2023_08_01__233842_gps_file.txt'
    raw_data = read_gps_data(file_path)
    filtered_data = parse_gps_data(raw_data)
    print(filtered_data) # for bug testing
    convert_to_kml(filtered_data)


if __name__ == "__main__":
    main()
