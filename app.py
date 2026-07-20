from collections import deque
from datetime import datetime
import random
import textwrap
import streamlit as st
import streamlit.components.v1 as components

# ==========================================
# 1. PAGE CONFIG & BRANDING
# ==========================================
st.set_page_config(
    page_title="Skybus Route & Boarding System",
    page_icon="✈️",
    layout="wide",
)

# Skybus Custom Header CSS
header_css = """
<style>
    .skybus-header {
        background-color: #FF5722;
        color: white;
        padding: 20px 25px;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(255, 87, 34, 0.25);
    }
    .skybus-header h1 { margin: 0; font-weight: 800; font-size: 28px; }
    .info-card {
        background: #FFFFFF;
        border-left: 5px solid #FF5722;
        padding: 12px 18px;
        border-radius: 6px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
        margin-bottom: 15px;
    }
</style>
"""
st.markdown(header_css, unsafe_allow_html=True)


# Dynamic Random Generators (Seeded per flight leg for consistency during navigation)
def get_random_seat(flight_num):
    random.seed(int(flight_num) + 42)
    row = random.randint(1, 32)
    letter = random.choice(["A", "B", "C", "D", "E", "F"])
    return f"{row}{letter}"


def get_random_gate(flight_num):
    random.seed(int(flight_num) + 99)
    concourse = random.choice(["A", "B", "C", "D"])
    gate_num = random.randint(1, 25)
    return f"{concourse}{gate_num}"


# ==========================================
# 2. FULL NETWORK DATASET
# ==========================================

routes_raw = [
    # Inter-Base Transcontinental Bridges
    (100, "KBGR", "KSFB", "Daily"),
    (102, "KIWA", "KBLI", "Daily"),
    (104, "TJBQ", "KSFB", "Daily"),
    (106, "PAFA", "KBLI", "Daily"),
    (108, "KBGR", "TJBQ", "Mon,Wed,Fri,Sun"),
    (110, "KIWA", "PAFA", "Mon,Tue,Thu,Sat"),
    (112, "KSFB", "KIWA", "Daily"),
    (114, "KBGR", "KBLI", "Daily"),
    (116, "KMSY", "KIWA", "Daily"),
    (118, "KOMA", "KPVU", "Daily"),
    (120, "KSWF", "KIWA", "Daily"),
    (200, "KSFB", "KRIC", "Daily"),
    (202, "KIWA", "KPVU", "Daily"),
    (204, "KGRR", "KSWF", "Mon,Wed,Fri,Sun"),
    (206, "KMSY", "KOMA", "Tue,Thu,Sat,Sun"),
    (208, "KSFB", "KMSY", "Daily"),
    (210, "KBLI", "KPVU", "Mon,Wed,Fri"),
    # Hub 1: KBGR Spokes
    (300, "KBGR", "KBOS", "Daily"),
    (302, "KBGR", "KPWM", "Daily"),
    (304, "KBGR", "KPVD", "Daily"),
    (306, "KBGR", "KBTV", "Mon,Wed,Fri"),
    (308, "KBGR", "KACK", "Tue,Thu,Sat,Sun"),
    (310, "KBGR", "KMVY", "Fri,Sat,Sun"),
    (312, "KBGR", "KBDL", "Daily"),
    (314, "KBGR", "KSYR", "Mon,Wed,Fri"),
    (316, "KBGR", "KROC", "Tue,Thu,Sat"),
    (318, "KBGR", "KPBG", "Mon,Fri"),
    # Hub 2: KSFB Spokes
    (400, "KSFB", "KEYW", "Daily"),
    (402, "KSFB", "KPNS", "Daily"),
    (404, "KSFB", "KTLH", "Daily"),
    (406, "KSFB", "KCHS", "Daily"),
    (408, "KSFB", "KSAV", "Mon,Wed,Fri,Sun"),
    (410, "KSFB", "KBHM", "Tue,Thu,Sat"),
    (412, "KSFB", "KGSP", "Mon,Wed,Fri"),
    (414, "KSFB", "KMYR", "Daily"),
    (416, "KSFB", "KAGS", "Tue,Thu,Sat"),
    (418, "KSFB", "KCAE", "Mon,Wed,Fri,Sun"),
    # Hub 3: TJBQ Spokes
    (500, "TJBQ", "TJSJ", "Daily"),
    (502, "TJBQ", "TIST", "Daily"),
    (504, "TJBQ", "TISX", "Daily"),
    (506, "TJBQ", "TJPS", "Daily"),
    (508, "TJBQ", "TJIG", "Daily"),
    (510, "TJBQ", "TNCM", "Mon,Wed,Fri,Sun"),
    (512, "TJBQ", "MDPC", "Daily"),
    (514, "TJBQ", "MDSD", "Daily"),
    (516, "TJBQ", "MBPV", "Tue,Thu,Sat"),
    (518, "TJBQ", "MYNN", "Mon,Fri"),
    # Hub 4: KIWA Spokes
    (600, "KIWA", "KLAS", "Daily"),
    (602, "KIWA", "KSAN", "Daily"),
    (604, "KIWA", "KPSP", "Daily"),
    (606, "KIWA", "KTUS", "Daily"),
    (608, "KIWA", "KFLG", "Daily"),
    (610, "KIWA", "KABQ", "Daily"),
    (612, "KIWA", "KSLC", "Daily"),
    (614, "KIWA", "KRNO", "Mon,Wed,Fri,Sun"),
    (616, "KIWA", "KFAT", "Tue,Thu,Sat"),
    (618, "KIWA", "KOAK", "Daily"),
    # Hub 5: KBLI Spokes
    (700, "KBLI", "KGEG", "Daily"),
    (702, "KBLI", "KYKM", "Mon,Wed,Fri"),
    (704, "KBLI", "KPSC", "Daily"),
    (706, "KBLI", "KEAT", "Tue,Thu,Sat"),
    (708, "KBLI", "KALW", "Mon,Fri"),
    (710, "KBLI", "KRDM", "Daily"),
    (712, "KBLI", "KEUG", "Daily"),
    (714, "KBLI", "KMFR", "Mon,Wed,Fri,Sun"),
    (716, "KBLI", "KOTH", "Tue,Thu,Sat"),
    (718, "KBLI", "KLWS", "Mon,Wed,Fri"),
    # Hub 6: PAFA Spokes
    (900, "PAFA", "PANC", "Daily"),
    (902, "PAFA", "PAJN", "Daily"),
    (904, "PAFA", "PAKT", "Mon,Wed,Fri,Sun"),
    (906, "PAFA", "PASI", "Tue,Thu,Sat"),
    (908, "PAFA", "PABR", "Daily"),
    (910, "PAFA", "PAOT", "Mon,Wed,Fri"),
    (912, "PAFA", "PAOM", "Daily"),
    (914, "PAFA", "PABE", "Mon,Wed,Fri,Sun"),
    (916, "PAFA", "PACV", "Tue,Thu,Sat"),
    (918, "PAFA", "PAPG", "Mon,Fri"),
    # Focus Cities
    (1000, "KSWF", "KALB", "Daily"),
    (1002, "KSWF", "KSYR", "Daily"),
    (1004, "KSWF", "KROC", "Mon,Wed,Fri"),
    (1006, "KSWF", "KBUF", "Daily"),
    (1008, "KSWF", "KBTV", "Tue,Thu,Sat"),
    (1010, "KSWF", "KMHT", "Daily"),
    (1012, "KSWF", "KPVD", "Daily"),
    (1014, "KSWF", "KORF", "Mon,Wed,Fri,Sun"),
    (1016, "KSWF", "KABE", "Daily"),
    (1018, "KSWF", "KAVP", "Tue,Thu,Sat"),
    (1100, "KRIC", "KROA", "Daily"),
    (1102, "KRIC", "KCHO", "Daily"),
    (1104, "KRIC", "KLYH", "Mon,Wed,Fri"),
    (1106, "KRIC", "KILM", "Daily"),
    (1108, "KRIC", "KEWN", "Tue,Thu,Sat"),
    (1110, "KRIC", "KOAJ", "Mon,Wed,Fri"),
    (1112, "KRIC", "KTRI", "Daily"),
    (1114, "KRIC", "KCHS", "Daily"),
    (1116, "KRIC", "KAVL", "Tue,Thu,Sat,Sun"),
    (1118, "KRIC", "KSBY", "Mon,Fri"),
    (1200, "KMSY", "KBTR", "Daily"),
    (1202, "KMSY", "KLFT", "Daily"),
    (1204, "KMSY", "KLCH", "Mon,Wed,Fri"),
    (1206, "KMSY", "KMOB", "Daily"),
    (1208, "KMSY", "KGPT", "Daily"),
    (1210, "KMSY", "KHSV", "Tue,Thu,Sat"),
    (1212, "KMSY", "KJAN", "Daily"),
    (1214, "KMSY", "KSHV", "Mon,Wed,Fri,Sun"),
    (1216, "KMSY", "KLIT", "Daily"),
    (1218, "KMSY", "KPNS", "Daily"),
    (1300, "KGRR", "KTVC", "Daily"),
    (1302, "KGRR", "KMQT", "Mon,Wed,Fri"),
    (1304, "KGRR", "KPLN", "Tue,Thu,Sat"),
    (1306, "KGRR", "KAZO", "Daily"),
    (1308, "KGRR", "KLAN", "Daily"),
    (1310, "KGRR", "KFNT", "Daily"),
    (1312, "KGRR", "KMSN", "Mon,Wed,Fri,Sun"),
    (1314, "KGRR", "KGRB", "Daily"),
    (1316, "KGRR", "KATW", "Tue,Thu,Sat"),
    (1318, "KGRR", "KSBN", "Daily"),
    (1400, "KOMA", "KLNK", "Daily"),
    (1402, "KOMA", "KGRI", "Daily"),
    (1404, "KOMA", "KEAR", "Mon,Wed,Fri"),
    (1406, "KOMA", "KLBF", "Tue,Thu,Sat"),
    (1408, "KOMA", "KBFF", "Mon,Fri"),
    (1410, "KOMA", "KSUX", "Daily"),
    (1412, "KOMA", "KFSD", "Daily"),
    (1414, "KOMA", "KDSM", "Daily"),
    (1416, "KOMA", "KCID", "Mon,Wed,Fri,Sun"),
    (1418, "KOMA", "KRST", "Tue,Thu,Sat"),
    (1500, "KPVU", "KCDC", "Daily"),
    (1502, "KPVU", "KSGU", "Daily"),
    (1504, "KPVU", "KEKO", "Mon,Wed,Fri"),
    (1506, "KPVU", "KPIH", "Daily"),
    (1508, "KPVU", "KIDA", "Daily"),
    (1510, "KPVU", "KTWF", "Tue,Thu,Sat"),
    (1512, "KPVU", "KBOI", "Daily"),
    (1514, "KPVU", "KJAC", "Mon,Wed,Fri,Sun"),
    (1516, "KPVU", "KWYS", "Fri,Sat,Sun"),
    (1518, "KPVU", "KBZN", "Daily"),
    # International
    (800, "KBGR", "CYHZ", "Daily"),
    (802, "KBGR", "CYUL", "Daily"),
    (804, "KBGR", "CYYT", "Mon,Wed,Fri"),
    (806, "KBGR", "TXKF", "Tue,Thu,Sat,Sun"),
    (808, "KBGR", "EINN", "Mon,Wed,Fri,Sun"),
    (810, "KSFB", "MYNN", "Daily"),
    (812, "KSFB", "MKJS", "Daily"),
    (814, "KSFB", "MBPV", "Tue,Thu,Sat"),
    (816, "KSFB", "MROC", "Mon,Wed,Fri,Sun"),
    (818, "KSFB", "MPTO", "Tue,Thu,Sat"),
    (820, "TJBQ", "MDPC", "Daily"),
    (822, "TJBQ", "TNCM", "Daily"),
    (824, "TJBQ", "SKBO", "Mon,Wed,Fri"),
    (826, "TJBQ", "TAPA", "Tue,Thu,Sat"),
    (828, "TJBQ", "MYNN", "Mon,Fri"),
    (830, "KIWA", "MMSD", "Daily"),
    (832, "KIWA", "MMPR", "Daily"),
    (834, "KIWA", "MMME", "Mon,Wed,Fri,Sun"),
    (836, "KIWA", "MMGL", "Tue,Thu,Sat"),
    (838, "KIWA", "MMMX", "Daily"),
    (840, "KBLI", "CYVR", "Daily"),
    (842, "KBLI", "CYYJ", "Daily"),
    (844, "KBLI", "CYYC", "Daily"),
    (846, "KBLI", "CYEG", "Mon,Wed,Fri,Sun"),
    (848, "KBLI", "MMSD", "Tue,Thu,Sat"),
    (850, "PAFA", "CYXY", "Mon,Wed,Fri"),
    (852, "PAFA", "CYZF", "Tue,Thu,Sat"),
    (854, "PAFA", "CYEG", "Mon,Wed,Fri,Sun"),
    (856, "PAFA", "RJAA", "Wed,Fri,Sun"),
    (858, "PAFA", "RKSI", "Tue,Thu,Sat"),
    (860, "KBGR", "EGSS", "Daily"),
    (862, "KBGR", "LFOB", "Mon,Wed,Fri,Sun"),
    (864, "KBGR", "LIME", "Tue,Thu,Sat"),
    (866, "KBGR", "EICK", "Mon,Wed,Fri"),
    (868, "KBGR", "LEGE", "Tue,Thu,Sat,Sun"),
    (870, "KBGR", "EDJA", "Mon,Thu,Sat"),
]


@st.cache_data
def get_full_network():
    network = []
    for flt, orig, dest, days in routes_raw:
        network.append(
            {"Flight": flt, "Origin": orig, "Destination": dest, "Days": days}
        )
        network.append(
            {
                "Flight": flt + 1,
                "Origin": dest,
                "Destination": orig,
                "Days": days,
            }
        )
    return network


# ==========================================
# 3. ROUTE FINDER ENGINE
# ==========================================


def find_routes(network, origin, destination, max_connections=10):
    origin = origin.upper()
    destination = destination.upper()

    queue = deque()
    for leg in network:
        if leg["Origin"] == origin:
            queue.append([leg])

    valid_paths = []

    while queue:
        path = queue.popleft()
        current_node = path[-1]["Destination"]
        connections = len(path) - 1

        if current_node == destination:
            valid_paths.append(path)
            if len(valid_paths) >= 15:
                break
            continue

        if max_connections is not None and connections >= max_connections:
            continue

        visited_airports = {leg["Origin"] for leg in path}
        visited_airports.add(current_node)

        for nxt in network:
            if (
                nxt["Origin"] == current_node
                and nxt["Destination"] not in visited_airports
            ):
                queue.append(path + [nxt])

    return valid_paths


# ==========================================
# 4. APP UI
# ==========================================

st.markdown(
    """
<div class="skybus-header">
    <h1>✈️ SKYBUS AIRLINES</h1>
    <p style="margin:4px 0 0 0; opacity: 0.9;">Network Route Search & Mobile Boarding System</p>
</div>
""",
    unsafe_allow_html=True,
)

p_col1, p_col2 = st.columns(2)
with p_col1:
    st.markdown(
        """
    <div class="info-card">
        <div style="font-size: 11px; color: #888; font-weight: bold; text-transform: uppercase;">Passenger</div>
        <div style="font-size: 18px; font-weight: bold; color: #111;">👤 John Bowman</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with p_col2:
    st.markdown(
        """
    <div class="info-card">
        <div style="font-size: 11px; color: #888; font-weight: bold; text-transform: uppercase;">In-Flight Wi-Fi</div>
        <div style="font-size: 18px; font-weight: bold; color: #FF5722;">📶 High-Speed SkyFly</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

network = get_full_network()
all_airports = sorted(list(set([f["Origin"] for f in network])))

st.subheader("🔍 Search Any Route on Network Map")

col1, col2, col3 = st.columns(3)
with col1:
    orig_select = st.selectbox(
        "Origin Airport",
        options=all_airports,
        index=all_airports.index("KRIC") if "KRIC" in all_airports else 0,
    )
with col2:
    dest_select = st.selectbox(
        "Destination Airport",
        options=all_airports,
        index=all_airports.index("PANC") if "PANC" in all_airports else 1,
    )
with col3:
    max_conn_str = st.selectbox(
        "Max Connections Allowed",
        options=[
            "Unlimited / Up to 10",
            "1 Connection",
            "2 Connections",
            "3 Connections",
            "4 Connections",
        ],
        index=0,
    )

if "1 " in max_conn_str:
    max_conn = 1
elif "2 " in max_conn_str:
    max_conn = 2
elif "3 " in max_conn_str:
    max_conn = 3
elif "4 " in max_conn_str:
    max_conn = 4
else:
    max_conn = 10

if st.button("Search Route Options", type="primary"):
    if orig_select == dest_select:
        st.warning("Please choose two different airports.")
    else:
        routes_found = find_routes(
            network, orig_select, dest_select, max_connections=max_conn
        )
        st.session_state["search_results"] = routes_found
        st.session_state["search_orig"] = orig_select
        st.session_state["search_dest"] = dest_select

# ==========================================
# 5. SEARCH RESULTS
# ==========================================

if "search_results" in st.session_state:
    results = st.session_state["search_results"]
    orig = st.session_state["search_orig"]
    dest = st.session_state["search_dest"]

    st.markdown("---")
    st.markdown(
        f"### Possible Routes for **{orig} ➔ {dest}** ({len(results)} option(s) found)"
    )

    if not results:
        st.info(
            f"No routes found connecting {orig} to {dest} within {max_conn} connections."
        )
    else:
        itinerary_labels = []
        for i, path in enumerate(results):
            stops = len(path) - 1
            stop_str = "Nonstop" if stops == 0 else f"{stops} Connection(s)"
            leg_chain = " ➔ ".join(
                [f"{leg['Origin']}" for leg in path]
                + [path[-1]["Destination"]]
            )
            itinerary_labels.append(f"Option {i+1} [{stop_str}]: {leg_chain}")

        selected_option_idx = st.radio(
            "Select an option to view leg details and issue boarding pass:",
            range(len(itinerary_labels)),
            format_func=lambda x: itinerary_labels[x],
        )

        selected_path = results[selected_option_idx]

        st.markdown(
            f"#### 📋 Leg Breakdown for Option {selected_option_idx + 1}"
        )
        for idx, leg in enumerate(selected_path, 1):
            st.write(
                f"**Leg {idx}:** Flight **#{leg['Flight']}** | `{leg['Origin']}` ➔ `{leg['Destination']}` | Operating Days: *{leg['Days']}*"
            )

        st.session_state["selected_itinerary"] = selected_path


# ==========================================
# 6. MOBILE BOARDING PASS
# ==========================================

if "selected_itinerary" in st.session_state:
    st.markdown("---")
    st.subheader("📲 Mobile Boarding Pass")

    path = st.session_state["selected_itinerary"]

    selected_leg_index = 0
    if len(path) > 1:
        leg_names = [
            f"Leg {i+1}: {leg['Origin']} ➔ {leg['Destination']} (Flight #{leg['Flight']})"
            for i, leg in enumerate(path)
        ]
        selected_leg_index = st.selectbox(
            "Select Flight Leg for Pass:",
            range(len(leg_names)),
            format_func=lambda x: leg_names[x],
        )

    active_leg = path[selected_leg_index]
    assigned_seat = get_random_seat(active_leg["Flight"])
    assigned_gate = get_random_gate(active_leg["Flight"])
    today_date = datetime.now().strftime("%d %b %Y").upper()

    card_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: transparent;
            margin: 0;
            padding: 10px;
        }}
        .boarding-pass-card {{
            max-width: 420px;
            margin: 0 auto;
            background: #ffffff;
            border: 2px solid #FF5722;
            border-radius: 14px;
            overflow: hidden;
            box-shadow: 0 6px 18px rgba(0,0,0,0.12);
        }}
        .bp-header {{
            background-color: #FF5722;
            color: white;
            padding: 14px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .bp-body {{
            padding: 18px;
            color: #222;
        }}
        .bp-field {{
            font-size: 11px;
            color: #777;
            text-transform: uppercase;
            font-weight: 700;
            margin-bottom: 2px;
        }}
        .bp-value {{
            font-size: 15px;
            font-weight: 700;
            color: #111;
        }}
        .barcode {{
            font-family: 'Courier New', Courier, monospace;
            background: #f8f9fa;
            letter-spacing: 4px;
            padding: 10px;
            text-align: center;
            border-radius: 6px;
            font-weight: bold;
            margin-top: 15px;
            border: 1px dashed #ccc;
            font-size: 12px;
        }}
    </style>
    </head>
    <body>
        <div class="boarding-pass-card">
            <div class="bp-header">
                <div>
                    <span style="font-size: 18px; font-weight: 800; letter-spacing: 1px;">SKYBUS</span>
                    <span style="font-size: 10px; margin-left: 6px; background: rgba(255,255,255,0.25); padding: 3px 7px; border-radius: 10px;">MOBILE PASS</span>
                </div>
                <div style="font-weight: bold; font-size: 14px;">Flight #{active_leg['Flight']}</div>
            </div>
            <div class="bp-body">
                <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #eee; padding-bottom: 10px; margin-bottom: 10px;">
                    <div>
                        <div class="bp-field">Passenger Name</div>
                        <div class="bp-value">John Bowman</div>
                    </div>
                    <div style="text-align: right;">
                        <div class="bp-field">Wi-Fi Access</div>
                        <div class="bp-value" style="color: #FF5722;">High-Speed SkyFly</div>
                    </div>
                </div>
                
                <div style="display: flex; justify-content: space-between; align-items: center; margin: 12px 0;">
                    <div>
                        <div style="font-size: 30px; font-weight: 900; color: #111;">{active_leg['Origin']}</div>
                        <div class="bp-field">Departure</div>
                    </div>
                    <div style="font-size: 22px; color: #FF5722;">✈️</div>
                    <div style="text-align: right;">
                        <div style="font-size: 30px; font-weight: 900; color: #111;">{active_leg['Destination']}</div>
                        <div class="bp-field">Arrival</div>
                    </div>
                </div>

                <div style="display: flex; justify-content: space-between; background: #F8F9FA; padding: 10px; border-radius: 8px; text-align: center;">
                    <div>
                        <div class="bp-field">Date</div>
                        <div class="bp-value">{today_date}</div>
                    </div>
                    <div>
                        <div class="bp-field">Gate</div>
                        <div class="bp-value">{assigned_gate}</div>
                    </div>
                    <div>
                        <div class="bp-field">Zone</div>
                        <div class="bp-value">Zone 1</div>
                    </div>
                    <div>
                        <div class="bp-field">Seat</div>
                        <div class="bp-value" style="color: #FF5722;">{assigned_seat}</div>
                    </div>
                </div>

                <div class="barcode">
                    ||| | ||||| ||| |||| || ||||| ||||| ||| ||||||| | ||||
                    <br>
                    <span style="font-size: 10px; color: #777; font-family: sans-serif; letter-spacing: normal;">SKYB-{active_leg['Flight']}-JOHN-BOWMAN</span>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    components.html(card_html, height=390)
