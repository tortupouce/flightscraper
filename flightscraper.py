from amadeus import Client, ResponseError
from datetime import datetime, timedelta

# API credentials (fill with yours)
AMADEUS_API_KEY = ""
AMADEUS_API_SECRET = ""

amadeus = Client(
    client_id=AMADEUS_API_KEY,
    client_secret=AMADEUS_API_SECRET
)

def build_amadeus_passenger_args(pax):

    total_adults = pax.get('adults', 0) + pax.get('students', 0) + pax.get('seniors', 0)
    children = pax.get('children_11', 0) + pax.get('children_17', 0)
    infants = pax.get('infants_lap', 0) + pax.get('infants_seat', 0)

    return {
        'adults': total_adults,
        'children': children,
        'infants': infants
    }

def generate_booking_link(origin, destination, departure_date, passengers_dict, return_date=None):
    base_url = "https://www.kayak.com/flights"
    pax_url_parts = []

    # For Kayak
    pax_url_parts.append(f"{passengers_dict.get('adults', 0)}adults")
    if passengers_dict.get('seniors', 0):
        pax_url_parts.append(f"{passengers_dict['seniors']}seniors")
    if passengers_dict.get('students', 0):
        pax_url_parts.append(f"{passengers_dict['students']}students")

    child_parts = []
    if passengers_dict.get('infants_lap', 0):
        child_parts.append(f"{passengers_dict['infants_lap']}L")
    if passengers_dict.get('infants_seat', 0):
        child_parts.append(f"{passengers_dict['infants_seat']}S")
    child_parts.extend(['11'] * passengers_dict.get('children_11', 0))
    child_parts.extend(['17'] * passengers_dict.get('children_17', 0))

    if child_parts:
        child_str = "children-" + "-".join(child_parts)
        pax_url_parts.append(child_str)

    pax_url = "/".join(pax_url_parts)
    if return_date:
        url = f"{base_url}/{origin}-{destination}/{departure_date}/{return_date}/{pax_url}"
    else:
        url = f"{base_url}/{origin}-{destination}/{departure_date}/{pax_url}"
    return url

def search_flights_return(origin, destination, departure_date, passengers_dict, max_price=None, stopover_city=None):
    all_options = []
    try:
        amadeus_args = build_amadeus_passenger_args(passengers_dict)
        # print(f"DEBUG: Searching flights with params: origin={origin}, destination={destination}, date={departure_date}, passengers={amadeus_args}")

        if stopover_city:
            multi_legs = get_multi_leg_options(origin, stopover_city, destination, departure_date, passengers_dict)
            for multi_leg in multi_legs:
                all_options.append({
                    'type': 'multi_leg',
                    'price': multi_leg['total_price'],
                    'flight': multi_leg
                })
        else:
            response = amadeus.shopping.flight_offers_search.get(
                originLocationCode=origin,
                destinationLocationCode=destination,
                departureDate=departure_date,
                currencyCode="EUR",
                max=10,
                **amadeus_args
            )
            if not response.data:
                print("DEBUG: No data returned from API.")
            for flight in response.data:
                price = float(flight['price']['total'])
                all_options.append({
                    'type': 'direct',
                    'price': price,
                    'flight': flight
                })

        if max_price is not None:
            all_options = [opt for opt in all_options if opt['price'] <= max_price]

        all_options.sort(key=lambda x: x['price'])

    except ResponseError as error:
        print(f"❗ API Error: [{error.response.status_code}] {error}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return all_options

def print_flight_options(all_options, origin, destination, departure_date, passengers_dict, stopover_city=None):
    if not all_options:
        print(f"No flight options found for {departure_date}")
        return

    for idx, option in enumerate(all_options, start=1):
        print(f"\n // {option['type']} | Option {idx}")
        if option['type'] == 'direct':
            flight = option['flight']
            segments = flight['itineraries'][0]['segments']
            for seg in segments:
                print(f"  {seg['carrierCode']}: {seg['departure']['iataCode']} → {seg['arrival']['iataCode']} | {seg['departure']['at']} → {seg['arrival']['at']}")
            print(f"💰 Price: €{option['price']:.2f}")
            print(f"🔗 Kayak Link: {generate_booking_link(origin, destination, departure_date, passengers_dict)}")

        elif option['type'] == 'multi_leg':
            multi_leg = option['flight']
            first = multi_leg['first_leg']
            second = multi_leg['second_leg']
            second_leg_departure_time_str = second['itineraries'][0]['segments'][0]['departure']['at']
            second_leg_departure_date = datetime.fromisoformat(second_leg_departure_time_str).strftime('%Y-%m-%d')

            print(f"Leg 1: {origin} → {stopover_city}")
            for seg in first['itineraries'][0]['segments']:
                print(f"  {seg['carrierCode']}: {seg['departure']['iataCode']} → {seg['arrival']['iataCode']} | {seg['departure']['at']} → {seg['arrival']['at']}")
            print(f"🔗 Kayak Link (Leg 1): {generate_booking_link(origin, stopover_city, departure_date, passengers_dict)}")

            print(f"Leg 2: {stopover_city} → {destination}")
            for seg in second['itineraries'][0]['segments']:
                print(f"  {seg['carrierCode']}: {seg['departure']['iataCode']} → {seg['arrival']['iataCode']} | {seg['departure']['at']} → {seg['arrival']['at']}")
            print(f"🔗 Kayak Link (Leg 2): {generate_booking_link(stopover_city, destination, second_leg_departure_date, passengers_dict)}")

            print(f"💰 Combined Price: €{option['price']:.2f}")

def get_multi_leg_options(origin, stopover, destination, departure_date, passengers_dict):
    multi_leg_options = []
    try:
        amadeus_args = build_amadeus_passenger_args(passengers_dict)

        first_leg_response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin,
            destinationLocationCode=stopover,
            departureDate=departure_date,
            currencyCode="EUR",
            max=5,
            **amadeus_args
        )
        first_leg_data = first_leg_response.data
    except ResponseError as e:
        print(f"Error fetching first leg flights: {e}")
        return multi_leg_options

    for first in first_leg_data:
        if not first.get('itineraries') or not first['itineraries'][0].get('segments'):
            continue

        first_arrival = first['itineraries'][0]['segments'][-1]['arrival']['at']
        first_arrival_time = datetime.fromisoformat(first_arrival)
        layover_min = first_arrival_time + timedelta(hours=2)
        layover_max = first_arrival_time + timedelta(hours=8)

        try:
            second_leg_response = amadeus.shopping.flight_offers_search.get(
                originLocationCode=stopover,
                destinationLocationCode=destination,
                departureDate=layover_min.strftime('%Y-%m-%d'),
                currencyCode="EUR",
                max=5,
                **amadeus_args
            )
            second_leg_data = second_leg_response.data
        except ResponseError as e:
            print(f"Error fetching second leg flights: {e}")
            continue

        for second in second_leg_data:
            if not second.get('itineraries') or not second['itineraries'][0].get('segments'):
                continue

            second_departure = second['itineraries'][0]['segments'][0]['departure']['at']
            second_departure_time = datetime.fromisoformat(second_departure)

            if layover_min <= second_departure_time <= layover_max:
                total_price = float(first['price']['total']) + float(second['price']['total'])
                multi_leg_options.append({
                    'first_leg': first,
                    'second_leg': second,
                    'total_price': total_price
                })

    return multi_leg_options

def get_passenger_input():
    def get_int(prompt, default=0):
        try:
            return int(input(prompt).strip() or str(default))
        except ValueError:
            return default

    return {
        'adults': get_int("Number of adults (default = 1): ", 1),
        'seniors': get_int("Number of seniors (default = 0): "),
        'students': get_int("Number of students (default = 0): "),
        'infants_lap': get_int("Infants on lap under 2 (L) (default = 0): "),
        'infants_seat': get_int("Children under 2 with seat (S) (default = 0): "),
        'children_11': get_int("Children under 11 (default = 0): "),
        'children_17': get_int("Children under 17 (default = 0): ")
    }

if __name__ == "__main__":
    print("""
                                                                                                                                                                                                                          
8 8888888888   8 8888          8 8888     ,o888888o.    8 8888        8 8888888 8888888888           d888888o.       ,o888888o.    8 888888888o.            .8.          8 888888888o   8 8888888888   8 888888888o.   
8 8888         8 8888          8 8888    8888     `88.  8 8888        8       8 8888               .`8888:' `88.    8888     `88.  8 8888    `88.          .888.         8 8888    `88. 8 8888         8 8888    `88.  
8 8888         8 8888          8 8888 ,8 8888       `8. 8 8888        8       8 8888               8.`8888.   Y8 ,8 8888       `8. 8 8888     `88         :88888.        8 8888     `88 8 8888         8 8888     `88  
8 8888         8 8888          8 8888 88 8888           8 8888        8       8 8888               `8.`8888.     88 8888           8 8888     ,88        . `88888.       8 8888     ,88 8 8888         8 8888     ,88  
8 888888888888 8 8888          8 8888 88 8888           8 8888        8       8 8888                `8.`8888.    88 8888           8 8888.   ,88'       .8. `88888.      8 8888.   ,88' 8 888888888888 8 8888.   ,88'  
8 8888         8 8888          8 8888 88 8888           8 8888        8       8 8888                 `8.`8888.   88 8888           8 888888888P'       .8`8. `88888.     8 888888888P'  8 8888         8 888888888P'   
8 8888         8 8888          8 8888 88 8888   8888888 8 8888888888888       8 8888                  `8.`8888.  88 8888           8 8888`8b          .8' `8. `88888.    8 8888         8 8888         8 8888`8b       
8 8888         8 8888          8 8888 `8 8888       .8' 8 8888        8       8 8888              8b   `8.`8888. `8 8888       .8' 8 8888 `8b.       .8'   `8. `88888.   8 8888         8 8888         8 8888 `8b.     
8 8888         8 8888          8 8888    8888     ,88'  8 8888        8       8 8888              `8b.  ;8.`8888    8888     ,88'  8 8888   `8b.    .888888888. `88888.  8 8888         8 8888         8 8888   `8b.   
8 8888         8 888888888888  8 8888     `8888888P'    8 8888        8       8 8888               `Y8888P ,88P'     `8888888P'    8 8888     `88. .8'       `8. `88888. 8 8888         8 888888888888 8 8888     `88.
""")


    print("\n🔍 A flight search tool giving best routes and days with the amadeus api and gives Kayak Links")
    print("\n Created by the one and only tortupouce")

    origin = input("Enter origin airport code (e.g., JFK): ").strip().upper()
    destination = input("Enter destination airport code (e.g., ATH): ").strip().upper()

    date_range_choice = input("Search single date or date range? (S/R): ").strip().upper()
    if date_range_choice == "R":
        start_date = input("Enter start departure date (YYYY-MM-DD): ").strip()
        end_date = input("Enter end departure date (YYYY-MM-DD): ").strip()
    else:
        start_date = input("Enter departure date (YYYY-MM-DD): ").strip()
        end_date = start_date

    stopover = input("Enter desired stopover airport code (optional, e.g., LHR): ").strip().upper() or None
    passengers_dict = get_passenger_input()

    if start_date == end_date:
        options = search_flights_return(origin, destination, start_date, passengers_dict, stopover_city=stopover)
        print_flight_options(options, origin, destination, start_date, passengers_dict, stopover)
    else:
        current_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_dt = datetime.strptime(end_date, "%Y-%m-%d")
        all_results = []

        while current_date <= end_date_dt:
            date_str = current_date.strftime("%Y-%m-%d")
            print(f"\n🔎 Searching flights for {date_str}...")
            results = search_flights_return(origin, destination, date_str, passengers_dict, stopover_city=stopover)
            for res in results:
                res['search_date'] = date_str
            all_results.extend(results)
            current_date += timedelta(days=1)

        all_results.sort(key=lambda x: x['price'])
        for idx, option in enumerate(all_results, start=1):
            print(f"\n=== Option {idx} | Search Date: {option['search_date']} ===")
            print_flight_options([option], origin, destination, option['search_date'], passengers_dict, stopover)
