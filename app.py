import csv
import io
from datetime import datetime, timedelta
from collections import deque
import streamlit as st

# ==========================================
# 1. PAGE CONFIG & SKYBUS CUSTOM BRANDING
# ==========================================
st.set_page_config(
    page_title="Skybus Operations & Boarding System",
    page_icon="✈️",
    layout="wide"
)

# Custom CSS for Skybus #FF5722 Vibrant Orange Theme & Boarding Pass Styling
st.markdown("""
<style>
    /* Skybus Brand Colors */
    :root {
        --skybus-orange: #FF5722;
        --skybus-dark: #1A1A1A;
        --skybus-light: #F4F6F8;
    }
    
    /* Header Styling */
    .skybus-header {
        background-color: #FF5722;
        color: white;
        padding: 20px 25px;
        border-radius: 10px;
        margin-bottom: 25px;
        box-shadow: 0 4px 12px rgba(255, 87, 34, 0.25);
    }
    
    .skybus-header h1 {
        margin: 0;
        font-weight: 800;
        letter-spacing: 1px;
    }
    
    /* Passenger & Wi-Fi Banner */
    .info-card {
        background: #FFFFFF;
        border-left: 5px solid #FF5722;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        margin-bottom: 20px;
    }
    
    /* Boarding Pass Modal/Card */
    .boarding-pass {
        background: white;
        border: 2px solid #FF5722;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        margin-top: 15px;
        margin-bottom: 25px;
        color: #333;
    }
    
    .bp-header {
        background-color: #FF5722;
        color: white;
        padding: 15px 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .bp-body {
        padding: 20px;
    }
    
    .bp-field {
        font-size: 12px;
        color: #777;
        text-transform: uppercase;
        margin-bottom: 2px;
        font-weight: 600;
    }
    
    .bp-value {
        font-size: 16px;
        font-weight: 700;
        color: #222;
    }
    
    .barcode {
        font-family: 'Courier New', Courier, monospace;
        background: #f0f0f0;
        letter-spacing: 4px;
        padding: 10px;
        text-align: center;
        border-radius: 6px;
        font-weight: bold;
        margin-top: 15px;
        border: 1px dashed #ccc;
    }
    
    .stButton>button {
        background-color: #FF5722 !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
        border-radius: 6px !important;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# 2. ROUTE NETWORK DATASET GENERATION
# ==========================================

routes_data = [
    # --- Inter-Base Trunk Network (100-299) ---
    (100, "KBGR", "KSFB", 185, "Daily"),
    (102, "KIWA", "KBLI", 195, "Daily"),
    (104, "TJBQ", "KSFB", 175, "Daily"),
    (106, "PAFA", "KBLI", 210, "Daily"),
    (108, "KBGR", "TJBQ", 240, "Mon,Wed,Fri,Sun"),
    (110, "KIWA", "PAFA", 330, "Mon,Tue,Thu,Sat"),
    (200, "KSFB", "KRIC", 110, "Daily"),
    (202, "KIWA", "KPVU", 85, "Daily"),
    (204, "KGRR", "KSWF", 105, "Mon,Wed,Fri,Sun"),
    (206, "KMSY", "KOMA", 135, "Tue,Thu,Sat,Sun"),
    (208, "KSFB", "KMSY", 120, "Daily"),
    (210, "KBLI", "KPVU", 115, "Mon,Wed,Fri"),

    # --- Hub 1: KBGR Spokes (300-319) ---
    (300, "KBGR", "KBOS", 55, "Daily"),
    (302, "KBGR", "KPWM", 40, "Daily"),
    (304, "KBGR", "KPVD", 65, "Daily"),
    (306, "KBGR", "KBTV", 60, "Mon,Wed,Fri"),
    (308, "KBGR", "KACK", 50, "Tue,Thu,Sat,Sun"),
    (310, "KBGR", "KMVY", 50, "Fri,Sat,Sun"),
    (312, "KBGR", "KBDL", 70, "Daily"),
    (314, "KBGR", "KSYR", 80, "Mon,Wed,Fri"),
    (316, "KBGR", "KROC", 90, "Tue,Thu,Sat"),
    (318, "KBGR", "KPBG", 60, "Mon,Fri"),

    # --- Hub 2: KSFB Spokes (400-419) ---
    (400, "KSFB", "KEYW", 70, "Daily"),
    (402, "KSFB", "KPNS", 75, "Daily"),
    (404, "KSFB", "KTLH", 55, "Daily"),
    (406, "KSFB", "KCHS", 65, "Daily"),
    (408, "KSFB", "KSAV", 60, "Mon,Wed,Fri,Sun"),
    (410, "KSFB", "KBHM", 90, "Tue,Thu,Sat"),
    (412, "KSFB", "KGSP", 80, "Mon,Wed,Fri"),
    (414, "KSFB", "KMYR", 70, "Daily"),
    (416, "KSFB", "KAGS", 75, "Tue,Thu,Sat"),
    (418, "KSFB", "KCAE", 70, "Mon,Wed,Fri,Sun"),

    # --- Hub 3: TJBQ Spokes (500-519) ---
    (500, "TJBQ", "TJSJ", 35, "Daily"),
    (502, "TJBQ", "TIST", 50, "Daily"),
    (504, "TJBQ", "TISX", 55, "Daily"),
    (506, "TJBQ", "TJPS", 30, "Daily"),
    (508, "TJBQ", "TJIG", 35, "Daily"),
    (510, "TJBQ", "TNCM", 75, "Mon,Wed,Fri,Sun"),
    (512, "TJBQ", "MDPC", 45, "Daily"),
    (514, "TJBQ", "MDSD", 50, "Daily"),
    (516, "TJBQ", "MBPV", 80, "Tue,Thu,Sat"),
    (518, "TJBQ", "MYNN", 110, "Mon,Fri"),

    # --- Hub 4: KIWA Spokes (600-619) ---
    (600, "KIWA", "KLAS", 60, "Daily"),
    (602, "KIWA", "KSAN", 65, "Daily"),
    (604, "KIWA", "KPSP", 55, "Daily"),
    (606, "KIWA", "KTUS", 40, "Daily"),
    (608, "KIWA", "KFLG", 40, "Daily"),
    (610, "KIWA", "KABQ", 70, "Daily"),
    (612, "KIWA", "KSLC", 95, "Daily"),
    (614, "KIWA", "KRNO", 100, "Mon,Wed,Fri,Sun"),
    (616, "KIWA", "KFAT", 85, "Tue,Thu,Sat"),
    (618, "KIWA", "KOAK", 115, "Daily"),

    # --- Hub 5: KBLI Spokes (700-719) ---
    (700, "KBLI", "KGEG", 60, "Daily"),
    (702, "KBLI", "KYKM", 50, "Mon,Wed,Fri"),
    (704, "KBLI", "KPSC", 55, "Daily"),
    (706, "KBLI", "KEAT", 45, "Tue,Thu,Sat"),
    (708, "KBLI", "KALW", 60, "Mon,Fri"),
    (710, "KBLI", "KRDM", 75, "Daily"),
    (712, "KBLI", "KEUG", 70, "Daily"),
    (714, "KBLI", "KMFR", 85, "Mon,Wed,Fri,Sun"),
    (716, "KBLI", "KOTH", 80, "Tue,Thu,Sat"),
    (718, "KBLI", "KLWS", 70, "Mon,Wed,Fri"),

    # --- Hub 6: PAFA Spokes (900-919) ---
    (900, "PAFA", "PANC", 55, "Daily"),
    (902, "PAFA", "PAJN", 85, "Daily"),
    (904, "PAFA", "PAKT", 115, "Mon,Wed,Fri,Sun"),
    (906, "PAFA", "PASI", 100, "Tue,Thu,Sat"),
    (908, "PAFA", "PABR", 80, "Daily"),
    (910, "PAFA", "PAOT", 75, "Mon,Wed,Fri"),
    (912, "PAFA", "PAOM", 80, "Daily"),
    (914, "PAFA", "PABE", 70, "Mon,Wed,Fri,Sun"),
    (916, "PAFA", "PACV", 65, "Tue,Thu,Sat"),
    (918, "PAFA", "PAPG", 95, "Mon,Fri"),

    # --- Focus Cities (1000-1519) ---
    (1000, "KSWF", "KALB", 40, "Daily"), (1002, "KSWF", "KSYR", 50, "Daily"),
    (1004, "KSWF", "KROC", 60, "Mon,Wed,Fri"), (1006, "KSWF", "KBUF", 70, "Daily"),
    (1008, "KSWF", "KBTV", 50, "Tue,Thu,Sat"), (1010, "KSWF", "KMHT", 45, "Daily"),
    (1012, "KSWF", "KPVD", 45, "Daily"), (1014, "KSWF", "KORF", 80, "Mon,Wed,Fri,Sun"),
    (1016, "KSWF", "KABE", 35, "Daily"), (1018, "KSWF", "KAVP", 35, "Tue,Thu,Sat"),

    (1100, "KRIC", "KROA", 45, "Daily"), (1102, "KRIC", "KCHO", 35, "Daily"),
    (1104, "KRIC", "KLYH", 40, "Mon,Wed,Fri"), (1106, "KRIC", "KILM", 55, "Daily"),
    (1108, "KRIC", "KEWN", 50, "Tue,Thu,Sat"), (1110, "KRIC", "KOAJ", 50, "Mon,Wed,Fri"),
    (1112, "KRIC", "KTRI", 65, "Daily"), (1114, "KRIC", "KCHS", 70, "Daily"),
    (1116, "KRIC", "KAVL", 75, "Tue,Thu,Sat,Sun"), (1118, "KRIC", "KSBY", 40, "Mon,Fri"),

    (1200, "KMSY", "KBTR", 35, "Daily"), (1202, "KMSY", "KLFT", 40, "Daily"),
    (1204, "KMSY", "KLCH", 50, "Mon,Wed,Fri"), (1206, "KMSY", "KMOB", 45, "Daily"),
    (1208, "KMSY", "KGPT", 35, "Daily"), (1210, "KMSY", "KHSV", 75, "Tue,Thu,Sat"),
    (1212, "KMSY", "KJAN", 55, "Daily"), (1214, "KMSY", "KSHV", 70, "Mon,Wed,Fri,Sun"),
    (1216, "KMSY", "KLIT", 75, "Daily"), (1218, "KMSY", "KPNS", 50, "Daily"),

    (1300, "KGRR", "KTVC", 45, "Daily"), (1302, "KGRR", "KMQT", 65, "Mon,Wed,Fri"),
    (1304, "KGRR", "KPLN", 55, "Tue,Thu,Sat"), (1306, "KGRR", "KAZO", 30, "Daily"),
    (1308, "KGRR", "KLAN", 30, "Daily"), (1310, "KGRR", "KFNT", 35, "Daily"),
    (1312, "KGRR", "KMSN", 50, "Mon,Wed,Fri,Sun"), (1314, "KGRR", "KGRB", 45, "Daily"),
    (1316, "KGRR", "KATW", 45, "Tue,Thu,Sat"), (1318, "KGRR", "KSBN", 35, "Daily"),

    (1400, "KOMA", "KLNK", 30, "Daily"), (1402, "KOMA", "KGRI", 45, "Daily"),
    (1404, "KOMA", "KEAR", 50, "Mon,Wed,Fri"), (1406, "KOMA", "KLBF", 60, "Tue,Thu,Sat"),
    (1408, "KOMA", "KBFF", 85, "Mon,Fri"), (1410, "KOMA", "KSUX", 35, "Daily"),
    (1412, "KOMA", "KFSD", 50, "Daily"), (1414, "KOMA", "KDSM", 40, "Daily"),
    (1416, "KOMA", "KCID", 50, "Mon,Wed,Fri,Sun"), (1418, "KOMA", "KRST", 55, "Tue,Thu,Sat"),

    (1500, "KPVU", "KCDC", 50, "Daily"), (1502, "KPVU", "KSGU", 55, "Daily"),
    (1504, "KPVU", "KEKO", 60, "Mon,Wed,Fri"), (1506, "KPVU", "KPIH", 45, "Daily"),
    (1508, "KPVU", "KIDA", 55, "Daily"), (1510, "KPVU", "KTWF", 50, "Tue,Thu,Sat"),
    (1512, "KPVU", "KBOI", 70, "Daily"), (1514, "KPVU", "KJAC", 65, "Mon,Wed,Fri,Sun"),
    (1516, "KPVU", "KWYS", 60, "Fri,Sat,Sun"), (1518, "KPVU", "KBZN", 75, "Daily"),

    # --- International Routes (800-871) ---
    (800, "KBGR", "CYHZ", 75, "Daily"), (802, "KBGR", "CYUL", 70, "Daily"),
    (804, "KBGR", "CYYT", 130, "Mon,Wed,Fri"), (806, "KBGR", "TXKF", 145, "Tue,Thu,Sat,Sun"),
    (808, "KBGR", "EINN", 360, "Mon,Wed,Fri,Sun"),
    (810, "KSFB", "MYNN", 75, "Daily"), (812, "KSFB", "MKJS", 115, "Daily"),
    (814, "KSFB", "MBPV", 125, "Tue,Thu,Sat"), (816, "KSFB", "MROC", 210, "Mon,Wed,Fri,Sun"),
    (818, "KSFB", "MPTO", 230, "Tue,Thu,Sat"),
    (820, "TJBQ", "MDPC", 45, "Daily"), (822, "TJBQ", "TNCM", 75, "Daily"),
    (824, "TJBQ", "SKBO", 210, "Mon,Wed,Fri"), (826, "TJBQ", "TAPA", 95, "Tue,Thu,Sat"),
    (828, "TJBQ", "MYNN", 110, "Mon,Fri"),
    (830, "KIWA", "MMSD", 105, "Daily"), (832, "KIWA", "MMPR", 140, "Daily"),
    (834, "KIWA", "MMME", 120, "Mon,Wed,Fri,Sun"), (836, "KIWA", "MMGL", 150, "Tue,Thu,Sat"),
    (838, "KIWA", "MMMX", 195, "Daily"),
    (840, "KBLI", "CYVR", 35, "Daily"), (842, "KBLI", "CYYJ", 30, "Daily"),
    (844, "KBLI", "CYYC", 90, "Daily"), (846, "KBLI", "CYEG", 110, "Mon,Wed,Fri,Sun"),
    (848, "KBLI", "MMSD", 260, "Tue,Thu,Sat"),
    (850, "PAFA", "CYXY", 85, "Mon,Wed,Fri"), (852, "PAFA", "CYZF", 120, "Tue,Thu,Sat"),
    (854, "PAFA", "CYEG", 210, "Mon,Wed,Fri,Sun"), (856, "PAFA", "RJAA", 430, "Wed,Fri,Sun"),
    (858, "PAFA", "RKSI", 460, "Tue,Thu,Sat"),
    (860, "KBGR", "EGSS", 390, "Daily"), (862, "KBGR", "LFOB", 410, "Mon,Wed,Fri,Sun"),
    (864, "KBGR", "LIME", 450, "Tue,Thu,Sat"), (866, "KBGR", "EICK", 370, "Mon,Wed,Fri"),
    (868, "KBGR", "LEGE", 440, "Tue,Thu,Sat,Sun"), (870, "KBGR", "EDJA", 430, "Mon,Thu,Sat")
]

@st.cache_data
def load_schedule_list():
    outbound_time = datetime.strptime("08:00", "%H:%M")
    flights = []
    for flt_out, orig, dest, duration, days in routes_data:
        flt_in = flt_out + 1
        dep_out_str = outbound_time.strftime("%H:%M")
        arr_out_time = outbound_time + timedelta(minutes=duration)
        arr_out_str = arr_out_time.strftime("%H:%M")
        
        flights.append({
            "Flight_Number": flt_out, "Origin": orig, "Destination": dest,
            "Days_Of_Week": days, "Departure_Time": dep_out_str,
            "Arrival_Time": arr_out_str, "Duration_Mins": duration
        })
        
        inbound_dep_time = arr_out_time + timedelta(minutes=60)
        dep_in_str = inbound_dep_time.strftime("%H:%M")
        arr_in_time = inbound_dep_time + timedelta(minutes=duration)
        arr_in_str = arr_in_time.strftime("%H:%M")
        
        flights.append({
            "Flight_Number": flt_in, "Origin": dest, "Destination": orig,
            "Days_Of_Week": days, "Departure_Time": dep_in_str,
            "Arrival_Time": arr_in_str, "Duration_Mins": duration
        })
    return flights


# ==========================================
# 3. ITINERARY SEARCH ENGINE (BFS)
# ==========================================

class FlightSearchEngine:
    def __init__(self, flights_data):
        self.flights = flights_data

    @staticmethod
    def parse_time(time_str):
        return datetime.strptime(time_str, "%H:%M")

    def search_itinerary(self, origin, destination, max_connections=2):
        origin = origin.upper()
        destination = destination.upper()
        
        queue = deque()
        valid_itineraries = []

        for flight in self.flights:
            if flight["Origin"] == origin:
                queue.append([flight])

        while queue:
            path = queue.popleft()
            current_leg = path[-1]
            current_dest = current_leg["Destination"]
            connections_used = len(path) - 1

            if current_dest == destination:
                valid_itineraries.append(path)
                continue

            # Connection check
            if max_connections is None or connections_used < max_connections:
                last_arr_time = self.parse_time(current_leg["Arrival_Time"])
                
                for next_flight in self.flights:
                    if next_flight["Origin"] == current_dest:
                        visited_airports = {f["Origin"] for f in path}
                        if next_flight["Destination"] in visited_airports:
                            continue
                            
                        next_dep_time = self.parse_time(next_flight["Departure_Time"])
                        layover_mins = (next_dep_time - last_arr_time).total_seconds() / 60
                        
                        if 45 <= layover_mins <= 360:
                            queue.append(path + [next_flight])

        return valid_itineraries


# ==========================================
# 4. STREAMLIT UI IMPLEMENTATION
# ==========================================

# Header Banner
st.markdown("""
<div class="skybus-header">
    <h1>✈️ SKYBUS AIRLINES</h1>
    <p style="margin: 5px 0 0 0; font-weight: 500;">Flight Operations & Mobile Boarding System</p>
</div>
""", unsafe_allow_html=True)

# Passenger Profile & Wi-Fi Details
col_pass, col_wifi = st.columns(2)
with col_pass:
    st.markdown("""
    <div class="info-card">
        <div style="font-size: 11px; color: #888; font-weight: bold; text-transform: uppercase;">Passenger Profile</div>
        <div style="font-size: 18px; font-weight: bold; color: #111;">👤 John Bowman</div>
    </div>
    """, unsafe_allow_html=True)

with col_wifi:
    st.markdown("""
    <div class="info-card">
        <div style="font-size: 11px; color: #888; font-weight: bold; text-transform: uppercase;">In-Flight Wi-Fi Status</div>
        <div style="font-size: 18px; font-weight: bold; color: #FF5722;">📶 High-Speed SkyFly (Active)</div>
    </div>
    """, unsafe_allow_html=True)

# Load engine
flights_data = load_schedule_list()
engine = FlightSearchEngine(flights_data)

# Extract unique airport codes for dropdowns
all_airports = sorted(list(set([f["Origin"] for f in flights_data] + [f["Destination"] for f in flights_data])))

st.subheader("🔍 Search Flight Itineraries")

# Search Controls
s_col1, s_col2, s_col3 = st.columns(3)

with s_col1:
    origin_input = st.selectbox("Origin Airport", options=all_airports, index=all_airports.index("KBGR") if "KBGR" in all_airports else 0)

with s_col2:
    dest_input = st.selectbox("Destination Airport", options=all_airports, index=all_airports.index("KSFB") if "KSFB" in all_airports else 1)

with s_col3:
    conn_option = st.selectbox(
        "Maximum Connections Allowed",
        options=["0 (Nonstop Only)", "1 Connection", "2 Connections", "3 Connections", "4 Connections", "Unlimited"]
    )

# Map connection selection
if "0" in conn_option:
    max_conn_val = 0
elif "1" in conn_option:
    max_conn_val = 1
elif "2" in conn_option:
    max_conn_val = 2
elif "3" in conn_option:
    max_conn_val = 3
elif "4" in conn_option:
    max_conn_val = 4
else:
    max_conn_val = None

# Perform Search
if st.button("Find Routes"):
    if origin_input == dest_input:
        st.warning("Origin and Destination airports must be different.")
    else:
        results = engine.search_itinerary(origin_input, dest_input, max_connections=max_conn_val)
        st.session_state["search_results"] = results
        st.session_state["origin_search"] = origin_input
        st.session_state["dest_search"] = dest_input

# Display Results
if "search_results" in st.session_state:
    results = st.session_state["search_results"]
    orig = st.session_state["origin_search"]
    dest = st.session_state["dest_search"]

    st.markdown(f"### Results for **{orig} ➔ {dest}** ({len(results)} option(s) found)")

    if not results:
        st.info("No matching itineraries found within the selected connection parameters.")
    else:
        for idx, option in enumerate(results, 1):
            num_stops = len(option) - 1
            stops_label = "Nonstop" if num_stops == 0 else f"{num_stops} Stop(s)"
            
            with st.expander(f"Option {idx}: {orig} to {dest} — [{stops_label}]", expanded=(idx == 1)):
                for leg_idx, leg in enumerate(option, 1):
                    st.write(f"**Leg {leg_idx}:** Flight **Skybus #{leg['Flight_Number']}** | "
                             f"`{leg['Origin']}` ({leg['Departure_Time']}) ➔ `{leg['Destination']}` ({leg['Arrival_Time']}) | "
                             f"Duration: {leg['Duration_Mins']} mins | Days: *{leg['Days_Of_Week']}*")
                    
                    # Show layover time if applicable
                    if leg_idx < len(option):
                        arr = engine.parse_time(leg['Arrival_Time'])
                        nxt_dep = engine.parse_time(option[leg_idx]['Departure_Time'])
                        layover = int((nxt_dep - arr).total_seconds() / 60)
                        st.info(f"⏳ Layover in `{leg['Destination']}`: **{layover} minutes**")

                # Mobile Boarding Pass Trigger
                if st.button(f"🎫 Issue Boarding Pass for Option {idx}", key=f"bp_btn_{idx}"):
                    st.session_state["active_bp"] = option

# ==========================================
# 5. EDGE-TO-EDGE MOBILE BOARDING PASS
# ==========================================

if "active_bp" in st.session_state:
    bp_option = st.session_state["active_bp"]
    st.markdown("---")
    st.subheader("📲 Mobile Boarding Pass")

    # If multi-leg, allow leg switching
    selected_leg_idx = 0
    if len(bp_option) > 1:
        leg_titles = [f"Leg {i+1}: {leg['Origin']} -> {leg['Destination']}" for i, leg in enumerate(bp_option)]
        selected_leg_idx = st.radio("Select Flight Leg:", range(len(leg_titles)), format_func=lambda x: leg_titles[x], horizontal=True)

    leg_data = bp_option[selected_leg_idx]

    # Render Boarding Pass UI Card
    st.markdown(f"""
    <div class="boarding-pass">
        <div class="bp-header">
            <div>
                <span style="font-size: 20px; font-weight: 800; letter-spacing: 1px;">SKYBUS</span>
                <span style="font-size: 12px; margin-left: 8px; background: rgba(255,255,255,0.2); padding: 3px 8px; border-radius: 12px;">BOARDING PASS</span>
            </div>
            <div style="font-weight: bold; font-size: 14px;">Flight {leg_data['Flight_Number']}</div>
        </div>
        <div class="bp-body">
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #eee; padding-bottom: 15px; margin-bottom: 15px;">
                <div>
                    <div class="bp-field">Passenger</div>
                    <div class="bp-value">John Bowman</div>
                </div>
                <div style="text-align: right;">
                    <div class="bp-field">In-Flight Wi-Fi</div>
                    <div class="bp-value" style="color: #FF5722;">High-Speed SkyFly</div>
                </div>
            </div>
            
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <div>
                    <div style="font-size: 28px; font-weight: 900; color: #111;">{leg_data['Origin']}</div>
                    <div class="bp-field">Departs {leg_data['Departure_Time']}</div>
                </div>
                <div style="font-size: 22px; color: #FF5722;">✈️</div>
                <div style="text-align: right;">
                    <div style="font-size: 28px; font-weight: 900; color: #111;">{leg_data['Destination']}</div>
                    <div class="bp-field">Arrives {leg_data['Arrival_Time']}</div>
                </div>
            </div>

            <div style="display: flex; justify-content: space-between; background: #F8F9FA; padding: 12px; border-radius: 8px;">
                <div>
                    <div class="bp-field">Gate</div>
                    <div class="bp-value">B12</div>
                </div>
                <div>
                    <div class="bp-field">Zone</div>
                    <div class="bp-value">Zone 1</div>
                </div>
                <div>
                    <div class="bp-field">Seat</div>
                    <div class="bp-value">14A</div>
                </div>
                <div>
                    <div class="bp-field">Days</div>
                    <div class="bp-value">{leg_data['Days_Of_Week']}</div>
                </div>
            </div>

            <div class="barcode">
                ||| | ||||| ||| |||| || ||||| ||||| ||| ||||||| | ||||
                <br>
                <span style="font-size: 10px; color: #666; font-family: sans-serif;">SKYB-{leg_data['Flight_Number']}-BOWMAN-JOHN</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
