import streamlit as st
import pandas as pd
import random
from datetime import datetime, time

# Set page config
st.set_page_config(
    page_title="SkyFly Flight Search & Booking",
    page_icon="✈️",
    layout="wide"
)

# -----------------------------------------------------------------------------
# 1. FLEET & AMENITIES DATA CONFIGURATION
# -----------------------------------------------------------------------------
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

# Helper: Format total minutes to "Xh Ym"
def format_duration(minutes: int) -> str:
    h = minutes // 60
    m = minutes % 60
    if h == 0:
        return f"{m}m"
    elif m == 0:
        return f"{h}h"
    return f"{h}h {m}m"

# Helper: Assign an aircraft type and tail number deterministically based on flight number
def assign_aircraft(flight_num: str, duration_mins: int) -> dict:
    rng = random.Random(hash(flight_num))
    if duration_mins >= 240:
        ac_key = "A321"
    elif duration_mins >= 150:
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

# Helper: Generate pre-occupied seats for a leg
def generate_occupied_seats(flight_num: str, total_seats: int, rows: int) -> tuple[list, set]:
    rng = random.Random(hash(flight_num) + 42)
    # 45% to 70% of seats randomly pre-booked
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

# Helper: Seat amenities lookup
def get_seat_amenities(seat_code: str):
    row = int(seat_code[:-1])
    letter = seat_code[-1]
    
    pos_map = {
        'A': 'Window (Left)', 'B': 'Middle (Left)', 'C': 'Aisle (Left)',
        'D': 'Aisle (Right)', 'E': 'Middle (Right)', 'F': 'Window (Right)'
    }
    
    power_map = {
        'A': 'Shared AC Power Outlet (Between seats A & B)',
        'B': 'Shared AC Power Outlet (Between seats A & B)',
        'C': 'Shared AC Power Outlet (Between seats B & C)',
        'D': 'Shared AC Power Outlet (Between seats D & E)',
        'E': 'Shared AC Power Outlet (Between seats D & E)',
        'F': 'Shared AC Power Outlet (Between seats E & F)'
    }
    
    is_exit_row = row in [12, 13]
    legroom = 'Extra Legroom (Exit Row - 34" Pitch)' if is_exit_row else 'Standard Economy (30" Pitch)'
    recline = 'None (Exit Row)' if row == 12 else 'Standard 3-inch Recline'
    
    return {
        'seat': seat_code,
        'row': row,
        'letter': letter,
        'position': pos_map.get(letter, 'Standard'),
        'power': power_map.get(letter, 'Shared Power Port'),
        'wifi': 'High-Speed SkyFly In-Flight Wi-Fi Available',
        'legroom': legroom,
        'recline': recline
    }

# -----------------------------------------------------------------------------
# 2. MOCK DATA GENERATION
# -----------------------------------------------------------------------------
@st.cache_data
def load_mock_flights():
    data = [
        {
            "id": "FL-101",
            "airline": "SkyFly Express",
            "price": 280,
            "total_mins": 195,
            "stops": 0,
            "legs": [
                {"flight": "SF101", "origin": "JFK", "dest": "ORD", "dep": "08:00", "arr": "11:15", "mins": 195}
            ]
        },
        {
            "id": "FL-102",
            "airline": "SkyFly Connect",
            "price": 340,
            "total_mins": 330,
            "stops": 1,
            "legs": [
                {"flight": "SF204", "origin": "JFK", "dest": "CLT", "dep": "07:30", "arr": "09:45", "mins": 135},
                {"flight": "SF509", "origin": "CLT", "dest": "ORD", "dep": "11:00", "arr": "13:15", "mins": 135}
            ]
        },
        {
            "id": "FL-103",
            "airline": "SkyFly Direct",
            "price": 410,
            "total_mins": 360,
            "stops": 0,
            "legs": [
                {"flight": "SF880", "origin": "JFK", "dest": "LAX", "dep": "09:15", "arr": "12:15", "mins": 360}
            ]
        },
        {
            "id": "FL-104",
            "airline": "SkyFly Connect",
            "price": 390,
            "total_mins": 465,
            "stops": 1,
            "legs": [
                {"flight": "SF312", "origin": "JFK", "dest": "DFW", "dep": "10:00", "arr": "13:15", "mins": 255},
                {"flight": "SF418", "origin": "DFW", "dest": "LAX", "dep": "15:00", "arr": "16:30", "mins": 150}
            ]
        }
    ]
    
    # Attach aircraft assignments & formatted durations to legs
    for item in data:
        item["formatted_duration"] = format_duration(item["total_mins"])
        for leg in item["legs"]:
            leg["formatted_duration"] = format_duration(leg["mins"])
            leg["aircraft"] = assign_aircraft(leg["flight"], leg["mins"])
            
    return data

flights = load_mock_flights()

# -----------------------------------------------------------------------------
# 3. SESSION STATE MANAGEMENT
# -----------------------------------------------------------------------------
if "selected_flight" not in st.session_state:
    st.session_state.selected_flight = None
if "selected_seats" not in st.session_state:
    st.session_state.selected_seats = {}  # {leg_flight_num: seat_code}

# -----------------------------------------------------------------------------
# 4. HEADER & TOP NAVIGATION
# -----------------------------------------------------------------------------
st.title("✈️ SkyFly Air Travel")

if st.session_state.selected_flight:
    # Top bar back button when a flight has been selected
    col_nav1, col_nav2 = st.columns([1, 5])
    with col_nav1:
        if st.button("⬅️ Back to Search"):
            st.session_state.selected_flight = None
            st.rerun()

# -----------------------------------------------------------------------------
# 5. VIEW 1: FLIGHT SEARCH RESULTS (If no flight selected)
# -----------------------------------------------------------------------------
if not st.session_state.selected_flight:
    st.subheader("Search & Select Flights")
    
    # Sidebar Filters
    st.sidebar.header("Filter Results")
    max_price = st.sidebar.slider("Max Price ($)", 200, 600, 600)
    stops_filter = st.sidebar.multiselect("Stops", options=[0, 1], default=[0, 1])
    
    filtered_flights = [
        f for f in flights 
        if f["price"] <= max_price and f["stops"] in stops_filter
    ]
    
    st.markdown(f"**Showing {len(filtered_flights)} flights**")
    
    for fl in filtered_flights:
        with st.container(border=True):
            col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 2])
            
            first_leg = fl["legs"][0]
            last_leg = fl["legs"][-1]
            
            with col1:
                st.markdown(f"### {fl['airline']}")
                st.caption(f"{len(fl['legs'])} Leg(s)")
            
            with col2:
                st.markdown(f"**{first_leg['dep']} → {last_leg['arr']}**")
                st.caption(f"{first_leg['origin']} to {last_leg['dest']}")
            
            with col3:
                st.markdown(f"**⏱️ {fl['formatted_duration']}**")
                st.caption("Non-stop" if fl["stops"] == 0 else f"{fl['stops']} Stop")
            
            with col4:
                st.markdown(f"### ${fl['price']}")
                st.caption("Economy")
            
            with col5:
                st.write("")
                if st.button("Select Flight", key=f"btn_{fl['id']}", type="primary"):
                    st.session_state.selected_flight = fl
                    st.rerun()
            
            # Leg details expander
            with st.expander("Flight Details & Assigned Aircraft"):
                for idx, leg in enumerate(fl["legs"]):
                    ac = leg["aircraft"]
                    st.markdown(
                        f"**Leg {idx+1}: {leg['flight']}** ({leg['origin']} → {leg['dest']}) | "
                        f"🕒 {leg['dep']} - {leg['arr']} ({leg['formatted_duration']}) | "
                        f"🛩️ **{ac['model']}** (`{ac['tail']}` - {ac['seats']} seats)"
                    )

# -----------------------------------------------------------------------------
# 6. VIEW 2: POST-SELECTION & INTERACTIVE SEAT MAP
# -----------------------------------------------------------------------------
else:
    flight = st.session_state.selected_flight
    
    st.success(f"Flight Selected! Total Price: **${flight['price']}** | Total Duration: **{flight['formatted_duration']}**")
    st.divider()
    
    st.subheader("Seat Selection & Aircraft Overview")
    st.info("Select a seat for each leg of your trip to view seat amenities, power port access, and Wi-Fi features.")
    
    for idx, leg in enumerate(flight["legs"]):
        flight_num = leg["flight"]
        ac = leg["aircraft"]
        
        st.markdown(f"### Leg {idx+1}: {leg['origin']} ✈️ {leg['dest']} ({flight_num})")
        
        # Aircraft badge summary
        st.markdown(
            f"> 🛩️ **Aircraft Assigned:** {ac['model']} &nbsp;|&nbsp; "
            f"🏷️ **Tail Number:** `{ac['tail']}` &nbsp;|&nbsp; "
            f"💺 **Capacity:** {ac['seats']} Seats (3x3 All Economy) &nbsp;|&nbsp; "
            f"⏱️ **Duration:** {leg['formatted_duration']}"
        )
        
        # Generate seat data
        all_seats, occupied_seats = generate_occupied_seats(flight_num, ac["seats"], ac["rows"])
        
        col_map, col_info = st.columns([3, 2])
        
        # Current selected seat for this leg
        current_seat = st.session_state.selected_seats.get(flight_num)
        
        with col_info:
            st.markdown("#### 💺 Seat Details & Amenities")
            
            # Quick Seat Selector Dropdown
            available_seats = [s for s in all_seats if s not in occupied_seats]
            
            selected_from_dropdown = st.selectbox(
                f"Choose your seat for {flight_num}:",
                options=["None Selected"] + available_seats,
                index=0 if not current_seat or current_seat not in available_seats else available_seats.index(current_seat) + 1,
                key=f"select_{flight_num}"
            )
            
            if selected_from_dropdown != "None Selected":
                st.session_state.selected_seats[flight_num] = selected_from_dropdown
                current_seat = selected_from_dropdown
            
            if current_seat:
                amenities = get_seat_amenities(current_seat)
                
                # Interactive Amenity Card
                with st.container(border=True):
                    st.markdown(f"### Seat {amenities['seat']} Details")
                    st.markdown(f"* **Position:** `{amenities['position']}`")
                    st.markdown(f"* **Legroom:** {amenities['legroom']}")
                    st.markdown(f"* **Recline:** {amenities['recline']}")
                    st.markdown(f"* **⚡ Power Outlet:** {amenities['power']}")
                    st.markdown(f"* **📶 Wi-Fi:** {amenities['wifi']}")
                    st.markdown("* **🧳 Storage:** Shared overhead bin space & under-seat storage")
            else:
                st.warning("Please choose a seat from the selector or map to inspect amenities.")
                
        with col_map:
            st.markdown("#### 🗺️ Interactive Seat Layout (3x3)")
            st.caption("🟥 Occupied &nbsp;&nbsp; 🟩 Selected &nbsp;&nbsp; ⬜ Available")
            
            # Legend & Row visual generator (first 10 rows for display)
            with st.container(border=True, height=350):
                for r in range(1, ac["rows"] + 1):
                    c1, c2, c3, c_aisle, c4, c5, c6 = st.columns([1, 1, 1, 0.6, 1, 1, 1])
                    letters = ['A', 'B', 'C', 'D', 'E', 'F']
                    cols = [c1, c2, c3, c4, c5, c6]
                    
                    for letter, col in zip(letters, cols):
                        code = f"{r}{letter}"
                        is_occ = code in occupied_seats
                        is_sel = code == current_seat
                        
                        btn_label = f"🔴 {code}" if is_occ else (f"🟩 {code}" if is_sel else f"⬜ {code}")
                        
                        if col.button(btn_label, key=f"btn_{flight_num}_{code}", disabled=is_occ):
                            st.session_state.selected_seats[flight_num] = code
                            st.rerun()
                    
                    c_aisle.markdown(f"<p style='text-align: center; color: gray;'>{r}</p>", unsafe_allow_html=True)

        st.divider()

    if st.button("Confirm Booking & Continue", type="primary", use_container_width=True):
        st.balloons()
        st.success("🎉 Seats confirmed! Your flight has been booked successfully.")
