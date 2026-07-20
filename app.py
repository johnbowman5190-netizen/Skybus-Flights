import streamlit as st
from datetime import datetime, timedelta
import random

# Page config
st.set_page_config(
    page_title="SkyFly Flight Search & Seat Selection",
    page_icon="✈️",
    layout="wide"
)

# -----------------------------------------------------------------------------
# MOBILE-FRIENDLY CSS STYLING
# -----------------------------------------------------------------------------
st.markdown("""
    <style>
    /* Responsive column behavior on mobile viewports */
    div[data-testid="stColumn"] {
        min-width: 0px !important;
    }
    
    /* Touch-friendly seat map buttons on mobile */
    div[data-testid="stHorizontalBlock"] button {
        padding: 4px 2px !important;
        font-size: 11px !important;
        min-height: 34px !important;
        margin: 0px !important;
    }
    
    .flight-card {
        background-color: #f8f9fa;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 1. YOUR RESTORED CUSTOM ROUTE NETWORK & FLEET DATA
# -----------------------------------------------------------------------------

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
    """Formats total minutes into 'Xh Ym'."""
    h = minutes // 60
    m = minutes % 60
    if h == 0:
        return f"{m}m"
    elif m == 0:
        return f"{h}h"
    return f"{h}h {m}m"

def get_row_list(total_rows: int) -> list:
    """Generates row list, skipping Row 13."""
    rows = []
    curr = 1
    while len(rows) < total_rows:
        if curr != 13:
            rows.append(curr)
        curr += 1
    return rows

def calculate_leg_price(duration_mins: int, dest: str) -> int:
    """Calculates realistic USD base pricing."""
    is_intl = dest in ["RJAA", "RKSI", "EGKK", "TJBQ"]
    base_fare = 55.0
    rate_per_min = 0.72 if is_intl else 0.52
    return round(base_fare + (duration_mins * rate_per_min))

def calculate_itinerary_price(itin: list) -> int:
    """Calculates total itinerary price with connection discount."""
    total = sum(calculate_leg_price(leg["Duration"], leg["Destination"]) for leg in itin)
    if len(itin) > 1:
        total *= 0.88  # 12% multi-leg discount
    return round(total)

def assign_aircraft(flight_num: str, duration_mins: int) -> dict:
    """Deterministically assigns aircraft and tail number based on route."""
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

def generate_occupied_seats(flight_num: str, total_seats: int, total_rows: int) -> tuple[list, set, list]:
    """Generates deterministic occupied seat map skipping row 13."""
    rng = random.Random(hash(flight_num) + 99)
    num_occupied = rng.randint(int(total_seats * 0.45), int(total_seats * 0.70))
    
    rows = get_row_list(total_rows)
    all_seats = []
    for r in rows:
        for letter in ['A', 'B', 'C', 'D', 'E', 'F']:
            seat_code = f"{r}{letter}"
            all_seats.append(seat_code)
            if len(all_seats) == total_seats:
                break
        if len(all_seats) == total_seats:
            break
            
    occupied = set(rng.sample(all_seats, num_occupied))
    return all_seats, occupied, rows

def get_seat_amenities(seat_code: str):
    """Returns seat amenities and position specs."""
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
    
    # Exit rows are row 12 and row 14 (since row 13 is omitted)
    is_exit = row in [12, 14]
    legroom = 'Extra Legroom (Exit Row - 34" Pitch)' if is_exit else 'Standard Economy (30" Pitch)'
    recline = 'None (Pre-Exit Row)' if row == 11 else ('Full Recline (Exit Row)' if is_exit else 'Standard 3-inch Recline')
    
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
# 3. ROUTE SEARCH ENGINE
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
                layover_mins = (flight["DepTime"] - curr_time).total_seconds() / 60.0
                if layover_mins < 0:
                    layover_mins += 24 * 60
                    
                layover_hrs = layover_mins / 60.0
                if 0.75 <= layover_hrs <= max_layover_hours:
                    queue.append((flight["Destination"], flight["ArrTime"], path + [flight]))
                    
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
# 4. SESSION STATE
# -----------------------------------------------------------------------------
if "selected_itinerary" not in st.session_state:
    st.session_state.selected_itinerary = None
if "selected_seats" not in st.session_state:
    st.session_state.selected_seats = {}

# -----------------------------------------------------------------------------
# 5. VIEW 1: SEARCH & SELECTION (RESTORED CUSTOM NETWORK)
# -----------------------------------------------------------------------------
if not st.session_state.selected_itinerary:
    st.title("✈️ SkyFly Route Search")
    
    catalog = get_flight_catalog()
    all_airports = sorted(list(set([f["Origin"] for f in catalog] + [f["Destination"] for f in catalog])))
    
    c_orig, c_dest = st.columns(2)
    with c_orig:
        origin = st.selectbox("From (Origin)", options=all_airports, index=all_airports.index("KSFB") if "KSFB" in all_airports else 0)
    with c_dest:
        dest_options = [a for a in all_airports if a != origin]
        destination = st.selectbox("To (Destination)", options=dest_options, index=dest_options.index("KBGR") if "KBGR" in dest_options else 0)
        
    c_conn, c_layover = st.columns(2)
    with c_conn:
        max_conn = st.selectbox("Max Connections", options=[0, 1, 2], index=1)
    with c_layover:
        max_layover = st.slider("Max Layover (Hrs)", 1.0, 10.0, 6.0, step=0.5)
        
    st.divider()
    
    itineraries = search_flights(origin, destination, max_connections=max_conn, max_layover_hours=max_layover)
    st.markdown(f"**Found {len(itineraries)} itinerary option(s) for `{origin}` ➔ `{destination}`**")
    
    if not itineraries:
        st.warning("No direct or connecting routes found for this pair with current filters. Try increasing max connections or layover duration.")
    else:
        for idx, itin in enumerate(itineraries):
            total_price = calculate_itinerary_price(itin)
            total_flight_mins = sum(leg["Duration"] for leg in itin)
            formatted_total_dur = format_duration(total_flight_mins)
            num_stops = len(itin) - 1
            stops_label = "Non-stop" if num_stops == 0 else f"{num_stops} Stop"
            
            first_leg = itin[0]
            last_leg = itin[-1]
            
            with st.container(border=True):
                col_main, col_action = st.columns([3, 1])
                
                with col_main:
                    st.markdown(f"### {first_leg['DepStr']} → {last_leg['ArrStr']}")
                    st.caption(f"**Route:** {' ➔ '.join([l['Origin'] for l in itin] + [last_leg['Destination']])}")
                    st.markdown(f"⏱️ **Duration:** {formatted_total_dur} ({stops_label}) &nbsp;|&nbsp; 🛩️ **Aircraft:** {first_leg['Aircraft']['model']}")
                    
                with col_action:
                    st.markdown(f"### ${total_price} USD")
                    if st.button("Select Flight", key=f"select_itin_{idx}", type="primary", use_container_width=True):
                        st.session_state.selected_itinerary = {
                            "legs": itin,
                            "price": total_price,
                            "total_mins": total_flight_mins,
                            "formatted_duration": formatted_total_dur
                        }
                        st.rerun()
                
                with st.expander("Show Flight Breakdown"):
                    for l_idx, leg in enumerate(itin):
                        ac = leg["Aircraft"]
                        st.write(
                            f"**Leg {l_idx+1}: {leg['FlightNum']}** (`{leg['Origin']}` ➔ `{leg['Destination']}`) | "
                            f"🕒 {leg['DepStr']}-{leg['ArrStr']} ({format_duration(leg['Duration'])}) | "
                            f"Tail: `{ac['tail']}` ({ac['model']}) | Fare: **${calculate_leg_price(leg['Duration'], leg['Destination'])} USD**"
                        )

# -----------------------------------------------------------------------------
# 6. VIEW 2: POST-SELECTION & SEAT MAP (NO ROW 13)
# -----------------------------------------------------------------------------
else:
    itin_data = st.session_state.selected_itinerary
    legs = itin_data["legs"]
    
    if st.button("⬅️ Back to Search"):
        st.session_state.selected_itinerary = None
        st.session_state.selected_seats = {}
        st.rerun()
            
    st.title("💺 Seat Selection & Aircraft Details")
    st.success(
        f"Trip: **{legs[0]['Origin']} ➔ {legs[-1]['Destination']}** | "
        f"Total Price: **${itin_data['price']} USD** | Duration: **{itin_data['formatted_duration']}**"
    )
    st.divider()
    
    for idx, leg in enumerate(legs):
        flt_id = leg["FlightID"]
        ac = leg["Aircraft"]
        leg_dur_str = format_duration(leg["Duration"])
        
        st.markdown(f"### Leg {idx+1}: {leg['Origin']} ✈️ {leg['Destination']} ({leg['FlightNum']})")
        st.caption(f"Aircraft: **{ac['model']}** | Tail: `{ac['tail']}` | Capacity: **{ac['seats']} Seats** (3x3 Layout, No Row 13) | Duration: **{leg_dur_str}**")
        
        all_seats, occupied_seats, row_list = generate_occupied_seats(flt_id, ac["seats"], ac["rows"])
        current_seat = st.session_state.selected_seats.get(flt_id)
        
        col_info, col_map = st.columns([1, 1])
        
        with col_info:
            st.markdown("#### Seat Inspector")
            available_seats = [s for s in all_seats if s not in occupied_seats]
            
            dropdown_sel = st.selectbox(
                f"Choose Seat ({leg['FlightNum']}):",
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
                    st.markdown(f"### Seat {amenities['seat']}")
                    st.write(f"• **Position:** {amenities['position']}")
                    st.write(f"• **Legroom:** {amenities['legroom']}")
                    st.write(f"• **Recline:** {amenities['recline']}")
                    st.write(f"• ⚡ **Power:** {amenities['power']}")
                    st.write(f"• 📶 **Wi-Fi:** {amenities['wifi']}")
            else:
                st.info("Tap a seat on the map or select from the dropdown to inspect amenities.")
                
        with col_map:
            st.markdown("#### Interactive Seat Map")
            st.caption("🔴 Occupied &nbsp;&nbsp; 🟩 Selected &nbsp;&nbsp; ⬜ Available")
            
            with st.container(border=True, height=360):
                for r in row_list:
                    c1, c2, c3, c_aisle, c4, c5, c6 = st.columns([1, 1, 1, 0.6, 1, 1, 1])
                    letters = ['A', 'B', 'C', 'D', 'E', 'F']
                    cols = [c1, c2, c3, c4, c5, c6]
                    
                    for letter, col in zip(letters, cols):
                        code = f"{r}{letter}"
                        is_occ = code in occupied_seats
                        is_sel = code == current_seat
                        
                        btn_label = f"🔴" if is_occ else (f"🟩{code}" if is_sel else f"⬜{code}")
                        
                        if col.button(btn_label, key=f"map_{flt_id}_{code}", disabled=is_occ):
                            st.session_state.selected_seats[flt_id] = code
                            st.rerun()
                            
                    c_aisle.markdown(f"<p style='text-align: center; color: gray; font-size: 11px;'>{r}</p>", unsafe_allow_html=True)
                    
        st.divider()
        
    if st.button("Confirm Seat Selection & Book Ticket", type="primary", use_container_width=True):
        st.balloons()
        st.success(f"🎉 Success! Ticket booked for ${itin_data['price']} USD. All seats reserved!")
