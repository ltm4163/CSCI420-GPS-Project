import pynmea2
import simplekml
import datetime
import math

def read_gps_data(file_path):
    with open(file_path, 'r') as file:
        return file.readlines()

def filter_gps_data(raw_data):
    return [line for line in raw_data if "$GPRMC" in line or "$GPGGA" in line]

def convert_to_kml(gps_data):
    kml = simplekml.Kml()
    current_path_color, current_speed_over_ground = '7f00ffff', 0
    current_path_coords = []
    # previous_time = None

    for line in gps_data:
        if "$GPRMC" in line:
            try:
                current_speed_over_ground = pynmea2.parse(line).spd_over_grnd
            except pynmea2.ParseError as e:
                print(f'Parse error (RMC): {e}')
                continue
        elif "$GPGGA" in line:
            try:
                msg = pynmea2.parse(line)
                latitude, longitude, altitude = msg.latitude, msg.longitude, msg.altitude

                # time = datetime.datetime.combine(datetime.date.today(), msg.timestamp)
                # if previous_time is not None:
                #     diff = time - previous_time
                #     print(diff.total_seconds())
                # previous_time = time


                if current_path_coords:
                    if altitude > current_path_coords[-1][2] and abs(altitude-current_path_coords[-1][2]) > 0.2 and current_speed_over_ground > 10:
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
                print(f'Parse error: {e}')
                continue

    if current_path_coords:
        linestring = kml.newlinestring(name="Path", description="GPS Path")
        linestring.style.linestyle.color = current_path_color
        linestring.coords.addcoordinates(current_path_coords)
        linestring.altitudemode = simplekml.AltitudeMode.relativetoground
        linestring.extrude = 1

    kml.save("output.kml")

def main():
    file_path = '2023_August_Sept_Oct_GPS_FILES/2023_08_01__233842_gps_file.txt'
    raw_data = read_gps_data(file_path)
    filtered_data = filter_gps_data(raw_data)
    convert_to_kml(filtered_data)

if __name__ == "__main__":
    main()







