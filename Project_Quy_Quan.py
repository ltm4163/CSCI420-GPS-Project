import pynmea2
import simplekml
from simplekml import Style

def read_gps_data(file_path):
    with open(file_path, 'r') as file:
        return file.readlines()

def filter_gps_data(raw_data):
    filtered_data = [line for line in raw_data if "$GPRMC" in line or "$GPGGA" in line]
    return filtered_data

def convert_to_kml(gps_data):
    kml = simplekml.Kml()

    current_path_color = '7f00ffff'  # Yellow by default
    current_path_coords = []
    current_speed_over_ground = 0

    for line in gps_data:
        if "$GPRMC" in line:
            try:
                msg = pynmea2.parse(line)
                current_speed_over_ground = msg.spd_over_grnd
            except pynmea2.ParseError as e:
                print('Parse error (RMC): {}'.format(e))
                continue
        elif "$GPGGA" in line:
            try:
                msg = pynmea2.parse(line)
                latitude = msg.latitude
                longitude = msg.longitude
                altitude = msg.altitude

                if True:
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

            except pynmea2.ParseError as e:
                print('Parse error: {}'.format(e))
                continue

    if current_path_coords:
        linestring = kml.newlinestring(name="Path", description="GPS Path")
        linestring.style.linestyle.color = current_path_color
        linestring.coords.addcoordinates(current_path_coords)

    kml.save("output.kml")

def main():
    file_path = '2023_August_Sept_Oct_GPS_FILES/2023_08_01__233842_gps_file.txt'
    raw_data = read_gps_data(file_path)
    filtered_data = filter_gps_data(raw_data)
    convert_to_kml(filtered_data)

if __name__ == "__main__":
    main()






