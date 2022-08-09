import webbrowser # needed to use web browser
from datetime import date # needed to get today's date
import geopy # needed for lat lon calcs
from geopy.distance import geodesic # needed for bounding box calc

# default values for start and end date are today
startDate = date.today().strftime("%Y-%m-%d")
endDate = date.today().strftime("%Y-%m-%d")

# center lat lon
lat = 37.869004
lon = -122.257750
radius = 3 # bounding box radius in km : kept small just to limit file size

ready = False
print("Welcome to the simple netCDF grabber for HRRR data")

while not ready:
    print("\nThe current settings are:")
    print(f"Start Date: {str(startDate)}")
    print(f"End Date: {str(endDate)}")
    print(f"Lat Lon: {str(lat)} {str(lon)}\n")

    print("Type 'D' to change dates, 'L' to change the center lat lon, or anything else to continue")
    choice = input("Enter your choice: ")

    if str(choice).lower() == 'd':
        startDate = input("Enter new start date in the format of YY-MM-DD: ")
        endDate = input("Enter new end date in the format of YY-MM-DD: ")
    elif str(choice).lower() == 'l':
        lat = float(input("Enter the new lat coordinate in degrees: "))
        lon = float(input("Enter the new lon coordinate in degrees: "))
    else:
        ready = True



origin = geopy.Point(lat, lon) # center point

# pull north
dest = geodesic(kilometers= radius).destination(origin, 0)
north = dest.latitude

# pull south
dest = geodesic(kilometers= radius).destination(origin, 180)
south = dest.latitude

# pull north
dest = geodesic(kilometers= radius).destination(origin, 90)
east = dest.longitude

# pull south
dest = geodesic(kilometers= radius).destination(origin, 270)
west = dest.longitude

print(f"\nBounding box coordinates: \nN: {str(north)} \nW: {str(west)} \nE: {str(east)} \nS: {str(south)} \n")

# then make a url variable
url = f"https://thredds-jumbo.unidata.ucar.edu/thredds/ncss/grib/NCEP/HRRR/CONUS_2p5km/Best?var=High_cloud_cover_high_cloud&var=Low_cloud_cover_low_cloud&var=Medium_cloud_cover_middle_cloud&var=Pressure_surface&var=Total_cloud_cover_entire_atmosphere&var=Wind_speed_gust_surface&var=Temperature_height_above_ground&var=u-component_of_wind_height_above_ground&var=v-component_of_wind_height_above_ground&north={str(north)}&west={str(west)}&east={str(east)}&south={str(south)}&horizStride=1&time_start={str(startDate)}T01%3A00%3A00Z&time_end={str(endDate)}T12%3A00%3A00Z&timeStride=1&vertCoord=&accept=netcdf"
  
# then call the default open method described above
webbrowser.open(url)