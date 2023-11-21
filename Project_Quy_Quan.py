import pynmea2
import simplekml
import pandas as pd
from math import radians, sin, cos, sqrt, atan2


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
                if start_new_path or (
                        last_position is not None and (latitude, longitude) != last_position) and speed > 10:
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
                # Calculate slope (grade)
                previous_altitude = current_path_coords[-1][2]
                distance = haversine((latitude, longitude), (current_path_coords[-1][0], current_path_coords[-1][1]))

                if distance > 0:
                    grade = ((altitude - previous_altitude) / distance) * 100  # Slope in percentage
                    # Compare slope to determine uphill (10% grade or higher)
                    if grade >= 1 and current_speed_over_ground > 10:
                        new_path_color = 'ff0000ff'  # Red for uphill
                    else:
                        new_path_color = '7f00ffff'  # Yellow for flat or downhill
                else:
                    new_path_color = '7f00ffff'  # Assume flat if distance is zero
                # Compare altitudes to determine uphill or downhill
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


def haversine(coord1, coord2):
    # Calculate the haversine distance between two coordinates in kilometers
    lat1, lon1 = radians(coord1[0]), radians(coord1[1])
    lat2, lon2 = radians(coord2[0]), radians(coord2[1])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = 6371 * c  # Earth radius in kilometers

    return distance


def main():
    file_path = '2023_August_Sept_Oct_GPS_FILES/2023_08_02__183833_gps_file.txt'
    raw_data = read_gps_data(file_path)
    filtered_data = parse_gps_data(raw_data)
    print(filtered_data)  # for bug testing
    convert_to_kml(filtered_data)


if __name__ == "__main__":
    main()
