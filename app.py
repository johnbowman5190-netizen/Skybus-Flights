import streamlit as st
from datetime import datetime, timedelta
import random
import string

# Page Configuration
st.set_page_config(
    page_title="Skybus Airlines - Flight Search & Boarding Pass",
    page_icon="✈️",
    layout="wide"
)

# -----------------------------------------------------------------------------
# SKYBUS ORANGE & WHITE BRANDING + MOBILE PHONE FRAME STYLING
# -----------------------------------------------------------------------------
st.markdown("""
    <style>
    /* Primary Orange Color Scheme Override */
    :root {
        --skybus-orange: #FF5500;
        --skybus-orange-hover: #E04B00;
        --skybus-light-orange: #FFF0E6;
    }
    
    /* Streamlit Primary Buttons in Skybus Orange */
    div.stButton > button[kind="primary"] {
        background-color: #FF5500 !important;
        border-color: #FF5500 !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #E04B00 !important;
        border-color: #E04B00 !important;
    }

    /* Mobile Phone Shell Container */
    .phone-container {
        width: 100%;
        max-width: 380px;
        margin: 0 auto;
        background-color: #0F0F0F;
        border-radius: 36px;
        padding: 12px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.4);
        border: 4px solid #333333;
    }
    .phone-screen {
        background: linear-gradient(180deg, #FF5500 0%, #E04B00 140px, #F8F9FA 140px);
        border-radius: 28px;
        padding: 16px 16px 24px 16px;
        color: #1E293B;
        min-height: 620px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .phone-status-bar {
        display: flex;
        justify-content: space-between;
        color: #FFFFFF;
        font-size: 11px;
        font-weight: 600;
        margin-bottom: 12px;
        padding: 0 6px;
    }
    .phone-card {
        background-color: #FFFFFF;
        border-radius: 18px;
        padding: 18px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.12);
        margin-top: 10px;
    }
    .phone-stub {
        background-color: #FFFFFF;
        border-radius: 18px;
        padding: 16px;
        border-top: 2px dashed #CBD5E1;
        margin-top: 2px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.08);
        text-align: center;
    }
    .barcode-text {
        font-family: 'Courier New', Courier, monospace;
        letter-spacing: 5px;
        font-weight: bold;
        font-size: 20px;
        color: #0F172A;
    }
    .home-indicator {
        width: 120px;
        height: 4px;
        background-color: #CBD5E1;
        border-radius: 2px;
        margin: 16px auto 0 auto;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 1. FULL ROUTE NETWORK (60+ DIRECT LEGS LINKING ALL 18 BASES)
# -----------------------------------------------------------------------------

ROUTES_RAW = [
    # KSFB Base Trunks & Spokes
    ("KSFB", "KBGR", 185), ("KSFB", "KIWA", 270), ("KSFB", "KMSY", 120), ("KSFB", "TJBQ", 175),
    ("KSFB", "KRIC", 110), ("KSFB", "KEYW", 75),  ("KSFB", "KGRR", 130), ("KSFB", "KSWF", 140),
    ("KSFB", "KBLI", 310), ("KSFB", "PAFA", 410), ("KSFB", "KOMA", 155), ("KSFB", "KPVU", 250),
    
    # KBGR Base Trunks & Spokes
    ("KBGR", "KSWF", 75),  ("KBGR", "TJBQ", 240), ("KBGR", "KBLI", 310), ("KBGR", "KRIC", 95),
    ("KBGR", "PAFA", 380), ("KBGR", "KIWA", 290), ("KBGR", "KGRR", 115), ("KBGR", "KMSY", 210),
    
    # KIWA Base Trunks & Spokes
    ("KIWA", "KBLI", 195), ("KIWA", "PAFA", 330), ("KIWA", "KPVU", 85),  ("KIWA", "KMSY", 180),
    ("KIWA", "KOMA", 140), ("KIWA", "KSFB", 270), ("KIWA", "KRIC", 240), ("KIWA", "KGRR", 210),
    
    # KBLI Base Trunks & Spokes
    ("KBLI", "PAFA", 210), ("KBLI", "KPVU", 115), ("KBLI", "EGKK", 560), ("KBLI", "KBGR", 310),
    ("KBLI", "RJAA", 520), ("KBLI", "RKSI", 550), ("KBLI", "KOMA", 190), ("KBLI", "KSFB", 310),
    
    # PAFA Base Trunks & Spokes
    ("PAFA", "PANC", 55),  ("PAFA", "PAYA", 80),  ("PAFA", "RJAA", 430), ("PAFA", "RKSI", 460),
    ("PAFA", "KIWA", 330), ("PAFA", "EGKK", 580), ("PAFA", "KBLI", 210), ("PAFA", "KSFB", 410),
    
    # KMSY Base Trunks & Spokes
    ("KMSY", "KOMA", 135), ("KMSY", "KRIC", 100), ("KMSY", "KSFB", 120), ("KMSY", "PAFA", 390),
    ("KMSY", "TJBQ", 190), ("KMSY", "KIWA", 180), ("KMSY", "KBGR", 210),
    
    # Feeders & Connectors
    ("KSWF", "KGRR", 105), ("KSWF", "KRIC", 80),  ("KPVU", "KBLI", 115), ("KPVU", "KIWA", 85),
    ("PANC", "PAYA", 45),  ("TJBQ", "KSFB", 175), ("KEYW", "KSFB", 75),  ("KOMA", "KGRR", 90),
    ("KRIC", "KSWF", 80),  ("KGRR", "KOMA", 90)
]

# Generate Bidirectional Catalog
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
    """Generates aircraft row numbers skipping Row 13."""
    rows = []
    curr = 1
    while len(rows) < total_rows:
        if curr != 13:
            rows.append(curr)
        curr += 1
    return rows

def calculate_leg_price(duration_mins: int, dest: str) -> int:
    is_intl = dest in ["RJAA", "RKSI", "EGKK", "TJBQ"]
    rate = 0.70 if is_intl else 0.48
    return round(45.0 + (duration_mins * rate))

def calculate_itinerary_price(itin: list) -> int:
    total = sum(calculate_leg_price(leg["Duration"], leg["Destination"]) for leg in itin)
    if len(itin) > 1:
        total *= 0.85
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
            flt_id = f"SB{num}-{wave.replace(':', '')}"
            dep_time = datetime.strptime(wave, "%H:%M")
            arr_time = dep_time + timedelta(minutes=dur)
            catalog.append({
                "FlightNum": f"SB{num}",
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

def search_flights_unconstrained(origin, destination):
    """Unconstrained search: returns all direct and multi-leg connections sorted by duration."""
    catalog = get_flight_catalog()
    results, queue = [], []
    
    for flight in catalog:
        if flight["Origin"] == origin:
            queue.append((flight["Destination"], flight["ArrTime"], [flight]))
            
    while queue:
        curr_apt, curr_time, path = queue.pop(0)
        if curr_apt == destination:
            results.append(path)
            if len(results) >= 25: break
            continue
        if len(path) >= 3:
            continue
            
        for flight in catalog:
            if flight["Origin"] == curr_apt:
                layover_mins = (flight["DepTime"] - curr_time).total_seconds() / 60.0
                if layover_mins < 0:
                    layover_mins += 1440
                layover_hrs = layover_mins / 60.0
                if 0.5 <= layover_hrs <= 24.0:
                    queue.append((flight["Destination"], flight["ArrTime"], path + [flight]))
                    
    results.sort(key=lambda p: sum(l["Duration"] for l in p))
    return results

@st.cache_data
def generate_occupied_seats(flight_num: str, total_seats: int, total_rows: int):
    rng = random.Random(hash(flight_num) + 42)
    num_occupied = rng.randint(int(total_seats * 0.40), int(total_seats * 0.65))
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
        'wifi': 'High-Speed Skybus In-Flight Wi-Fi'
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

PASSENGER_NAME = "John Bowman"

# -----------------------------------------------------------------------------
# VIEW 1: FLIGHT SEARCH & SELECTION
# -----------------------------------------------------------------------------
if st.session_state.page == "search":
    st.title("🍊 Skybus - Search Flights")
    st.caption("Connecting 18 bases, feeders, and international hubs worldwide.")
    
    catalog = get_flight_catalog()
    all_airports = sorted(list(set([f["Origin"] for f in catalog] + [f["Destination"] for f in catalog])))
    
    col_a, col_b = st.columns(2)
    with col_a:
        origin = st.selectbox("From (Origin)", options=all_airports, index=all_airports.index("KSFB") if "KSFB" in all_airports else 0)
    with col_b:
        dest_options = [a for a in all_airports if a != origin]
        destination = st.selectbox("To (Destination)", options=dest_options, index=dest_options.index("KBGR") if "KBGR" in dest_options else 0)
        
    st.divider()
    
    itineraries = search_flights_unconstrained(origin, destination)
    st.markdown(f"**Found {len(itineraries)} flight option(s) for `{origin}` ➔ `{destination}`**")
    
    if not itineraries:
        st.warning("No connections available for this airport pair.")
    else:
        for idx, itin in enumerate(itineraries):
            total_price = calculate_itinerary_price(itin)
            total_mins = sum(leg["Duration"] for leg in itin)
            formatted_dur = format_duration(total_mins)
            stops_label = "Non-stop" if len(itin) == 1 else f"{len(itin)-1} Stop(s)"
            
            with st.container(border=True):
                c_main, c_buy = st.columns([3, 1])
                with c_main:
                    st.markdown(f"### {itin[0]['DepStr']} → {itin[-1]['ArrStr']}")
                    st.caption(f"**Route:** {' ➔ '.join([l['Origin'] for l in itin] + [itin[-1]['Destination']])}")
                    st.markdown(f"⏱️ **Total Flight Duration:** {formatted_dur} ({stops_label}) | 🛩️ **Aircraft:** {itin[0]['Aircraft']['model']}")
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
# VIEW 2: CLICKABLE SEAT SELECTION MAP (NO DROPDOWN)
# -----------------------------------------------------------------------------
elif st.session_state.page == "seat_selection":
    itin_data = st.session_state.selected_itinerary
    legs = itin_data["legs"]
    
    if st.button("⬅️ Back to Search"):
        st.session_state.page = "search"
        st.rerun()
        
    st.title("💺 Skybus Seat Selection")
    st.info(f"Passenger: **{PASSENGER_NAME}** | Trip: **{legs[0]['Origin']} ➔ {legs[-1]['Destination']}** | Fare: **${itin_data['price']} USD**")
    
    all_legs_selected = True
    
    for idx, leg in enumerate(legs):
        flt_id = leg["FlightID"]
        ac = leg["Aircraft"]
        occupied, row_list, all_seats = generate_occupied_seats(flt_id, ac["seats"], ac["rows"])
        current_seat = st.session_state.selected_seats.get(flt_id)
        
        if not current_seat:
            all_legs_selected = False
            
        st.markdown(f"### Leg {idx+1}: {leg['Origin']} ➔ {leg['Destination']} ({leg['FlightNum']})")
        st.caption(f"Aircraft: **{ac['model']}** (`{ac['tail']}`) | Duration: **{format_duration(leg['Duration'])}** (3x3 Layout, No Row 13)")
        
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
                st.warning("Click a seat on the map above to select it.")
                
        st.divider()
        
    if st.button("Confirm Seats and Flights", type="primary", use_container_width=True, disabled=not all_legs_selected):
        st.session_state.pnr = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        st.session_state.page = "confirmation"
        st.session_state.show_boarding_pass = False
        st.session_state.active_bp_index = 0
        st.rerun()

# -----------------------------------------------------------------------------
# VIEW 3: BOOKING CONFIRMATION & FULL-SCREEN MOBILE BOARDING PASS
# -----------------------------------------------------------------------------
elif st.session_state.page == "confirmation":
    itin_data = st.session_state.selected_itinerary
    legs = itin_data["legs"]
    pnr = st.session_state.pnr
    
    st.balloons()
    st.title("🎉 Skybus Booking Confirmed!")
    st.success(f"Passenger: **{PASSENGER_NAME}** | Booking Reference (PNR): **{pnr}**")
    
    c_summary, c_actions = st.columns([2, 1])
    
    with c_summary:
        with st.container(border=True):
            st.markdown("### Itinerary Summary")
            st.write(f"**Passenger Name:** {PASSENGER_NAME}")
            st.write(f"**Route:** {legs[0]['Origin']} ➔ {legs[-1]['Destination']}")
            st.write(f"**Total Fare Paid:** ${itin_data['price']} USD")
            
            st.markdown("---")
            for idx, leg in enumerate(legs):
                flt_id = leg["FlightID"]
                seat = st.session_state.selected_seats.get(flt_id, "12A")
                st.write(f"**Leg {idx+1}:** {leg['FlightNum']} (`{leg['Origin']}` ➔ `{leg['Destination']}`) | Dep: **{leg['DepStr']}** | Arr: **{leg['ArrStr']}** | Seat: **{seat}**")

    with c_actions:
        with st.container(border=True):
            st.markdown("### Passports & Boarding")
            if st.button("📱 Open Mobile Boarding Pass", type="primary", use_container_width=True):
                st.session_state.show_boarding_pass = not st.session_state.show_boarding_pass
                st.rerun()
                
            if st.button("🔄 Book Another Flight", use_container_width=True):
                st.session_state.page = "search"
                st.session_state.selected_itinerary = None
                st.session_state.selected_seats = {}
                st.rerun()

    # -----------------------------------------------------------------------------
    # FULL-SCREEN MOBILE PHONE BOARDING PASS
    # -----------------------------------------------------------------------------
    if st.session_state.show_boarding_pass:
        st.divider()
        st.subheader("📱 Smartphone Mobile Boarding Pass")
        
        # Navigation controls for multi-leg itineraries
        if len(legs) > 1:
            c_prev, c_label, c_next = st.columns([1, 2, 1])
            with c_prev:
                if st.button("◀️ Previous Leg", disabled=st.session_state.active_bp_index == 0):
                    st.session_state.active_bp_index -= 1
                    st.rerun()
            with c_label:
                st.markdown(f"<p style='text-align: center; font-weight: bold;'>Leg {st.session_state.active_bp_index + 1} of {len(legs)}</p>", unsafe_allow_html=True)
            with c_next:
                if st.button("Next Leg ▶️", disabled=st.session_state.active_bp_index == len(legs) - 1):
                    st.session_state.active_bp_index += 1
                    st.rerun()

        active_leg = legs[st.session_state.active_bp_index]
        active_seat = st.session_state.selected_seats.get(active_leg["FlightID"], "12A")
        
        # Render Full Phone UI Frame
        st.markdown(f"""
            <div class="phone-container">
                <div class="phone-screen">
                    <div>
                        <!-- Phone Status Bar -->
                        <div class="phone-status-bar">
                            <span>9:41</span>
                            <span>5G 📶 🔋 100%</span>
                        </div>
                        
                        <!-- Header -->
                        <div style="display: flex; justify-content: space-between; align-items: center; color: white; margin-bottom: 8px;">
                            <span style="font-weight: 800; font-size: 20px; letter-spacing: 1px;">SKYBUS</span>
                            <span style="background: rgba(255,255,255,0.25); padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: bold;">PASSENGER PASS</span>
                        </div>
                        
                        <!-- Main Flight Card -->
                        <div class="phone-card">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <div style="font-size: 32px; font-weight: 900; color: #FF5500;">{active_leg['Origin']}</div>
                                    <div style="font-size: 11px; color: #64748B; font-weight: bold;">ORIGIN</div>
                                </div>
                                <div style="font-size: 22px;">✈️</div>
                                <div style="text-align: right;">
                                    <div style="font-size: 32px; font-weight: 900; color: #FF5500;">{active_leg['Destination']}</div>
                                    <div style="font-size: 11px; color: #64748B; font-weight: bold;">DESTINATION</div>
                                </div>
                            </div>
                            
                            <hr style="border: 0; border-top: 1px solid #E2E8F0; margin: 14px 0;">
                            
                            <div style="margin-bottom: 12px;">
                                <div style="font-size: 10px; color: #64748B; font-weight: bold;">PASSENGER</div>
                                <div style="font-size: 16px; font-weight: bold; color: #0F172A;">{PASSENGER_NAME}</div>
                            </div>
                            
                            <div style="display: flex; justify-content: space-between; font-size: 12px;">
                                <div>
                                    <div style="font-size: 10px; color: #64748B;">FLIGHT</div>
                                    <div style="font-weight: bold; font-size: 14px; color: #0F172A;">{active_leg['FlightNum']}</div>
                                </div>
                                <div>
                                    <div style="font-size: 10px; color: #64748B;">GATE</div>
                                    <div style="font-weight: bold; font-size: 14px; color: #0F172A;">B{random.randint(1, 15)}</div>
                                </div>
                                <div>
                                    <div style="font-size: 10px; color: #64748B;">BOARDING</div>
                                    <div style="font-weight: bold; font-size: 14px; color: #0F172A;">{active_leg['DepStr']}</div>
                                </div>
                                <div>
                                    <div style="font-size: 10px; color: #64748B;">SEAT</div>
                                    <div style="font-weight: bold; font-size: 15px; color: #FF5500;">{active_seat}</div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Tear-off Stub & Barcode -->
                        <div class="phone-stub">
                            <div style="font-size: 11px; color: #64748B; margin-bottom: 6px;">BOOKING REF: <b style="color: #0F172A;">{pnr}</b></div>
                            <div class="barcode-text">||| | ||||| ||| || ||||</div>
                            <div style="font-size: 9px; color: #94A3B8; margin-top: 4px;">SCAN AT TSA & GATE READER</div>
                        </div>
                    </div>
                    
                    <!-- Phone Home Indicator Bar -->
                    <div class="home-indicator"></div>
                </div>
            </div>
        """, unsafe_allow_html=True)
