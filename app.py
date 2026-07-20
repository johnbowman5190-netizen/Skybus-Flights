import streamlit as st
from datetime import datetime, timedelta
import random

# Set page config
st.set_page_config(
    page_title="SkyFly Flight Search & Seat Selection",
    page_icon="✈️",
    layout="wide"
)

# -----------------------------------------------------------------------------
# 1. ROUTE NETWORK & FLEET DATA CONFIGURATION
# -----------------------------------------------------------------------------

# Route Database: (Flight Number, Origin, Destination, Duration Mins, Frequency)
ROUTES_DATA = [
    # Inter-Base Trunk Network (100-299)
    (100, "KBGR", "KSFB", 185, "Daily"), (101, "KSFB", "KBGR", 185, "Daily"),
    (102, "KIWA", "KBLI", 195, "Daily"), (103, "KBLI", "KIWA", 195, "Daily"),
    (104, "TJBQ", "KSFB", 175, "Daily"), (105, "KSFB", "TJBQ", 175, "Daily"),
    (106, "PAFA", "KBLI", 210, "Daily"), (107, "KBLI", "PAFA", 210, "Daily"),
    (108, "KBGR", "TJBQ", 240, "Mon,Wed,Fri,Sun"), (109, "TJBQ", "KBGR", 240, "Mon,Wed,Fri,Sun"),
    (110, "KIWA", "PAFA", 330, "Mon,Tue,Thu,Sat"), (111, "PAFA", "KIWA", 330, "Mon,Tue,Thu,Sat"),
    (112, "KSFB", "KIWA", 270, "Daily"), (113, "KIWA", "KSFB", 270, "Daily"),
    (114, "KBGR", "KBLI", 310, "Daily"), (115, "KBLI", "KBGR", 310, "Daily"),
    (116, "KMSY", "KIWA", 180, "Daily"), (117, "KIWA", "KMSY", 180, "Daily"),
    
    # Secondary Trunk Network (200-299)
    (200, "KSFB", "KRIC", 110, "Daily"), (201, "KRIC", "KSFB", 110, "Daily"),
    (202, "KIWA", "KPVU", 85, "Daily"),  (203, "KPVU", "KIWA", 85, "Daily"),
    (204, "KGRR", "KSWF", 105, "Mon,Wed,Fri,Sun"), (205, "KSWF", "KGRR", 105, "Mon,Wed,Fri,Sun"),
    (206, "KMSY", "KOMA", 135, "Tue,Thu,Sat,Sun"), (207, "KOMA", "KMSY", 135, "Tue,Thu,Sat,Sun"),
    (208, "KSFB", "KMSY", 120, "Daily"), (209, "KMSY", "KSFB", 120, "Daily"),
    (210, "KBLI", "KPVU", 115, "Mon,Wed,Fri"),     (211, "KPVU", "KBLI", 115, "Mon,Wed,Fri"),
    
    # International Long-Haul Network (800-899)
    (856, "PAFA", "RJAA", 430, "Wed,Fri,Sun"),    (857, "RJAA", "PAFA", 430, "Wed,Fri,Sun"),
    (858, "PAFA", "RKSI", 460, "Tue,Thu,Sat"),    (859, "RKSI", "PAFA", 460, "Tue,Thu,Sat"),
    (860, "KBLI", "EGKK", 560, "Tue,Thu,Sat"),    (861, "EGKK", "KBLI", 560, "Tue,Thu,Sat"),
    
    # Regional Feeder Network (900-999)
    (900, "PAFA", "PANC", 55, "Daily"),  (901, "PANC", "PAFA", 55, "Daily"),
    (902, "PAFA", "PAYA", 80, "Daily"),  (903, "PAYA", "PAFA", 80, "Daily"),
    (904, "KSFB", "KEYW", 75, "Daily"),  (905, "KEYW", "KSFB", 75, "Daily")
]

DEP_WAVES = ["06:00", "10:30", "15:00", "19:30"]

AIRCRAFT_FLEET = {
    "A319": {
        "model": "Airbus A319",
        "seats": 150,
        "rows": 25,
        "tails": ["N800SB", "N801SB", "N802SB", "N803SB"]
    },
    "A320": {
        "model": "Airbus A320",
        "seats": 180,
        "rows": 30,
        "tails": ["N804SB", "N805SB", "N806SB", "N807SB"]
    },
    "A321": {
        "model": "Airbus A321",
        "seats": 220,
        "rows": 37,
        "tails": ["N808SB", "N809SB", "N810SB", "N811SB"]
    }
}

# -----------------------------------------------------------------------------
# 2. HELPER FUNCTIONS
# -----------------------------------------------------------------------------

def format_duration(minutes: int) -> str:
    """Format minutes into 'Xh Ym'."""
    h = minutes // 60
    m = minutes % 60
    if h == 0:
        return f"{m}m"
    elif m == 0:
        return f"{h}h"
    return f"{h}h {m}m"

def calculate_leg_price(duration_mins: int, dest: str) -> int:
    """Calculate realistic USD base pricing based on flight duration & route type."""
    is_intl = dest.startswith(("CY", "EG", "LF", "LI", "LE", "ED", "RJ", "RK", "MM", "MD", "TN", "MY", "MK", "MB", "MR", "MP", "SK", "TA", "TX"))
    base_fare = 55.0
    rate_per_min = 0.72 if is_intl else 0.52
    return round(base_fare + (duration_mins * rate_per_min))

def calculate_itinerary_price(itin: list) -> int:
    """Calculate total price for an itinerary with a connection discount if multi-leg."""
    total = sum(calculate_leg_price(leg["Duration"], leg["Destination"]) for leg in itin)
    if len(itin) > 1:
        total *= 0.88  # 12% multi-leg discount
    return round(total)

def assign_aircraft(flight_num: str, duration_mins: int) -> dict:
    """Deterministically assign aircraft & tail number based on duration & flight number."""
    rng = random.Random(hash(flight_num))
    if duration_mins >= 240:
        ac_key = "A321"
    elif duration_mins >= 120:
        ac_key = "A320"
    else:
        ac_key = rng.choice(["A319", "A320"])
    
    spec = AIRCRAFT_FLEET[ac_key]
    tail = rng.choice(spec["tails"])
    return {
        "type": ac_key,
        "model": spec["model"],
        "tail": tail,
        "seats": spec["seats"],
        "rows": spec["rows"]
    }

def generate_occupied_seats(flight_num: str, total_seats: int, rows: int) -> tuple[list, set]:
    """Generate deterministic occupied seat map."""
    rng = random.Random(hash(flight_num) + 99)
    num_occupied = rng.randint(int(total_seats * 0.45), int(total_seats * 0.70))
    
    all_seats = []
    for r in range(1, rows + 1):
        for letter in ['A', 'B', 'C', 'D', 'E', 'F']:
            seat_code = f"{r}{letter}"
            all_seats.append(seat_code)
            if len(all_seats) == total_seats:
                break
        if len(all_seats) == total_seats:
            break
            
    occupied = set(rng.sample(all_seats, num_occupied))
    return all_seats, occupied

def get_seat_amenities(seat_code: str):
    """Return amenities for a given seat position."""
    row = int(seat_code[:-1])
    letter = seat_code[-1]
    
    pos_map = {
        'A': 'Window (Left)', 'B': 'Middle (Left)', 'C': 'Aisle (Left)',
        'D': 'Aisle (Right)', 'E': 'Middle (Right)', 'F': 'Window (Right)'
    }
    
    power_map = {
        'A': 'Shared Power Outlet (Between seats A & B)',
        'B': 'Shared Power Outlet (Between seats A & B)',
        'C': 'Shared Power Outlet (Between seats B & C)',
        'D': 'Shared Power Outlet (Between seats D & E)',
        'E': 'Shared Power Outlet (Between seats D & E)',
        'F': 'Shared Power Outlet (Between seats E & F)'
    }
    
    is_exit = row in [12, 13]
    legroom = 'Extra Legroom (Exit Row - 34" Pitch)' if is_exit else 'Standard Economy (30" Pitch)'
    recline = 'None (Exit Row)' if row == 12 else 'Standard 3-inch Recline'
    
    return {
        'seat': seat_code,
        'row': row,
        'position': pos_map.get(letter, 'Standard'),
        'power': power_map.get(letter, 'Shared Power Port'),
        'wifi': 'High-Speed SkyFly In-Flight Wi-Fi Available',
        'legroom': legroom,
        'recline': recline
    }

# -----------------------------------------------------------------------------
# 3. CATALOG & ROUTE SEARCH ENGINE (BFS)
# -----------------------------------------------------------------------------

@st.cache_data
def get_flight_catalog():
    catalog = []
    for num, orig, dest, dur, freq in ROUTES_DATA:
        for wave in DEP_WAVES:
            flt_id = f"SF{num}-{wave.replace(':', '')}"
            dep_time = datetime.strptime(wave, "%H:%M")
            arr_time = dep_time + timedelta(minutes=dur)
            
            catalog.append({
                "FlightNum": f"SF{num}",
                "FlightID": flt_id,
                "Origin": orig,
                "Destination": dest,
                "Duration": dur,
                "DepTime": dep_time,
                "ArrTime": arr_time,
                "DepStr": wave,
                "ArrStr": arr_time.strftime("%H:%M"),
                "Frequency": freq,
                "Aircraft": assign_aircraft(flt_id, dur)
            })
    return catalog

def search_flights(origin, destination, max_connections=2, max_layover_hours=6.0):
    catalog = get_flight_catalog()
    results = []
    
    # BFS Queue: (current_airport, current_time, leg_list)
    queue = []
    
    for flight in catalog:
        if flight["Origin"] == origin:
            queue.append((flight["Destination"], flight["ArrTime"], [flight]))
            
    while queue:
        curr_apt, curr_time, path = queue.pop(0)
        
        if curr_apt == destination:
            results.append(path)
            continue
            
        if len(path) > max_connections:
            continue
            
        for flight in catalog:
            if flight["Origin"] == curr_apt:
                # Calculate layover time
                layover_mins = (flight["DepTime"] - curr_time).total_seconds() / 60.0
                if layover_mins < 0:
                    layover_mins += 24 * 60  # next day departure
                    
                layover_hrs = layover_mins / 60.0
                if 0.75 <= layover_hrs <= max_layover_hours:  # min 45m connection
                    queue.append((flight["Destination"], flight["ArrTime"], path + [flight]))
                    
    # Sort results by total flight duration + layover time
    def total_journey_time(p):
        flight_dur = sum(leg["Duration"] for leg in p)
        layovers = 0
        for i in range(len(p) - 1):
            gap = (p[i+1]["DepTime"] - p[i]["ArrTime"]).total_seconds() / 60.0
            if gap < 0:
                gap += 24 * 60
            layovers += gap
        return flight_dur + layovers
        
    results.sort(key=total_journey_time)
    return results

# -----------------------------------------------------------------------------
# 4. SESSION STATE MANAGEMENT
# -----------------------------------------------------------------------------
if "selected_itinerary" not in st.session_state:
    st.session_state.selected_itinerary = None
if "selected_seats" not in st.session_state:
    st.session_state.selected_seats = {}

# -----------------------------------------------------------------------------
# 5. VIEW 1: FLIGHT SEARCH & SELECTION (ORIGIN & DESTINATION RESTORED)
# -----------------------------------------------------------------------------
if not st.session_state.selected_itinerary:
    st.title("✈️ SkyFly Network Flight Search")
    st.markdown("Search flights across our network and choose your route.")
    
    catalog = get_flight_catalog()
    all_airports = sorted(list(set([f["Origin"] for f in catalog] + [f["Destination"] for f in catalog])))
    
    # Restored Origin & Destination Selection
    col_orig, col_dest, col_conn, col_layover = st.columns([2, 2, 2, 2])
    
    with col_orig:
        origin = st.selectbox("From (Origin)", options=all_airports, index=all_airports.index("KSFB") if "KSFB" in all_airports else 0)
        
    with col_dest:
        dest_options = [a for a in all_airports if a != origin]
        destination = st.selectbox("To (Destination)", options=dest_options, index=dest_options.index("KBGR") if "KBGR" in dest_options else 0)
        
    with col_conn:
        max_conn = st.selectbox("Max Connections", options=[0, 1, 2], index=1)
        
    with col_layover:
        max_layover = st.slider("Max Layover (Hours)", 1.0, 10.0, 6.0, step=0.5)
        
    st.divider()
    
    # Perform Search
    itineraries = search_flights(origin, destination, max_connections=max_conn, max_layover_hours=max_layover)
    
    st.subheader(f"Available Flights from {origin} to {destination}")
    st.caption(f"Found {len(itineraries)} itinerary option(s)")
    
    if not itineraries:
        st.warning("No flights available for this route with the selected filter parameters. Try increasing max connections or layover duration.")
    else:
        for idx, itin in enumerate(itineraries):
            total_price = calculate_itinerary_price(itin)
            total_flight_mins = sum(leg["Duration"] for leg in itin)
            formatted_total_dur = format_duration(total_flight_mins)
            num_stops = len(itin) - 1
            stops_label = "Non-stop" if num_stops == 0 else f"{num_stops} Stop{'s' if num_stops > 1 else ''}"
            
            first_leg = itin[0]
            last_leg = itin[-1]
            
            with st.container(border=True):
                c1, c2, c3, c4, c5 = st.columns([2.5, 2, 2, 1.8, 2])
                
                with c1:
                    st.markdown(f"### {first_leg['DepStr']} → {last_leg['ArrStr']}")
                    st.caption(f"Route: {' ➔ '.join([l['Origin'] for l in itin] + [last_leg['Destination']])}")
                    
                with c2:
                    st.markdown(f"**⏱️ Total Duration:** {formatted_total_dur}")
                    st.caption(stops_label)
                    
                with c3:
                    st.markdown(f"**🛩️ Aircraft:** {first_leg['Aircraft']['model']}")
                    st.caption(f"Tail `{first_leg['Aircraft']['tail']}`")
                    
                with c4:
                    st.markdown(f"### ${total_price} USD")
                    st.caption("Economy Class")
                    
                with c5:
                    st.write("")
                    if st.button("Select Flight", key=f"select_itin_{idx}", type="primary"):
                        st.session_state.selected_itinerary = {
                            "legs": itin,
                            "price": total_price,
                            "total_mins": total_flight_mins,
                            "formatted_duration": formatted_total_dur
                        }
                        st.rerun()
                
                # Expandable Leg Details
                with st.expander("Show Flight Leg Breakdown"):
                    for l_idx, leg in enumerate(itin):
                        ac = leg["Aircraft"]
                        st.markdown(
                            f"**Leg {l_idx+1}: {leg['FlightNum']}** (`{leg['Origin']}` ✈️ `{leg['Destination']}`) &nbsp;|&nbsp; "
                            f"🕒 {leg['DepStr']} - {leg['ArrStr']} (**{format_duration(leg['Duration'])}**) &nbsp;|&nbsp; "
                            f"🛩️ **{ac['model']}** (Tail: `{ac['tail']}` - {ac['seats']} Seats) &nbsp;|&nbsp; "
                            f"💲 Leg Fare: **${calculate_leg_price(leg['Duration'], leg['Destination'])} USD**"
                        )

# -----------------------------------------------------------------------------
# 6. VIEW 2: POST-SELECTION AIRCRAFT & INTERACTIVE SEAT MAP
# -----------------------------------------------------------------------------
else:
    itin_data = st.session_state.selected_itinerary
    legs = itin_data["legs"]
    
    col_back, col_title = st.columns([1, 5])
    with col_back:
        if st.button("⬅️ Back to Search"):
            st.session_state.selected_itinerary = None
            st.session_state.selected_seats = {}
            st.rerun()
            
    st.title("💺 Seat Selection & Aircraft Details")
    st.success(
        f"Selected Itinerary: **{legs[0]['Origin']} ✈️ {legs[-1]['Destination']}** &nbsp;|&nbsp; "
        f"Total Price: **${itin_data['price']} USD** &nbsp;|&nbsp; "
        f"Total Flight Time: **{itin_data['formatted_duration']}**"
    )
    st.divider()
    
    for idx, leg in enumerate(legs):
        flt_id = leg["FlightID"]
        ac = leg["Aircraft"]
        leg_price = calculate_leg_price(leg["Duration"], leg["Destination"])
        leg_dur_str = format_duration(leg["Duration"])
        
        st.markdown(f"### Leg {idx+1}: {leg['Origin']} ✈️ {leg['Destination']} ({leg['FlightNum']})")
        
        # Aircraft Info Header
        st.markdown(
            f"> 🛩️ **Aircraft Assigned:** {ac['model']} &nbsp;|&nbsp; "
            f"🏷️ **Tail Number:** `{ac['tail']}` &nbsp;|&nbsp; "
            f"💺 **Capacity:** {ac['seats']} Seats (3x3 Economy) &nbsp;|&nbsp; "
            f"⏱️ **Duration:** {leg_dur_str} &nbsp;|&nbsp; "
            f"💵 **Leg Price:** ${leg_price} USD"
        )
        
        all_seats, occupied_seats = generate_occupied_seats(flt_id, ac["seats"], ac["rows"])
        current_seat = st.session_state.selected_seats.get(flt_id)
        
        col_map, col_info = st.columns([3, 2])
        
        with col_info:
            st.markdown("#### 💺 Seat Inspector & Amenities")
            
            available_seats = [s for s in all_seats if s not in occupied_seats]
            
            dropdown_sel = st.selectbox(
                f"Select seat for {leg['FlightNum']} ({leg['Origin']}➔{leg['Destination']}):",
                options=["None Selected"] + available_seats,
                index=0 if not current_seat or current_seat not in available_seats else available_seats.index(current_seat) + 1,
                key=f"drop_{flt_id}"
            )
            
            if dropdown_sel != "None Selected":
                st.session_state.selected_seats[flt_id] = dropdown_sel
                current_seat = dropdown_sel
                
            if current_seat:
                amenities = get_seat_amenities(current_seat)
                with st.container(border=True):
                    st.markdown(f"### Selected Seat: {amenities['seat']}")
                    st.markdown(f"* **Position:** `{amenities['position']}`")
                    st.markdown(f"* **Legroom:** {amenities['legroom']}")
                    st.markdown(f"* **Recline:** {amenities['recline']}")
                    st.markdown(f"* **⚡ Power Outlet:** {amenities['power']}")
                    st.markdown(f"* **📶 Wi-Fi:** {amenities['wifi']}")
                    st.markdown("* **🧳 Storage:** Overhead bin space & under-seat storage included")
            else:
                st.info("Click a seat in the map or choose from the dropdown to view amenities.")
                
        with col_map:
            st.markdown("#### 🗺️ Interactive Seat Map (3x3)")
            st.caption("🔴 Occupied &nbsp;&nbsp; 🟩 Selected &nbsp;&nbsp; ⬜ Available")
            
            with st.container(border=True, height=360):
                for r in range(1, ac["rows"] + 1):
                    c1, c2, c3, c_aisle, c4, c5, c6 = st.columns([1, 1, 1, 0.6, 1, 1, 1])
                    letters = ['A', 'B', 'C', 'D', 'E', 'F']
                    cols = [c1, c2, c3, c4, c5, c6]
                    
                    for letter, col in zip(letters, cols):
                        code = f"{r}{letter}"
                        is_occ = code in occupied_seats
                        is_sel = code == current_seat
                        
                        btn_label = f"🔴 {code}" if is_occ else (f"🟩 {code}" if is_sel else f"⬜ {code}")
                        
                        if col.button(btn_label, key=f"map_{flt_id}_{code}", disabled=is_occ):
                            st.session_state.selected_seats[flt_id] = code
                            st.rerun()
                            
                    c_aisle.markdown(f"<p style='text-align: center; color: gray; font-size: 12px;'>{r}</p>", unsafe_allow_html=True)
                    
        st.divider()
        
    if st.button("Confirm Seat Selection & Book Ticket", type="primary", use_container_width=True):
        st.balloons()
        st.success(f"🎉 Success! Ticket booked for ${itin_data['price']} USD. All seats reserved!")
