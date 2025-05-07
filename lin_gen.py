def validate_coordinate(value, coord_type):
    """Validate latitude/longitude values"""
    min_val, max_val = (-90, 90) if coord_type == "latitude" else (-180, 180)
    try:
        num = float(value)
        if min_val <= num <= max_val:
            return num
        raise ValueError
    except ValueError:
        print(f"Invalid {coord_type}! Must be between {min_val} and {max_val}")
        exit()

def generate_map_links():
    """Generate Bing and Google Maps links from user input"""
    print("Enter coordinates (decimal degrees):")
    
    # Get and validate coordinates
    lat = validate_coordinate(input("Latitude (-90 to 90): "), "latitude")
    lon = validate_coordinate(input("Longitude (-180 to 180): "), "longitude")

    # Create Bing Maps URL
    bing_url = (
        f"https://www.bing.com/maps?cp={lat}~{lon}"
        f"&sty=a&lvl=19"
    )

    # Create Google Maps URL
    google_url = (
        f"https://maps.google.com/?ll={lat},{lon}"
        f"&t=k&z=19"
    )

    print("\nGenerated Map Links:")
    print(f"Bing Maps:   {bing_url}")
    print(f"Google Maps: {google_url}")

if __name__ == "__main__":
    generate_map_links()