from collections import deque
from datetime import datetime
import random
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
# 2. UPDATED FULL NETWORK DATASET
# ==========================================

routes_raw = [
    # ----------------------------------------------------
    # I. INTER-HUB DIRECT EXPRESS ROUTES (SX 100 - SX 231)
    # Full Mesh Network Across All 12 Hubs
    # ----------------------------------------------------
    (100, "PAFA", "KBLI", "Daily"),  # SX 100 / SX 101
    (102, "PAFA", "KIWA", "Daily"),  # SX 102 / SX 103
    (104, "PAFA", "KPVU", "Daily"),  # SX 104 / SX 105
    (106, "PAFA", "KOMA", "Daily"),  # SX 106 / SX 107
    (108, "PAFA", "KMSY", "Daily"),  # SX 108 / SX 109
    (110, "PAFA", "KGRR", "Daily"),  # SX 110 / SX 111
    (112, "PAFA", "KSWF", "Daily"),  # SX 112 / SX 113
    (114, "PAFA", "KBGR", "Daily"),  # SX 114 / SX 115
    (116, "PAFA", "KRIC", "Daily"),  # SX 116 / SX 117
    (118, "PAFA", "KSFB", "Daily"),  # SX 118 / SX 119
    (120, "PAFA", "TJBQ", "Daily"),  # SX 120 / SX 121
    (122, "KBLI", "KIWA", "Daily"),  # SX 122 / SX 123
    (124, "KBLI", "KPVU", "Daily"),  # SX 124 / SX 125
    (126, "KBLI", "KOMA", "Daily"),  # SX 126 / SX 127
    (128, "KBLI", "KMSY", "Daily"),  # SX 128 / SX 129
    (130, "KBLI", "KGRR", "Daily"),  # SX 130 / SX 131
    (132, "KBLI", "KSWF", "Daily"),  # SX 132 / SX 133
    (134, "KBLI", "KBGR", "Daily"),  # SX 134 / SX 135
    (136, "KBLI", "KRIC", "Daily"),  # SX 136 / SX 137
    (138, "KBLI", "KSFB", "Daily"),  # SX 138 / SX 139
    (140, "KBLI", "TJBQ", "Daily"),  # SX 140 / SX 141
    (142, "KIWA", "KPVU", "Daily"),  # SX 142 / SX 143
    (144, "KIWA", "KOMA", "Daily"),  # SX 144 / SX 145
    (146, "KIWA", "KMSY", "Daily"),  # SX 146 / SX 147
    (148, "KIWA", "KGRR", "Daily"),  # SX 148 / SX 149
    (150, "KIWA", "KSWF", "Daily"),  # SX 150 / SX 151
    (152, "KIWA", "KBGR", "Daily"),  # SX 152 / SX 153
    (154, "KIWA", "KRIC", "Daily"),  # SX 154 / SX 155
    (156, "KIWA", "KSFB", "Daily"),  # SX 156 / SX 157
    (158, "KIWA", "TJBQ", "Daily"),  # SX 158 / SX 159
    (160, "KPVU", "KOMA", "Daily"),  # SX 160 / SX 161
    (162, "KPVU", "KMSY", "Daily"),  # SX 162 / SX 163
    (164, "KPVU", "KGRR", "Daily"),  # SX 164 / SX 165
    (166, "KPVU", "KSWF", "Daily"),  # SX 166 / SX 167
    (168, "KPVU", "KBGR", "Daily"),  # SX 168 / SX 169
    (170, "KPVU", "KRIC", "Daily"),  # SX 170 / SX 171
    (172, "KPVU", "KSFB", "Daily"),  # SX 172 / SX 173
    (174, "KPVU", "TJBQ", "Daily"),  # SX 174 / SX 175
    (176, "KOMA", "KMSY", "Daily"),  # SX 176 / SX 177
    (178, "KOMA", "KGRR", "Daily"),  # SX 178 / SX 179
    (180, "KOMA", "KSWF", "Daily"),  # SX 180 / SX 181
    (182, "KOMA", "KBGR", "Daily"),  # SX 182 / SX 183
    (184, "KOMA", "KRIC", "Daily"),  # SX 184 / SX 185
    (186, "KOMA", "KSFB", "Daily"),  # SX 186 / SX 187
    (188, "KOMA", "TJBQ", "Daily"),  # SX 188 / SX 189
    (190, "KMSY", "KGRR", "Daily"),  # SX 190 / SX 191
    (192, "KMSY", "KSWF", "Daily"),  # SX 192 / SX 193
    (194, "KMSY", "KBGR", "Daily"),  # SX 194 / SX 195
    (196, "KMSY", "KRIC", "Daily"),  # SX 196 / SX 197
    (198, "KMSY", "KSFB", "Daily"),  # SX 198 / SX 199
    (200, "KMSY", "TJBQ", "Daily"),  # SX 200 / SX 201
    (202, "KGRR", "KSWF", "Daily"),  # SX 202 / SX 203
    (204, "KGRR", "KBGR", "Daily"),  # SX 204 / SX 205
    (206, "KGRR", "KRIC", "Daily"),  # SX 206 / SX 207
    (208, "KGRR", "KSFB", "Daily"),  # SX 208 / SX 209
    (210, "KGRR", "TJBQ", "Daily"),  # SX 210 / SX 211
    (212, "KSWF", "KBGR", "Daily"),  # SX 212 / SX 213
    (214, "KSWF", "KRIC", "Daily"),  # SX 214 / SX 215
    (216, "KSWF", "KSFB", "Daily"),  # SX 216 / SX 217
    (218, "KSWF", "TJBQ", "Daily"),  # SX 218 / SX 219
    (220, "KBGR", "KRIC", "Daily"),  # SX 220 / SX 221
    (222, "KBGR", "KSFB", "Daily"),  # SX 222 / SX 223
    (224, "KBGR", "TJBQ", "Daily"),  # SX 224 / SX 225
    (226, "KRIC", "KSFB", "Daily"),  # SX 226 / SX 227
    (228, "KRIC", "TJBQ", "Daily"),  # SX 228 / SX 229
    (230, "KSFB", "TJBQ", "Daily"),  # SX 230 / SX 231
    # ----------------------------------------------------
    # II. GEOGRAPHIC BRIDGE CONNECTORS & REGIONAL SPOKES
    # ----------------------------------------------------
    # PAFA Bridge Spokes
    (300, "PAFA", "PAJN", "Daily"),
    (302, "PAFA", "PAKT", "Daily"),
    (304, "PAFA", "PANC", "Daily"),
    (306, "PAFA", "PABR", "Daily"),
    # KBLI Bridge Spokes
    (320, "KBLI", "PAJN", "Daily"),
    (322, "KBLI", "PAKT", "Daily"),
    (324, "KBLI", "KBOI", "Daily"),
    (326, "KBLI", "KGEG", "Daily"),
    # KPVU Bridge Spokes
    (340, "KPVU", "KBOI", "Daily"),
    (342, "KPVU", "KSGU", "Daily"),
    (344, "KPVU", "KLAS", "Daily"),
    (346, "KPVU", "KJAC", "Daily"),
    # KIWA Bridge Spokes
    (360, "KIWA", "KSGU", "Daily"),
    (362, "KIWA", "KLAS", "Daily"),
    (364, "KIWA", "KELP", "Daily"),
    (366, "KIWA", "KSAT", "Daily"),
    (368, "KIWA", "KSAN", "Daily"),
    # KMSY Bridge Spokes
    (380, "KMSY", "KELP", "Daily"),
    (382, "KMSY", "KSAT", "Daily"),
    (384, "KMSY", "KSGF", "Daily"),
    (386, "KMSY", "KLIT", "Daily"),
    (388, "KMSY", "KPNS", "Daily"),
    # KOMA Bridge Spokes
    (400, "KOMA", "KMLI", "Daily"),
    (402, "KOMA", "KSGF", "Daily"),
    (404, "KOMA", "KLIT", "Daily"),
    (406, "KOMA", "KFSD", "Daily"),
    # KGRR Bridge Spokes
    (420, "KGRR", "KMLI", "Daily"),
    (422, "KGRR", "KPNS", "Daily"),
    (424, "KGRR", "KPIT", "Daily"),
    (426, "KGRR", "KCAK", "Daily"),
    (428, "KGRR", "KTVC", "Daily"),
    # KSWF Bridge Spokes
    (440, "KSWF", "KABE", "Daily"),
    (442, "KSWF", "KMDT", "Daily"),
    (444, "KSWF", "KPWM", "Daily"),
    (446, "KSWF", "KCAK", "Daily"),
    (448, "KSWF", "KPVD", "Daily"),
    # KBGR Bridge Spokes
    (460, "KBGR", "KPWM", "Daily"),
    (462, "KBGR", "KBOS", "Daily"),
    (464, "KBGR", "KPVD", "Daily"),
    # KRIC Bridge Spokes
    (480, "KRIC", "KCHS", "Daily"),
    (482, "KRIC", "KILM", "Daily"),
    (484, "KRIC", "KABE", "Daily"),
    (486, "KRIC", "KMDT", "Daily"),
    (488, "KRIC", "KPIT", "Daily"),
    (490, "KRIC", "KROA", "Daily"),
    # KSFB Bridge Spokes
    (500, "KSFB", "KCHS", "Daily"),
    (502, "KSFB", "KILM", "Daily"),
    (504, "KSFB", "KPNS", "Daily"),
    (506, "KSFB", "KEYW", "Daily"),
    (508, "KSFB", "MDPC", "Daily"),
    (510, "KSFB", "MBPV", "Daily"),
    # ----------------------------------------------------
    # III. TJBQ CARIBBEAN REGIONAL SPOKES (SX 850 - SX 869)
    # ----------------------------------------------------
    (850, "TJBQ", "TJSJ", "Daily"),  # San Juan, PR
    (852, "TJBQ", "TJPS", "Daily"),  # Ponce, PR
    (854, "TJBQ", "TIST", "Daily"),  # St. Thomas, USVI
    (856, "TJBQ", "TISX", "Daily"),  # St. Croix, USVI
    (858, "TJBQ", "TNCM", "Daily"),  # St. Maarten
    (860, "TJBQ", "TKPK", "Daily"),  # St. Kitts
    (862, "TJBQ", "TFFR", "Daily"),  # Guadeloupe
    (864, "TJBQ", "TFFF", "Daily"),  # Martinique
    (866, "TJBQ", "TQPF", "Daily"),  # Anguilla
    (868, "TJBQ", "TAPA", "Daily"),  # Antigua
]


@st.cache_data
def get_full_network():
    network = []
    for flt, orig, dest, days in routes_raw:
        orig_clean = str(orig).strip().upper()
        dest_clean = str(dest).strip().upper()

        # Outbound Leg
        network.append(
            {
                "Flight": int(flt),
                "Origin": orig_clean,
                "Destination": dest_clean,
                "Days": str(days),
            }
        )
        # Inbound Return Leg (Auto-generated)
        network.append(
            {
                "Flight": int(flt) + 1,
                "Origin": dest_clean,
                "Destination": orig_clean,
                "Days": str(days),
            }
        )
    return network


# ==========================================
# 3. DIVERSIFIED ROUTE FINDER ENGINE
# ==========================================


def find_routes(network, origin, destination, max_connections=10):
    origin = origin.strip().upper()
    destination = destination.strip().upper()

    queue = deque()
    for leg in network:
        if leg["Origin"] == origin:
            queue.append([leg])

    valid_paths = []
    max_search_depth = max_connections if max_connections is not None else 10

    while queue:
        path = queue.popleft()
        current_node = path[-1]["Destination"]
        connections = len(path) - 1

        if current_node == destination:
            valid_paths.append(path)
            if len(valid_paths) >= 300:
                break
            continue

        if connections >= max_search_depth:
            continue

        visited_airports = {leg["Origin"] for leg in path}
        visited_airports.add(current_node)

        for nxt in network:
            if (
                nxt["Origin"] == current_node
                and nxt["Destination"] not in visited_airports
            ):
                queue.append(path + [nxt])

    if not valid_paths:
        return []

    # Sort paths by shortest leg count first
    valid_paths.sort(key=lambda p: len(p))

    # Diversify connecting hubs for multi-stop routes
    paths_by_first_hub = {}
    for path in valid_paths:
        first_hub = path[0]["Destination"]
        if first_hub not in paths_by_first_hub:
            paths_by_first_hub[first_hub] = []
        paths_by_first_hub[first_hub].append(path)

    diverse_paths = []
    added_signatures = set()

    for hub, paths in paths_by_first_hub.items():
        best_path = paths[0]
        sig = tuple(
            (leg["Flight"], leg["Origin"], leg["Destination"])
            for leg in best_path
        )
        diverse_paths.append(best_path)
        added_signatures.add(sig)

    for path in valid_paths:
        if len(diverse_paths) >= 15:
            break
        sig = tuple(
            (leg["Flight"], leg["Origin"], leg["Destination"]) for leg in path
        )
        if sig not in added_signatures:
            diverse_paths.append(path)
            added_signatures.add(sig)

    diverse_paths.sort(key=lambda p: len(p))
    return diverse_paths[:15]


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
                f"**Leg {idx}:** Flight **SX #{leg['Flight']}** | `{leg['Origin']}` ➔ `{leg['Destination']}` | Operating Days: *{leg['Days']}*"
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
            f"Leg {i+1}: {leg['Origin']} ➔ {leg['Destination']} (Flight SX #{leg['Flight']})"
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
                <div style="font-weight: bold; font-size: 14px;">SX #{active_leg['Flight']}</div>
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
