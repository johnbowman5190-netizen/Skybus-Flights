import streamlit as st
from datetime import datetime, timedelta
import random
import string

# Page Configuration
st.set_page_config(
    page_title="SkyFly Express - Search, Book & Boarding Pass",
    page_icon="✈️",
    layout="wide"
)

# -----------------------------------------------------------------------------
# MOBILE & BOARDING PASS STYLING
# -----------------------------------------------------------------------------
st.markdown("""
    <style>
    div[data-testid="stColumn"] {
        min-width: 0px !important;
    }
    div[data-testid="stHorizontalBlock"] button {
        padding: 4px 2px !important;
        font-size: 11px !important;
        min-height: 34px !important;
        margin: 0px !important;
    }
    .bp-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
        color: white;
        padding: 24px;
        border-radius: 16px 16px 0px 0px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
    }
    .bp-stub {
        background-color: #ffffff;
        color: #0f172a;
        padding: 20px;
        border-radius: 0px 0px 16px 16px;
        border-top: 2px dashed #94a3b8;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2);
    }
    .barcode-text {
        font-family: 'Courier New', Courier, monospace;
        letter-spacing: 4px;
        font-weight: bold;
        font-size: 22px;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 1. FULL ROUTE NETWORK DATA & FLEET SETUP
# -----------------------------------------------------------------------------

ROUTES_RAW = [
    # Inter-Base Trunk Network
    ("KSFB", "KBGR", 185), ("KSFB", "KIWA", 270), ("KSFB", "KMSY", 120), ("KSFB", "TJBQ", 175),
    ("KSFB", "KRIC", 110), ("KSFB", "KEYW", 75),  ("KSFB", "KGRR", 130), ("KSFB", "KSWF", 140),
    ("KSFB", "KBLI", 310), ("KSFB", "PAFA", 410),
    
    ("KBGR", "KSWF", 75),  ("KBGR", "TJBQ", 240), ("KBGR", "KBLI", 310), ("KBGR", "KRIC", 95),
    ("KBGR", "PAFA", 380), ("KBGR", "KIWA", 290),
    
    ("KIWA", "KBLI", 195), ("KIWA", "PAFA", 330), ("KIWA", "KPVU", 85),  ("KIWA", "KMSY", 180),
    ("KIWA", "KOMA", 140), ("KIWA", "KSFB", 270),
    
    ("KBLI", "PAFA", 210), ("KBLI", "KPVU", 115), ("KBLI", "EGKK", 560), ("KBLI", "KBGR", 310),
    ("KBLI", "RJAA", 520), ("KBLI", "RKSI", 550),
    
    ("PAFA", "PANC", 55),  ("PAFA", "PAYA", 80),  ("PAFA", "RJAA", 430), ("PAFA", "RKSI", 460),
    ("PAFA", "KIWA", 330), ("PAFA", "EGKK", 580),
    
    ("KMSY", "KOMA", 135), ("KMSY", "KRIC", 100), ("KMSY", "KSFB", 120), ("KMSY", "PAFA", 390),
    
    ("KSWF", "KGRR", 105), ("KSWF", "KRIC", 80),  ("KPVU", "KBLI", 115), ("KPVU", "KIWA", 85),
    ("PANC", "PAYA", 45),  ("TJBQ", "KSFB", 175), ("KEYW", "KSFB", 75),  ("KOMA", "KGRR", 90)
]

# Create Bidirectional Routes
ROUTES_DATA = []
flt_num = 100
for orig, dest, dur in ROUTES_RAW:
    ROUTES_DATA.append((flt_num, orig, dest, dur, "Daily"))
    ROUTES_DATA.append((flt_num + 1, dest, orig, dur, "Daily"))
    flt_num += 2

DEP_WAVES = ["06:00", "10:30", "15:00", "19:30"]

AIRCRAFT_FLEET = {
    "A319": {"model": "Airbus A319", "seats": 150, "rows": 25, "tails": ["N800SB", "N801SB", "N802SB"]},
    "A320": {"model": "Airbus A320", "seats": 180, "rows": 30, "tails": ["N804SB", "N805SB", "N806SB"]},
    "A321": {"model": "Airbus A321", "seats": 220, "rows": 37, "tails": ["N808SB", "N809SB", "N810SB"]}
}

# -----------------------------------------------------------------------------
# 2. HELPER FUNCTIONS
# -----------------------------------------------------------------------------

def format_duration(minutes: int) -> str:
    h, m = divmod(minutes, 60)
    if h == 0: return f"{m}m"
    if m == 0: return f"{h}h"
    return f"{h}h {m}m"

def get_row_list(total_rows: int) -> list:
    """Generates row numbers skipping Row 13."""
    rows = []
    curr = 1
    while len(rows) < total_rows:
        if curr != 13:
            rows.append(curr)
        curr += 1
    return rows

def calculate_leg_price(duration_mins: int, dest: str) -> int:
    is_intl = dest in ["RJAA", "RKSI", "EGKK", "TJBQ"]
    rate = 0.75 if is_intl else 0.52
    return round(50.0 + (duration_mins * rate))

def calculate_itinerary_price(itin: list) -> int:
    total = sum(calculate_leg_price(leg["Duration"], leg["Destination"]) for leg in itin)
    if len(itin) > 1:
        total *= 0.88  # Connection discount
    return round(total)

def assign_aircraft(flight_num: str, duration_mins: int) -> dict:
    rng = random.Random(hash(flight_num))
    ac_key = "A321" if duration_mins >= 240 else ("A320" if duration_mins >= 120 else rng.choice(["A319", "A320"]))
    spec = AIRCRAFT_FLEET[ac_key]
    return {
        "type": ac_key,
        "model": spec["model"],
        "tail": rng.choice(spec["tails"]),
        "seats": spec["seats"],
        "rows": spec["rows"]
    }

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

def search_flights(origin, destination, max_connections=2, max_layover_hours=8.0):
    catalog = get_flight_catalog()
    results, queue = [], []
    
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
                    layover_mins += 1440
                layover_hrs = layover_mins / 60.0
                if 0.75 <= layover_hrs <= max_layover_hours:
                    queue.append((flight["Destination"], flight["ArrTime"], path + [flight]))
                    
    results.sort(key=lambda p: sum(l["Duration"] for l in p))
    return results

@st.cache_data
def generate_occupied_seats(flight_num: str, total_seats: int, total_rows: int):
    rng = random.Random(hash(flight_num) + 99)
    num_occupied = rng.randint(int(total_seats * 0.45), int(total_seats * 0.70))
    rows = get_row_list(total_rows)
    all_seats = []
    for r in rows:
        for letter in ['A', 'B', 'C', 'D', 'E', 'F']:
            all_seats.append(f"{r}{letter}")
            if len(all_seats) == total_seats: break
        if len(all_seats) == total_seats: break
    return set(rng.sample(all_seats, num_occupied)), rows, all_seats

def get_seat_amenities(seat_code: str):
    row = int(seat_code[:-1])
    letter = seat_code[-1]
    pos_map = {'A': 'Window (Left)', 'B': 'Middle (Left)', 'C': 'Aisle (Left)', 'D': 'Aisle (Right)', 'E': 'Middle (Right)', 'F': 'Window (Right)'}
    is_exit = row in [12, 14]
    return {
        'seat': seat_code,
        'position': pos_map.get(letter, 'Standard Seat'),
        'legroom': 'Extra Legroom Exit Row (34" Pitch)' if is_exit else 'Standard Economy (30" Pitch)',
        'recline': 'Full Recline' if is_exit else 'Standard Recline (3")',
        'power': 'Shared In-Seat USB & Power Outlet',
        'wifi': 'High-Speed SkyFly In-Flight Wi-Fi'
    }

# -----------------------------------------------------------------------------
# 3. SESSION STATE MANAGEMENT
# -----------------------------------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "search"
if "selected_itinerary" not in st.session_state:
    st.session_state.selected_itinerary = None
if "selected_seats" not in st.session_state:
    st.session_state.selected_seats = {}
if "pnr" not in st.session_state:
    st.session_state.pnr = None
if "active_bp_index" not in st.session_state:
    st.session_state.active_bp_index = 0
if "show_boarding_pass" not in st.session_state:
    st.session_state.show_boarding_pass = False

# -----------------------------------------------------------------------------
# VIEW 1: FLIGHT SEARCH & ROUTE SELECTION
# -----------------------------------------------------------------------------
if st.session_state.page == "search":
    st.title("✈️ SkyFly Route Search & Flight Booking")
    catalog = get_flight_catalog()
    all_airports = sorted(list(set([f["Origin"] for f in catalog] + [f["Destination"] for f in catalog])))
    
    col_a, col_b = st.columns(2)
    with col_a:
        origin = st.selectbox("From (Origin)", options=all_airports, index=all_airports.index("KSFB") if "KSFB" in all_airports else 0)
    with col_b:
        dest_options = [a for a in all_airports if a != origin]
        destination = st.selectbox("To (Destination)", options=dest_options, index=dest_options.index("KBGR") if "KBGR" in dest_options else 0)
        
    c_conn, c_layover = st.columns(2)
    with c_conn:
        max_conn = st.selectbox("Max Connections", options=[0, 1, 2], index=1)
    with c_layover:
        max_layover = st.slider("Max Layover (Hours)", 1.0, 10.0, 6.0, step=0.5)
        
    st.divider()
    itineraries = search_flights(origin, destination, max_connections=max_conn, max_layover_hours=max_layover)
    st.markdown(f"**Found {len(itineraries)} itinerary option(s) for `{origin}` ➔ `{destination}`**")
    
    if not itineraries:
        st.warning("No routes found for this pair with current filter. Try increasing max connections or layover hours.")
    else:
        for idx, itin in enumerate(itineraries):
            total_price = calculate_itinerary_price(itin)
            total_mins = sum(leg["Duration"] for leg in itin)
            formatted_dur = format_duration(total_mins)
            stops_label = "Non-stop" if len(itin) == 1 else f"{len(itin)-1} Stop"
            
            with st.container(border=True):
                c_main, c_buy = st.columns([3, 1])
                with c_main:
                    st.markdown(f"### {itin[0]['DepStr']} → {itin[-1]['ArrStr']}")
                    st.caption(f"**Route:** {' ➔ '.join([l['Origin'] for l in itin] + [itin[-1]['Destination']])}")
                    st.markdown(f"⏱️ **Duration:** {formatted_dur} ({stops_label}) | 🛩️ **Aircraft:** {itin[0]['Aircraft']['model']}")
                with c_buy:
                    st.markdown(f"### ${total_price} USD")
                    if st.button("Select Flight", key=f"select_itin_{idx}", type="primary", use_container_width=True):
                        st.session_state.selected_itinerary = {
                            "legs": itin,
                            "price": total_price,
                            "total_mins": total_mins,
                            "formatted_dur": formatted_dur
                        }
                        st.session_state.selected_seats = {}
                        st.session_state.page = "seat_selection"
                        st.rerun()

# -----------------------------------------------------------------------------
# VIEW 2: INTERACTIVE SEAT SELECTION MAP (NO DROPDOWN)
# -----------------------------------------------------------------------------
elif st.session_state.page == "seat_selection":
    itin_data = st.session_state.selected_itinerary
    legs = itin_data["legs"]
    
    if st.button("⬅️ Back to Search Results"):
        st.session_state.page = "search"
        st.rerun()
        
    st.title("💺 Seat Selection")
    st.info(f"Route: **{legs[0]['Origin']} ➔ {legs[-1]['Destination']}** | Total Fare: **${itin_data['price']} USD**")
    
    all_legs_selected = True
    
    for idx, leg in enumerate(legs):
        flt_id = leg["FlightID"]
        ac = leg["Aircraft"]
        occupied, row_list, all_seats = generate_occupied_seats(flt_id, ac["seats"], ac["rows"])
        
        current_seat = st.session_state.selected_seats.get(flt_id)
        if not current_seat:
            all_legs_selected = False
            
        st.markdown(f"### Leg {idx+1}: {leg['Origin']} ➔ {leg['Destination']} ({leg['FlightNum']})")
        st.caption(f"Aircraft: **{ac['model']}** ({ac['tail']}) | Duration: **{format_duration(leg['Duration'])}**")
        
        col_map, col_details = st.columns([1.6, 1])
        
        with col_map:
            st.markdown("**Click an available seat (⬜) on the seat map:**")
            st.caption("🔴 Occupied &nbsp;&nbsp; 🟩 Selected &nbsp;&nbsp; ⬜ Available")
            
            with st.container(border=True, height=360):
                for r in row_list:
                    c1, c2, c3, c_aisle, c4, c5, c6 = st.columns([1, 1, 1, 0.6, 1, 1, 1])
                    cols = [c1, c2, c3, c4, c5, c6]
                    for letter, col in zip(['A', 'B', 'C', 'D', 'E', 'F'], cols):
                        code = f"{r}{letter}"
                        is_occ = code in occupied
                        is_sel = code == current_seat
                        label = "🔴" if is_occ else (f"🟩{code}" if is_sel else f"⬜{code}")
                        
                        if col.button(label, key=f"seat_btn_{flt_id}_{code}", disabled=is_occ):
                            st.session_state.selected_seats[flt_id] = code
                            st.rerun()
                            
                    c_aisle.markdown(f"<p style='text-align: center; color: gray; font-size: 11px;'>{r}</p>", unsafe_allow_html=True)
                    
        with col_details:
            st.markdown("#### Selected Seat & Amenities")
            if current_seat:
                amenities = get_seat_amenities(current_seat)
                with st.container(border=True):
                    st.markdown(f"### Seat {amenities['seat']}")
                    st.write(f"📍 **Position:** {amenities['position']}")
                    st.write(f"📐 **Legroom:** {amenities['legroom']}")
                    st.write(f"💺 **Recline:** {amenities['recline']}")
                    st.write(f"⚡ **Power:** {amenities['power']}")
                    st.write(f"📶 **Connectivity:** {amenities['wifi']}")
            else:
                st.warning("No seat selected for this leg yet. Please click an available seat on the map.")
                
        st.divider()
        
    if st.button("Confirm Seats and Flights", type="primary", use_container_width=True, disabled=not all_legs_selected):
        # Generate PNR and move to confirmation view
        st.session_state.pnr = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        st.session_state.page = "confirmation"
        st.session_state.show_boarding_pass = False
        st.session_state.active_bp_index = 0
        st.rerun()

# -----------------------------------------------------------------------------
# VIEW 3: BOOKING CONFIRMATION & MOBILE BOARDING PASS
# -----------------------------------------------------------------------------
elif st.session_state.page == "confirmation":
    itin_data = st.session_state.selected_itinerary
    legs = itin_data["legs"]
    pnr = st.session_state.pnr
    
    st.balloons()
    st.title("🎉 Booking Confirmed!")
    st.success(f"Your reservation is complete. Confirmation Reference (PNR): **{pnr}**")
    
    c_summary, c_actions = st.columns([2, 1])
    
    with c_summary:
        with st.container(border=True):
            st.markdown("### Itinerary Summary")
            st.write(f"**Route:** {legs[0]['Origin']} ➔ {legs[-1]['Destination']}")
            st.write(f"**Total Fare:** ${itin_data['price']} USD")
            st.write(f"**Passenger:** SkyFly Guest")
            
            st.markdown("---")
            for idx, leg in enumerate(legs):
                flt_id = leg["FlightID"]
                seat = st.session_state.selected_seats.get(flt_id, "Assigned at Gate")
                st.write(f"**Leg {idx+1}:** {leg['FlightNum']} (`{leg['Origin']}` ➔ `{leg['Destination']}`) | Dep: **{leg['DepStr']}** | Arr: **{leg['ArrStr']}** | Seat: **{seat}**")

    with c_actions:
        with st.container(border=True):
            st.markdown("### Passports & Passes")
            if st.button("📱 Open Mobile Boarding Pass", type="primary", use_container_width=True):
                st.session_state.show_boarding_pass = not st.session_state.show_boarding_pass
                st.rerun()
                
            if st.button("🔄 Start New Search", use_container_width=True):
                st.session_state.page = "search"
                st.session_state.selected_itinerary = None
                st.session_state.selected_seats = {}
                st.rerun()

    # -----------------------------------------------------------------------------
    # DIGITAL MOBILE BOARDING PASS COMPONENT
    # -----------------------------------------------------------------------------
    if st.session_state.show_boarding_pass:
        st.divider()
        st.subheader("📱 Digital Mobile Boarding Pass")
        
        # Navigation controls for multi-leg itineraries
        if len(legs) > 1:
            c_prev, c_label, c_next = st.columns([1, 2, 1])
            with c_prev:
                if st.button("◀️ Previous Leg", disabled=st.session_state.active_bp_index == 0):
                    st.session_state.active_bp_index -= 1
                    st.rerun()
            with c_label:
                st.markdown(f"<p style='text-align: center; font-weight: bold;'>Showing Leg {st.session_state.active_bp_index + 1} of {len(legs)}</p>", unsafe_allow_html=True)
            with c_next:
                if st.button("Next Leg ▶️", disabled=st.session_state.active_bp_index == len(legs) - 1):
                    st.session_state.active_bp_index += 1
                    st.rerun()

        active_leg = legs[st.session_state.active_bp_index]
        active_seat = st.session_state.selected_seats.get(active_leg["FlightID"], "12A")
        
        # Render Mobile Pass Card
        bp_col1, bp_col2, bp_col3 = st.columns([1, 2, 1])
        with bp_col2:
            st.markdown(f"""
                <div class="bp-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                        <span style="font-weight: bold; font-size: 16px;">✈️ SKYFLY EXPRESS</span>
                        <span style="background: rgba(255,255,255,0.2); padding: 3px 10px; border-radius: 12px; font-size: 11px;">BOARDING PASS</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 15px;">
                        <div>
                            <div style="font-size: 28px; font-weight: bold; letter-spacing: 1px;">{active_leg['Origin']}</div>
                            <div style="font-size: 11px; opacity: 0.8;">ORIGIN</div>
                        </div>
                        <div style="font-size: 20px;">✈️</div>
                        <div style="text-align: right;">
                            <div style="font-size: 28px; font-weight: bold; letter-spacing: 1px;">{active_leg['Destination']}</div>
                            <div style="font-size: 11px; opacity: 0.8;">DESTINATION</div>
                        </div>
                    </div>
                    <hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.2); margin: 15px 0;">
                    <div style="display: flex; justify-content: space-between; font-size: 12px;">
                        <div>
                            <div style="opacity: 0.7;">FLIGHT</div>
                            <div style="font-weight: bold; font-size: 14px;">{active_leg['FlightNum']}</div>
                        </div>
                        <div>
                            <div style="opacity: 0.7;">GATE</div>
                            <div style="font-weight: bold; font-size: 14px;">B{random.randint(1, 18)}</div>
                        </div>
                        <div>
                            <div style="opacity: 0.7;">BOARDING</div>
                            <div style="font-weight: bold; font-size: 14px;">{active_leg['DepStr']}</div>
                        </div>
                        <div>
                            <div style="opacity: 0.7;">SEAT</div>
                            <div style="font-weight: bold; font-size: 14px; color: #4ade80;">{active_seat}</div>
                        </div>
                    </div>
                </div>
                <div class="bp-stub">
                    <div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 10px;">
                        <div><b>PASSENGER:</b> SKYFLY GUEST</div>
                        <div><b>PNR:</b> {pnr}</div>
                    </div>
                    <div style="text-align: center; margin-top: 15px;">
                        <div class="barcode-text">||| | ||||| ||| || |||||| ||||</div>
                        <div style="font-size: 10px; color: #64748b; margin-top: 4px;">SCAN AT BOARDING GATE</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
