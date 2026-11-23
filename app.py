import random
from datetime import datetime
from collections import deque, defaultdict
import math
import streamlit as st
import streamlit.components.v1 as components

# ==========================================
# 1. PAGE CONFIG, SESSION STATE & COLOR SETTINGS
# ==========================================
st.set_page_config(
    page_title="Skybus Route & Boarding System",
    page_icon="✈️",
    layout="wide"
)

# Live seat-booking tracker across Streamlit reruns
if "booked_seats" not in st.session_state:
    st.session_state.booked_seats = {}  # {int(flight_num): seats_booked_in_session}

# Custom accent color matching the logo (#F28425)
ACCENT_COLOR = "#F28425"

# Styling using your custom accent color + fare bucket badges
st.markdown(f"""
<style>
.skybus-banner {{
    background-color: {ACCENT_COLOR};
    width: 100%;
    padding: 5px 0px;
    border-radius: 10px;
    text-align: center;
    margin-bottom: 20px;
    box-shadow: 0 4px 12px rgba(242, 132, 37, 0.25);
}}
.skybus-banner img {{
    max-height: 240px;
    width: auto;
}}
.info-card {{
    background: #FFFFFF;
    border-left: 5px solid {ACCENT_COLOR};
    padding: 12px 18px;
    border-radius: 6px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.06);
    margin-bottom: 20px;
}}
.fare-badge {{
    display: inline-block;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.4px;
    text-transform: uppercase;
}}
.fare-bird10 {{
    background-color: {ACCENT_COLOR};
    color: #FFFFFF;
}}
.fare-standard {{
    background-color: #F3F4F6;
    color: #1F2937;
    border: 1px solid #D1D5DB;
}}
.scarcity-pill {{
    color: #B45309;
    font-size: 12px;
    font-weight: 600;
}}
</style>
""", unsafe_allow_html=True)

# 1. Full-Width Banner with Centered Logo
st.markdown("""
<div class="skybus-banner">
    <img src="https://raw.githubusercontent.com/johnbowman5190-netizen/Skybus-Flights/main/Untitled%20drawing.png" alt="Skybus Logo">
</div>
""", unsafe_allow_html=True)

# 2. Passenger Info & Rewards Card Below Banner
st.markdown(
    """
    <div class="info-card">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
            <div>
                <div style="font-size: 11px; color: #888; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px;">Passenger</div>
                <div style="font-size: 18px; font-weight: bold; color: #111;">👤 John Bowman</div>
            </div>
            <div>
                <div style="font-size: 11px; color: #888; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px;">Monarch Miles Rewards #</div>
                <div style="font-size: 16px; font-weight: bold; color: #F28425;">👑 6827165938</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")


def get_random_seat(flight_num):
    random.seed(int(flight_num) + 42)
    # Exclude row 13 for realism
    valid_rows = [r for r in range(1, 33) if r != 13]
    row = random.choice(valid_rows)
    letter = random.choice(["A", "B", "C", "D", "E", "F"])
    return f"{row}{letter}"


def get_random_gate(flight_num):
    random.seed(int(flight_num) + 99)
    concourse = random.choice(["A", "B", "C", "D"])
    gate_num = random.randint(1, 25)
    return f"{concourse}{gate_num}"

def get_seats_sold(flight_num, capacity=180):
    """Returns deterministic baseline cabin load + live session bookings for a flight."""
    f_id = int(flight_num)
    random.seed(f_id + 77)
    # ~55% of flights still have 1-8 $10 BIRD-10 seats available; others step into higher buckets
    if random.random() < 0.55:
        baseline = random.randint(2, 9)
    else:
        baseline = random.randint(10, int(capacity * 0.78))
    live_booked = st.session_state.booked_seats.get(f_id, 0)
    return min(capacity, baseline + live_booked)

# ==========================================
# 2. UPDATED FULL NETWORK DATASET
# ==========================================

routes_raw = [
    # ----------------------------------------------------
    # I. INTER-HUB DIRECT EXPRESS ROUTES (SX 100 - SX 208)
    # Full Mesh Network Across All 12 Hubs
    # ----------------------------------------------------
    (100, "PAFA", "KBLI", "Daily"),  # SX 100 / SX 101
    (102, "PAFA", "KONT", "Daily"),  # SX 102 / SX 103
    (104, "PAFA", "KIWA", "Daily"),  # SX 104 / SX 105
    (106, "PAFA", "KPVU", "Daily"),  # SX 106 / SX 107
    (108, "PAFA", "KCOS", "Daily"),  # SX 108 / SX 109
    (110, "PAFA", "KBGR", "Daily"),  # SX 110 / SX 111
    (112, "KBLI", "KONT", "Daily"),  # SX 112 / SX 113
    (114, "KBLI", "KIWA", "Daily"),  # SX 114 / SX 115
    (116, "KBLI", "KPVU", "Daily"),  # SX 116 / SX 117
    (118, "KBLI", "KCOS", "Daily"),  # SX 118 / SX 119
    (120, "KBLI", "KSAT", "Daily"),  # SX 120 / SX 121
    (122, "KBLI", "KOMA", "Daily"),  # SX 122 / SX 123
    (124, "KBLI", "KMSY", "Daily"),  # SX 124 / SX 125
    (126, "KBLI", "KGRR", "Daily"),  # SX 126 / SX 127
    (128, "KBLI", "KTYS", "Daily"),  # SX 128 / SX 129
    (130, "KBLI", "KSWF", "Daily"),  # SX 130 / SX 131
    (132, "KBLI", "KBGR", "Daily"),  # SX 132 / SX 133
    (134, "KBLI", "KRIC", "Daily"),  # SX 134 / SX 135
    (136, "KBLI", "KSFB", "Daily"),  # SX 136 / SX 137
    (138, "KONT", "KIWA", "Daily"),  # SX 138 / SX 139
    (140, "KONT", "KPVU", "Daily"),  # SX 140 / SX 141
    (142, "KONT", "KCOS", "Daily"),  # SX 142 / SX 143
    (144, "KONT", "KSAT", "Daily"),  # SX 144 / SX 145
    (146, "KONT", "KOMA", "Daily"),  # SX 146 / SX 147
    (148, "KONT", "KMSY", "Daily"),  # SX 148 / SX 149
    (150, "KONT", "KGRR", "Daily"),  # SX 150 / SX 151
    (152, "KONT", "KTYS", "Daily"),  # SX 152 / SX 153
    (154, "KONT", "KSWF", "Daily"),  # SX 154 / SX 155
    (156, "KONT", "KBGR", "Daily"),  # SX 156 / SX 157
    (158, "KONT", "KRIC", "Daily"),  # SX 158 / SX 159
    (160, "KONT", "KSFB", "Daily"),  # SX 160 / SX 161
    (162, "KIWA", "KPVU", "Daily"),  # SX 162 / SX 163
    (164, "KIWA", "KCOS", "Daily"),  # SX 164 / SX 165
    (166, "KIWA", "KSAT", "Daily"),  # SX 166 / SX 167
    (168, "KIWA", "KOMA", "Daily"),  # SX 168 / SX 169
    (170, "KIWA", "KMSY", "Daily"),  # SX 170 / SX 171
    (172, "KIWA", "KGRR", "Daily"),  # SX 172 / SX 173
    (174, "KIWA", "KTYS", "Daily"),  # SX 174 / SX 175
    (176, "KIWA", "KSWF", "Daily"),  # SX 176 / SX 177
    (178, "KIWA", "KBGR", "Daily"),  # SX 178 / SX 179
    (180, "KIWA", "KRIC", "Daily"),  # SX 180 / SX 181
    (182, "KIWA", "KSFB", "Daily"),  # SX 182 / SX 183
    (184, "KPVU", "KCOS", "Daily"),  # SX 184 / SX 185
    (186, "KPVU", "KSAT", "Daily"),  # SX 186 / SX 187
    (188, "KPVU", "KOMA", "Daily"),  # SX 188 / SX 189
    (190, "KPVU", "KMSY", "Daily"),  # SX 190 / SX 191
    (192, "KPVU", "KGRR", "Daily"),  # SX 192 / SX 193
    (194, "KPVU", "KTYS", "Daily"),  # SX 194 / SX 195
    (196, "KPVU", "KSWF", "Daily"),  # SX 196 / SX 197
    (198, "KPVU", "KBGR", "Daily"),  # SX 198 / SX 199
    (200, "KPVU", "KRIC", "Daily"),  # SX 200 / SX 201
    (202, "KPVU", "KSFB", "Daily"),  # SX 202 / SX 203
    (204, "KCOS", "KSAT", "Daily"),  # SX 204 / SX 205
    (206, "KCOS", "KOMA", "Daily"),  # SX 206 / SX 207
    (208, "KCOS", "KMSY", "Daily"),  # SX 208 / SX 209
    (210, "KCOS", "KGRR", "Daily"),  # SX 210 / SX 211
    (212, "KCOS", "KTYS", "Daily"),  # SX 212 / SX 213
    (214, "KCOS", "KSWF", "Daily"),  # SX 214 / SX 215
    (216, "KCOS", "KBGR", "Daily"),  # SX 216 / SX 217
    (218, "KCOS", "KRIC", "Daily"),  # SX 218 / SX 219
    (220, "KCOS", "KSFB", "Daily"),  # SX 220 / SX 221
    (222, "KSAT", "KOMA", "Daily"),  # SX 222 / SX 223
    (224, "KSAT", "KMSY", "Daily"),  # SX 224 / SX 225
    (226, "KSAT", "KGRR", "Daily"),  # SX 226 / SX 227
    (228, "KSAT", "KTYS", "Daily"),  # SX 228 / SX 229
    (230, "KSAT", "KSWF", "Daily"),  # SX 230 / SX 231
    (232, "KSAT", "KBGR", "Daily"),  # SX 232 / SX 233
    (234, "KSAT", "KRIC", "Daily"),  # SX 234 / SX 235
    (236, "KSAT", "KSFB", "Daily"),  # SX 236 / SX 237
    (238, "KOMA", "KMSY", "Daily"),  # SX 238 / SX 239
    (240, "KOMA", "KGRR", "Daily"),  # SX 240 / SX 241
    (242, "KOMA", "KTYS", "Daily"),  # SX 242 / SX 243
    (244, "KOMA", "KSWF", "Daily"),  # SX 244 / SX 245
    (246, "KOMA", "KBGR", "Daily"),  # SX 246 / SX 247
    (248, "KOMA", "KRIC", "Daily"),  # SX 248 / SX 249
    (250, "KOMA", "KSFB", "Daily"),  # SX 250 / SX 251
    (252, "KMSY", "KGRR", "Daily"),  # SX 252 / SX 253
    (254, "KMSY", "KTYS", "Daily"),  # SX 254 / SX 255
    (256, "KMSY", "KSWF", "Daily"),  # SX 256 / SX 257
    (258, "KMSY", "KBGR", "Daily"),  # SX 258 / SX 259
    (260, "KMSY", "KRIC", "Daily"),  # SX 260 / SX 261
    (262, "KMSY", "KSFB", "Daily"),  # SX 262 / SX 263
    (264, "KMSY", "TJBQ", "Daily"),  # SX 264 / SX 265
    (266, "KGRR", "KTYS", "Daily"),  # SX 266 / SX 267
    (268, "KGRR", "KSWF", "Daily"),  # SX 268 / SX 269
    (270, "KGRR", "KBGR", "Daily"),  # SX 270 / SX 271
    (272, "KGRR", "KRIC", "Daily"),  # SX 272 / SX 273
    (274, "KGRR", "KSFB", "Daily"),  # SX 274 / SX 275
    (276, "KGRR", "TJBQ", "Daily"),  # SX 276 / SX 277
    (278, "KTYS", "KSWF", "Daily"),  # SX 278 / SX 279
    (280, "KTYS", "KBGR", "Daily"),  # SX 280 / SX 281
    (282, "KTYS", "KRIC", "Daily"),  # SX 282 / SX 283
    (284, "KTYS", "KSFB", "Daily"),  # SX 284 / SX 285
    (286, "KTYS", "TJBQ", "Daily"),  # SX 286 / SX 287
    (288, "KSWF", "KBGR", "Daily"),  # SX 288 / SX 289
    (290, "KSWF", "KRIC", "Daily"),  # SX 290 / SX 291
    (292, "KSWF", "KSFB", "Daily"),  # SX 292 / SX 293
    (294, "KSWF", "TJBQ", "Daily"),  # SX 294 / SX 295
    (296, "KBGR", "KRIC", "Daily"),  # SX 296 / SX 297
    (298, "KBGR", "KSFB", "Daily"),  # SX 298 / SX 299
    (300, "KBGR", "TJBQ", "Daily"),  # SX 300 / SX 301
    (302, "KRIC", "KSFB", "Daily"),  # SX 302 / SX 303
    (304, "KRIC", "TJBQ", "Daily"),  # SX 304 / SX 305
    (306, "KSFB", "TJBQ", "Daily"),  # SX 306 / SX 307

    # ----------------------------------------------------
    # II. GEOGRAPHIC BRIDGE CONNECTORS & REGIONAL SPOKES
    # ----------------------------------------------------
    # PAFA Bridge Spokes (1300 Block - Alaska Hub)
    # ----------------------------------------------------
    (1300, "PAFA", "PAJN", "Daily"),  # Juneau, AK
    (1302, "PAFA", "PAKT", "Tue, Thu, Sat"),  # Ketchikan, AK
    (1304, "PAFA", "PABR", "Mon, Wed, Fri, Sun"),  # Utqiaġvik, AK
    (1306, "PAFA", "PAOT", "Tue, Thu, Sat"),  # Kotzebue, AK
    (1308, "PAFA", "PASC", "Daily"),  # Deadhorse, AK (North Slope worker corridor)
    (1310, "PAFA", "PADQ", "Mon, Wed, Fri"),  # Kodiak, AK
    (1312, "PAFA", "PAOM", "Tue, Thu, Sat"),  # Nome, AK
    (1314, "PAFA", "PAPG", "Tue, Thu, Sat"),  # Petersburg, AK
    (1316, "PAFA", "PASI", "Mon, Wed, Fri"),  # Sitka, AK
    (1318, "PAFA", "PAYA", "Tue, Thu, Sat"),  # Yakutat, AK
    (1320, "PAFA", "PAVD", "Mon, Fri"),  # Valdez, AK
    (1322, "PAFA", "PAEN", "Mon, Wed, Fri, Sun"),  # Kenai, AK
    (1324, "PAFA", "PAKW", "Tue, Thu, Sat"),  # Wrangell, AK
    (1326, "PAFA", "PAHO", "Mon, Wed, Fri, Sun"),  # Homer, AK
    (1328, "PAFA", "PHNL", "Fri, Sun"),  # Honolulu, HI
    (1330, "PAFA", "PHOG", "Thu, Sun"),  # Kahului, HI
    (1332, "PAFA", "PHKO", "Wed, Sat"),  # Kailua-Kona, HI
    (1334, "PAFA", "PAGS", "Tue, Thu, Sat"),  # Gustavus, AK
    (1336, "PAFA", "PADL", "Mon, Wed, Fri"),  # Dillingham, AK
    (1338, "PAFA", "PAKN", "Mon, Wed, Fri, Sun"),  # King Salmon, AK
    (1340, "PAFA", "PANC", "Daily"),  # Anchorage, AK
    (1342, "PAFA", "PABE", "Mon, Wed, Fri"),  # Bethel, AK
    (1344, "PAFA", "PACV", "Tue, Thu, Sat"),  # Cordova, AK
    (1346, "PAFA", "PACB", "Thu, Sun"),  # Cold Bay, AK
    (1348, "PAFA", "PADK", "Wed, Sat"),  # Adak, AK
    (1350, "PAFA", "PAGA", "Tue, Thu, Sat"),  # Galena, AK
    (1352, "PAFA", "PAUL", "Mon, Wed, Fri"),  # Unalakleet, AK
    (1354, "PAFA", "KBZN", "Thu, Sun"),  # Bozeman, MT
    (1356, "PAFA", "KMSO", "Tue, Sat"),  # Missoula, MT
    (1358, "PAFA", "KBOI", "Tue, Thu, Sat"),  # Boise, ID
    (1360, "PAFA", "PHLI", "Tue, Sat"),  # Lihue, HI
    (1362, "PAFA", "PASN", "Wed, Sat"),  # St. Paul Island, AK
    (1364, "PAFA", "KGEG", "Mon, Wed, Fri, Sun"),  # Spokane, WA
    (1366, "PAFA", "KFCA", "Thu, Sun"),  # Kalispell / Glacier Park, MT
    (1368, "PAFA", "KEUG", "Tue, Thu, Sat"),  # Eugene, OR
    (1370, "PAFA", "KBIL", "Mon, Fri"),  # Billings, MT
    (1372, "PAFA", "KRNO", "Tue, Thu, Sat"),  # Reno-Tahoe, NV
    (1374, "PAFA", "KOAK", "Daily"),  # Oakland, CA
    (1376, "PAFA", "KLAS", "Mon, Wed, Fri, Sun"),  # Las Vegas, NV
    (1378, "PAFA", "KPSP", "Tue, Thu, Sat"),  # Palm Springs, CA

    # ----------------------------------------------------
    # KPVU Bridge Spokes (1400 Block - Intermountain West Hub)
    # ----------------------------------------------------
    (1400, "KPVU", "KBOI", "Mon, Wed, Fri, Sun"),  # Boise, ID
    (1402, "KPVU", "KSGU", "Mon, Wed, Fri, Sun"),  # St. George, UT
    (1404, "KPVU", "KIFP", "Thu, Sun"),  # Bullhead City, AZ
    (1406, "KPVU", "KJAC", "Mon, Wed, Fri, Sun"),  # Jackson, WY
    (1408, "KPVU", "KGEG", "Tue, Thu, Sat"),  # Spokane, WA
    (1410, "KPVU", "KEUG", "Mon, Fri"),  # Eugene, OR
    (1412, "KPVU", "KFLG", "Tue, Thu, Sat"),  # Flagstaff, AZ
    (1414, "KPVU", "KCPR", "Mon, Wed, Fri"),  # Casper, WY
    (1416, "KPVU", "KGJT", "Tue, Thu, Sat"),  # Grand Junction, CO
    (1418, "KPVU", "KIDA", "Mon, Wed, Fri, Sun"),  # Idaho Falls, ID
    (1420, "KPVU", "KBZN", "Mon, Wed, Fri, Sun"),  # Bozeman, MT
    (1422, "KPVU", "KMSO", "Tue, Thu, Sat"),  # Missoula, MT
    (1424, "KPVU", "KTWF", "Tue, Thu, Sat"),  # Twin Falls, ID
    (1426, "KPVU", "KPIH", "Mon, Wed, Fri"),  # Pocatello, ID
    (1428, "KPVU", "KRNO", "Mon, Wed, Fri, Sun"),  # Reno, NV
    (1430, "KPVU", "PHNL", "Wed, Sat"),  # Honolulu, HI
    (1432, "KPVU", "PHOG", "Thu, Sun"),  # Kahului, HI
    (1434, "KPVU", "KYKM", "Tue, Thu, Sat"),  # Yakima, WA
    (1436, "KPVU", "KPSC", "Mon, Wed, Fri, Sun"),  # Pasco, WA
    (1438, "KPVU", "KMFR", "Mon, Fri"),  # Medford, OR
    (1440, "KPVU", "KRDM", "Mon, Wed, Fri, Sun"),  # Redmond, OR
    (1442, "KPVU", "KOTH", "Thu, Sun"),  # North Bend, OR
    (1444, "KPVU", "KALW", "Tue, Thu, Sat"),  # Walla Walla, WA
    (1446, "KPVU", "KEAT", "Mon, Wed, Fri"),  # Wenatchee, WA
    (1448, "KPVU", "KLWS", "Tue, Thu, Sat"),  # Lewiston, ID
    (1450, "KPVU", "KHLN", "Mon, Wed, Fri"),  # Helena, MT
    (1452, "KPVU", "KGTF", "Tue, Thu, Sat"),  # Great Falls, MT
    (1454, "KPVU", "KCDC", "Mon, Wed, Fri, Sun"),  # Cedar City, UT
    (1456, "KPVU", "KVEL", "Tue, Thu, Sat"),  # Vernal, UT
    (1458, "KPVU", "KSBA", "Thu, Sun"),  # Santa Barbara, CA
    (1460, "KPVU", "KFAT", "Mon, Fri"),  # Fresno, CA
    (1462, "KPVU", "KBFL", "Tue, Thu, Sat"),  # Bakersfield, CA
    (1464, "KPVU", "KRDD", "Mon, Wed, Fri"),  # Redding, CA
    (1466, "KPVU", "KPSP", "Mon, Wed, Fri, Sun"),  # Palm Springs, CA
    (1468, "KPVU", "PHLI", "Mon, Fri"),  # Lihue, HI
    (1470, "KPVU", "KDVT", "Mon, Wed, Fri, Sun"),  # Phoenix, AZ
    (1472, "KPVU", "KTUS", "Tue, Thu, Sat"),  # Tucson, AZ
    (1474, "KPVU", "KABQ", "Mon, Wed, Fri, Sun"),  # Albuquerque, NM
    (1476, "KPVU", "KSAF", "Tue, Thu, Sat"),  # Santa Fe, NM
    (1478, "KPVU", "KBJC", "Mon, Wed, Fri, Sun"),  # Broomfield, CO
    (1480, "KPVU", "KCOS", "Mon, Wed, Fri, Sun"),  # Colorado Springs, CO
    (1482, "KPVU", "KDRO", "Tue, Thu, Sat"),  # Durango, CO
    (1484, "KPVU", "KLAS", "Daily"),  # Las Vegas, NV
    (1486, "KPVU", "KEKO", "Thu, Sun"),  # Elko, NV
    (1488, "KPVU", "KCNY", "Mon, Wed, Fri"),  # Moab, UT
    (1490, "KPVU", "KOGD", "Mon, Fri"),  # Ogden, UT
    (1492, "KPVU", "KCYS", "Tue, Thu, Sat"),  # Cheyenne, WY
    (1494, "KPVU", "KCOD", "Mon, Fri"),  # Cody, WY
    (1496, "KPVU", "KSMF", "Mon, Wed, Fri, Sun"),  # Sacramento, CA
    (1498, "KPVU", "KPRC", "Mon, Wed, Fri"),  # Prescott, AZ

    # ----------------------------------------------------
    # KIWA Bridge Spokes (300 Block - Southwest Hub)
    # ----------------------------------------------------
    (300, "KIWA", "KSGU", "Mon, Wed, Fri, Sun"),  # St. George, UT
    (302, "KIWA", "KIFP", "Thu, Sun"),  # Bullhead City, AZ
    (304, "KIWA", "KELP", "Mon, Wed, Fri, Sun"),  # El Paso, TX
    (306, "KIWA", "KSAN", "Mon, Fri"),  # San Diego, CA
    (308, "KIWA", "KFLG", "Tue, Thu, Sat"),  # Flagstaff, AZ
    (310, "KIWA", "KMAF", "Mon, Wed, Fri, Sun"),  # Midland, TX
    (312, "KIWA", "KABQ", "Mon, Wed, Fri, Sun"),  # Albuquerque, NM
    (314, "KIWA", "KTUS", "Mon, Fri"),  # Tucson, AZ
    (316, "KIWA", "KPSP", "Mon, Wed, Fri, Sun"),  # Palm Springs, CA
    (318, "KIWA", "KROW", "Tue, Thu, Sat"),  # Roswell, NM
    (320, "KIWA", "KPRC", "Mon, Wed, Fri"),  # Prescott, AZ
    (322, "KIWA", "KDRO", "Mon, Wed, Fri, Sun"),  # Durango, CO
    (324, "KIWA", "KEKO", "Tue, Thu, Sat"),  # Elko, NV
    (326, "KIWA", "KSBP", "Thu, Sun"),  # San Luis Obispo, CA
    (330, "KIWA", "PHNL", "Wed, Sat"),  # Honolulu, HI
    (332, "KIWA", "PHOG", "Thu, Sun"),  # Kahului, HI
    (334, "KIWA", "PHKO", "Wed, Sat"),  # Kailua-Kona, HI
    (336, "KIWA", "KSBA", "Thu, Sun"),  # Santa Barbara, CA
    (338, "KIWA", "KMRY", "Mon, Wed, Fri, Sun"),  # Monterey, CA
    (340, "KIWA", "KFAT", "Mon, Wed, Fri, Sun"),  # Fresno, CA
    (342, "KIWA", "KBFL", "Mon, Wed, Fri"),  # Bakersfield, CA
    (344, "KIWA", "KCDC", "Thu, Sun"),  # Cedar City, UT
    (346, "KIWA", "KACV", "Tue, Thu, Sat"),  # Arcata, CA
    (348, "KIWA", "KACT", "Tue, Thu, Sat"),  # Waco, TX
    (350, "KIWA", "KSJT", "Mon, Wed, Fri, Sun"),  # San Angelo, TX
    (352, "KIWA", "KVCT", "Tue, Thu, Sat"),  # Victoria, TX
    (354, "KIWA", "KABI", "Tue, Thu, Sat"),  # Abilene, TX
    (356, "KIWA", "KAMA", "Tue, Thu, Sat"),  # Amarillo, TX
    (358, "KIWA", "KLBB", "Mon, Wed, Fri, Sun"),  # Lubbock, TX
    (360, "KIWA", "KOKC", "Mon, Wed, Fri, Sun"),  # Oklahoma City, OK
    (362, "KIWA", "KTUL", "Tue, Thu, Sat"),  # Tulsa, OK
    (364, "KIWA", "KLAW", "Mon, Wed, Fri"),  # Lawton, OK
    (366, "KIWA", "KCRP", "Mon, Wed, Fri, Sun"),  # Corpus Christi, TX
    (368, "KIWA", "KHRL", "Thu, Sun"),  # Harlingen, TX
    (370, "KIWA", "KMFE", "Tue, Thu, Sat"),  # McAllen, TX
    (372, "KIWA", "KLRD", "Mon, Fri"),  # Laredo, TX
    (374, "KIWA", "KCOS", "Mon, Wed, Fri, Sun"),  # Colorado Springs, CO
    (376, "KIWA", "KGJT", "Tue, Thu, Sat"),  # Grand Junction, CO
    (378, "KIWA", "KPUB", "Thu, Sun"),  # Pueblo, CO
    (380, "KIWA", "KSAF", "Mon, Wed, Fri"),  # Santa Fe, NM
    (382, "KIWA", "KSBD", "Mon, Wed, Fri, Sun"),  # San Bernardino, CA
    (384, "KIWA", "KOGD", "Tue, Thu, Sat"),  # Ogden, UT
    (386, "KIWA", "KSMF", "Mon, Wed, Fri, Sun"),  # Sacramento, CA
    (388, "KIWA", "KRDD", "Mon, Wed, Fri"),  # Redding, CA
    (390, "KIWA", "KRNO", "Tue, Thu, Sat"),  # Reno, NV

    # ----------------------------------------------------
    # KBLI Bridge Spokes (400 Block - Pacific Northwest Hub)
    # ----------------------------------------------------
    (400, "KBLI", "PAJN", "Tue, Thu, Sat"),  # Juneau, AK
    (402, "KBLI", "PAKT", "Mon, Wed, Fri, Sun"),  # Ketchikan, AK
    (404, "KBLI", "KBOI", "Mon, Wed, Fri, Sun"),  # Boise, ID
    (406, "KBLI", "KGEG", "Mon, Wed, Fri, Sun"),  # Spokane, WA
    (408, "KBLI", "KEUG", "Mon, Wed, Fri, Sun"),  # Eugene, OR
    (410, "KBLI", "KYKM", "Tue, Thu, Sat"),  # Yakima, WA
    (412, "KBLI", "KPSC", "Mon, Wed, Fri"),  # Pasco, WA
    (414, "KBLI", "KMFR", "Mon, Fri"),  # Medford, OR
    (416, "KBLI", "KRDM", "Mon, Wed, Fri, Sun"),  # Redmond, OR
    (418, "KBLI", "KOTH", "Thu, Sun"),  # North Bend, OR
    (420, "KBLI", "KALW", "Tue, Thu, Sat"),  # Walla Walla, WA
    (422, "KBLI", "KEAT", "Mon, Wed, Fri"),  # Wenatchee, WA
    (424, "KBLI", "KLWS", "Tue, Thu, Sat"),  # Lewiston, ID
    (426, "KBLI", "KTWF", "Mon, Wed, Fri"),  # Twin Falls, ID
    (428, "KBLI", "KCLM", "Tue, Thu, Sat"),  # Port Angeles, WA
    (430, "KBLI", "PHNL", "Wed, Sat"),  # Honolulu, HI
    (432, "KBLI", "PHOG", "Thu, Sun"),  # Kahului, HI
    (434, "KBLI", "PHKO", "Wed, Sat"),  # Kailua-Kona, HI
    (436, "KBLI", "PHLI", "Mon, Fri"),  # Lihue, HI
    (438, "KBLI", "KJAC", "Mon, Wed, Fri, Sun"),  # Jackson, WY
    (440, "KBLI", "KCPR", "Tue, Thu, Sat"),  # Casper, WY
    (442, "KBLI", "KIDA", "Mon, Wed, Fri, Sun"),  # Idaho Falls, ID
    (444, "KBLI", "KBZN", "Tue, Thu, Sat"),  # Bozeman, MT
    (446, "KBLI", "KMSO", "Mon, Wed, Fri"),  # Missoula, MT
    (448, "KBLI", "KPIH", "Tue, Thu, Sat"),  # Pocatello, ID
    (450, "KBLI", "KRNO", "Mon, Wed, Fri, Sun"),  # Reno, NV
    (452, "KBLI", "KACV", "Mon, Wed, Fri, Sun"),  # Arcata, CA
    (454, "KBLI", "KRDD", "Tue, Thu, Sat"),  # Redding, CA
    (456, "KBLI", "KHLN", "Thu, Sun"),  # Helena, MT
    (458, "KBLI", "KGTF", "Mon, Fri"),  # Great Falls, MT
    (460, "KBLI", "KMRY", "Mon, Wed, Fri"),  # Monterey, CA
    (462, "KBLI", "PAGS", "Tue, Thu, Sat"),  # Gustavus, AK
    (464, "KBLI", "KPSP", "Mon, Wed, Fri, Sun"),  # Palm Springs, CA
    (478, "KBLI", "KPDX", "Mon, Wed, Fri, Sun"),  # Portland, OR
    (480, "KBLI", "KLMT", "Mon, Fri"),  # Klamath Falls, OR
    (482, "KBLI", "KSLE", "Tue, Thu, Sat"),  # Salem, OR
    (484, "KBLI", "KPAE", "Mon, Fri"),  # Everett, WA
    (486, "KBLI", "KMWH", "Thu, Sun"),  # Moses Lake, WA
    (488, "KBLI", "KBIL", "Tue, Thu, Sat"),  # Billings, MT
    (490, "KBLI", "KGPI", "Mon, Wed, Fri"),  # Kalispell, MT
    (492, "KBLI", "KCOE", "Tue, Thu, Sat"),  # Coeur d'Alene, ID
    (494, "KBLI", "KSUN", "Mon, Fri"),  # Sun Valley, ID
    (496, "KBLI", "PASI", "Tue, Thu, Sat"),  # Sitka, AK
    (498, "KBLI", "PAYA", "Mon, Fri"),  # Yakutat, AK
    (1400, "KBLI", "KFAT", "Mon, Fri"),  # Fresno, CA
    (1402, "KBLI", "KBFL", "Tue, Thu, Sat"),  # Bakersfield, CA
    (1404, "KBLI", "KSBA", "Thu, Sun"),  # Santa Barbara, CA
    (1406, "KBLI", "KSMF", "Mon, Wed, Fri"),  # Sacramento, CA

    # ----------------------------------------------------
    # KMSY Bridge Spokes (500 Block - Gulf Coast Hub)
    # ----------------------------------------------------
    (500, "KMSY", "KELP", "Mon, Wed, Fri, Sun"),  # El Paso, TX
    (502, "KMSY", "KSGF", "Mon, Wed, Fri, Sun"),  # Springfield, MO
    (504, "KMSY", "KLIT", "Mon, Wed, Fri, Sun"),  # Little Rock, AR
    (506, "KMSY", "KPNS", "Mon, Wed, Fri, Sun"),  # Pensacola, FL
    (508, "KMSY", "KMOB", "Tue, Thu, Sat"),  # Mobile, AL
    (510, "KMSY", "KVPS", "Thu, Sun"),  # Eglin / Destin, FL
    (512, "KMSY", "KMAF", "Mon, Wed, Fri, Sun"),  # Midland / Odessa, TX
    (514, "KMSY", "KBTR", "Mon, Wed, Fri"),  # Baton Rouge, LA
    (516, "KMSY", "KGPT", "Thu, Sun"),  # Gulfport / Biloxi, MS
    (518, "KMSY", "KLFT", "Mon, Wed, Fri, Sun"),  # Lafayette, LA
    (520, "KMSY", "KMLU", "Tue, Thu, Sat"),  # Monroe, LA
    (522, "KMSY", "KHBG", "Mon, Fri"),  # Hattiesburg, MS
    (524, "KMSY", "KAEX", "Tue, Thu, Sat"),  # Alexandria, LA
    (526, "KMSY", "KLCH", "Mon, Wed, Fri"),  # Lake Charles, LA
    (528, "KMSY", "KTYR", "Mon, Wed, Fri, Sun"),  # Tyler, TX
    (530, "KMSY", "KAVL", "Thu, Sun"),  # Asheville, NC
    (532, "KMSY", "KTRI", "Tue, Thu, Sat"),  # Tri-Cities / Bristol, TN
    (534, "KMSY", "KCRP", "Tue, Thu, Sat"),  # Corpus Christi, TX
    (536, "KMSY", "KBPT", "Mon, Wed, Fri"),  # Beaumont / Port Arthur, TX
    (538, "KMSY", "KSHV", "Mon, Wed, Fri, Sun"),  # Shreveport, LA
    (540, "KMSY", "KECP", "Thu, Sun"),  # Panama City Beach, FL
    (542, "KMSY", "KMGM", "Tue, Thu, Sat"),  # Montgomery, AL
    (544, "KMSY", "KBHM", "Tue, Thu, Sat"),  # Birmingham, AL
    (546, "KMSY", "KPGD", "Tue, Thu, Sat"),  # Punta Gorda / Ft. Myers, FL
    (548, "KMSY", "KTYS", "Tue, Thu, Sat"),  # Knoxville, TN
    (550, "KMSY", "KDAY", "Tue, Thu, Sat"),  # Dayton, OH
    (552, "KMSY", "KCMH", "Mon, Wed, Fri, Sun"),  # Columbus, OH
    (554, "KMSY", "KCVG", "Mon, Wed, Fri, Sun"),  # Cincinnati, OH
    (556, "KMSY", "KLEX", "Tue, Thu, Sat"),  # Lexington, KY
    (558, "KMSY", "KEVV", "Mon, Wed, Fri"),  # Evansville, IN
    (560, "KMSY", "KJVY", "Tue, Thu, Sat"),  # Jeffersonville / Louisville area
    (562, "KMSY", "KOWB", "Mon, Wed, Fri, Sun"),  # Owensboro, KY
    (564, "KMSY", "KJEF", "Tue, Thu, Sat"),  # Jefferson City, MO
    (566, "KMSY", "KSPI", "Mon, Wed, Fri, Sun"),  # Springfield, IL
    (568, "KMSY", "KGCK", "Tue, Thu, Sat"),  # Garden City, KS
    (570, "KMSY", "KSLN", "Mon, Wed, Fri, Sun"),  # Salina, KS
    (572, "KMSY", "KICT", "Mon, Wed, Fri, Sun"),  # Wichita, KS
    (574, "KMSY", "KTOP", "Mon, Wed, Fri, Sun"),  # Topeka, KS
    (576, "KMSY", "KSTJ", "Tue, Thu, Sat"),  # St. Joseph, MO
    (578, "KMSY", "KBLV", "Mon, Wed, Fri, Sun"),  # Belleville / St. Louis area
    (580, "KMSY", "KTRI", "Tue, Thu, Sat"),  # Tri-Cities, TN
    (582, "KMSY", "KBLF", "Mon, Wed, Fri, Sun"),  # Bluefield, WV
    (584, "KMSY", "KCHA", "Tue, Thu, Sat"),  # Chattanooga, TN
    (586, "KMSY", "KLAW", "Tue, Thu, Sat"),  # Lawton, OK
    (588, "KMSY", "KTUL", "Mon, Wed, Fri, Sun"),  # Tulsa, OK
    (590, "KMSY", "KFSM", "Mon, Wed, Fri, Sun"),  # Fort Smith, AR
    (592, "KMSY", "KXNA", "Mon, Wed, Fri, Sun"),  # Northwest Arkansas
    (594, "KMSY", "KTUP", "Tue, Thu, Sat"),  # Tupelo, MS
    (596, "KMSY", "KMEI", "Mon, Wed, Fri, Sun"),  # Meridian, MS
    (598, "KMSY", "KHSV", "Mon, Wed, Fri, Sun"),  # Huntsville, AL
    (1500, "KMSY", "KPIB", "Tue, Thu, Sat"),  # Hattiesburg / Laurel, MS
    (1502, "KMSY", "KGTR", "Mon, Wed, Fri, Sun"),  # Columbus / Starkville, MS
    (1504, "KMSY", "KHEZ", "Tue, Thu, Sat"),  # Natchez, MS
    (1506, "KMSY", "KMOB", "Tue, Thu, Sat"),  # Mobile, AL
    (1508, "KMSY", "KJKA", "Mon, Wed, Fri, Sun"),  # Gulf Shores, AL
    (1510, "KMSY", "KCSG", "Tue, Thu, Sat"),  # Columbus, GA
    (1512, "KMSY", "KMCN", "Mon, Wed, Fri, Sun"),  # Macon, GA
    (1514, "KMSY", "KBWG", "Tue, Thu, Sat"),  # Bowling Green, KY
    (1516, "KMSY", "KGSP", "Mon, Wed, Fri, Sun"),  # Greenville / Spartanburg, SC
    (1518, "KMSY", "KACT", "Tue, Thu, Sat"),  # Waco, TX
    (1520, "KMSY", "KSJT", "Mon, Wed, Fri, Sun"),  # San Angelo, TX
    (1522, "KMSY", "KVCT", "Tue, Thu, Sat"),  # Victoria, TX
    (1524, "KMSY", "KABI", "Tue, Thu, Sat"),  # Abilene, TX
    (1526, "KMSY", "KAMA", "Tue, Thu, Sat"),  # Amarillo, TX
    (1528, "KMSY", "KLBB", "Mon, Wed, Fri, Sun"),  # Lubbock, TX

    # ----------------------------------------------------
    # KOMA Bridge Spokes (600 Block - Midwest Hub)
    # ----------------------------------------------------
    (600, "KOMA", "KMLI", "Mon, Wed, Fri, Sun"),  # Moline / Quad Cities, IL
    (602, "KOMA", "KSGF", "Mon, Wed, Fri, Sun"),  # Springfield, MO
    (604, "KOMA", "KLIT", "Mon, Wed, Fri, Sun"),  # Little Rock, AR
    (606, "KOMA", "KFSD", "Mon, Wed, Fri, Sun"),  # Sioux Falls, SD
    (608, "KOMA", "KCID", "Mon, Wed, Fri, Sun"),  # Cedar Rapids, IA
    (610, "KOMA", "KPIA", "Mon, Wed, Fri"),  # Peoria, IL
    (612, "KOMA", "KDSM", "Mon, Wed, Fri"),  # Des Moines, IA
    (614, "KOMA", "KLNK", "Tue, Thu, Sat"),  # Lincoln, NE
    (616, "KOMA", "KICT", "Mon, Wed, Fri, Sun"),  # Wichita, KS
    (618, "KOMA", "KBIS", "Mon, Wed, Fri, Sun"),  # Bismarck, ND
    (620, "KOMA", "KFAR", "Mon, Wed, Fri, Sun"),  # Fargo, ND
    (622, "KOMA", "KGRI", "Tue, Thu, Sat"),  # Grand Island, NE
    (624, "KOMA", "KSUX", "Mon, Wed, Fri"),  # Sioux City, IA
    (626, "KOMA", "KCOU", "Tue, Thu, Sat"),  # Columbia, MO
    (628, "KOMA", "KALO", "Mon, Fri"),  # Waterloo, IA
    (630, "KOMA", "KELP", "Tue, Thu, Sat"),  # El Paso, TX
    (632, "KOMA", "KMAF", "Tue, Thu, Sat"),  # Midland / Odessa, TX
    (634, "KOMA", "KABQ", "Mon, Wed, Fri, Sun"),  # Albuquerque, NM
    (636, "KOMA", "KTUS", "Mon, Wed, Fri, Sun"),  # Tucson, AZ
    (638, "KOMA", "KROW", "Tue, Thu, Sat"),  # Roswell, NM
    (640, "KOMA", "KPRC", "Thu, Sun"),  # Prescott, AZ
    (642, "KOMA", "KDRO", "Mon, Wed, Fri"),  # Durango, CO
    (646, "KOMA", "KBTR", "Thu, Sun"),  # Baton Rouge, LA
    (648, "KOMA", "KGPT", "Fri, Mon"),  # Gulfport / Biloxi, MS
    (650, "KOMA", "KLFT", "Tue, Thu, Sat"),  # Lafayette, LA
    (652, "KOMA", "KMLU", "Mon, Wed, Fri"),  # Monroe, LA
    (654, "KOMA", "KHBG", "Thu, Sun"),  # Hattiesburg, MS
    (656, "KOMA", "KAEX", "Tue, Thu, Sat"),  # Alexandria, LA
    (658, "KOMA", "KLCH", "Mon, Fri"),  # Lake Charles, LA
    (660, "KOMA", "KTYR", "Mon, Wed, Fri"),  # Tyler, TX
    (662, "KOMA", "KMKE", "Mon, Wed, Fri, Sun"),  # Milwaukee, WI
    (664, "KOMA", "KBMI", "Mon, Wed, Fri, Sun"),  # Bloomington / Normal, IL
    (666, "KOMA", "KDBQ", "Tue, Thu, Sat"),  # Dubuque, IA
    (668, "KOMA", "KRST", "Tue, Thu, Sat"),  # Rochester, MN
    (670, "KOMA", "KDLH", "Mon, Wed, Fri, Sun"),  # Duluth, MN
    (672, "KOMA", "KCRP", "Thu, Sun"),  # Corpus Christi, TX
    (674, "KOMA", "KSHV", "Mon, Fri"),  # Shreveport, LA
    (676, "KOMA", "KMQT", "Tue, Thu, Sat"),  # Marquette, MI
    (678, "KOMA", "KPLN", "Mon, Wed, Fri"),  # Pellston / Mackinac, MI
    (680, "KOMA", "KMGM", "Tue, Thu, Sat"),  # Montgomery, AL
    (682, "KOMA", "KBHM", "Tue, Thu, Sat"),  # Birmingham, AL
    (684, "KOMA", "KCIU", "Tue, Thu, Sat"),  # Sault Ste. Marie, MI
    (686, "KOMA", "KCMX", "Tue, Thu, Sat"),  # Houghton, MI
    (688, "KOMA", "KGRB", "Tue, Thu, Sat"),  # Green Bay, WI
    (690, "KOMA", "KDAY", "Tue, Thu, Sat"),  # Dayton, OH
    (692, "KOMA", "KCMH", "Mon, Wed, Fri, Sun"),  # Columbus, OH
    (694, "KOMA", "KCVG", "Mon, Wed, Fri, Sun"),  # Cincinnati, OH
    (696, "KOMA", "KLEX", "Tue, Thu, Sat"),  # Lexington, KY
    (698, "KOMA", "KEVV", "Mon, Wed, Fri"),  # Evansville, IN
    (1600, "KOMA", "KRFD", "Mon, Wed, Fri, Sun"),  # Chicago Rockford, IL
    (1602, "KOMA", "KGYY", "Tue, Thu, Sat"),  # Gary, IN
    (1604, "KOMA", "KCWA", "Tue, Thu, Sat"),  # Central Wisconsin
    (1606, "KOMA", "KATW", "Tue, Thu, Sat"),  # Appleton / Fox Cities, WI
    (1608, "KOMA", "KSTC", "Mon, Wed, Fri, Sun"),  # St. Cloud, MN
    (1610, "KOMA", "KLSE", "Tue, Thu, Sat"),  # La Crosse, WI
    (1612, "KOMA", "KIMT", "Mon, Wed, Fri, Sun"),  # Iron Mountain, MI
    (1614, "KOMA", "KESC", "Thu, Sun"),  # Escanaba, MI
    (1616, "KOMA", "KISQ", "Tue, Thu, Sat"),  # Schoolcraft County / Manistique, MI
    (1618, "KOMA", "KAPN", "Mon, Wed, Fri, Sun"),  # Alpena, MI
    (1620, "KOMA", "KINL", "Tue, Thu, Sat"),  # International Falls, MN
    (1622, "KOMA", "KBJI", "Mon, Wed, Fri, Sun"),  # Bemidji, MN
    (1624, "KOMA", "KMOT", "Tue, Thu, Sat"),  # Minot, ND
    (1626, "KOMA", "KDVL", "Tue, Thu, Sat"),  # Devils Lake, ND
    (1628, "KOMA", "KDIK", "Mon, Wed, Fri, Sun"),  # Dickinson, ND
    (1630, "KOMA", "KJMS", "Tue, Thu, Sat"),  # Jamestown, ND
    (1632, "KOMA", "KRAP", "Mon, Wed, Fri, Sun"),  # Rapid City, SD
    (1634, "KOMA", "KPIR", "Mon, Wed, Fri, Sun"),  # Pierre, SD
    (1636, "KOMA", "KJVY", "Tue, Thu, Sat"),  # Jeffersonville / Louisville area
    (1638, "KOMA", "KOWB", "Mon, Wed, Fri, Sun"),  # Owensboro, KY
    (1640, "KOMA", "KJEF", "Tue, Thu, Sat"),  # Jefferson City, MO
    (1642, "KOMA", "KSPI", "Mon, Wed, Fri, Sun"),  # Springfield, IL
    (1644, "KOMA", "KGCK", "Tue, Thu, Sat"),  # Garden City, KS
    (1646, "KOMA", "KSLN", "Mon, Wed, Fri, Sun"),  # Salina, KS
    (1648, "KOMA", "KICT", "Mon, Wed, Fri, Sun"),  # Wichita, KS
    (1650, "KOMA", "KTOP", "Mon, Wed, Fri, Sun"),  # Topeka, KS
    (1652, "KOMA", "KSTJ", "Tue, Thu, Sat"),  # St. Joseph, MO
    (1654, "KOMA", "KBLV", "Mon, Wed, Fri, Sun"),  # Belleville / St. Louis area
    
    
    # ----------------------------------------------------
    # KGRR Bridge Spokes (700 Block - Great Lakes Hub)
    # ----------------------------------------------------
    (700, "KGRR", "KMLI", "Mon, Wed, Fri, Sun"),  # Moline / Quad Cities, IL
    (702, "KGRR", "KPNS", "Thu, Sun"),  # Pensacola, FL
    (704, "KGRR", "KPIT", "Mon, Wed, Fri, Sun"),  # Pittsburgh, PA
    (706, "KGRR", "KCAK", "Mon, Wed, Fri, Sun"),  # Akron / Canton, OH
    (708, "KGRR", "KTVC", "Mon, Wed, Fri, Sun"),  # Traverse City, MI
    (710, "KGRR", "KHTS", "Tue, Thu, Sat"),  # Huntington, WV
    (712, "KGRR", "KCID", "Mon, Wed, Fri, Sun"),  # Cedar Rapids, IA
    (714, "KGRR", "KPIA", "Mon, Wed, Fri"),  # Peoria, IL
    (716, "KGRR", "KSBN", "Tue, Thu, Sat"),  # South Bend, IN
    (718, "KGRR", "KMKE", "Mon, Wed, Fri, Sun"),  # Milwaukee, WI
    (720, "KGRR", "KFWA", "Tue, Thu, Sat"),  # Fort Wayne, IN
    (722, "KGRR", "KLAN", "Mon, Fri"),  # Lansing, MI
    (724, "KGRR", "KAZO", "Mon, Fri"),  # Kalamazoo, MI
    (726, "KGRR", "KFNT", "Tue, Thu, Sat"),  # Flint, MI
    (728, "KGRR", "KTOL", "Mon, Wed, Fri"),  # Toledo, OH
    (730, "KGRR", "KMQT", "Mon, Wed, Fri, Sun"),  # Marquette, MI
    (732, "KGRR", "KPLN", "Tue, Thu, Sat"),  # Pellston / Mackinac, MI
    (734, "KGRR", "KERI", "Mon, Wed, Fri"),  # Erie, PA
    (736, "KGRR", "KBMI", "Thu, Sun"),  # Bloomington, IL
    (738, "KGRR", "KDBQ", "Mon, Fri"),  # Dubuque, IA
    (740, "KGRR", "KIPT", "Tue, Thu, Sat"),  # Williamsport, PA
    (742, "KGRR", "KTYS", "Tue, Thu, Sat"),  # Knoxville, TN
    (744, "KGRR", "KGRB", "Tue, Thu, Sat"),  # Green Bay, WI
    (746, "KGRR", "KDAY", "Tue, Thu, Sat"),  # Dayton, OH
    (748, "KGRR", "KCMH", "Mon, Wed, Fri, Sun"),  # Columbus, OH
    (750, "KGRR", "KCVG", "Mon, Wed, Fri, Sun"),  # Cincinnati, OH
    (752, "KGRR", "KLEX", "Tue, Thu, Sat"),  # Lexington, KY
    (754, "KGRR", "KEVV", "Mon, Wed, Fri"),  # Evansville, IN
    (756, "KGRR", "KRST", "Thu, Sun"),  # Rochester, MN
    (758, "KGRR", "KDLH", "Mon, Wed, Fri, Sun"),  # Duluth, MN
    (760, "KGRR", "KCIU", "Tue, Thu, Sat"),  # Sault Ste. Marie, MI
    (762, "KGRR", "KCMX", "Tue, Thu, Sat"),  # Houghton, MI
    (764, "KGRR", "KRFD", "Mon, Wed, Fri, Sun"),  # Chicago Rockford, IL
    (766, "KGRR", "KGYY", "Tue, Thu, Sat"),  # Gary, IN
    (768, "KGRR", "KCWA", "Tue, Thu, Sat"),  # Central Wisconsin
    (770, "KGRR", "KATW", "Mon, Wed, Fri, Sun"),  # Appleton / Fox Cities, WI
    (772, "KGRR", "KSTC", "Mon, Wed, Fri, Sun"),  # St. Cloud, MN
    (774, "KGRR", "KLSE", "Tue, Thu, Sat"),  # La Crosse, WI
    (776, "KGRR", "KIMT", "Mon, Wed, Fri, Sun"),  # Iron Mountain, MI
    (778, "KGRR", "KESC", "Thu, Sun"),  # Escanaba, MI
    (780, "KGRR", "KISQ", "Tue, Thu, Sat"),  # Manistique, MI
    (782, "KGRR", "KAPN", "Mon, Wed, Fri, Sun"),  # Alpena, MI
    (784, "KGRR", "KINL", "Tue, Thu, Sat"),  # International Falls, MN
    (786, "KGRR", "KBJI", "Mon, Wed, Fri, Sun"),  # Bemidji, MN
    (788, "KGRR", "KMOT", "Tue, Thu, Sat"),  # Minot, ND
    (790, "KGRR", "KDVL", "Tue, Thu, Sat"),  # Devils Lake, ND
    (792, "KGRR", "KDIK", "Mon, Wed, Fri, Sun"),  # Dickinson, ND
    (794, "KGRR", "KJMS", "Tue, Thu, Sat"),  # Jamestown, ND
    (796, "KGRR", "KRAP", "Mon, Wed, Fri, Sun"),  # Rapid City, SD
    (798, "KGRR", "KPIR", "Mon, Wed, Fri, Sun"),  # Pierre, SD
    (1700, "KGRR", "KJVY", "Tue, Thu, Sat"),  # Jeffersonville / Louisville area
    (1702, "KGRR", "KOWB", "Mon, Wed, Fri, Sun"),  # Owensboro, KY
    (1704, "KGRR", "KJEF", "Tue, Thu, Sat"),  # Jefferson City, MO
    (1706, "KGRR", "KSPI", "Mon, Wed, Fri, Sun"),  # Springfield, IL
    (1708, "KGRR", "KGCK", "Tue, Thu, Sat"),  # Garden City, KS
    (1710, "KGRR", "KSLN", "Mon, Wed, Fri, Sun"),  # Salina, KS
    (1712, "KGRR", "KICT", "Mon, Wed, Fri, Sun"),  # Wichita, KS
    (1714, "KGRR", "KTOP", "Mon, Wed, Fri, Sun"),  # Topeka, KS
    (1716, "KGRR", "KSTJ", "Tue, Thu, Sat"),  # St. Joseph, MO
    (1718, "KGRR", "KBLV", "Mon, Wed, Fri, Sun"),  # Belleville / St. Louis area
    (1720, "KGRR", "KMBS", "Mon, Wed, Fri"),  # Saginaw, MI
    (1722, "KGRR", "KBLF", "Mon, Wed, Fri, Sun"),  # Bluefield, WV

    # ----------------------------------------------------
    # International Flights (800 Block - Skybus Network)
    # ----------------------------------------------------
    # TJBQ International Spokes (Aguadilla, PR Hub)
    # ----------------------------------------------------
    (800, "TJBQ", "TNCM", "Mon, Wed, Fri, Sun"),  # Philipsburg, St. Maarten
    (802, "TJBQ", "TKPK", "Tue, Thu, Sat"),  # Basseterre, St. Kitts
    (804, "TJBQ", "TFFR", "Tue, Thu, Sat"),  # Pointe-à-Pitre, Guadeloupe
    (806, "TJBQ", "TFFF", "Mon, Wed, Fri"),  # Fort-de-France, Martinique
    (808, "TJBQ", "TAPA", "Thu, Sun"),  # St. John's, Antigua
    (810, "TJBQ", "TNCA", "Mon, Wed, Fri, Sun"),  # Oranjestad, Aruba
    (812, "TJBQ", "TNCB", "Tue, Thu, Sat"),  # Kralendijk, Bonaire
    (814, "TJBQ", "TNCC", "Mon, Wed, Fri, Sun"),  # Willemstad, Curaçao
    (816, "TJBQ", "TLPL", "Thu, Sun"),  # Vieux Fort, St. Lucia
    (818, "TJBQ", "TBPB", "Mon, Wed, Fri"),  # Bridgetown, Barbados
    (820, "TJBQ", "TVSA", "Tue, Thu, Sat"),  # Kingstown, St. Vincent
    (822, "TJBQ", "MDPC", "Mon, Wed, Fri, Sun"),  # Punta Cana, Dominican Republic

    # ----------------------------------------------------
    # KSFB International Spokes (Sanford / Orlando, FL Hub)
    # ----------------------------------------------------
    (830, "KSFB", "MYNN", "Mon, Wed, Fri, Sun"),  # Nassau, Bahamas
    (832, "KSFB", "MKJS", "Tue, Thu, Sat"),  # Montego Bay, Jamaica
    (834, "KSFB", "MDPC", "Mon, Wed, Fri, Sun"),  # Punta Cana, Dominican Republic
    (836, "KSFB", "MBPV", "Thu, Sun"),  # Providenciales, Turks & Caicos
    (838, "KSFB", "MROC", "Mon, Wed, Fri, Sun"),  # San José, Costa Rica
    (840, "KSFB", "MUVR", "Tue, Thu, Sat"),  # Varadero, Cuba
    (842, "KSFB", "MWCR", "Mon, Wed, Fri, Sun"),  # Grand Cayman, Cayman Islands
    (844, "KSFB", "TLPL", "Thu, Sun"),  # Vieux Fort, St. Lucia
    (846, "KSFB", "TBPB", "Mon, Wed, Fri"),  # Bridgetown, Barbados
    (848, "KSFB", "SKCG", "Tue, Thu, Sat"),  # Cartagena, Colombia
    (850, "KSFB", "SKRG", "Tue, Thu, Sat"),  # Medellín, Colombia
    (852, "KSFB", "SPJC", "Mon, Wed, Fri"),  # Lima, Peru

    # ----------------------------------------------------
    # PAFA International Spokes (Fairbanks, AK Hub)
    # ----------------------------------------------------
    (860, "PAFA", "CYVR", "Mon, Wed, Fri, Sun"),  # Vancouver, BC, Canada
    (862, "PAFA", "CYYC", "Tue, Thu, Sat"),  # Calgary, AB, Canada
    (864, "PAFA", "CYEG", "Tue, Thu, Sat"),  # Edmonton, AB, Canada
    (866, "PAFA", "CYXY", "Mon, Wed, Fri"),  # Whitehorse, YT, Canada
    (868, "PAFA", "CYYJ", "Tue, Thu, Sat"),  # Victoria, BC, Canada
    (870, "PAFA", "CYXS", "Thu, Sun"),  # Prince George, BC, Canada
    (872, "PAFA", "CYZF", "Tue, Thu, Sat"),  # Yellowknife, NT, Canada
    (874, "PAFA", "CYEV", "Mon, Fri"),  # Inuvik, NT, Canada
    (876, "PAFA", "CYWG", "Thu, Sun"),  # Winnipeg, MB, Canada
    (878, "PAFA", "CYUL", "Mon, Wed, Fri"),  # Montréal, QC, Canada
    (880, "PAFA", "MMTJ", "Tue, Thu, Sat"),  # Tijuana, Mexico
    (882, "PAFA", "ROAH", "Wed, Sat"),  # Naha, Japan
    (884, "PAFA", "RORS", "Thu, Sun"),  # Shimojishima, Japan

    # ----------------------------------------------------
    # KBLI International Spokes (Bellingham, WA Hub)
    # ----------------------------------------------------
    (1800, "KBLI", "CYVR", "Tue, Thu, Sat"),  # Vancouver, BC, Canada
    (1802, "KBLI", "CYYJ", "Mon, Wed, Fri, Sun"),  # Victoria, BC, Canada
    (1804, "KBLI", "CYYC", "Mon, Wed, Fri, Sun"),  # Calgary, AB, Canada
    (1806, "KBLI", "CYEG", "Mon, Wed, Fri"),  # Edmonton, AB, Canada
    (1808, "KBLI", "CYXX", "Mon, Wed, Fri, Sun"),  # Abbotsford, BC, Canada
    (1810, "KBLI", "CYLW", "Tue, Thu, Sat"),  # Kelowna, BC, Canada
    (1812, "KBLI", "CYXS", "Thu, Sun"),  # Prince George, BC, Canada
    (1814, "KBLI", "CYXY", "Mon, Fri"),  # Whitehorse, YT, Canada
    (1816, "KBLI", "CYQB", "Thu, Sun"),  # Quebec City, QC, Canada
    (1818, "KBLI", "CYHZ", "Wed, Sat"),  # Halifax, NS, Canada
    (1820, "KBLI", "MMSD", "Thu, Sun"),  # Los Cabos, Mexico
    (1822, "KBLI", "MMPR", "Mon, Wed, Fri"),  # Puerto Vallarta, Mexico
    (1824, "KBLI", "MMGL", "Tue, Thu, Sat"),  # Guadalajara, Mexico
    (1826, "KBLI", "RKPK", "Wed, Sat"),  # Busan, South Korea
    (1828, "KBLI", "RPLC", "Thu, Sun"),  # Clark, Philippines

    # ----------------------------------------------------
    # KIWA International Spokes (Mesa / Phoenix, AZ Hub)
    # ----------------------------------------------------
    (1840, "KIWA", "MMSD", "Mon, Wed, Fri, Sun"),  # Los Cabos, Mexico
    (1842, "KIWA", "MMPR", "Mon, Wed, Fri, Sun"),  # Puerto Vallarta, Mexico
    (1844, "KIWA", "MMMZ", "Tue, Thu, Sat"),  # Mazatlán, Mexico
    (1846, "KIWA", "MMGL", "Mon, Wed, Fri, Sun"),  # Guadalajara, Mexico
    (1848, "KIWA", "MMHO", "Tue, Thu, Sat"),  # Hermosillo, Mexico
    (1850, "KIWA", "MMVR", "Tue, Thu, Sat"),  # Veracruz, Mexico
    (1852, "KIWA", "MMPB", "Tue, Thu, Sat"),  # Puebla, Mexico
    (1854, "KIWA", "MMBT", "Mon, Fri"),  # Huatulco, Mexico
    (1856, "KIWA", "MRLB", "Thu, Sun"),  # Liberia, Costa Rica
    (1858, "KIWA", "MNMG", "Wed, Sat"),  # Managua, Nicaragua
    (1860, "KIWA", "MPPA", "Mon, Wed, Fri"),  # Panama City, Panama
    (1862, "KIWA", "SKCL", "Tue, Thu, Sat"),  # Cali, Colombia
    (1864, "KIWA", "SPQU", "Wed, Sat"),  # Arequipa, Peru
    (1866, "KIWA", "SCEL", "Tue, Thu, Sat"),  # Santiago, Chile
    (1868, "KIWA", "CYEG", "Mon, Fri"),  # Edmonton, AB, Canada

    # ----------------------------------------------------
    # KMSY International Spokes (New Orleans, LA Hub)
    # ----------------------------------------------------
    (1880, "KMSY", "MMUN", "Mon, Wed, Fri, Sun"),  # Cancún, Mexico
    (1882, "KMSY", "MMCZ", "Thu, Sun"),  # Cozumel, Mexico
    (1884, "KMSY", "MZBZ", "Mon, Wed, Fri"),  # Belize City, Belize
    (1886, "KMSY", "MGGT", "Tue, Thu, Sat"),  # Guatemala City, Guatemala
    (1888, "KMSY", "MMBT", "Mon, Fri"),  # Huatulco, Mexico
    (1890, "KMSY", "MUHA", "Mon, Wed, Fri, Sun"),  # Havana, Cuba
    (1892, "KMSY", "MKJP", "Tue, Thu, Sat"),  # Kingston, Jamaica
    (1894, "KMSY", "MYSM", "Thu, Sun"),  # San Salvador, Bahamas
    (1896, "KMSY", "TJSJ", "Mon, Wed, Fri, Sun"),  # San Juan, PR
    (1898, "KMSY", "TIST", "Mon, Wed, Fri, Sun"),  # St. Thomas, VI
    (2800, "KMSY", "TNCC", "Thu, Sun"),  # Curaçao
    (2802, "KMSY", "SYCJ", "Wed, Sat"),  # Georgetown, Guyana
    (2804, "KMSY", "SMJP", "Thu, Sun"),  # Paramaribo, Suriname

    # ----------------------------------------------------
    # KGRR International Spokes (Grand Rapids, MI Hub)
    # ----------------------------------------------------
    (2820, "KGRR", "CYHM", "Tue, Thu, Sat"),  # Hamilton, ON, Canada
    (2822, "KGRR", "CYUL", "Mon, Wed, Fri, Sun"),  # Montréal, QC, Canada
    (2824, "KGRR", "MMUN", "Mon, Wed, Fri, Sun"),  # Cancún, Mexico
    (2826, "KGRR", "MDPC", "Thu, Sun"),  # Punta Cana, Dominican Republic
    (2828, "KGRR", "TNCA", "Thu, Sun"),  # Oranjestad, Aruba
    (2830, "KGRR", "MROC", "Mon, Thu, Sat"),  # San José, Costa Rica
    (2832, "KGRR", "SKBO", "Tue, Thu, Sat"),  # Bogotá, Colombia
    (2834, "KGRR", "SPJC", "Wed, Sat"),  # Lima, Peru
    (2836, "KGRR", "BIKF", "Mon, Wed, Fri"),  # Reykjavik, Iceland
    (2838, "KGRR", "LPPD", "Wed, Sat"),  # Ponta Delgada, Portugal
    (2840, "KGRR", "EINN", "Thu, Sun"),  # Shannon, Ireland
    (2842, "KGRR", "EGPK", "Wed, Sat"),  # Glasgow, UK
    (2844, "KGRR", "EGLL", "Mon, Wed, Fri, Sun"),  # London, UK
    (2846, "KGRR", "LFPG", "Mon, Wed, Fri, Sun"),  # Paris, France
    (2848, "KGRR", "EDDF", "Tue, Thu, Sat"),  # Frankfurt, Germany
    (2850, "KGRR", "EHAM", "Mon, Wed, Fri, Sun"),  # Amsterdam, Netherlands
    (2852, "KGRR", "LEMD", "Mon, Wed, Fri"),  # Madrid, Spain
    (2854, "KGRR", "LEBL", "Tue, Thu, Sat"),  # Barcelona, Spain
    (2856, "KGRR", "LIRF", "Tue, Thu, Sat"),  # Rome, Italy
    (2858, "KGRR", "LPPT", "Mon, Wed, Fri"),  # Lisbon, Portugal

    # ----------------------------------------------------
    # KBGR International Spokes (Bangor, ME Hub)
    # ----------------------------------------------------
    (2870, "KBGR", "CYHZ", "Mon, Wed, Fri, Sun"),  # Halifax, NS, Canada
    (2872, "KBGR", "BIKF", "Mon, Wed, Fri, Sun"),  # Reykjavik, Iceland
    (2874, "KBGR", "EINN", "Mon, Wed, Fri"),  # Shannon, Ireland
    (2876, "KBGR", "EIDW", "Mon, Wed, Fri, Sun"),  # Dublin, Ireland
    (2878, "KBGR", "EDDM", "Tue, Thu, Sat"),  # Munich, Germany
    (2880, "KBGR", "LSZH", "Thu, Sun"),  # Zurich, Switzerland
    (2882, "KBGR", "ENGM", "Wed, Sat"),  # Oslo, Norway
    (2884, "KBGR", "ESSA", "Thu, Sun"),  # Stockholm, Sweden
    (2886, "KBGR", "MPTO", "Tue, Thu, Sat"),  # Panama City, Panama
    (2888, "KBGR", "EHAM", "Mon, Wed, Fri"),  # Amsterdam, Netherlands
    (2890, "KBGR", "LOWW", "Mon, Wed, Fri"),  # Vienna, Austria

    # ----------------------------------------------------
    # KSWF International Spokes (Stewart / Newburgh, NY Hub)
    # ----------------------------------------------------
    (3800, "KSWF", "CYUL", "Mon, Wed, Fri, Sun"),  # Montréal, QC, Canada
    (3802, "KSWF", "BIKF", "Mon, Wed, Fri, Sun"),  # Reykjavik, Iceland
    (3804, "KSWF", "EINN", "Mon, Wed, Fri"),  # Shannon, Ireland
    (3806, "KSWF", "EIDW", "Mon, Wed, Fri, Sun"),  # Dublin, Ireland
    (3808, "KSWF", "EBBR", "Mon, Wed, Fri"),  # Brussels, Belgium
    (3810, "KSWF", "EFHK", "Tue, Thu, Sat"),  # Helsinki, Finland
    (3812, "KSWF", "LGAV", "Wed, Sat"),  # Athens, Greece
    (3814, "KSWF", "LROP", "Thu, Sun"),  # Bucharest, Romania
    (3816, "KSWF", "TXKF", "Thu, Sun"),  # Bermuda

    # ----------------------------------------------------
    # KRIC International Spokes (Richmond, VA Hub)
    # ----------------------------------------------------
    (3830, "KRIC", "EGCC", "Mon, Wed, Fri"),  # Manchester, UK
    (3832, "KRIC", "LOWW", "Tue, Thu, Sat"),  # Vienna, Austria
    (3834, "KRIC", "EKCH", "Mon, Wed, Fri"),  # Copenhagen, Denmark
    (3836, "KRIC", "SEQM", "Thu, Sun"),  # Quito, Ecuador
    (3838, "KRIC", "SAEZ", "Wed, Sat"),  # Buenos Aires, Argentina
    (3840, "KRIC", "EGLL", "Tue, Thu, Sat"),  # London Heathrow, United Kingdom
    (3842, "KRIC", "LFPG", "Mon, Wed, Fri"),  # Paris, France
    (3844, "KRIC", "EDDF", "Thu, Sun"),  # Frankfurt, Germany
    (3846, "KRIC", "EIDW", "Mon, Fri, Sun"),  # Dublin, Ireland
    (3848, "KRIC", "MMUN", "Sat, Sun"),  # Cancún, Mexico
    (3850, "KRIC", "TXKF", "Thu, Sun"),  # Bermuda


    # ----------------------------------------------------
    # KPVU International Spokes (Provo, UT Hub)
    # ----------------------------------------------------
    (3850, "KPVU", "CYYC", "Mon, Wed, Fri, Sun"),  # Calgary, AB, Canada
    (3852, "KPVU", "CYEG", "Tue, Thu, Sat"),  # Edmonton, AB, Canada
    (3854, "KPVU", "CYZF", "Thu, Sun"),  # Yellowknife, NT, Canada
    (3856, "KPVU", "CYVR", "Mon, Wed, Fri"),  # Vancouver, BC, Canada
    (3858, "KPVU", "MMUN", "Sat, Sun"),  # Cancún, Mexico
    (3860, "KPVU", "MMSD", "Thu, Sun"),  # San José del Cabo, Mexico
    (3862, "KPVU", "BIKF", "Tue, Thu, Sat"),  # Keflavík, Iceland
    (3864, "KPVU", "MROC", "Wed, Sat"),  # San José, Costa Rica
    
    # ----------------------------------------------------
    # --- KOMA International Routes (Omaha, NE Hub)
    # ----------------------------------------------------
    (3870, "KOMA", "CYYC", "Mon, Thu, Sat"),  # Calgary, AB, Canada
    (3872, "KOMA", "CYVR", "Wed, Fri, Sun"),  # Vancouver, BC, Canada
    (3874, "KOMA", "MROC", "Sat, Sun"),  # San José, Costa Rica
    (3876, "KOMA", "SKBO", "Fri, Sun"),  # Bogotá, Colombia
    (3878, "KOMA", "BIKF", "Tue, Thu, Sun"),  # Keflavík / Reykjavík, Iceland
    (3880, "KOMA", "MDPC", "Wed, Sat"),         # Punta Cana, Dominican Republic
    (3882, "KOMA", "CYWG", "Mon, Wed, Fri"),    # Winnipeg, MB, Canada
    (3884, "KOMA", "EGLL", "Wed, Fri, Sun"),    # London Heathrow, United Kingdom
    (3886, "KOMA", "MBPV", "Wed, Sat"),         # Providenciales, Turks & Caicos
    (3888, "KOMA", "SPJC", "Wed, Sat"),         # Lima, Peru


    
    # ----------------------------------------------------
    # TJBQ Caribbean Regional Spokes (1500 Block - Caribbean Hub)
    # ----------------------------------------------------
    (1500, "TJBQ", "TJPS", "Tue, Thu, Sat, Sun"),  # Ponce, PR
    (1502, "TJBQ", "TIST", "Mon, Wed, Fri, Sun"),  # St. Thomas, USVI
    (1504, "TJBQ", "TISX", "Tue, Thu, Sat"),  # St. Croix, USVI
    (1506, "TJBQ", "TJSJ", "Mon, Wed, Fri, Sun"),  # San Juan, PR
    (1508, "TJBQ", "KMYR", "Thu, Sun"),  # Myrtle Beach, SC
    (1510, "TJBQ", "KILM", "Mon, Fri"),  # Wilmington, NC
    (1512, "TJBQ", "KPVD", "Mon, Wed, Fri, Sun"),  # Providence, RI
    (1514, "TJBQ", "KABE", "Tue, Thu, Sat"),  # Allentown / Lehigh Valley, PA
    (1516, "TJBQ", "KPIT", "Mon, Wed, Fri, Sun"),  # Pittsburgh, PA
    (1518, "TJBQ", "KPNS", "Thu, Sun"),  # Pensacola, FL

    # ----------------------------------------------------
    # KSWF Bridge Spokes (900 Block - Northeast / Hudson Valley Hub)
    # ----------------------------------------------------
    (900, "KSWF", "KABE", "Tue, Thu, Sat"),  # Allentown, PA
    (902, "KSWF", "KMDT", "Mon, Wed, Fri, Sun"),  # Harrisburg, PA
    (904, "KSWF", "KPWM", "Mon, Wed, Fri, Sun"),  # Portland, ME
    (906, "KSWF", "KCAK", "Mon, Wed, Fri, Sun"),  # Akron / Canton, OH
    (908, "KSWF", "KPVD", "Mon, Wed, Fri, Sun"),  # Providence, RI
    (910, "KSWF", "KCRW", "Tue, Thu, Sat"),  # Charleston, WV
    (912, "KSWF", "KBTV", "Mon, Wed, Fri, Sun"),  # Burlington, VT
    (914, "KSWF", "KORH", "Mon, Wed, Fri"),  # Worcester, MA
    (916, "KSWF", "KSYR", "Tue, Thu, Sat"),  # Syracuse, NY
    (918, "KSWF", "KBGM", "Mon, Fri"),  # Binghamton, NY
    (920, "KSWF", "KITH", "Tue, Thu, Sat"),  # Ithaca, NY
    (922, "KSWF", "KART", "Mon, Wed, Fri"),  # Watertown, NY
    (924, "KSWF", "KAVP", "Mon, Fri"),  # Wilkes-Barre / Scranton, PA
    (926, "KSWF", "KELM", "Tue, Thu, Sat"),  # Elmira / Corning, NY
    (928, "KSWF", "KHVN", "Mon, Fri"),  # New Haven, CT
    (930, "KSWF", "KMHT", "Mon, Wed, Fri, Sun"),  # Manchester, NH
    (932, "KSWF", "KACK", "Thu, Sun"),  # Nantucket, MA
    (934, "KSWF", "KMVY", "Thu, Sun"),  # Martha's Vineyard, MA
    (936, "KSWF", "KLEB", "Mon, Wed, Fri"),  # Lebanon, NH
    (938, "KSWF", "KPBG", "Tue, Thu, Sat"),  # Plattsburgh, NY
    (940, "KSWF", "KSLK", "Mon, Fri"),  # Saranac Lake, NY
    (942, "KSWF", "KFMH", "Thu, Sun"),  # Falmouth / Cape Cod, MA
    (944, "KSWF", "KIPT", "Mon, Wed, Fri, Sun"),  # Williamsport, PA
    (946, "KSWF", "KALB", "Mon, Fri"),  # Albany, NY
    (948, "KSWF", "KERI", "Thu, Sun"),  # Erie, PA
    (950, "KSWF", "KCHO", "Tue, Thu, Sat"),  # Charlottesville, VA
    (952, "KSWF", "KMQT", "Tue, Thu, Sat"),  # Marquette, MI
    (954, "KSWF", "KPLN", "Mon, Wed, Fri"),  # Pellston / Mackinac, MI
    (956, "KSWF", "KGSO", "Tue, Thu, Sat"),  # Greensboro, NC
    (958, "KSWF", "KJQF", "Tue, Thu, Sat"),  # Concord / Charlotte, NC
    (960, "KSWF", "KPGV", "Tue, Thu, Sat"),  # Greenville, NC
    (962, "KSWF", "KTYS", "Tue, Thu, Sat"),  # Knoxville, TN
    (964, "KSWF", "KMBS", "Tue, Thu, Sat"),  # Saginaw, MI
    (966, "KSWF", "KISP", "Mon, Fri"),  # Islip / Long Island, NY
    (968, "KSWF", "KHPN", "Mon, Fri"),  # White Plains / Westchester, NY
    (970, "KSWF", "KROC", "Mon, Wed, Fri, Sun"),  # Rochester, NY
    (972, "KSWF", "KBUF", "Mon, Wed, Fri, Sun"),  # Buffalo, NY
    (974, "KSWF", "KOGS", "Tue, Thu, Sat"),  # Ogdensburg, NY
    (976, "KSWF", "KMSS", "Mon, Wed, Fri"),  # Massena, NY
    (978, "KSWF", "KFRG", "Thu, Sun"),  # Farmingdale / Long Island, NY
    (980, "KSWF", "KACY", "Tue, Thu, Sat"),  # Atlantic City, NJ
    (982, "KSWF", "KTTN", "Mon, Fri"),  # Trenton, NJ
    (984, "KSWF", "KMIV", "Tue, Thu, Sat"),  # Millville, NJ
    (986, "KSWF", "KLBE", "Mon, Wed, Fri"),  # Latrobe / Greensburg, PA
    (988, "KSWF", "KJST", "Tue, Thu, Sat"),  # Johnstown, PA
    (990, "KSWF", "KBFD", "Mon, Fri"),  # Bradford, PA
    (992, "KSWF", "KDUJ", "Tue, Thu, Sat"),  # DuBois, PA
    (994, "KSWF", "KRDG", "Mon, Wed, Fri"),  # Reading, PA
    (996, "KSWF", "KLNS", "Tue, Thu, Sat"),  # Lancaster, PA
    (998, "KSWF", "KGON", "Mon, Wed, Fri, Sun"),  # Groton / New London, CT
    (1900, "KSWF", "KOQU", "Thu, Sun"),  # Quonset State / North Kingstown, RI
    (1902, "KSWF", "KSBY", "Mon, Wed, Fri, Sun"),  # Salisbury, MD
    (1904, "KSWF", "KHGR", "Tue, Thu, Sat"),  # Hagerstown, MD

    # ----------------------------------------------------
    # KBGR Bridge Spokes (1000 Block - Northern New England Hub)
    # ----------------------------------------------------
    (1000, "KBGR", "KPWM", "Mon, Fri"),  # Portland, ME
    (1002, "KBGR", "KMHT", "Mon, Wed, Fri, Sun"),  # Manchester, NH
    (1004, "KBGR", "KPVD", "Mon, Wed, Fri, Sun"),  # Providence, RI
    (1006, "KBGR", "KBTV", "Mon, Wed, Fri, Sun"),  # Burlington, VT
    (1008, "KBGR", "KACK", "Thu, Sun"),  # Nantucket, MA
    (1010, "KBGR", "KMVY", "Thu, Sun"),  # Martha's Vineyard, MA
    (1012, "KBGR", "KPQB", "Mon, Wed, Fri"),  # Presque Isle, ME
    (1014, "KBGR", "KORH", "Tue, Thu, Sat"),  # Worcester, MA
    (1016, "KBGR", "KHVN", "Tue, Thu, Sat"),  # New Haven, CT
    (1018, "KBGR", "KRKD", "Mon, Fri"),  # Rockland, ME
    (1020, "KBGR", "KBHB", "Mon, Wed, Fri, Sun"),  # Bar Harbor, ME
    (1022, "KBGR", "KLEB", "Tue, Thu, Sat"),  # Lebanon, NH
    (1024, "KBGR", "KPBG", "Mon, Wed, Fri"),  # Plattsburgh, NY
    (1026, "KBGR", "KSLK", "Mon, Fri"),  # Saranac Lake, NY
    (1028, "KBGR", "KFMH", "Thu, Sun"),  # Falmouth / Cape Cod, MA
    (1030, "KBGR", "KALB", "Mon, Wed, Fri"),  # Albany, NY
    (1032, "KBGR", "KSYR", "Mon, Wed, Fri, Sun"),  # Syracuse, NY
    (1034, "KBGR", "KERI", "Mon, Wed, Fri"),  # Erie, PA
    (1036, "KBGR", "KMQT", "Tue, Thu, Sat"),  # Marquette, MI
    (1038, "KBGR", "KPLN", "Mon, Wed, Fri"),  # Pellston / Mackinac, MI
    (1040, "KBGR", "KDAY", "Tue, Thu, Sat"),  # Dayton, OH
    (1042, "KBGR", "KCMH", "Mon, Wed, Fri, Sun"),  # Columbus, OH
    (1044, "KBGR", "KCVG", "Mon, Wed, Fri, Sun"),  # Cincinnati, OH
    (1046, "KBGR", "KLEX", "Tue, Thu, Sat"),  # Lexington, KY
    (1048, "KBGR", "KEVV", "Mon, Wed, Fri"),  # Evansville, IN
    (1050, "KBGR", "KAUG", "Mon, Fri"),  # Augusta, ME
    (1052, "KBGR", "KSFM", "Tue, Thu, Sat"),  # Sanford, ME
    (1054, "KBGR", "KPSM", "Tue, Thu, Sat"),  # Portsmouth, NH
    (1056, "KBGR", "KCON", "Mon, Wed, Fri"),  # Concord, NH
    (1058, "KBGR", "KMPV", "Tue, Thu, Sat"),  # Barre / Montpelier, VT
    (1060, "KBGR", "KHYA", "Mon, Wed, Fri, Sun"),  # Hyannis / Cape Cod, MA
    (1062, "KBGR", "KEWB", "Tue, Thu, Sat"),  # New Bedford, MA

    # ----------------------------------------------------
    # KRIC Bridge Spokes (1100 Block - Mid-Atlantic Hub)
    # ----------------------------------------------------
    (1100, "KRIC", "KCHS", "Mon, Wed, Fri, Sun"),  # Charleston, SC
    (1102, "KRIC", "KILM", "Mon, Wed, Fri"),  # Wilmington, NC
    (1104, "KRIC", "KABE", "Tue, Thu, Sat"),  # Allentown, PA
    (1106, "KRIC", "KMDT", "Tue, Thu, Sat"),  # Harrisburg, PA
    (1108, "KRIC", "KPIT", "Mon, Wed, Fri, Sun"),  # Pittsburgh, PA
    (1110, "KRIC", "KROA", "Mon, Wed, Fri"),  # Roanoke, VA
    (1112, "KRIC", "KHTS", "Tue, Thu, Sat"),  # Huntington, WV
    (1114, "KRIC", "KCRW", "Tue, Thu, Sat"),  # Charleston, WV
    (1116, "KRIC", "KSAV", "Mon, Wed, Fri, Sun"),  # Savannah, GA
    (1118, "KRIC", "KAVL", "Mon, Wed, Fri, Sun"),  # Asheville, NC
    (1120, "KRIC", "KTRI", "Tue, Thu, Sat"),  # Tri-Cities / Bristol, TN
    (1122, "KRIC", "KEWN", "Mon, Fri"),  # New Bern, NC
    (1124, "KRIC", "KFAY", "Mon, Wed, Fri"),  # Fayetteville, NC
    (1126, "KRIC", "KPHF", "Mon, Fri"),  # Newport News / Williamsburg, VA
    (1128, "KRIC", "KLYH", "Tue, Thu, Sat"),  # Lynchburg, VA
    (1130, "KRIC", "KSBN", "Mon, Wed, Fri"),  # South Bend, IN
    (1132, "KRIC", "KFWA", "Tue, Thu, Sat"),  # Fort Wayne, IN
    (1134, "KRIC", "KTOL", "Mon, Fri"),  # Toledo, OH
    (1136, "KRIC", "KBQK", "Thu, Sun"),  # Brunswick, GA
    (1138, "KRIC", "KMYR", "Mon, Wed, Fri, Sun"),  # Myrtle Beach, SC
    (1140, "KRIC", "KCHO", "Mon, Fri"),  # Charlottesville, VA
    (1142, "KRIC", "KIPT", "Thu, Sun"),  # Williamsport, PA
    (1144, "KRIC", "KMLB", "Mon, Wed, Fri"),  # Melbourne, FL
    (1146, "KRIC", "KECP", "Tue, Thu, Sat"),  # Panama City Beach, FL
    (1148, "KRIC", "KALB", "Mon, Wed, Fri"),  # Albany, NY
    (1150, "KRIC", "KERI", "Mon, Wed, Fri"),  # Erie, PA
    (1152, "KRIC", "KGSO", "Tue, Thu, Sat"),  # Greensboro, NC
    (1154, "KRIC", "KJQF", "Tue, Thu, Sat"),  # Concord / Charlotte, NC
    (1156, "KRIC", "KPGV", "Tue, Thu, Sat"),  # Greenville, NC
    (1158, "KRIC", "KMGM", "Tue, Thu, Sat"),  # Montgomery, AL
    (1160, "KRIC", "KBHM", "Tue, Thu, Sat"),  # Birmingham, AL
    (1162, "KRIC", "KPGD", "Tue, Thu, Sat"),  # Punta Gorda / Ft. Myers, FL
    (1164, "KRIC", "KTYS", "Tue, Thu, Sat"),  # Knoxville, TN
    (1166, "KRIC", "KDAY", "Tue, Thu, Sat"),  # Dayton, OH
    (1168, "KRIC", "KCMH", "Mon, Wed, Fri, Sun"),  # Columbus, OH
    (1170, "KRIC", "KCVG", "Mon, Wed, Fri, Sun"),  # Cincinnati, OH
    (1172, "KRIC", "KLEX", "Tue, Thu, Sat"),  # Lexington, KY
    (1174, "KRIC", "KEVV", "Mon, Wed, Fri"),  # Evansville, IN
    (1176, "KRIC", "KTUP", "Tue, Thu, Sat"),  # Tupelo, MS
    (1178, "KRIC", "KMEI", "Mon, Wed, Fri, Sun"),  # Meridian, MS
    (1180, "KRIC", "KHSV", "Tue, Thu, Sat"),  # Huntsville, AL
    (1182, "KRIC", "KPIB", "Tue, Thu, Sat"),  # Hattiesburg / Laurel, MS
    (1184, "KRIC", "KGTR", "Mon, Wed, Fri, Sun"),  # Columbus / Starkville, MS
    (1186, "KRIC", "KHEZ", "Tue, Thu, Sat"),  # Natchez, MS
    (1188, "KRIC", "KMOB", "Mon, Wed, Fri, Sun"),  # Mobile, AL
    (1190, "KRIC", "KJKA", "Mon, Wed, Fri, Sun"),  # Gulf Shores, AL
    (1192, "KRIC", "KCSG", "Tue, Thu, Sat"),  # Columbus, GA
    (1194, "KRIC", "KMCN", "Mon, Wed, Fri, Sun"),  # Macon, GA
    (1196, "KRIC", "KBWG", "Tue, Thu, Sat"),  # Bowling Green, KY
    (1198, "KRIC", "KGSP", "Mon, Wed, Fri, Sun"),  # Greenville / Spartanburg, SC
    (2100, "KRIC", "KHGR", "Tue, Thu, Sat"),  # Hagerstown, MD
    (2102, "KRIC", "KILG", "Mon, Wed, Fri, Sun"),  # Wilmington / Philadelphia area, DE
    (2104, "KRIC", "KACY", "Tue, Thu, Sat"),  # Atlantic City, NJ
    (2106, "KRIC", "KPKB", "Mon, Wed, Fri, Sun"),  # Parkersburg, WV
    (2108, "KRIC", "KCKB", "Tue, Thu, Sat"),  # Clarksburg, WV
    (2110, "KRIC", "KMGW", "Mon, Wed, Fri"),  # Morgantown, WV
    (2112, "KRIC", "KLWB", "Mon, Wed, Fri, Sun"),  # Lewisburg, WV
    (2114, "KRIC", "KRDU", "Mon, Fri"),  # Raleigh / Durham, NC
    (2116, "KRIC", "KFLO", "Tue, Thu, Sat"),  # Florence, SC
    (2118, "KRIC", "KCAE", "Mon, Wed, Fri, Sun"),  # Columbia, SC
    (2120, "KRIC", "KAGS", "Tue, Thu, Sat"),  # Augusta, GA
    (2122, "KRIC", "KSGJ", "Tue, Thu, Sat"),  # St. Augustine, FL
    (2124, "KRIC", "KPIE", "Mon, Wed, Fri, Sun"),  # St. Petersburg / Clearwater, FL
    (2126, "KRIC", "KGNV", "Mon, Wed, Fri"),  # Gainesville, FL
    (2128, "KRIC", "KSRQ", "Tue, Thu, Sat"),  # Sarasota / Bradenton, FL
    (2130, "KRIC", "KFLL", "Mon, Wed, Fri, Sun"),  # Fort Lauderdale, FL
    (2132, "KRIC", "KEYW", "Mon, Wed, Fri, Sun"),  # Key West, FL
    (2134, "KRIC", "KVPS", "Thu, Sun"),  # Destin / Eglin AFB, FL
    (2136, "KRIC", "KMBS", "Tue, Thu, Sat"),  # Saginaw, MI
    (2138, "KRIC", "KBLF", "Mon, Wed, Fri, Sun"),  # Bluefield, WV

    # ----------------------------------------------------
    # KSFB Bridge Spokes (1200 Block - Florida / Southeast Hub)
    # ----------------------------------------------------
    (1200, "KSFB", "KCHS", "Mon, Wed, Fri, Sun"),  # Charleston, SC
    (1202, "KSFB", "KILM", "Tue, Thu, Sat"),  # Wilmington, NC
    (1204, "KSFB", "KPNS", "Mon, Wed, Fri, Sun"),  # Pensacola, FL
    (1206, "KSFB", "KEYW", "Thu, Sun"),  # Key West, FL
    (1208, "KSFB", "KSAV", "Mon, Wed, Fri, Sun"),  # Savannah, GA
    (1210, "KSFB", "KMOB", "Mon, Wed, Fri, Sun"),  # Mobile, AL
    (1212, "KSFB", "KVPS", "Thu, Sun"),  # Eglin / Destin, FL
    (1214, "KSFB", "KTLH", "Tue, Thu, Sat"),  # Tallahassee, FL
    (1216, "KSFB", "KMYR", "Mon, Wed, Fri, Sun"),  # Myrtle Beach, SC
    (1218, "KSFB", "KGPT", "Mon, Wed, Fri, Sun"),  # Gulfport / Biloxi, MS
    (1220, "KSFB", "KBQK", "Thu, Sun"),  # Brunswick, GA
    (1222, "KSFB", "KGNV", "Mon, Fri"),  # Gainesville, FL
    (1224, "KSFB", "KVRB", "Mon, Wed, Fri"),  # Vero Beach, FL
    (1226, "KSFB", "KAVL", "Mon, Wed, Fri, Sun"),  # Asheville, NC
    (1228, "KSFB", "KTRI", "Tue, Thu, Sat"),  # Tri-Cities / Bristol, TN
    (1230, "KSFB", "KEWN", "Mon, Fri"),  # New Bern, NC
    (1232, "KSFB", "KFAY", "Mon, Wed, Fri"),  # Fayetteville, NC
    (1234, "KSFB", "KPHF", "Tue, Thu, Sat"),  # Newport News / Williamsburg, VA
    (1236, "KSFB", "KLYH", "Tue, Thu, Sat"),  # Lynchburg, VA
    (1238, "KSFB", "KMLB", "Mon, Fri"),  # Melbourne, FL
    (1240, "KSFB", "KECP", "Tue, Thu, Sat"),  # Panama City Beach, FL
    (1242, "KSFB", "KCHO", "Thu, Sun"),  # Charlottesville, VA
    (1244, "KSFB", "KGSO", "Tue, Thu, Sat"),  # Greensboro, NC
    (1246, "KSFB", "KJQF", "Tue, Thu, Sat"),  # Concord / Charlotte, NC
    (1248, "KSFB", "KPGV", "Tue, Thu, Sat"),  # Greenville, NC
    (1250, "KSFB", "KMGM", "Tue, Thu, Sat"),  # Montgomery, AL
    (1252, "KSFB", "KBHM", "Tue, Thu, Sat"),  # Birmingham, AL
    (1254, "KSFB", "KPGD", "Tue, Thu, Sat"),  # Punta Gorda / Ft. Myers, FL
    (1256, "KSFB", "KTYS", "Tue, Thu, Sat"),  # Knoxville, TN
    (1258, "KSFB", "KDAY", "Tue, Thu, Sat"),  # Dayton, OH
    (1260, "KSFB", "KCMH", "Mon, Wed, Fri, Sun"),  # Columbus, OH
    (1262, "KSFB", "KCVG", "Mon, Wed, Fri, Sun"),  # Cincinnati, OH
    (1264, "KSFB", "KLEX", "Tue, Thu, Sat"),  # Lexington, KY
    (1266, "KSFB", "KEVV", "Mon, Wed, Fri"),  # Evansville, IN
    (1268, "KSFB", "KTUP", "Tue, Thu, Sat"),  # Tupelo, MS
    (1270, "KSFB", "KMEI", "Mon, Wed, Fri, Sun"),  # Meridian, MS
    (1272, "KSFB", "KHSV", "Tue, Thu, Sat"),  # Huntsville, AL
    (1274, "KSFB", "KPIB", "Tue, Thu, Sat"),  # Hattiesburg / Laurel, MS
    (1276, "KSFB", "KGTR", "Mon, Wed, Fri, Sun"),  # Columbus / Starkville, MS
    (1278, "KSFB", "KHEZ", "Tue, Thu, Sat"),  # Natchez, MS
    (1280, "KSFB", "KMOB", "Mon, Wed, Fri, Sun"),  # Mobile, AL
    (1282, "KSFB", "KJKA", "Mon, Wed, Fri, Sun"),  # Gulf Shores, AL
    (1284, "KSFB", "KCSG", "Tue, Thu, Sat"),  # Columbus, GA
    (1286, "KSFB", "KMCN", "Mon, Wed, Fri, Sun"),  # Macon, GA
    (1288, "KSFB", "KBWG", "Tue, Thu, Sat"),  # Bowling Green, KY
    (1290, "KSFB", "KGSP", "Mon, Wed, Fri, Sun"),  # Greenville / Spartanburg, SC
    (1292, "KSFB", "KHGR", "Tue, Thu, Sat"),  # Hagerstown, MD
    (1294, "KSFB", "KILG", "Mon, Wed, Fri, Sun"),  # Wilmington / Philadelphia area, DE
    (1296, "KSFB", "KACY", "Mon, Wed, Fri, Sun"),  # Atlantic City, NJ
    (1298, "KSFB", "KPKB", "Mon, Wed, Fri, Sun"),  # Parkersburg, WV
    (2200, "KSFB", "KCKB", "Tue, Thu, Sat"),  # Clarksburg, WV
    (2202, "KSFB", "KMGW", "Tue, Thu, Sat"),  # Morgantown, WV
    (2204, "KSFB", "KLWB", "Mon, Wed, Fri, Sun"),  # Lewisburg, WV
    (2206, "KSFB", "KRDU", "Mon, Wed, Fri, Sun"),  # Raleigh / Durham, NC
    (2208, "KSFB", "KFLO", "Tue, Thu, Sat"),  # Florence, SC
    (2210, "KSFB", "KCAE", "Mon, Wed, Fri, Sun"),  # Columbia, SC
    (2212, "KSFB", "KAGS", "Tue, Thu, Sat"),  # Augusta, GA
    (2214, "KSFB", "KSGJ", "Tue, Thu, Sat"),  # St. Augustine, FL
    (2216, "KSFB", "KPIE", "Mon, Wed, Fri, Sun"),  # St. Petersburg / Clearwater, FL
    (2218, "KSFB", "KGNV", "Mon, Fri"),  # Gainesville, FL
    (2220, "KSFB", "KSRQ", "Tue, Thu, Sat"),  # Sarasota / Bradenton, FL
    (2222, "KSFB", "KFLL", "Mon, Fri"),  # Fort Lauderdale, FL

    # ----------------------------------------------------
    # KSAT Bridge Spokes (1500 Block - Texas / South-Central Hub)
    # ----------------------------------------------------
    (1500, "KSAT", "KELP", "Daily"),  # El Paso, TX
    (1502, "KSAT", "KMAF", "Mon, Wed, Fri, Sun"),  # Midland / Odessa, TX
    (1504, "KSAT", "KLBB", "Mon, Wed, Fri, Sun"),  # Lubbock, TX
    (1506, "KSAT", "KAMA", "Tue, Thu, Sat"),  # Amarillo, TX
    (1508, "KSAT", "KMFE", "Mon, Wed, Fri, Sun"),  # McAllen, TX
    (1510, "KSAT", "KHRL", "Tue, Thu, Sat"),  # Harlingen / South Padre Island, TX
    (1512, "KSAT", "KBRO", "Mon, Wed, Fri"),  # Brownsville, TX
    (1514, "KSAT", "KCRP", "Tue, Thu, Sat"),  # Corpus Christi, TX
    (1516, "KSAT", "KLRD", "Mon, Wed, Fri"),  # Laredo, TX
    (1518, "KSAT", "KABI", "Tue, Thu, Sat"),  # Abilene, TX
    (1520, "KSAT", "KTYR", "Mon, Fri"),  # Tyler, TX
    (1522, "KSAT", "KGGG", "Tue, Sat"),  # Longview, TX
    (1524, "KSAT", "KACT", "Tue, Thu, Sat"),  # Waco, TX
    (1526, "KSAT", "KGRK", "Mon, Wed, Fri"),  # Killeen / Fort Cavazos, TX
    (1528, "KSAT", "KBPT", "Tue, Thu, Sat"),  # Beaumont / Port Arthur, TX
    (1530, "KSAT", "KSHV", "Mon, Wed, Fri, Sun"),  # Shreveport, LA
    (1532, "KSAT", "KLFT", "Tue, Thu, Sat"),  # Lafayette, LA
    (1534, "KSAT", "KBTR", "Mon, Wed, Fri, Sun"),  # Baton Rouge, LA
    (1536, "KSAT", "KLCH", "Tue, Thu, Sat"),  # Lake Charles, LA
    (1538, "KSAT", "KMLU", "Mon, Fri"),  # Monroe, LA
    (1540, "KSAT", "KLIT", "Mon, Wed, Fri, Sun"),  # Little Rock, AR
    (1542, "KSAT", "KXNA", "Tue, Thu, Sat"),  # Bentonville / Fayetteville, AR
    (1544, "KSAT", "KOKC", "Mon, Wed, Fri, Sun"),  # Oklahoma City, OK
    (1546, "KSAT", "KTUL", "Mon, Wed, Fri, Sun"),  # Tulsa, OK
    (1548, "KSAT", "KICT", "Tue, Thu, Sat"),  # Wichita, KS
    (1550, "KSAT", "KMCI", "Daily"),  # Kansas City, MO
    (1552, "KSAT", "KSGF", "Tue, Thu, Sat"),  # Springfield / Branson, MO
    (1554, "KSAT", "KDSM", "Mon, Wed, Fri, Sun"),  # Des Moines, IA
    (1556, "KSAT", "KABQ", "Mon, Wed, Fri, Sun"),  # Albuquerque, NM
    (1558, "KSAT", "KTUS", "Tue, Thu, Sat"),  # Tucson, AZ
    (1560, "KSAT", "KLAS", "Daily"),  # Las Vegas, NV
    (1562, "KSAT", "KPNS", "Mon, Wed, Fri, Sun"),  # Pensacola, FL
    (1564, "KSAT", "KVPS", "Tue, Thu, Sat"),  # Eglin / Destin, FL
    (1566, "KSAT", "KECP", "Thu, Sun"),  # Panama City Beach, FL
    (1568, "KSAT", "KPIE", "Mon, Wed, Fri, Sun"),  # St. Petersburg / Clearwater, FL

    # ----------------------------------------------------
    # KTYS Bridge Spokes (1600 Block - Appalachia / Interior Southeast Hub)
    # ----------------------------------------------------
    (1600, "KTYS", "KCRW", "Mon, Wed, Fri, Sun"),  # Charleston, WV
    (1602, "KTYS", "KHTS", "Tue, Thu, Sat"),  # Huntington, WV
    (1604, "KTYS", "KCKB", "Tue, Thu, Sat"),  # Clarksburg, WV
    (1606, "KTYS", "KMGW", "Mon, Fri"),  # Morgantown, WV
    (1608, "KTYS", "KPKB", "Tue, Thu, Sat"),  # Parkersburg, WV
    (1610, "KTYS", "KLWB", "Thu, Sun"),  # Lewisburg, WV
    (1612, "KTYS", "KLEX", "Mon, Wed, Fri, Sun"),  # Lexington, KY
    (1614, "KTYS", "KSDF", "Daily"),  # Louisville, KY
    (1616, "KTYS", "KCVG", "Mon, Wed, Fri, Sun"),  # Cincinnati, OH
    (1618, "KTYS", "KCMH", "Daily"),  # Columbus, OH
    (1620, "KTYS", "KDAY", "Tue, Thu, Sat"),  # Dayton, OH
    (1622, "KTYS", "KCAK", "Mon, Wed, Fri, Sun"),  # Akron / Canton, OH
    (1624, "KTYS", "KTOL", "Tue, Thu, Sat"),  # Toledo, OH
    (1626, "KTYS", "KIND", "Daily"),  # Indianapolis, IN
    (1628, "KTYS", "KFWA", "Tue, Thu, Sat"),  # Fort Wayne, IN
    (1630, "KTYS", "KSBN", "Mon, Wed, Fri, Sun"),  # South Bend, IN
    (1632, "KTYS", "KEVV", "Tue, Thu, Sat"),  # Evansville, IN
    (1634, "KTYS", "KPIA", "Tue, Thu, Sat"),  # Peoria, IL
    (1636, "KTYS", "KBLV", "Mon, Wed, Fri, Sun"),  # Belleville / St. Louis MidAmerica, IL
    (1638, "KTYS", "KRFD", "Mon, Wed, Fri, Sun"),  # Rockford, IL
    (1640, "KTYS", "KMLI", "Tue, Thu, Sat"),  # Quad Cities / Moline, IL
    (1642, "KTYS", "KMSN", "Mon, Wed, Fri, Sun"),  # Madison, WI
    (1644, "KTYS", "KATW", "Tue, Thu, Sat"),  # Appleton, WI
    (1646, "KTYS", "KGRB", "Mon, Wed, Fri"),  # Green Bay, WI
    (1648, "KTYS", "KFNT", "Mon, Wed, Fri, Sun"),  # Flint, MI
    (1650, "KTYS", "KAZO", "Tue, Thu, Sat"),  # Kalamazoo, MI
    (1652, "KTYS", "KMDT", "Mon, Wed, Fri, Sun"),  # Harrisburg, PA
    (1654, "KTYS", "KABE", "Tue, Thu, Sat"),  # Allentown / Lehigh Valley, PA
    (1656, "KTYS", "KAVP", "Tue, Thu, Sat"),  # Wilkes-Barre / Scranton, PA
    (1658, "KTYS", "KROA", "Mon, Wed, Fri"),  # Roanoke, VA
    (1660, "KTYS", "KORF", "Mon, Wed, Fri, Sun"),  # Norfolk / Virginia Beach, VA
    (1662, "KTYS", "KMYR", "Mon, Wed, Fri, Sun"),  # Myrtle Beach, SC
    (1664, "KTYS", "KCHS", "Mon, Wed, Fri, Sun"),  # Charleston, SC
    (1666, "KTYS", "KSAV", "Tue, Thu, Sat"),  # Savannah, GA
    (1668, "KTYS", "KPIE", "Mon, Wed, Fri, Sun"),  # St. Petersburg / Clearwater, FL
    (1670, "KTYS", "KPGD", "Tue, Thu, Sat"),  # Punta Gorda / Ft. Myers, FL
    (1672, "KTYS", "KVPS", "Thu, Sun"),  # Eglin / Destin, FL
    (1674, "KTYS", "KPNS", "Mon, Wed, Fri, Sun"),  # Pensacola, FL

    # ----------------------------------------------------
    # KONT Bridge Spokes (1700 Block - Southern California / West Coast Hub)
    # ----------------------------------------------------
    (1700, "KONT", "KFAT", "Mon, Wed, Fri, Sun"),  # Fresno, CA
    (1702, "KONT", "KSBP", "Tue, Thu, Sat"),  # San Luis Obispo, CA
    (1704, "KONT", "KSBA", "Mon, Wed, Fri, Sun"),  # Santa Barbara, CA
    (1706, "KONT", "KMRY", "Tue, Thu, Sat"),  # Monterey, CA
    (1708, "KONT", "KOAK", "Daily"),  # Oakland, CA
    (1710, "KONT", "KSJC", "Mon, Wed, Fri, Sun"),  # San Jose, CA
    (1712, "KONT", "KSMF", "Daily"),  # Sacramento, CA
    (1714, "KONT", "KSCK", "Tue, Thu, Sat"),  # Stockton, CA
    (1716, "KONT", "KRDD", "Mon, Fri"),  # Redding, CA
    (1718, "KONT", "KACV", "Tue, Thu, Sat"),  # Arcata / Eureka, CA
    (1720, "KONT", "KBFL", "Mon, Wed, Fri"),  # Bakersfield, CA
    (1722, "KONT", "KSTS", "Tue, Thu, Sat"),  # Santa Rosa / Sonoma, CA
    (1724, "KONT", "KLAS", "Daily"),  # Las Vegas, NV
    (1726, "KONT", "KRNO", "Mon, Wed, Fri, Sun"),  # Reno / Tahoe, NV
    (1728, "KONT", "KTUS", "Mon, Wed, Fri, Sun"),  # Tucson, AZ
    (1730, "KONT", "KFLG", "Tue, Thu, Sat"),  # Flagstaff, AZ
    (1732, "KONT", "KYUM", "Mon, Fri"),  # Yuma, AZ
    (1734, "KONT", "KPDX", "Daily"),  # Portland, OR
    (1736, "KONT", "KEUG", "Mon, Wed, Fri, Sun"),  # Eugene, OR
    (1738, "KONT", "KMFR", "Tue, Thu, Sat"),  # Medford, OR
    (1740, "KONT", "KRDM", "Mon, Wed, Fri"),  # Redmond / Bend, OR
    (1742, "KONT", "KGEG", "Mon, Wed, Fri, Sun"),  # Spokane, WA
    (1744, "KONT", "KPSC", "Tue, Thu, Sat"),  # Pasco / Tri-Cities, WA
    (1746, "KONT", "KBOI", "Mon, Wed, Fri, Sun"),  # Boise, ID
    (1748, "KONT", "KIDA", "Tue, Thu, Sat"),  # Idaho Falls, ID
    (1750, "KONT", "KTWF", "Thu, Sun"),  # Twin Falls, ID
    (1752, "KONT", "KOGD", "Tue, Thu, Sat"),  # Ogden, UT
    (1754, "KONT", "KSGU", "Mon, Wed, Fri"),  # St. George, UT
    (1756, "KONT", "KBZN", "Mon, Wed, Fri, Sun"),  # Bozeman, MT
    (1758, "KONT", "KMSO", "Tue, Thu, Sat"),  # Missoula, MT
    (1760, "KONT", "KGPI", "Thu, Sun"),  # Kalispell / Glacier Park, MT
    (1762, "KONT", "KBIL", "Tue, Thu, Sat"),  # Billings, MT
    (1764, "KONT", "KGJT", "Tue, Thu, Sat"),  # Grand Junction, CO
    (1766, "KONT", "KABQ", "Mon, Wed, Fri, Sun"),  # Albuquerque, NM
    (1768, "KONT", "KELP", "Mon, Wed, Fri, Sun"),  # El Paso, TX

    # ----------------------------------------------------
    # KCOS Bridge Spokes (1900 Block - Colorado / Rocky Mountain Hub)
    # ----------------------------------------------------
    (1900, "KCOS", "KGJT", "Mon, Wed, Fri, Sun"),  # Grand Junction, CO
    (1902, "KCOS", "KMTJ", "Tue, Thu, Sat"),  # Montrose / Telluride, CO
    (1904, "KCOS", "KDRO", "Mon, Wed, Fri"),  # Durango, CO
    (1906, "KCOS", "KHDN", "Thu, Sun"),  # Hayden / Steamboat Springs, CO
    (1908, "KCOS", "KEGE", "Thu, Sun"),  # Eagle / Vail, CO
    (1910, "KCOS", "KABQ", "Mon, Wed, Fri, Sun"),  # Albuquerque, NM
    (1912, "KCOS", "KSAF", "Tue, Thu, Sat"),  # Santa Fe, NM
    (1914, "KCOS", "KROW", "Mon, Fri"),  # Roswell, NM
    (1916, "KCOS", "KCYS", "Tue, Thu, Sat"),  # Cheyenne, WY
    (1918, "KCOS", "KCPR", "Mon, Wed, Fri"),  # Casper, WY
    (1920, "KCOS", "KJAC", "Thu, Sun"),  # Jackson Hole, WY
    (1922, "KCOS", "KCOD", "Tue, Sat"),  # Cody / Yellowstone, WY
    (1924, "KCOS", "KRAP", "Mon, Wed, Fri, Sun"),  # Rapid City, SD
    (1926, "KCOS", "KFSD", "Mon, Wed, Fri, Sun"),  # Sioux Falls, SD
    (1928, "KCOS", "KBIS", "Tue, Thu, Sat"),  # Bismarck, ND
    (1930, "KCOS", "KFAR", "Mon, Wed, Fri, Sun"),  # Fargo, ND
    (1932, "KCOS", "KGFK", "Tue, Thu, Sat"),  # Grand Forks, ND
    (1934, "KCOS", "KMOT", "Mon, Fri"),  # Minot, ND
    (1936, "KCOS", "KBIL", "Mon, Wed, Fri, Sun"),  # Billings, MT
    (1938, "KCOS", "KBZN", "Mon, Wed, Fri, Sun"),  # Bozeman, MT
    (1940, "KCOS", "KMSO", "Tue, Thu, Sat"),  # Missoula, MT
    (1942, "KCOS", "KGTF", "Tue, Thu, Sat"),  # Great Falls, MT
    (1944, "KCOS", "KBOI", "Mon, Wed, Fri, Sun"),  # Boise, ID
    (1946, "KCOS", "KIDA", "Tue, Thu, Sat"),  # Idaho Falls, ID
    (1948, "KCOS", "KICT", "Mon, Wed, Fri, Sun"),  # Wichita, KS
    (1950, "KCOS", "KLNK", "Tue, Thu, Sat"),  # Lincoln, NE
    (1952, "KCOS", "KGRI", "Mon, Fri"),  # Grand Island, NE
    (1954, "KCOS", "KDSM", "Mon, Wed, Fri, Sun"),  # Des Moines, IA
    (1956, "KCOS", "KCID", "Tue, Thu, Sat"),  # Cedar Rapids, IA
    (1958, "KCOS", "KSGF", "Tue, Thu, Sat"),  # Springfield / Branson, MO
    (1960, "KCOS", "KXNA", "Mon, Wed, Fri, Sun"),  # Bentonville / Fayetteville, AR
    (1962, "KCOS", "KTUL", "Mon, Wed, Fri, Sun"),  # Tulsa, OK
    (1964, "KCOS", "KOKC", "Mon, Wed, Fri, Sun"),  # Oklahoma City, OK
    (1966, "KCOS", "KAMA", "Tue, Thu, Sat"),  # Amarillo, TX
    (1968, "KCOS", "KLBB", "Tue, Thu, Sat"),  # Lubbock, TX

]

AIRPORT_NAMES = {
    # Hubs
    "PAFA": "Fairbanks, AK",
    "KBLI": "Bellingham, WA",
    "KIWA": "Phoenix / Mesa, AZ",
    "KPVU": "Provo, UT",
    "KOMA": "Omaha, NE",
    "KMSY": "New Orleans, LA",
    "KGRR": "Grand Rapids, MI",
    "KSWF": "Newburgh / Stewart, NY",
    "KBGR": "Bangor, ME",
    "KRIC": "Richmond, VA",
    "KSFB": "Orlando / Sanford, FL",
    "TJBQ": "Aguadilla, PR",

    # Alaska & Hawaii
    "PABE": "Bethel, AK",
    "PABR": "Utqiaġvik (Barrow), AK",
    "PACB": "Cold Bay, AK",
    "PACV": "Cordova, AK",
    "PADK": "Adak, AK",
    "PADL": "Dillingham, AK",
    "PADQ": "Kodiak, AK",
    "PAEN": "Kenai, AK",
    "PAGA": "Galena, AK",
    "PAGS": "Gustavus, AK",
    "PAHO": "Homer, AK",
    "PAJN": "Juneau, AK",
    "PAKN": "King Salmon, AK",
    "PAKT": "Ketchikan, AK",
    "PAKW": "Wrangell, AK",
    "PANC": "Anchorage, AK",
    "PAOM": "Nome, AK",
    "PAOT": "Kotzebue, AK",
    "PAPG": "Petersburg, AK",
    "PASC": "Deadhorse / Prudhoe Bay, AK",
    "PASI": "Sitka, AK",
    "PAUL": "Unalakleet, AK",
    "PAVD": "Valdez, AK",
    "PAYA": "Yakutat, AK",
    "PHKO": "Kailua-Kona, HI",
    "PHLI": "Lihue, HI",
    "PHNL": "Honolulu, HI",
    "PHOG": "Kahului, HI (Maui)",

    # Intermountain West & Pacific Northwest
    "KACV": "Arcata / Eureka, CA",
    "KALW": "Walla Walla, WA",
    "KBFL": "Bakersfield, CA",
    "KBIL": "Billings, MT",
    "KBJC": "Broomfield, CO",
    "KBOI": "Boise, ID",
    "KBZN": "Bozeman, MT",
    "KCDC": "Cedar City, UT",
    "KCLM": "Port Angeles, WA",
    "KCNY": "Moab, UT",
    "KCOD": "Cody, WY",
    "KCOE": "Coeur d'Alene, ID",
    "KCOS": "Colorado Springs, CO",
    "KCPR": "Casper, WY",
    "KCYS": "Cheyenne, WY",
    "KDRO": "Durango, CO",
    "KDVT": "Phoenix / Deer Valley, AZ",
    "KEAT": "Wenatchee, WA",
    "KEGE": "Eagle / Vail, CO",
    "KEKO": "Elko, NV",
    "KEUG": "Eugene, OR",
    "KFAT": "Fresno, CA",
    "KFLG": "Flagstaff, AZ",
    "KGEG": "Spokane, WA",
    "KGJT": "Grand Junction, CO",
    "KGPI": "Kalispell, MT",
    "KGTF": "Great Falls, MT",
    "KHDN": "Hayden / Steamboat Springs, CO",
    "KHLN": "Helena, MT",
    "KIDA": "Idaho Falls, ID",
    "KIFP": "Bullhead City / Laughlin, AZ",
    "KJAC": "Jackson Hole, WY",
    "KLAS": "Las Vegas, NV",
    "KLMT": "Klamath Falls, OR",
    "KLWS": "Lewiston, ID",
    "KMFR": "Medford / Rogue Valley, OR",
    "KMRY": "Monterey, CA",
    "KMSO": "Missoula, MT",
    "KMTJ": "Montrose / Telluride, CO",
    "KMWH": "Moses Lake, WA",
    "KOAK": "Oakland, CA",
    "KOGD": "Ogden, UT",
    "KONT": "Ontario, CA",
    "KOTH": "North Bend / Coos Bay, OR",
    "KPAE": "Everett, WA",
    "KPDX": "Portland, OR",
    "KPIH": "Pocatello, ID",
    "KPRC": "Prescott, AZ",
    "KPSC": "Pasco / Tri-Cities, WA",
    "KPSP": "Palm Springs, CA",
    "KPUB": "Pueblo, CO",
    "KRDD": "Redding, CA",
    "KRDM": "Bend / Redmond, OR",
    "KRNO": "Reno / Tahoe, NV",
    "KSAN": "San Diego, CA",
    "KSBA": "Santa Barbara, CA",
    "KSBD": "San Bernardino, CA",
    "KSBP": "San Luis Obispo, CA",
    "KSCK": "Stockton, CA",
    "KSGU": "St. George, UT",
    "KSJC": "San Jose, CA",
    "KSLE": "Salem, OR",
    "KSMF": "Sacramento, CA",
    "KSTS": "Santa Rosa / Sonoma, CA",
    "KSUN": "Sun Valley, ID",
    "KTWF": "Twin Falls, ID",
    "KVEL": "Vernal, UT",
    "KYKM": "Yakima, WA",
    "KYUM": "Yuma, AZ",

    # Southwest & South Central
    "KABI": "Abilene, TX",
    "KABQ": "Albuquerque, NM",
    "KACT": "Waco, TX",
    "KAMA": "Amarillo, TX",
    "KBPT": "Beaumont / Port Arthur, TX",
    "KBRO": "Brownsville, TX",
    "KCRP": "Corpus Christi, TX",
    "KELP": "El Paso, TX",
    "KGGG": "Longview, TX",
    "KGRK": "Killeen / Fort Cavazos, TX",
    "KHRL": "Harlingen, TX",
    "KLAW": "Lawton, OK",
    "KLBB": "Lubbock, TX",
    "KLRD": "Laredo, TX",
    "KMAF": "Midland / Odessa, TX",
    "KMFE": "McAllen, TX",
    "KOKC": "Oklahoma City, OK",
    "KROW": "Roswell, NM",
    "KSAF": "Santa Fe, NM",
    "KSAT": "San Antonio, TX",
    "KSJT": "San Angelo, TX",
    "KTUL": "Tulsa, OK",
    "KTUS": "Tucson, AZ",
    "KTYR": "Tyler, TX",
    "KVCT": "Victoria, TX",

    # Gulf Coast & South
    "KAEX": "Alexandria, LA",
    "KBHM": "Birmingham, AL",
    "KBTR": "Baton Rouge, LA",
    "KBWG": "Bowling Green, KY",
    "KCHA": "Chattanooga, TN",
    "KFSM": "Fort Smith, AR",
    "KGPT": "Gulfport / Biloxi, MS",
    "KGTR": "Columbus / Starkville, MS",
    "KHBG": "Hattiesburg, MS",
    "KHEZ": "Natchez, MS",
    "KHSV": "Huntsville, AL",
    "KJKA": "Gulf Shores, AL",
    "KLCH": "Lake Charles, LA",
    "KLEX": "Lexington, KY",
    "KLFT": "Lafayette, LA",
    "KLIT": "Little Rock, AR",
    "KMEI": "Meridian, MS",
    "KMGM": "Montgomery, AL",
    "KMLU": "Monroe, LA",
    "KMOB": "Mobile, AL",
    "KOWB": "Owensboro, KY",
    "KPIB": "Hattiesburg / Laurel, MS",
    "KSDF": "Louisville, KY",
    "KSHV": "Shreveport, LA",
    "KTRI": "Tri-Cities / Bristol, TN",
    "KTUP": "Tupelo, MS",
    "KTYS": "Knoxville, TN",
    "KXNA": "Fayetteville / Northwest Arkansas, AR",

    # Midwest
    "KALO": "Waterloo, IA",
    "KBIS": "Bismarck, ND",
    "KBJI": "Bemidji, MN",
    "KBLV": "Belleville, IL",
    "KCID": "Cedar Rapids, IA",
    "KCOU": "Columbia, MO",
    "KDBQ": "Dubuque, IA",
    "KDIK": "Dickinson, ND",
    "KDLH": "Duluth, MN",
    "KDSM": "Des Moines, IA",
    "KDVL": "Devils Lake, ND",
    "KFAR": "Fargo, ND",
    "KFSD": "Sioux Falls, SD",
    "KGCK": "Garden City, KS",
    "KGFK": "Grand Forks, ND",
    "KGRI": "Grand Island, NE",
    "KICT": "Wichita, KS",
    "KINL": "International Falls, MN",
    "KJEF": "Jefferson City, MO",
    "KJMS": "Jamestown, ND",
    "KLNK": "Lincoln, NE",
    "KMCI": "Kansas City, MO",
    "KMLI": "Moline / Quad Cities, IL",
    "KMOT": "Minot, ND",
    "KPIA": "Peoria, IL",
    "KPIR": "Pierre, SD",
    "KRAP": "Rapid City, SD",
    "KRFD": "Rockford, IL",
    "KRST": "Rochester, MN",
    "KSGF": "Springfield, MO",
    "KSLN": "Salina, KS",
    "KSPI": "Springfield, IL",
    "KSTC": "St. Cloud, MN",
    "KSTJ": "St. Joseph, MO",
    "KSUX": "Sioux City, IA",
    "KTOP": "Topeka, KS",

    # Great Lakes
    "KAPN": "Alpena, MI",
    "KATW": "Appleton, WI",
    "KAZO": "Kalamazoo, MI",
    "KBMI": "Bloomington, IL",
    "KCAK": "Akron / Canton, OH",
    "KCIU": "Sault Ste. Marie, MI",
    "KCMH": "Columbus, OH",
    "KCMX": "Houghton, MI",
    "KCVG": "Cincinnati, OH",
    "KCWA": "Mosinee / Wausau, WI",
    "KDAY": "Dayton, OH",
    "KESC": "Escanaba, MI",
    "KEVV": "Evansville, IN",
    "KFNT": "Flint, MI",
    "KFWA": "Fort Wayne, IN",
    "KGRB": "Green Bay, WI",
    "KGYY": "Gary / Chicago, IN",
    "KIMT": "Iron Mountain, MI",
    "KIND": "Indianapolis, IN",
    "KISQ": "Sault Ste. Marie, MI",
    "KJVY": "Jeffersonville, IN",
    "KLAN": "Lansing, MI",
    "KLSE": "La Crosse, WI",
    "KMBS": "Saginaw, MI",
    "KMKE": "Milwaukee, WI",
    "KMQT": "Marquette, MI",
    "KMSN": "Madison, WI",
    "KPLN": "Pellston / Mackinac, MI",
    "KSBN": "South Bend, IN",
    "KTOL": "Toledo, OH",
    "KTVC": "Traverse City, MI",

    # Northeast & Mid-Atlantic
    "KABE": "Allentown / Lehigh Valley, PA",
    "KACK": "Nantucket, MA",
    "KACY": "Atlantic City, NJ",
    "KAGS": "Augusta, GA",
    "KALB": "Albany, NY",
    "KART": "Watertown, NY",
    "KAUG": "Augusta, ME",
    "KAVL": "Asheville, NC",
    "KAVP": "Wilkes-Barre / Scranton, PA",
    "KBFD": "Bradford, PA",
    "KBGM": "Binghamton, NY",
    "KBHB": "Bar Harbor, ME",
    "KBLF": "Bluefield, WV",
    "KBQK": "Brunswick, GA",
    "KBTV": "Burlington, VT",
    "KBUF": "Buffalo, NY",
    "KCAE": "Columbia, SC",
    "KCHO": "Charlottesville, VA",
    "KCHS": "Charleston, SC",
    "KCKB": "Clarksburg, WV",
    "KCON": "Concord, NH",
    "KCRW": "Charleston, WV",
    "KCSG": "Columbus, GA",
    "KDUJ": "DuBois, PA",
    "KELM": "Elmira / Corning, NY",
    "KERI": "Erie, PA",
    "KEWB": "New Bedford, MA",
    "KEWN": "New Bern, NC",
    "KFAY": "Fayetteville, NC",
    "KFLO": "Florence, SC",
    "KFMH": "Falmouth / Cape Cod, MA",
    "KFRG": "Farmingdale / Long Island, NY",
    "KGON": "Groton / New London, CT",
    "KGSO": "Greensboro, NC",
    "KGSP": "Greenville / Spartanburg, SC",
    "KHGR": "Hagerstown, MD",
    "KHPN": "White Plains / Westchester, NY",
    "KHTS": "Huntington, WV",
    "KHVN": "New Haven, CT",
    "KHYA": "Hyannis / Cape Cod, MA",
    "KILG": "Wilmington, DE",
    "KILM": "Wilmington, NC",
    "KIPT": "Williamsport, PA",
    "KISP": "Islip / Long Island, NY",
    "KITH": "Ithaca, NY",
    "KJQF": "Concord / Charlotte, NC",
    "KJST": "Johnstown, PA",
    "KLBE": "Latrobe / Greensburg, PA",
    "KLEB": "Lebanon, NH",
    "KLNS": "Lancaster, PA",
    "KLWB": "Lewisburg, WV",
    "KLYH": "Lynchburg, VA",
    "KMCN": "Macon, GA",
    "KMDT": "Harrisburg, PA",
    "KMGW": "Morgantown, WV",
    "KMHT": "Manchester, NH",
    "KMIV": "Millville, NJ",
    "KMPV": "Barre / Montpelier, VT",
    "KMSS": "Massena, NY",
    "KMVY": "Martha's Vineyard, MA",
    "KMYR": "Myrtle Beach, SC",
    "KOGS": "Ogdensburg, NY",
    "KOQU": "Quonset State / North Kingstown, RI",
    "KORF": "Norfolk / Virginia Beach, VA",
    "KORH": "Worcester, MA",
    "KPBG": "Plattsburgh, NY",
    "KPGV": "Greenville, NC",
    "KPHF": "Newport News / Williamsburg, VA",
    "KPIT": "Pittsburgh, PA",
    "KPKB": "Parkersburg, WV",
    "KPQB": "Presque Isle, ME",
    "KPSM": "Portsmouth, NH",
    "KPVD": "Providence, RI",
    "KPWM": "Portland, ME",
    "KRDG": "Reading, PA",
    "KRDU": "Raleigh / Durham, NC",
    "KRKD": "Rockland, ME",
    "KROA": "Roanoke, VA",
    "KROC": "Rochester, NY",
    "KSAV": "Savannah, GA",
    "KSBY": "Salisbury, MD",
    "KSFM": "Sanford, ME",
    "KSLK": "Saranac Lake, NY",
    "KSYR": "Syracuse, NY",
    "KTTN": "Trenton, NJ",

    # Florida
    "KECP": "Panama City Beach, FL",
    "KEYW": "Key West, FL",
    "KFLL": "Fort Lauderdale, FL",
    "KGNV": "Gainesville, FL",
    "KMLB": "Melbourne, FL",
    "KPGD": "Punta Gorda / Ft. Myers, FL",
    "KPIE": "St. Petersburg / Clearwater, FL",
    "KPNS": "Pensacola, FL",
    "KSGJ": "St. Augustine, FL",
    "KSRQ": "Sarasota / Bradenton, FL",
    "KTLH": "Tallahassee, FL",
    "KVPS": "Eglin / Destin, FL",
    "KVRB": "Vero Beach, FL",

    # Caribbean & Latin America
    "MBPV": "Providenciales, Turks & Caicos",
    "MDPC": "Punta Cana, Dominican Republic",
    "MGGT": "Guatemala City, Guatemala",
    "MKJP": "Kingston, Jamaica",
    "MKJS": "Montego Bay, Jamaica",
    "MMBT": "Huatulco, Mexico",
    "MMCZ": "Cozumel, Mexico",
    "MMGL": "Guadalajara, Mexico",
    "MMHO": "Hermosillo, Mexico",
    "MMMZ": "Mazatlán, Mexico",
    "MMPB": "Puebla, Mexico",
    "MMPR": "Puerto Vallarta, Mexico",
    "MMSD": "Los Cabos, Mexico",
    "MMTJ": "Tijuana, Mexico",
    "MMUN": "Cancún, Mexico",
    "MMVR": "Veracruz, Mexico",
    "MNMG": "Managua, Nicaragua",
    "MPPA": "Howard / Panama Pacifico, Panama",
    "MRLB": "Liberia / Guanacaste, Costa Rica",
    "MROC": "San José, Costa Rica",
    "MUHA": "Havana, Cuba",
    "MUVR": "Varadero, Cuba",
    "MWCR": "Grand Cayman, Cayman Islands",
    "MYNN": "Nassau, Bahamas",
    "MYSM": "San Salvador, Bahamas",
    "MZBZ": "Belize City, Belize",
    "SAEZ": "Buenos Aires Ezeiza, Argentina",
    "SCEL": "Santiago, Chile",
    "SEQM": "Quito, Ecuador",
    "SKBO": "Bogota, Colombia",
    "SKCG": "Cartagena, Colombia",
    "SKCL": "Cali, Colombia",
    "SKRG": "Medellin, Colombia",
    "SMJP": "Paramaribo, Suriname",
    "SPJC": "Lima, Peru",
    "SPQU": "Arequipa, Peru",
    "SYCJ": "Georgetown, Guyana",
    "TAPA": "Antigua",
    "TBPB": "Bridgetown, Barbados",
    "TFFF": "Martinique",
    "TFFR": "Guadeloupe",
    "TIST": "St. Thomas, USVI",
    "TISX": "St. Croix, USVI",
    "TJPS": "Ponce, PR",
    "TJSJ": "San Juan, PR",
    "TKPK": "St. Kitts",
    "TLPL": "St. Lucia",
    "TNCA": "Aruba",
    "TNCB": "Bonaire",
    "TNCC": "Curaçao",
    "TNCM": "St. Maarten",
    "TVSA": "St. Vincent",

    # Canada
    "CYDF": "Deer Lake, NL, Canada",
    "CYEG": "Edmonton, AB, Canada",
    "CYEV": "Inuvik, NT, Canada",
    "CYFC": "Fredericton, NB, Canada",
    "CYHM": "Hamilton / Toronto South, ON, Canada",
    "CYHZ": "Halifax, NS, Canada",
    "CYLW": "Kelowna, BC, Canada",
    "CYQB": "Quebec City, QC, Canada",
    "CYQM": "Moncton, NB, Canada",
    "CYQY": "Sydney, NS, Canada",
    "CYSJ": "Saint John, NB, Canada",
    "CYUL": "Montréal, QC, Canada",
    "CYVR": "Vancouver, BC, Canada",
    "CYWG": "Winnipeg, MB, Canada",
    "CYXS": "Prince George, BC, Canada",
    "CYXX": "Abbotsford, BC, Canada",
    "CYXY": "Whitehorse, YT, Canada",
    "CYYC": "Calgary, AB, Canada",
    "CYYG": "Charlottetown, PE, Canada",
    "CYYJ": "Victoria, BC, Canada",
    "CYYT": "St. John's, NL, Canada",
    "CYZF": "Yellowknife, NT, Canada",

    # Europe, Asia & Transatlantic
    "BIKF": "Reykjavik / Keflavik, Iceland",
    "EBBR": "Brussels, Belgium",
    "EDDF": "Frankfurt, Germany",
    "EDDM": "Munich, Germany",
    "EFHK": "Helsinki, Finland",
    "EGCC": "Manchester, United Kingdom",
    "EGLL": "London Heathrow, United Kingdom",
    "EGPK": "Glasgow, Scotland",
    "EHAM": "Amsterdam, Netherlands",
    "EIDW": "Dublin, Ireland",
    "EINN": "Shannon, Ireland",
    "EKCH": "Copenhagen, Denmark",
    "ENGM": "Oslo, Norway",
    "ESSA": "Stockholm Arlanda, Sweden",
    "LEBL": "Barcelona, Spain",
    "LEMD": "Madrid, Spain",
    "LFPG": "Paris Charles de Gaulle, France",
    "LGAV": "Athens, Greece",
    "LIRF": "Rome Fiumicino, Italy",
    "LOWW": "Vienna, Austria",
    "LPPD": "Ponta Delgada (Azores), Portugal",
    "LPPT": "Lisbon, Portugal",
    "LROP": "Bucharest, Romania",
    "LSZH": "Zurich, Switzerland",
    "RKPK": "Busan, South Korea",
    "ROAH": "Naha, Japan",
    "RORS": "Shimojishima, Japan",
    "RPLC": "Clark, Philippines",
    "TXKF": "Bermuda",

}


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

import math

# ==============================================================================
# AIRPORT COORDINATES MAP (Latitude, Longitude)
# Contains all 185 unique airports across your route network blocks.
# Format: "ICAO/IATA": (latitude, longitude)
# ==============================================================================

    # --------------------------------------------------------------------------
    # HUB AIRPORTS
    # --------------------------------------------------------------------------
import math

AIRPORT_COORDS = {
    # HUBS / FOCUS CITIES
    "PAFA": (64.8151, -147.8564), "KPVU": (40.2192, -111.7233),
    "KIWA": (33.3078, -111.6550), "KBLI": (48.7927, -122.5375),
    "KMSY": (29.9934, -90.2580),  "KOMA": (41.3025, -95.8942),
    "KGRR": (42.8808, -85.5228),  "TJBQ": (18.4949, -67.1294),
    "KSWF": (41.5041, -74.1048),  "KBGR": (44.8074, -68.8281),
    "KRIC": (37.5052, -77.3197),  "KSFB": (28.7776, -81.2375),
    "KONT": (34.0560, -117.6012), "KCOS": (38.8058, -104.7008),
    "KSAT": (29.5337, -98.4698),  "KTYS": (35.8110, -83.9940),

    # ALASKA SPOKES
    "PAJN": (58.3594, -134.5762), "PAKT": (55.3556, -131.7137),
    "PABR": (71.2854, -156.7660), "PAOT": (66.8847, -162.5986),
    "PASC": (70.1947, -148.4652), "PADQ": (57.7499, -152.4939),
    "PAOM": (64.5122, -165.4453), "PAPG": (56.8017, -132.9453),
    "PASI": (57.0471, -135.3616), "PAYA": (59.5033, -139.6602),
    "PAVD": (61.1339, -146.2483), "PAEN": (60.5731, -151.2450),
    "PAKW": (56.4843, -132.3698), "PAHO": (59.6456, -151.4766),
    "PADL": (59.0454, -158.5033), "PAKN": (58.6768, -156.6492),
    "PAGS": (58.4244, -135.7075),

    # HAWAII SPOKES
    "PHNL": (21.3187, -157.9224), "PHOG": (20.8986, -156.4305),
    "PHKO": (19.7388, -155.9874), "PHLI": (21.9760, -159.3390),

    # INTERMOUNTAIN & PACIFIC NORTHWEST SPOKES
    "KALW": (46.0944, -118.2881), "KBIL": (45.8077, -108.5429),
    "KBOI": (43.5644, -116.2228), "KBZN": (45.7775, -111.1531),
    "KCDC": (37.7010, -113.0988), "KCLM": (48.1202, -123.4997),
    "KCNY": (38.7550, -109.7548), "KCOD": (44.5202, -109.0238),
    "KCPR": (42.9080, -106.4644), "KCYS": (41.1557, -104.8118),
    "KEAT": (47.3999, -120.2068), "KEGE": (39.6426, -106.9177),
    "KEUG": (44.1233, -123.2186), "KGEG": (47.6199, -117.5338),
    "KGJT": (39.1224, -108.5267), "KGPI": (48.3105, -114.2560),
    "KGTF": (47.4820, -111.3707), "KHDN": (40.4812, -107.2177),
    "KHLN": (46.6068, -111.9827), "KIDA": (43.5146, -112.0702),
    "KJAC": (43.6073, -110.7377), "KLWS": (46.3745, -117.0154),
    "KMFR": (42.3742, -122.8735), "KMSO": (46.9163, -114.0906),
    "KMTJ": (38.5098, -107.8943), "KOGD": (41.1959, -112.0122),
    "KOTH": (43.4171, -124.2460), "KPDX": (45.5898, -122.5951),
    "KPIH": (42.9113, -112.5959), "KPSC": (46.2647, -119.1190),
    "KRDM": (44.2541, -121.1500), "KRNO": (39.4991, -119.7681),
    "KSGU": (37.0364, -113.5103), "KTWF": (42.4818, -114.4877),
    "KVEL": (40.4409, -109.5099), "KYKM": (46.5682, -120.5440),

    # SOUTHWEST SPOKES
    "KABQ": (35.0402, -106.6091), "KACV": (40.9781, -124.1086),
    "KBFL": (35.4336, -119.0567), "KDRO": (37.1515, -107.7538),
    "KDVT": (33.6883, -112.0825), "KEKO": (40.8249, -115.7917),
    "KELP": (31.8066, -106.3778), "KFAT": (36.7762, -119.7181),
    "KFLG": (35.1384, -111.6712), "KSEZ": (34.8486, -111.7886),
    "KIFP": (35.1561, -114.5595), "KLAS": (36.0840, -115.1537),
    "KMAF": (31.9425, -102.2019), "KMRY": (36.5870, -121.8430),
    "KOAK": (37.7213, -122.2208), "KPRC": (34.6545, -112.4196),
    "KPSP": (33.8297, -116.5067), "KRDD": (40.5090, -122.2934),
    "KROW": (33.3015, -104.5306), "KSAF": (35.6171, -106.0894),
    "KSBA": (34.4262, -119.8403), "KSBD": (34.0953, -117.2349),
    "KSBP": (35.2371, -120.6424), "KSCK": (37.8942, -121.2383),
    "KSJC": (37.3626, -121.9290), "KSMF": (38.6954, -121.5908),
    "KSTS": (38.5090, -122.8129), "KTUS": (32.1161, -110.9410),
    "KYUM": (32.6566, -114.6060),

    # GULF COAST & MIDWEST SPOKES
    "KABI": (32.4163, -99.6804),  "KACT": (31.6113, -97.2293),
    "KAEX": (31.3274, -92.5498),  "KALO": (42.5571, -92.4003),
    "KAMA": (35.2194, -101.7059), "KATW": (44.2575, -88.5192),
    "KBHM": (33.5629, -86.7535),  "KBIS": (46.7727, -100.7460),
    "KBJI": (47.5098, -94.9333),  "KBLV": (38.5451, -89.8458),
    "KBMI": (40.4771, -88.9159),  "KBPT": (29.9508, -94.0207),
    "KBRO": (25.9068, -97.4259),  "KBTR": (30.5332, -91.1496),
    "KBWG": (36.9696, -86.4137),  "KCHA": (35.0353, -85.2038),
    "KCID": (41.8847, -91.7108),  "KCOU": (38.8181, -92.2196),
    "KCRP": (27.7704, -97.5012),  "KCSG": (32.5163, -84.9388),
    "KCWA": (44.7776, -89.6661),  "KDBQ": (42.4020, -90.7095),
    "KDIK": (46.7979, -102.8023), "KDSM": (41.5340, -93.6631),
    "KDVL": (48.1158, -98.9036),  "KESC": (45.7445, -87.0988),
    "KFAR": (46.9197, -96.8157),  "KFSD": (43.5820, -96.7418),
    "KFSM": (35.3364, -94.3687),  "KGCK": (37.9275, -100.7244),
    "KGFK": (47.9473, -97.1738),  "KGGG": (32.3840, -94.7115),
    "KGPT": (30.4073, -89.0701),  "KGRI": (40.9675, -98.3096),
    "KGRK": (31.0672, -97.8289),  "KGTR": (33.4547, -88.5912),
    "KGYY": (41.6163, -87.4139),  "KHBG": (31.2829, -89.2530),
    "KHEZ": (31.7915, -91.2991),  "KHRL": (26.2285, -97.6544),
    "KHSV": (34.6404, -86.7756),  "KICT": (37.6499, -97.4331),
    "KIMT": (45.8184, -88.1143),  "KINL": (48.5682, -93.4003),
    "KISQ": (45.9744, -86.1714),  "KJEF": (38.5962, -92.1578),
    "KJKA": (30.2882, -87.6713),  "KJMS": (46.9298, -98.6782),
    "KJVY": (38.2731, -85.7397),  "KLAW": (34.5676, -98.4153),
    "KLBB": (33.6636, -101.8228), "KLCH": (30.1261, -93.2233),
    "KLFT": (30.2053, -91.9876),  "KLIT": (34.7294, -92.2243),
    "KLNK": (40.8510, -96.7592),  "KLRD": (27.5438, -99.4616),
    "KLSE": (43.8794, -91.2567),  "KMCI": (39.2976, -94.7139),
    "KMCN": (32.6939, -83.6431),  "KMEI": (32.3432, -88.7554),
    "KMFE": (26.1758, -98.2386),  "KMGM": (32.3006, -86.3940),
    "KMLI": (41.4485, -90.5075),  "KMLU": (32.5109, -92.0376),
    "KMOB": (30.6914, -88.2428),  "KMOT": (48.2575, -101.2803),
    "KOKC": (35.3931, -97.6007),  "KOWB": (37.7408, -87.1656),
    "KPIA": (40.6642, -89.6933),  "KPIB": (31.4673, -89.3374),
    "KPIR": (44.3845, -100.2862), "KPNS": (30.4734, -87.1866),
    "KRAP": (44.0453, -103.0572), "KRFD": (42.1954, -89.0982),
    "KSDF": (38.1741, -85.7365),  "KSGF": (37.2457, -93.3886),
    "KSHV": (32.4466, -93.8256),  "KSJT": (31.3564, -100.4963),
    "KSLN": (38.7911, -97.6519),  "KSPI": (39.8441, -89.6779),
    "KSTC": (45.5456, -94.0699),  "KSTJ": (39.7733, -94.9056),
    "KSUX": (42.4026, -96.3844),  "KTOP": (39.0706, -95.6258),
    "KTRI": (36.4752, -82.4074),  "KTUL": (36.1984, -95.8881),
    "KTUP": (34.2690, -88.7656),  "KTYR": (32.3541, -95.4024),
    "KVCT": (28.8475, -96.9774),  "KVPS": (30.4832, -86.5254),
    "KXNA": (36.2819, -94.3068),

    # GREAT LAKES SPOKES
    "KAPN": (45.0781, -83.5603),  "KAZO": (42.2349, -85.5521),
    "KCAK": (40.9161, -81.4422),  "KCIU": (46.2508, -84.4725),
    "KCMH": (39.9981, -82.8919),  "KCMX": (47.1684, -88.4891),
    "KCVG": (39.0461, -84.6622),  "KDAY": (39.9024, -84.2194),
    "KDLH": (46.8421, -92.1936),  "KERI": (42.0820, -80.1762),
    "KEVV": (38.0383, -87.5308),  "KFNT": (42.9654, -83.7436),
    "KFWA": (40.9785, -85.1951),  "KGRB": (44.4846, -88.1297),
    "KHTS": (38.3667, -82.5580),  "KIND": (39.7173, -86.2944),
    "KLAN": (42.7787, -84.5874),  "KLEX": (38.0364, -84.6058),
    "KMBS": (43.5328, -84.0796),  "KMKE": (42.9472, -87.8966),
    "KMQT": (46.3536, -87.3953),  "KMSN": (43.1399, -89.3375),
    "KPIT": (40.4915, -80.2329),  "KPLN": (45.5708, -84.7967),
    "KRST": (43.9083, -92.4980),  "KSBN": (41.7086, -86.3173),
    "KTOL": (41.5868, -83.8078),  "KTVC": (44.7414, -85.5822),

    # NORTHEAST & NORTHERN NEW ENGLAND SPOKES
    "KABE": (40.6521, -75.4408),  "KACK": (41.2531, -70.0602),
    "KALB": (42.7483, -73.8017),  "KART": (44.0022, -75.7217),
    "KAUG": (44.3206, -69.7972),  "KAVP": (41.3385, -75.7234),
    "KBFD": (41.8031, -78.6401),  "KBGM": (42.2086, -75.9797),
    "KBHB": (44.4498, -68.3616),  "KBTV": (44.4730, -73.1533),
    "KBUF": (42.9405, -78.7322),  "KCON": (43.2028, -71.5022),
    "KDUJ": (41.1783, -78.8986),  "KELM": (42.1599, -76.8914),
    "KEWB": (41.6761, -70.9583),  "KFMH": (41.6585, -70.5215),
    "KFRG": (40.7288, -73.4134),  "KGON": (41.3301, -72.0456),
    "KHPN": (41.0670, -73.7076),  "KHVN": (41.2638, -72.8868),
    "KHYA": (41.6693, -70.2804),  "KIPT": (41.2419, -76.9211),
    "KISP": (40.7952, -73.1002),  "KITH": (42.4913, -76.4585),
    "KJST": (40.3229, -78.8338),  "KLBE": (40.2759, -79.4048),
    "KLEB": (43.6261, -72.3042),  "KLNS": (40.1217, -76.2960),
    "KMDT": (40.1935, -76.7634),  "KMHT": (42.9326, -71.4357),
    "KMIV": (39.3678, -75.0722),  "KMPV": (44.2035, -72.5623),
    "KMSS": (44.9358, -74.8456),  "KMVY": (41.3931, -70.6143),
    "KOGS": (44.6819, -75.4656),  "KOQU": (41.5972, -71.4122),
    "KORH": (42.2673, -71.8757),  "KPBG": (44.6509, -73.4681),
    "KPQB": (46.6889, -68.0448),  "KPSM": (43.0779, -70.8233),
    "KPVD": (41.7240, -71.4282),  "KPWM": (43.6462, -70.3088),
    "KRDG": (40.3785, -75.9652),  "KRKD": (44.0601, -69.0992),
    "KROC": (43.1189, -77.6724),  "KSBY": (38.3405, -75.5103),
    "KSFM": (43.3939, -70.7075),  "KSLK": (44.3853, -74.2062),
    "KSYR": (43.1112, -76.1063),  "KTTN": (40.2767, -74.8135),

    # MID-ATLANTIC & SOUTHEAST SPOKES
    "KACY": (39.4576, -74.5772),  "KAGS": (33.3699, -82.0292),
    "KAVL": (35.4362, -82.5418),  "KBLF": (37.2934, -81.2155),
    "KBQK": (31.2590, -81.4663),  "KCAE": (33.9388, -81.1195),
    "KCHO": (38.1386, -78.4529),  "KCHS": (32.8986, -80.0405),
    "KCKB": (39.2965, -80.2280),  "KCRW": (38.3731, -81.5932),
    "KECP": (30.3571, -85.7956),  "KEWN": (35.0730, -77.0429),
    "KFAY": (34.9912, -78.8803),  "KFLO": (34.1874, -79.7153),
    "KFLL": (26.0726, -80.1527),  "KGNV": (29.6901, -82.2718),
    "KGSO": (36.0978, -79.9373),  "KGSP": (34.8957, -82.2188),
    "KHGR": (39.7077, -77.7297),  "KILG": (39.6787, -75.6065),
    "KILM": (34.2706, -77.9026),  "KEYW": (24.5557, -81.7596),
    "KJQF": (35.3878, -80.7092),  "KLWB": (37.8583, -80.3995),
    "KLYH": (37.3267, -79.2004),  "KMGW": (39.6425, -79.9157),
    "KMLB": (28.1028, -80.6453),  "KMYR": (33.6797, -78.9283),
    "KORF": (36.8946, -76.2012),  "KPGD": (26.9163, -82.0006),
    "KPGV": (35.6353, -77.3853),  "KPHF": (37.1319, -76.4930),
    "KPIE": (27.9105, -82.6874),  "KPKB": (39.3453, -81.4423),
    "KRDU": (35.8776, -78.7875),  "KROA": (37.3255, -79.9754),
    "KSAV": (32.1276, -81.2021),  "KSGJ": (29.9593, -81.3397),
    "KSRQ": (27.3954, -82.5544),  "KTLH": (30.3965, -84.3503),
    "KVRB": (27.6556, -80.4179),

    # CANADA
    "CYDF": (49.2082, -57.3961),  "CYEG": (53.3097, -113.5800),
    "CYFC": (45.8689, -66.5372),  "CYHM": (43.1736, -79.9350),
    "CYHZ": (44.8808, -63.5086),  "CYQB": (46.7911, -71.3933),
    "CYQM": (46.1132, -64.6772),  "CYQY": (46.1614, -60.0478),
    "CYSJ": (45.3161, -65.8903),  "CYUL": (45.4706, -73.7408),
    "CYVR": (49.1939, -123.1840), "CYWG": (49.9100, -97.2397),
    "CYXS": (53.8894, -122.6790), "CYXY": (60.7096, -135.0673),
    "CYYC": (51.1188, -114.0099), "CYYG": (46.2900, -63.1211),
    "CYYJ": (48.6469, -123.4258), "CYYT": (47.6186, -52.7519),
    "CYZF": (62.4631, -114.4403),

    # MEXICO & CENTRAL AMERICA
    "MGGT": (14.5833, -90.5275),  "MMBT": (15.7753, -96.2625),
    "MMCZ": (20.5224, -86.9255),  "MMGL": (20.5218, -103.3112),
    "MMHO": (29.0958, -111.0478), "MMMZ": (23.1614, -106.3712),
    "MMPB": (19.1583, -98.3711),  "MMPR": (20.6801, -105.2541),
    "MMSD": (23.1518, -109.7210), "MMTJ": (32.5411, -116.9700),
    "MMUN": (21.0365, -86.8771),  "MMVR": (19.1458, -96.1897),
    "MNMG": (12.1444, -86.1683),  "MPPA": (8.9775, -79.5997),
    "MROC": (9.9939, -84.2088),   "MRLB": (10.5933, -85.5444),
    "MZBZ": (17.5391, -88.3082),

    # CARIBBEAN & US TERRITORIES
    "MBPV": (21.7736, -72.2659),  "MDPC": (18.5674, -68.3634),
    "MKJP": (17.9356, -76.7875),  "MKJS": (18.5037, -77.9134),
    "MUHA": (22.9892, -82.4092),  "MUVR": (23.1592, -81.4328),
    "MWCR": (19.2922, -81.3578),  "MYNN": (25.0390, -77.4662),
    "MYSM": (24.0864, -74.5247),  "TAPA": (17.1367, -61.7927),
    "TBPB": (13.0746, -59.4925),  "TFFF": (14.5910, -61.0032),
    "TFFR": (16.2653, -61.5318),  "TIST": (18.3373, -64.9734),
    "TISX": (17.7019, -64.7986),  "TJPS": (18.0083, -66.5630),
    "TJSJ": (18.4394, -66.0018),  "TKPK": (17.3112, -62.7187),
    "TLPL": (13.7332, -60.9526),  "TNCA": (12.5014, -70.0152),
    "TNCB": (12.1310, -68.2685),  "TNCC": (12.1889, -68.9598),
    "TNCM": (18.0410, -63.1089),  "TVSA": (13.1569, -61.1481),

    # SOUTH AMERICA
    "SAEZ": (-34.8222, -58.5358), "SCEL": (-33.3930, -70.7858),
    "SEQM": (-0.1292, -78.3575),  "SKBO": (-4.7016, -74.1469),
    "SKCG": (10.4424, -75.5130),  "SKCL": (3.5433, -76.3814),
    "SKRG": (6.1645, -75.4233),   "SMJP": (5.4431, -55.1903),
    "SPJC": (-12.0219, -77.1143), "SPQU": (-16.3411, -71.5831),
    "SYCJ": (6.4981, -58.2539),

    # EUROPE & ICELAND
    "BIKF": (63.9850, -22.6056),  "EBBR": (50.9014, 4.4844),
    "EDDF": (50.0379, 8.5622),    "EDDM": (48.3538, 11.7861),
    "EFHK": (60.3172, 24.9633),   "EGCC": (53.3537, -2.2750),
    "EGPK": (55.5094, -4.5867),   "EGLL": (51.4700, -0.4543),
    "EHAM": (52.3105, 4.7683),    "EIDW": (53.4213, -6.2701),
    "EINN": (52.7020, -8.9248),   "EKCH": (55.6180, 12.6508),
    "ENGM": (60.1939, 11.1004),   "ESSA": (59.6519, 17.9186),
    "LEBL": (41.2974, 2.0833),    "LEMD": (40.4936, -3.5668),
    "LFPG": (49.0097, 2.5479),    "LGAV": (37.9364, 23.9445),
    "LIRF": (41.8003, 12.2389),   "LOWW": (48.1103, 16.5697),
    "LPPD": (37.7412, -25.6979),  "LPPT": (38.7813, -9.1359),
    "LROP": (44.5722, 26.1022),   "LSZH": (47.4647, 8.5492),
    "TXKF": (32.3640, -64.6787),

    # ASIA & PACIFIC
    "RKPK": (35.1795, 128.9381),  "ROAH": (26.1958, 127.6458),
    "RORS": (24.8267, 125.1458),  "RPLC": (15.1878, 120.5606),
}

# ==========================================
# 4. SKYBUS PRICING, TAX & ROUTING ENGINE
# ==========================================

AIRCRAFT_CAPACITY = {"A319": 150, "A320": 180, "A321": 220}
US_TERRITORIES = {"TJBQ", "TJSJ", "TJPS", "TIST", "TISX"}

# Rural / EAS airports exempt from the $5.30 domestic segment tax and $4.50 PFC
RURAL_EXEMPT_AIRPORTS = {
    "KBFD", "KDUJ", "KJST", "KIPT", "KSLK", "KMSS", "KOGS", "KART",
    "KAUG", "KBHB", "KPQB", "KRKD", "KLEB", "KMPV", "KPIR", "KDVL",
    "KJMS", "KDIK", "KGCK", "KSLN", "KGRI", "KALO", "KDBQ", "KSTJ",
    "KJEF", "KCOU", "KBLF", "KHEZ", "KMEI", "KTUP", "KGTR", "KEKO",
    "KVEL", "KCNY", "KCDC", "KIFP", "KLMT", "KOTH", "KEAT", "KALW",
    "KLWS", "KPIH", "KCOD", "KCLM", "KSEZ", "KPRC", "KROW", "KISQ",
    "KIMT", "KESC", "KCMX", "KCIU", "KAPN", "KPLN", "KINL", "KBJI",
    "KCON", "KFMH", "KFRG", "KMIV", "KOQU", "KSFM", "KLWB", "KMGW",
    "KPKB", "KCKB", "PABR", "PAOT", "PASC", "PAOM", "PAPG", "PAYA",
    "PAVD", "PAKW", "PAHO", "PADL", "PAKN", "PAGS",
}

# Market & operating-cost multipliers (default = 1.00)
AIRPORT_MULTIPLIERS = {
    # Remote / Overwater / 2-ACT Long-Haul
    "PAFA": 1.30, "PABR": 1.45, "PASC": 1.45, "PAOT": 1.40, "PAOM": 1.40,
    "PADL": 1.40, "PAKN": 1.40, "PADQ": 1.35, "PAJN": 1.30, "PAKT": 1.30,
    "PASI": 1.30, "PAPG": 1.35, "PAYA": 1.35, "PAVD": 1.35, "PAEN": 1.30,
    "PAKW": 1.35, "PAHO": 1.30, "PAGS": 1.35,
    "PHNL": 1.30, "PHOG": 1.30, "PHKO": 1.30, "PHLI": 1.35,
    "TJBQ": 1.25, "TJSJ": 1.25, "TJPS": 1.25, "TIST": 1.30, "TISX": 1.30,
    # High-Yield Ski / Island / Resort
    "KEYW": 1.30, "KJAC": 1.25, "KEGE": 1.25, "KHDN": 1.20, "KMTJ": 1.20,
    "KDRO": 1.15, "KBZN": 1.15, "KGPI": 1.15, "KMSO": 1.15, "KMVY": 1.25,
    "KACK": 1.25, "KHYA": 1.15, "KPSP": 1.15, "KLAS": 1.15, "KSBA": 1.15,
    "KMRY": 1.15, "KHPN": 1.15, "KAVL": 1.12, "KCHS": 1.12, "KSAV": 1.12,
    "KMYR": 1.10, "KFLL": 1.10, "KSRQ": 1.10, "KECP": 1.10, "KVPS": 1.10,
    # Thin Regional / Price-Stimulation Spokes
    "KBLF": 0.85, "KPKB": 0.85, "KCKB": 0.90, "KDIK": 0.85, "KPIR": 0.85,
    "KDVL": 0.85, "KJMS": 0.85, "KGCK": 0.88, "KSLN": 0.88, "KGRI": 0.88,
    "KALO": 0.88, "KDBQ": 0.88, "KSTJ": 0.88, "KJEF": 0.88, "KHEZ": 0.85,
    "KMEI": 0.85, "KTUP": 0.88, "KBFD": 0.85, "KDUJ": 0.85, "KJST": 0.85,
    "KSLK": 0.85, "KMSS": 0.85, "KOGS": 0.85, "KART": 0.88, "KAUG": 0.85,
    "KRKD": 0.85, "KPQB": 0.85, "KLEB": 0.88, "KMPV": 0.85,
    # International Handling & Slot Tiers
    "EGLL": 1.35, "LFPG": 1.30, "EDDF": 1.28, "EDDM": 1.28, "EHAM": 1.28,
    "LSZH": 1.32, "LOWW": 1.25, "EKCH": 1.25, "ENGM": 1.25, "ESSA": 1.25,
    "EFHK": 1.25, "EBBR": 1.25, "LIRF": 1.25, "LEMD": 1.25, "LEBL": 1.25,
    "LGAV": 1.25, "LROP": 1.20, "EIDW": 1.20, "EINN": 1.18, "EGCC": 1.22,
    "EGPK": 1.15, "BIKF": 1.20, "LPPT": 1.22, "LPPD": 1.18, "TXKF": 1.25,
    "SAEZ": 1.30, "SCEL": 1.30, "SPJC": 1.25, "SPQU": 1.22, "SEQM": 1.22,
    "SKBO": 1.20, "SKCG": 1.22, "SKCL": 1.20, "SKRG": 1.20, "SMJP": 1.25,
    "SYCJ": 1.25, "RKPK": 1.30, "ROAH": 1.30, "RORS": 1.32, "RPLC": 1.28,
}

# Directional foreign departure & arrival taxes/airport fees (USD) for all 96 non-US airports
FOREIGN_PORT_FEES = {
    # Canada
    "CYVR": {"dep": 44.00, "arr": 0.00, "label": "Canada ATSC + YVR AIF"},
    "CYYC": {"dep": 47.00, "arr": 0.00, "label": "Canada ATSC + YYC AIF"},
    "CYEG": {"dep": 47.00, "arr": 0.00, "label": "Canada ATSC + YEG AIF"},
    "CYUL": {"dep": 47.00, "arr": 0.00, "label": "Canada ATSC + YUL AIF"},
    "CYHZ": {"dep": 47.00, "arr": 0.00, "label": "Canada ATSC + YHZ AIF"},
    "CYQB": {"dep": 47.00, "arr": 0.00, "label": "Canada ATSC + YQB AIF"},
    "CYWG": {"dep": 49.00, "arr": 0.00, "label": "Canada ATSC + YWG AIF"},
    "CYYT": {"dep": 51.00, "arr": 0.00, "label": "Canada ATSC + YYT AIF"},
    "CYDF": {"dep": 48.00, "arr": 0.00, "label": "Canada ATSC + YDF AIF"},
    "CYFC": {"dep": 46.00, "arr": 0.00, "label": "Canada ATSC + YFC AIF"},
    "CYHM": {"dep": 43.00, "arr": 0.00, "label": "Canada ATSC + YHM AIF"},
    "CYQM": {"dep": 46.00, "arr": 0.00, "label": "Canada ATSC + YQM AIF"},
    "CYQY": {"dep": 46.00, "arr": 0.00, "label": "Canada ATSC + YQY AIF"},
    "CYSJ": {"dep": 46.00, "arr": 0.00, "label": "Canada ATSC + YSJ AIF"},
    "CYXS": {"dep": 44.00, "arr": 0.00, "label": "Canada ATSC + YXS AIF"},
    "CYXY": {"dep": 41.00, "arr": 0.00, "label": "Canada ATSC + YXY AIF"},
    "CYYG": {"dep": 46.00, "arr": 0.00, "label": "Canada ATSC + YYG AIF"},
    "CYYJ": {"dep": 42.00, "arr": 0.00, "label": "Canada ATSC + YYJ AIF"},
    "CYZF": {"dep": 44.00, "arr": 0.00, "label": "Canada ATSC + YZF AIF"},
    # Mexico
    "MMUN": {"dep": 36.00, "arr": 42.00, "label": "Mexico TUA / DNR Tourism Tax"},
    "MMCZ": {"dep": 38.00, "arr": 42.00, "label": "Mexico TUA / DNR Tourism Tax"},
    "MMSD": {"dep": 44.00, "arr": 42.00, "label": "Mexico TUA / DNR Tourism Tax"},
    "MMPR": {"dep": 42.00, "arr": 42.00, "label": "Mexico TUA / DNR Tourism Tax"},
    "MMGL": {"dep": 45.00, "arr": 42.00, "label": "Mexico TUA / DNR Tourism Tax"},
    "MMTJ": {"dep": 39.00, "arr": 42.00, "label": "Mexico TUA / DNR Tourism Tax"},
    "MMHO": {"dep": 38.00, "arr": 42.00, "label": "Mexico TUA / DNR Tourism Tax"},
    "MMMZ": {"dep": 44.00, "arr": 42.00, "label": "Mexico TUA / DNR Tourism Tax"},
    "MMBT": {"dep": 43.00, "arr": 42.00, "label": "Mexico TUA / DNR Tourism Tax"},
    "MMPB": {"dep": 36.00, "arr": 42.00, "label": "Mexico TUA / DNR Tourism Tax"},
    "MMVR": {"dep": 41.00, "arr": 42.00, "label": "Mexico TUA / DNR Tourism Tax"},
    # Central America
    "MROC": {"dep": 32.00, "arr": 15.00, "label": "Costa Rica Exit & Airport Tax"},
    "MRLB": {"dep": 32.00, "arr": 15.00, "label": "Costa Rica Exit & Airport Tax"},
    "MZBZ": {"dep": 55.50, "arr": 18.00, "label": "Belize PACT Conservation & Airport Tax"},
    "MPPA": {"dep": 45.00, "arr": 15.00, "label": "Panama Airport & Security Fee"},
    "MGGT": {"dep": 33.00, "arr": 15.00, "label": "Guatemala Departure & Security Tax"},
    "MNMG": {"dep": 44.00, "arr": 12.00, "label": "Nicaragua Airport & Tourist Tax"},
    # Caribbean & Bermuda (Foreign)
    "MYNN": {"dep": 62.00, "arr": 29.00, "label": "Bahamas Departure, Security & NAD Fee"},
    "MYSM": {"dep": 45.00, "arr": 29.00, "label": "Bahamas Out-Island Departure Tax"},
    "MBPV": {"dep": 58.00, "arr": 20.00, "label": "Turks & Caicos Airport & Tourism Tax"},
    "MDPC": {"dep": 48.00, "arr": 20.00, "label": "Dominican Republic Exit & Tourist Card"},
    "MKJP": {"dep": 65.00, "arr": 35.00, "label": "Jamaica Tourism Enhancement & Airport Fee"},
    "MKJS": {"dep": 65.00, "arr": 35.00, "label": "Jamaica Tourism Enhancement & Airport Fee"},
    "MUHA": {"dep": 30.00, "arr": 25.00, "label": "Cuba Airport & Sanitary Tax"},
    "MUVR": {"dep": 30.00, "arr": 25.00, "label": "Cuba Airport & Sanitary Tax"},
    "MWCR": {"dep": 52.00, "arr": 25.00, "label": "Cayman Islands Departure & Security Tax"},
    "TAPA": {"dep": 55.00, "arr": 20.00, "label": "Antigua Embarkation & Facility Fee"},
    "TBPB": {"dep": 58.00, "arr": 20.00, "label": "Barbados Departure & Security Levy"},
    "TFFF": {"dep": 42.00, "arr": 18.00, "label": "French Antilles Airport & Solidarity Tax"},
    "TFFR": {"dep": 42.00, "arr": 18.00, "label": "French Antilles Airport & Solidarity Tax"},
    "TKPK": {"dep": 52.00, "arr": 20.00, "label": "St. Kitts Departure & Environmental Levy"},
    "TLPL": {"dep": 54.00, "arr": 20.00, "label": "St. Lucia Airport Service & Security Tax"},
    "TNCA": {"dep": 54.00, "arr": 20.00, "label": "Aruba PFC & Tourism Levy"},
    "TNCB": {"dep": 48.00, "arr": 20.00, "label": "Bonaire Airport & Visitor Entry Tax"},
    "TNCC": {"dep": 52.00, "arr": 20.00, "label": "Curaçao Airport Passenger Facility Charge"},
    "TNCM": {"dep": 50.00, "arr": 18.00, "label": "St. Maarten Departure & Security Fee"},
    "TVSA": {"dep": 50.00, "arr": 20.00, "label": "St. Vincent Airport Service Charge"},
    "TXKF": {"dep": 68.00, "arr": 35.00, "label": "Bermuda Passenger Departure & Tourism Tax"},
    # South America
    "SKBO": {"dep": 54.00, "arr": 25.00, "label": "Colombia Aerocivil & Tourism Tax"},
    "SKCG": {"dep": 54.00, "arr": 25.00, "label": "Colombia Aerocivil & Tourism Tax"},
    "SKCL": {"dep": 54.00, "arr": 25.00, "label": "Colombia Aerocivil & Tourism Tax"},
    "SKRG": {"dep": 54.00, "arr": 25.00, "label": "Colombia Aerocivil & Tourism Tax"},
    "SPJC": {"dep": 48.00, "arr": 15.00, "label": "Peru TUUA & Tourism Tax"},
    "SPQU": {"dep": 46.00, "arr": 15.00, "label": "Peru TUUA & Tourism Tax"},
    "SEQM": {"dep": 56.00, "arr": 18.00, "label": "Ecuador Eco-Delta & Quito Airport Fee"},
    "SCEL": {"dep": 34.00, "arr": 15.00, "label": "Chile Embarque International Fee"},
    "SAEZ": {"dep": 64.00, "arr": 22.00, "label": "Argentina Tasa de Uso & Security Tax"},
    "SMJP": {"dep": 48.00, "arr": 20.00, "label": "Suriname Terminal & Security Fee"},
    "SYCJ": {"dep": 45.00, "arr": 20.00, "label": "Guyana Travel & Security Tax"},
    # Europe & Iceland
    "EGLL": {"dep": 162.00, "arr": 0.00,  "label": "UK Air Passenger Duty (APD) + LHR PSC"},
    "EGCC": {"dep": 144.00, "arr": 0.00,  "label": "UK Air Passenger Duty (APD) + MAN PSC"},
    "EGPK": {"dep": 134.00, "arr": 0.00,  "label": "UK Air Passenger Duty (APD) + PIK PSC"},
    "EDDF": {"dep": 108.00, "arr": 22.00, "label": "Germany Air Transport Tax + FRA PSC"},
    "EDDM": {"dep": 104.00, "arr": 20.00, "label": "Germany Air Transport Tax + MUC PSC"},
    "LFPG": {"dep": 88.00,  "arr": 20.00, "label": "France Solidarity/Eco Tax + CDG PSC"},
    "EHAM": {"dep": 78.00,  "arr": 18.00, "label": "Netherlands Flight Tax + AMS PSC"},
    "LSZH": {"dep": 62.00,  "arr": 18.00, "label": "Switzerland ZRH Passenger & Noise Fee"},
    "LOWW": {"dep": 58.00,  "arr": 16.00, "label": "Austria Air Transport Levy + VIE PSC"},
    "EBBR": {"dep": 54.00,  "arr": 16.00, "label": "Belgium Embarkation & BRU PSC"},
    "EIDW": {"dep": 36.00,  "arr": 14.00, "label": "Ireland DUB Passenger Service Charge"},
    "EINN": {"dep": 32.00,  "arr": 12.00, "label": "Ireland SNN Passenger Service Charge"},
    "BIKF": {"dep": 34.00,  "arr": 14.00, "label": "Iceland KEF Passenger & Security Fee"},
    "EKCH": {"dep": 46.00,  "arr": 15.00, "label": "Denmark Passenger Tax + CPH PSC"},
    "ENGM": {"dep": 48.00,  "arr": 15.00, "label": "Norway Air Passenger Tax + OSL PSC"},
    "ESSA": {"dep": 44.00,  "arr": 14.00, "label": "Sweden ARN Passenger & Security Fee"},
    "EFHK": {"dep": 38.00,  "arr": 14.00, "label": "Finland HEL Passenger & Security Fee"},
    "LEMD": {"dep": 38.00,  "arr": 14.00, "label": "Spain AENA Departure & Security Fee"},
    "LEBL": {"dep": 38.00,  "arr": 14.00, "label": "Spain AENA Departure & Security Fee"},
    "LIRF": {"dep": 52.00,  "arr": 16.00, "label": "Italy Council City Tax + FCO PSC"},
    "LGAV": {"dep": 46.00,  "arr": 15.00, "label": "Greece Airport Development & ATH PSC"},
    "LPPT": {"dep": 42.00,  "arr": 14.00, "label": "Portugal Carbon Tax + LIS PSC"},
    "LPPD": {"dep": 34.00,  "arr": 12.00, "label": "Portugal Azores PDL Passenger Fee"},
    "LROP": {"dep": 34.00,  "arr": 12.00, "label": "Romania OTP Passenger & Security Fee"},
    # Asia & Pacific
    "RKPK": {"dep": 26.00,  "arr": 10.00, "label": "South Korea Departure & PUS Facility Fee"},
    "ROAH": {"dep": 28.00,  "arr": 10.00, "label": "Japan Intl Tourist Tax + OKA PSFC"},
    "RORS": {"dep": 26.00,  "arr": 10.00, "label": "Japan Intl Tourist Tax + SHI PSFC"},
    "RPLC": {"dep": 36.00,  "arr": 12.00, "label": "Philippines Travel Tax & CRK Terminal Fee"},
}


def get_coords(code):
    """Safely retrieves airport coordinates even if AIRPORT_COORDS is defined lower in the file."""
    coords_map = globals().get("AIRPORT_COORDS", {})
    return coords_map.get(str(code).strip().upper())


def haversine_miles(coord1, coord2):
    """Calculates distance between two lat/lon points in statute miles."""
    if not coord1 or not coord2:
        return 0
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    R = 3958.8
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def haversine_nm(origin: str, dest: str) -> float:
    """Calculates distance between two ICAO codes in nautical miles safely."""
    c1, c2 = get_coords(origin), get_coords(dest)
    if not c1 or not c2:
        return 600.0
    lat1, lon1 = map(math.radians, c1)
    lat2, lon2 = map(math.radians, c2)
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return round(3440.065 * 2 * math.asin(math.sqrt(a)), 1)


def is_us_airport(code: str) -> bool:
    code = str(code).strip().upper()
    return code.startswith(("K", "PA", "PH")) or code in US_TERRITORIES


def parse_flight_int(flight_val) -> int:
    digits = "".join(ch for ch in str(flight_val) if ch.isdigit())
    return int(digits) if digits else 100


def compute_leg_taxes(origin: str, dest: str, taxable_fare: float, include_tsa: bool = True) -> dict:
    orig_us = is_us_airport(origin)
    dest_us = is_us_airport(dest)
    fees = {}

    if orig_us and dest_us:
        if origin in US_TERRITORIES or dest in US_TERRITORIES:
            fees["U.S. Territory Head Tax"] = 23.40
            if include_tsa:
                fees["TSA Sept 11 Security Fee"] = 5.60
            fees["U.S. Airport PFC"] = 4.50
        elif (
            (origin.startswith(("PA", "PH")) or dest.startswith(("PA", "PH")))
            and not (origin.startswith("PA") and dest.startswith("PA"))
            and not (origin.startswith("PH") and dest.startswith("PH"))
        ):
            fees["U.S. Federal Excise Tax (7.5%)"] = round(taxable_fare * 0.075, 2)
            fees["AK/HI Non-Contiguous Tax"] = 11.70
            if include_tsa:
                fees["TSA Sept 11 Security Fee"] = 5.60
            fees["U.S. Airport PFC"] = 4.50
        else:
            exempt_seg = origin in RURAL_EXEMPT_AIRPORTS or dest in RURAL_EXEMPT_AIRPORTS
            exempt_pfc = origin in RURAL_EXEMPT_AIRPORTS
            fees["U.S. Federal Excise Tax (7.5%)"] = round(taxable_fare * 0.075, 2)
            if not exempt_seg:
                fees["U.S. Flight Segment Tax"] = 5.30
            if include_tsa:
                fees["TSA Sept 11 Security Fee"] = 5.60
            if not exempt_pfc:
                fees["U.S. Airport PFC"] = 4.50

    elif orig_us and not dest_us:
        fees["U.S. Intl Departure Tax"] = 23.40
        if include_tsa:
            fees["TSA Sept 11 Security Fee"] = 5.60
        if origin not in RURAL_EXEMPT_AIRPORTS:
            fees["U.S. Airport PFC"] = 4.50
        dest_port = FOREIGN_PORT_FEES.get(dest)
        if dest_port and dest_port["arr"] > 0:
            fees[f"{dest_port['label']} (Arrival)"] = dest_port["arr"]

    elif not orig_us and dest_us:
        orig_port = FOREIGN_PORT_FEES.get(origin)
        if orig_port and orig_port["dep"] > 0:
            fees[f"{orig_port['label']} (Departure)"] = orig_port["dep"]
        fees["U.S. Intl Arrival Tax"] = 23.40
        fees["U.S. Customs (CBP) User Fee"] = 7.39
        fees["U.S. Immigration User Fee"] = 7.00
        fees["U.S. APHIS Agriculture Fee"] = 3.71

    else:
        orig_port = FOREIGN_PORT_FEES.get(origin)
        dest_port = FOREIGN_PORT_FEES.get(dest)
        if orig_port and orig_port["dep"] > 0:
            fees[f"{orig_port['label']} (Departure)"] = orig_port["dep"]
        if dest_port and dest_port["arr"] > 0:
            fees[f"{dest_port['label']} (Arrival)"] = dest_port["arr"]

    return fees

def quote_flight(
    origin: str,
    dest: str,
    aircraft: str = "A320",
    seats_sold: int = 0,
    include_tsa: bool = True,
    flight_num: int = 100,
    search_nonce: int | None = None,
    session_booked: int = 0,
) -> dict:
    capacity = AIRCRAFT_CAPACITY.get(aircraft, 180)
    total_sold = min(capacity, seats_sold + session_booked)
    seats_left = max(0, capacity - total_sold)
    if seats_left == 0:
        return {"sold_out": True}

    dist_nm = haversine_nm(origin, dest)
    m_air = (AIRPORT_MULTIPLIERS.get(origin, 1.0) + AIRPORT_MULTIPLIERS.get(dest, 1.0)) / 2
    ref_fare = (24.00 + (dist_nm * 0.068)) * m_air
    load_factor = total_sold / capacity

    # Completely random roll per flight per search for a $10 BIRD-10 base fare (~30% odds)
    rng = (
        random.Random(f"bird10-{flight_num}-{search_nonce}")
        if search_nonce is not None
        else random.SystemRandom()
    )
    won_bird10 = rng.random() < 0.30
    bird10_pool = rng.randint(1, 4) if won_bird10 else 0
    bird10_remaining = max(0, bird10_pool - session_booked)

    if won_bird10 and bird10_remaining > 0:
        bucket, base_fare, carrier_fee = "BIRD-10", 10.00, 0.00
        bucket_left = min(seats_left, bird10_remaining)
    elif load_factor < 0.65:
        bucket, base_fare, carrier_fee = "SAVER", max(29.00, round(ref_fare * 0.75)), 12.00
        bucket_left = seats_left
    elif load_factor < 0.82:
        bucket, base_fare, carrier_fee = "VALUE", max(44.00, round(ref_fare * 1.00)), 15.00
        bucket_left = seats_left
    elif load_factor < 0.92:
        bucket, base_fare, carrier_fee = "STANDARD", max(64.00, round(ref_fare * 1.30)), 18.00
        bucket_left = seats_left
    else:
        bucket, base_fare, carrier_fee = "LAST SEAT", max(89.00, round(ref_fare * 1.65)), 20.00
        bucket_left = seats_left

    tax_breakdown = compute_leg_taxes(origin, dest, base_fare + carrier_fee, include_tsa=include_tsa)
    taxes_total = round(sum(tax_breakdown.values()), 2)
    all_in_total = round(base_fare + carrier_fee + taxes_total, 2)

    tier = 0 if dist_nm < 600 else (1 if dist_nm < 1500 else 2)
    ancillaries = {
        "personal_item": 0.00,
        "carry_on_bag": [29.00, 39.00, 49.00][tier],
        "checked_bag_1": [15.00, 25.00, 35.00][tier],
        "checked_bag_2": [25.00, 35.00, 45.00][tier],
        "priority_boarding": [10.00, 14.00, 18.00][tier],
        "seat_selection": [12.00, 18.00, 26.00][tier],
        "wifi": [8.00, 12.00, 16.00][tier],
    }

    return {
        "sold_out": False,
        "route": f"{origin}-{dest}",
        "distance_nm": dist_nm,
        "bucket": bucket,
        "seats_left_in_bucket": bucket_left,
        "base_fare": round(base_fare, 2),
        "carrier_fee": round(carrier_fee, 2),
        "taxes_total": taxes_total,
        "tax_breakdown": tax_breakdown,
        "all_in_total": all_in_total,
        "ancillaries": ancillaries,
    }

def get_nonstop_flights(
    network: list[dict], origin: str, destination: str | None = None
) -> list[dict]:
    """Returns all active nonstop flights operating today from `origin`.
    If `destination` is provided (and not 'ALL'), filters to that nonstop pair.
    """
    origin = str(origin).strip().upper()
    dest_filter = (
        str(destination).strip().upper()
        if destination and str(destination).strip().upper() != "ALL"
        else None
    )

    flights = []
    for leg in network:
        if not leg_operates_today(get_leg_days(leg)):
            continue
        leg_orig = str(leg["Origin"]).strip().upper()
        leg_dest = str(leg["Destination"]).strip().upper()
        if leg_orig != origin:
            continue
        if dest_filter and leg_dest != dest_filter:
            continue
        flights.append(leg)

    return flights


def quote_single_leg(
    leg: dict, passengers: int = 1, search_nonce: int | None = None
) -> dict:
    """Prices a single nonstop flight using realistic cabin loads,
    random $10 BIRD-10 base-fare drops, and 2026 taxes/fees.
    """
    orig = str(leg["Origin"]).strip().upper()
    dest = str(leg["Destination"]).strip().upper()
    flt_num = parse_flight_int(leg.get("Flight", 100))

    fleet_info = get_flight_capacity_and_pax(leg)
    aircraft = fleet_info["aircraft_code"]
    session_booked = st.session_state.booked_seats.get(flt_num, 0)
    seats_remaining = (
        fleet_info["capacity"] - fleet_info["pax_count"] - session_booked
    )

    if seats_remaining < passengers:
        return {"sold_out": True}

    q = quote_flight(
        orig,
        dest,
        aircraft=aircraft,
        seats_sold=fleet_info["pax_count"],
        include_tsa=is_us_airport(orig),
        flight_num=flt_num,
        search_nonce=search_nonce,
        session_booked=session_booked,
    )
    if q.get("sold_out"):
        return {"sold_out": True}

    q["flight"] = leg.get("Flight", flt_num)
    q["flight_int"] = flt_num
    q["passengers"] = passengers
    q["group_base"] = round(q["base_fare"] * passengers, 2)
    q["group_carrier_fees"] = round(q["carrier_fee"] * passengers, 2)
    q["group_taxes"] = round(q["taxes_total"] * passengers, 2)
    q["group_all_in"] = round(q["all_in_total"] * passengers, 2)
    q["has_bird10"] = q["bucket"] == "BIRD-10"
    q["fleet_info"] = fleet_info
    q["live_pax"] = fleet_info["pax_count"] + session_booked
    q["live_load_factor"] = round(
        (q["live_pax"] / fleet_info["capacity"]) * 100, 1
    )
    return q

# ==========================================
# 3. FLEET, CAPACITY & ULCC DEMAND ENGINE
# ==========================================

HUBS = {"KRIC", "KSFB", "KSWF", "KBGR", "TJBQ"}
INTL_AIRPORTS = {"TJBQ", "TIST", "TISX"}

FLEET_SPECS = {
    "A319": {
        "name": "Airbus A319",
        "capacity": 150,
        "registrations": ["N800SB", "N801SB", "N802SB", "N803SB"],
    },
    "A320": {
        "name": "Airbus A320",
        "capacity": 180,
        "registrations": ["N804SB", "N805SB", "N806SB", "N807SB"],
    },
    "A321": {
        "name": "Airbus A321",
        "capacity": 220,
        "registrations": ["N808SB", "N809SB", "N810SB", "N811SB"],
    },
}


def get_flight_capacity_and_pax(leg, last_state=None):
    """Assigns aircraft model, tail registration, and realistic passenger load
    factor considering ULCC network dynamics: day of week, seasonal calendar,
    route type, and directional leisure asymmetry ("empty leg" effect).
    """
    flight_num = leg["Flight"]
    orig = str(leg["Origin"]).strip().upper()
    dest = str(leg["Destination"]).strip().upper()

    c1 = get_coords(orig)
    c2 = get_coords(dest)
    distance = haversine_miles(c1, c2) if (c1 and c2) else 600

    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    seed_value = f"{flight_num}-{today_str}"
    rng = random.Random(seed_value)

    # Route Classification Checks
    is_hub_to_hub = (orig in HUBS) and (dest in HUBS)
    touches_hub = (orig in HUBS) or (dest in HUBS)
    is_near_intl = (
        (orig in INTL_AIRPORTS)
        or (dest in INTL_AIRPORTS)
        or (not is_us_airport(orig))
        or (not is_us_airport(dest))
    )
    is_long_haul_intl = (
        orig.startswith(("L", "E", "F", "S", "R"))
        or dest.startswith(("L", "E", "F", "S", "R"))
        or orig == "BIKF"
        or dest == "BIKF"
    )

    # ---------------------------------------------------------
    # 1. AIRCRAFT TYPE SELECTION
    # ---------------------------------------------------------
    if is_long_haul_intl or distance >= 2000 or is_hub_to_hub:
        ac_type = "A321"
    elif is_near_intl:
        ac_type = (
            rng.choice(["A320", "A321"])
            if distance >= 1000
            else rng.choice(["A319", "A320"])
        )
    elif touches_hub:
        ac_type = (
            rng.choice(["A320", "A320", "A319"])
            if distance >= 700
            else rng.choice(["A319", "A319", "A320"])
        )
    else:
        ac_type = (
            rng.choice(["A319", "A319", "A320"])
            if distance < 450
            else rng.choice(["A320", "A319"])
        )

    spec = FLEET_SPECS[ac_type]

    # Re-use tail registration for consecutive same-type legs
    if (
        last_state is not None
        and last_state.get("type") == ac_type
        and last_state.get("tail")
    ):
        tail_number = last_state["tail"]
    else:
        tail_number = rng.choice(spec["registrations"])

    if last_state is not None:
        last_state["type"] = ac_type
        last_state["tail"] = tail_number

    # ---------------------------------------------------------
    # 2. REALISTIC ULCC DEMAND ENGINE
    # ---------------------------------------------------------
    dow = now.weekday()
    dow_multipliers = {
        0: 0.92,  # Monday (Business / Return leisure)
        1: 0.72,  # Tuesday (Heavy ULCC mid-week lull)
        2: 0.74,  # Wednesday (Mid-week lull)
        3: 0.91,  # Thursday (Early weekend departures)
        4: 1.02,  # Friday (Peak weekend outbound)
        5: 0.82,  # Saturday (Moderate)
        6: 1.05,  # Sunday (Peak weekend return)
    }
    dow_factor = dow_multipliers[dow]

    month, day = now.month, now.day
    is_thanksgiving = month == 11 and day >= 18
    is_holiday_season = (month == 12 and day >= 14) or (month == 1 and day <= 6)
    is_summer_peak = (month == 6 and day >= 15) or month in [7, 8]
    is_spring_break = (month == 3 and day >= 10) or (month == 4 and day <= 20)
    is_winter_lull = (month == 1 and day > 6) or month == 2
    is_fall_lull = month == 9 or (month == 10 and day <= 24)

    if is_holiday_season or is_thanksgiving:
        season_factor = 1.18
    elif is_summer_peak:
        season_factor = 1.10
    elif is_spring_break:
        season_factor = 1.05
    elif is_winter_lull or is_fall_lull:
        season_factor = 0.80
    else:
        season_factor = 0.95

    if is_long_haul_intl or is_hub_to_hub:
        route_factor = 1.06
    elif touches_hub:
        route_factor = 0.97
    else:
        route_factor = 0.84

    SUN_DESTINATIONS = {
        "KSFB", "TJBQ", "TIST", "TISX", "KMYR", "KEYW", "KPBI", "KRSW",
        "MMUN", "MMCZ", "MMSD", "MMPR", "MYNN", "MDPC", "MKJS", "TNCA",
    }
    is_heading_to_sun = dest in SUN_DESTINATIONS
    is_heading_from_sun = orig in SUN_DESTINATIONS

    directional_factor = 1.00
    if is_heading_to_sun:
        if dow in [3, 4]:
            directional_factor = 1.12
        elif dow in [0, 6]:
            directional_factor = 0.82
    elif is_heading_from_sun:
        if dow in [0, 6]:
            directional_factor = 1.12
        elif dow in [3, 4]:
            directional_factor = 0.82

    # ---------------------------------------------------------
    # 3. FINAL LOAD FACTOR CALCULATION
    # ---------------------------------------------------------
    baseline_load = 0.84
    target_lf = (
        baseline_load
        * dow_factor
        * season_factor
        * route_factor
        * directional_factor
    )

    variance = rng.uniform(-0.04, 0.04)
    final_load_factor = max(0.48, min(0.99, target_lf + variance))

    capacity = spec["capacity"]
    pax_count = int(capacity * final_load_factor)

    return {
        "aircraft_code": ac_type,
        "aircraft_name": spec["name"],
        "tail_number": tail_number,
        "capacity": capacity,
        "pax_count": pax_count,
        "load_factor": round((pax_count / capacity) * 100, 1),
    }

    # ---------------------------------------------------------
    # 1. AIRCRAFT TYPE SELECTION
    # ---------------------------------------------------------
    if is_long_haul_intl or distance >= 2000 or is_hub_to_hub:
        ac_type = "A321"
    elif is_near_intl:
        ac_type = (
            rng.choice(["A320", "A321"])
            if distance >= 1000
            else rng.choice(["A319", "A320"])
        )
    elif touches_hub:
        ac_type = (
            rng.choice(["A320", "A320", "A319"])
            if distance >= 700
            else rng.choice(["A319", "A319", "A320"])
        )
    else:
        ac_type = (
            rng.choice(["A319", "A319", "A320"])
            if distance < 450
            else rng.choice(["A320", "A319"])
        )

    spec = FLEET_SPECS[ac_type]

    # Re-use tail registration for consecutive same-type legs
    if (
        last_state is not None
        and last_state.get("type") == ac_type
        and last_state.get("tail")
    ):
        tail_number = last_state["tail"]
    else:
        tail_number = rng.choice(spec["registrations"])

    if last_state is not None:
        last_state["type"] = ac_type
        last_state["tail"] = tail_number

    # ---------------------------------------------------------
    # 2. REALISTIC ULCC DEMAND ENGINE
    # ---------------------------------------------------------
    dow = now.weekday()
    dow_multipliers = {
        0: 0.92,  # Monday (Business / Return leisure)
        1: 0.72,  # Tuesday (Heavy ULCC mid-week lull)
        2: 0.74,  # Wednesday (Mid-week lull)
        3: 0.91,  # Thursday (Early weekend departures)
        4: 1.02,  # Friday (Peak weekend outbound)
        5: 0.82,  # Saturday (Moderate)
        6: 1.05,  # Sunday (Peak weekend return)
    }
    dow_factor = dow_multipliers[dow]

    month, day = now.month, now.day
    is_thanksgiving = month == 11 and day >= 18
    is_holiday_season = (month == 12 and day >= 14) or (month == 1 and day <= 6)
    is_summer_peak = (month == 6 and day >= 15) or month in [7, 8]
    is_spring_break = (month == 3 and day >= 10) or (month == 4 and day <= 20)
    is_winter_lull = (month == 1 and day > 6) or month == 2
    is_fall_lull = month == 9 or (month == 10 and day <= 24)

    if is_holiday_season or is_thanksgiving:
        season_factor = 1.18
    elif is_summer_peak:
        season_factor = 1.10
    elif is_spring_break:
        season_factor = 1.05
    elif is_winter_lull or is_fall_lull:
        season_factor = 0.80
    else:
        season_factor = 0.95

    if is_long_haul_intl or is_hub_to_hub:
        route_factor = 1.06
    elif touches_hub:
        route_factor = 0.97
    else:
        route_factor = 0.84

    SUN_DESTINATIONS = {
        "KSFB", "TJBQ", "TIST", "TISX", "KMYR", "KEYW", "KPBI", "KRSW",
        "MMUN", "MMCZ", "MMSD", "MMPR", "MYNN", "MDPC", "MKJS", "TNCA",
    }
    is_heading_to_sun = dest in SUN_DESTINATIONS
    is_heading_from_sun = orig in SUN_DESTINATIONS

    directional_factor = 1.00
    if is_heading_to_sun:
        if dow in [3, 4]:
            directional_factor = 1.12
        elif dow in [0, 6]:
            directional_factor = 0.82
    elif is_heading_from_sun:
        if dow in [0, 6]:
            directional_factor = 1.12
        elif dow in [3, 4]:
            directional_factor = 0.82

    # ---------------------------------------------------------
    # 3. FINAL LOAD FACTOR & ADVANCE BOOKING CURVE
    # ---------------------------------------------------------
    baseline_load = 0.84
    target_lf = (
        baseline_load
        * dow_factor
        * season_factor
        * route_factor
        * directional_factor
    )

    variance = rng.uniform(-0.04, 0.04)
    final_load_factor = max(0.48, min(0.99, target_lf + variance))

    capacity = spec["capacity"]
    pax_count = int(capacity * final_load_factor)
    seats_sold_now = simulate_booking_curve(
        flight_num, capacity, pax_count, days_out=days_out
    )

    return {
        "aircraft_code": ac_type,
        "aircraft_name": spec["name"],
        "tail_number": tail_number,
        "capacity": capacity,
        "pax_count": pax_count,
        "seats_sold_now": seats_sold_now,
        "load_factor": round((pax_count / capacity) * 100, 1),
    }

# ==========================================
# 4. APP UI
# ==========================================

network = get_full_network()
all_airports = sorted(list(set([f["Origin"] for f in network])))
airport_names_map = globals().get("AIRPORT_NAMES", {})

st.subheader("🔍 Search Any Route on Network Map")

col1, col2, col3, col4 = st.columns([1, 1.3, 1, 1])

# 1. Origin Dropdown
with col1:
    orig_select = st.selectbox(
        "Origin Airport",
        options=all_airports,
        index=all_airports.index("KRIC") if "KRIC" in all_airports else 0,
        key="orig_select_val",
        format_func=lambda code: f"{code} - {airport_names_map.get(code, code)}",
    )

# 2. Calculate Active Destinations for Today from selected Origin
valid_destinations = get_reachable_destinations(
    network, orig_select, max_connections=6
)

if (
    "dest_select_val" not in st.session_state
    or st.session_state["dest_select_val"] not in valid_destinations
):
    st.session_state["dest_select_val"] = (
        valid_destinations[0] if valid_destinations else None
    )


# 3. Safe Callback for Random Selection
def set_random_destination():
    current_dest = st.session_state.get("dest_select_val", None)
    available = [a for a in valid_destinations if a != current_dest]
    if available:
        st.session_state["dest_select_val"] = random.SystemRandom().choice(
            available
        )


# 4. Destination Dropdown + Random Button
with col2:
    st.markdown(
        "<label style='font-size: 14px; font-weight: 500;'>Destination Airport</label>",
        unsafe_allow_html=True,
    )
    d_col1, d_col2 = st.columns([2.2, 1])

    with d_col1:
        if valid_destinations:
            dest_select = st.selectbox(
                "Destination Airport",
                options=valid_destinations,
                key="dest_select_val",
                label_visibility="collapsed",
                format_func=lambda code: f"{code} - {airport_names_map.get(code, code)}",
            )
        else:
            st.warning("No flights operate today from this airport.")
            dest_select = None

    with d_col2:
        st.button(
            "🎲 Random",
            on_click=set_random_destination,
            disabled=len(valid_destinations) <= 1,
            help="Pick a random destination operating today",
        )

# 5. Connections Allowed Dropdown
with col3:
    conn_str = st.selectbox(
        "Connections Allowed",
        options=[
            "Nonstop",
            "1 Connection",
            "2 Connections",
            "3 Connections",
            "4 Connections",
            "5 Connections",
            "6 Connections",
        ],
        index=2,
    )

# 6. Max Options Dropdown
with col4:
    max_display_count = st.selectbox(
        "Max Options to Show",
        options=[15, 25, 35, 50, 75],
        index=4,
    )

# 7. Passenger & Sort Controls (No advance-booking selector — $10 fares drop randomly!)
b_col1, b_col2 = st.columns([1, 2])
with b_col1:
    pax_count_input = st.number_input(
        "Passengers", min_value=1, max_value=9, value=1, step=1
    )

with b_col2:
    sort_mode = st.selectbox(
        "Sort Results By",
        options=[
            "Lowest All-In Fare",
            "Best Route Score",
            "Fewest Connections",
        ],
        index=0,
    )

conn_map = {
    "Nonstop": 0,
    "1 Connection": 1,
    "2 Connections": 2,
    "3 Connections": 3,
    "4 Connections": 4,
    "5 Connections": 5,
    "6 Connections": 6,
}
exact_conn = conn_map[conn_str]

# Search Action Button
if st.button("Search Route Options", type="primary"):
    if not dest_select:
        st.warning(
            "No valid destination selected or no operating flights today."
        )
    elif orig_select == dest_select:
        st.warning("Please choose two different airports.")
    else:
        routes_found = find_routes(
            network,
            orig_select,
            dest_select,
            exact_connections=exact_conn,
            max_display=max_display_count,
        )
        st.session_state["search_results"] = routes_found
        st.session_state["search_orig"] = orig_select
        st.session_state["search_dest"] = dest_select
        st.session_state["search_conn_str"] = conn_str
        # Fresh random roll for $10 BIRD-10 base fares on every new search
        st.session_state["search_nonce"] = random.SystemRandom().randint(
            1, 10_000_000
        )

# ==========================================
# 5. SEARCH RESULTS & FARE CALCULATOR
# ==========================================

if "search_results" in st.session_state:
    results = st.session_state["search_results"]
    orig = st.session_state["search_orig"]
    dest = st.session_state["search_dest"]
    selected_conn_str = st.session_state.get("search_conn_str", conn_str)
    search_nonce = st.session_state.get("search_nonce", 1)

    st.markdown("---")
    st.markdown(
        f"### Possible Routes for **{orig} ➔ {dest}** ({len(results)} option(s) found)"
    )

    if not results:
        st.info(
            f"No routes found connecting {orig} to {dest} with **{selected_conn_str}**."
        )
    else:
        quoted_options = []
        for path in results:
            q = quote_route_path(
                path,
                passengers=int(pax_count_input),
                search_nonce=search_nonce,
            )
            if not q.get("sold_out"):
                quoted_options.append((path, q))

        if sort_mode == "Lowest All-In Fare":
            quoted_options.sort(key=lambda item: item[1]["per_pax_all_in"])
        elif sort_mode == "Fewest Connections":
            quoted_options.sort(
                key=lambda item: (len(item[0]) - 1, item[1]["per_pax_all_in"])
            )

        if not quoted_options:
            st.warning(
                "All matching flights are currently sold out for the selected passenger count."
            )
        else:
            itinerary_labels = []
            for i, (path, q) in enumerate(quoted_options):
                stops = len(path) - 1
                stop_str = "Nonstop" if stops == 0 else f"{stops} Stop(s)"
                leg_chain = " ➔ ".join(
                    [f"{leg['Origin']}" for leg in path]
                    + [path[-1]["Destination"]]
                )
                if q["has_bird10"] and all(
                    l["bucket"] == "BIRD-10" for l in q["legs"]
                ):
                    tag = f"🐦 $10 BIRD-10 ({q['min_bird10_seats']} left)"
                elif q["has_bird10"]:
                    tag = f"🐦 Mixed $10 / {q['legs'][-1]['bucket']}"
                else:
                    tag = q["legs"][0]["bucket"]

                itinerary_labels.append(
                    f"Option {i+1} [{stop_str}] — ${q['per_pax_all_in']:.2f}/pax [{tag}]: {leg_chain}"
                )

            selected_option_idx = st.radio(
                "Select an option to view leg details, customize add-ons, and issue boarding pass:",
                range(len(itinerary_labels)),
                format_func=lambda x: itinerary_labels[x],
            )

            selected_path, selected_quote = quoted_options[selected_option_idx]

            badge_cls = (
                "fare-bird10"
                if selected_quote["has_bird10"]
                else "fare-standard"
            )
            scarcity_html = (
                f"<span class='scarcity-pill'>🎉 Lucky Drop! {selected_quote['min_bird10_seats']} seat(s) available at the $10 base fare!</span>"
                if selected_quote["has_bird10"]
                else "<span style='font-size:12px; color:#555;'>Standard market pricing based on route distance &amp; cabin demand</span>"
            )

            st.markdown(
                f"""
                <div class="info-card">
                    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
                        <div>
                            <span class="fare-badge {badge_cls}">{selected_quote['legs'][0]['bucket']}</span>
                            <span style="margin-left:8px; font-weight:700; font-size:16px;">
                                Base Fare: ${selected_quote['per_pax_base']:.2f} + Carrier Fee: ${selected_quote['per_pax_carrier_fees']:.2f} + Taxes/Fees: ${selected_quote['per_pax_taxes']:.2f}
                            </span>
                            <div style="margin-top:4px;">{scarcity_html}</div>
                        </div>
                        <div style="text-align:right;">
                            <div style="font-size:11px; color:#777; text-transform:uppercase; font-weight:700;">All-In Airfare ({pax_count_input} Pax)</div>
                            <div style="font-size:24px; font-weight:900; color:#F28425;">${selected_quote['group_all_in']:.2f}</div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                f"#### 📋 Leg Breakdown for Option {selected_option_idx + 1}"
            )
            last_state = {}
            for idx, (leg, lq) in enumerate(
                zip(selected_path, selected_quote["legs"]), 1
            ):
                flight_info = get_flight_capacity_and_pax(
                    leg, last_state=last_state
                )
                f_id = parse_flight_int(leg["Flight"])
                live_pax = min(
                    flight_info["capacity"],
                    flight_info["pax_count"]
                    + st.session_state.booked_seats.get(f_id, 0),
                )
                live_lf = round((live_pax / flight_info["capacity"]) * 100, 1)

                st.write(
                    f"**Leg {idx}:** Flight **SX #{leg['Flight']}** | `{leg['Origin']}` ➔ `{leg['Destination']}` ({lq['distance_nm']} nm) | "
                    f"Days: *{leg['Days']}* | "
                    f"✈️ **{flight_info['aircraft_name']}** (`{flight_info['tail_number']}`) | "
                    f"👥 **Load:** {live_pax}/{flight_info['capacity']} ({live_lf}%) | "
                    f"🎟️ **{lq['bucket']}**: `${lq['base_fare']:.2f}` base + `${lq['carrier_fee']:.2f}` fee + `${lq['taxes_total']:.2f}` tax = **`${lq['all_in_total']:.2f}`**"
                )

            with st.expander("🧾 View Itemized 2026 Government Taxes & Airport Fees"):
                for idx, lq in enumerate(selected_quote["legs"], 1):
                    st.markdown(
                        f"**Leg {idx} ({lq['route']} — Flight SX #{lq['flight']})**"
                    )
                    for fee_name, fee_val in lq["tax_breakdown"].items():
                        st.write(f"- {fee_name}: **${fee_val:.2f}**")

            # Optional Skybus Unbundled Ancillaries (including SkyFly Wi-Fi)
            st.markdown("#### 🧳 Optional Skybus Add-Ons (Per Passenger)")
            addons = selected_quote["per_pax_addons"]
            a_col1, a_col2, a_col3, a_col4, a_col5 = st.columns(5)
            with a_col1:
                add_carryon = st.checkbox(
                    f"Carry-On Bag (+${addons['carry_on_bag']:.2f})",
                    value=True,
                    help="1 under-seat personal item is always $0.00",
                )
            with a_col2:
                checked_bag_qty = st.selectbox(
                    "Checked Bags (50 lb)",
                    options=[
                        ("0 Bags ($0.00)", 0, 0.0),
                        (
                            f"1 Bag (+${addons['checked_bag_1']:.2f})",
                            1,
                            addons["checked_bag_1"],
                        ),
                        (
                            f"2 Bags (+${addons['checked_bag_1'] + addons['checked_bag_2']:.2f})",
                            2,
                            addons["checked_bag_1"] + addons["checked_bag_2"],
                        ),
                    ],
                    index=1,
                    format_func=lambda x: x[0],
                )
            with a_col3:
                add_priority = st.checkbox(
                    f"Zone 1 Priority (+${addons['priority_boarding']:.2f})",
                    value=True,
                )
            with a_col4:
                add_seat = st.checkbox(
                    f"Seat Selection (+${addons['seat_selection']:.2f})",
                    value=True,
                )
            with a_col5:
                add_wifi = st.checkbox(
                    f"SkyFly Wi-Fi (+${addons['wifi']:.2f})",
                    value=True,
                    help="High-speed gate-to-gate in-flight streaming & messaging",
                )

            per_pax_addon_total = (
                (addons["carry_on_bag"] if add_carryon else 0.0)
                + checked_bag_qty[2]
                + (addons["priority_boarding"] if add_priority else 0.0)
                + (addons["seat_selection"] if add_seat else 0.0)
                + (addons["wifi"] if add_wifi else 0.0)
            )
            grand_checkout_total = round(
                selected_quote["group_all_in"]
                + (per_pax_addon_total * int(pax_count_input)),
                2,
            )

            c_col1, c_col2 = st.columns([2, 1])
            with c_col1:
                st.info(
                    f"**Checkout Grand Total ({pax_count_input} Passenger(s) + Selected Add-Ons):** **${grand_checkout_total:.2f}**"
                )
            with c_col2:
                if st.button(
                    "🎟️ Book This Itinerary (Update Seat Inventory)",
                    use_container_width=True,
                ):
                    for leg in selected_path:
                        f_id = parse_flight_int(leg["Flight"])
                        st.session_state.booked_seats[f_id] = (
                            st.session_state.booked_seats.get(f_id, 0)
                            + int(pax_count_input)
                        )
                    st.success(
                        f"Booked {pax_count_input} seat(s)! Cabin availability updated."
                    )
                    st.rerun()

            st.session_state["selected_itinerary"] = selected_path
            st.session_state["selected_quote"] = selected_quote
            st.session_state["selected_addons"] = {
                "carry_on": add_carryon,
                "checked_bags": checked_bag_qty[1],
                "priority": add_priority,
                "seat_selected": add_seat,
                "wifi": add_wifi,
                "grand_total": grand_checkout_total,
            }

# ==========================================
# 6. MOBILE BOARDING PASS
# ==========================================

if "selected_itinerary" in st.session_state:
    st.markdown("---")
    st.subheader("📲 Mobile Boarding Pass")

    path = st.session_state["selected_itinerary"]
    active_quote = st.session_state.get("selected_quote")
    active_addons = st.session_state.get(
        "selected_addons",
        {
            "carry_on": True,
            "checked_bags": 1,
            "priority": True,
            "seat_selected": True,
            "wifi": True,
            "grand_total": 26.15,
        },
    )

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
    assigned_seat = (
        get_random_seat(active_leg["Flight"])
        if active_addons["seat_selected"]
        else "OPEN"
    )
    assigned_gate = get_random_gate(active_leg["Flight"])
    today_date = datetime.now().strftime("%d %b %Y").upper()

    bp_last_state = {}
    path_flight_infos = [
        get_flight_capacity_and_pax(leg, last_state=bp_last_state)
        for leg in path
    ]
    flight_info = path_flight_infos[selected_leg_index]

    f_id = parse_flight_int(active_leg["Flight"])
    live_pax = min(
        flight_info["capacity"],
        flight_info["pax_count"]
        + st.session_state.booked_seats.get(f_id, 0),
    )
    live_lf = round((live_pax / flight_info["capacity"]) * 100, 1)

    leg_fare_bucket = (
        active_quote["legs"][selected_leg_index]["bucket"]
        if active_quote
        else "BIRD-10"
    )
    leg_all_in = (
        active_quote["legs"][selected_leg_index]["all_in_total"]
        if active_quote
        else 26.15
    )
    boarding_zone = "Zone 1" if active_addons["priority"] else "Zone 2"
    checked_str = (
        f"🧳 {active_addons['checked_bags']} Checked"
        if active_addons["checked_bags"] > 0
        else "🧳 0 Checked"
    )
    carryon_str = (
        "🎒 1 Carry-on" if active_addons["carry_on"] else "👜 Personal Only"
    )
    wifi_html = (
        '<div style="font-size: 11px; color: #F28425; font-weight: 700; margin-top: 2px;">📶 SkyFly Wi-Fi: Active</div>'
        if active_addons.get("wifi")
        else '<div style="font-size: 11px; color: #888; font-weight: 600; margin-top: 2px;">📶 SkyFly Wi-Fi: Not Added</div>'
    )

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
        border: 2px solid #F28425;
        border-radius: 14px;
        overflow: hidden;
        box-shadow: 0 6px 18px rgba(0,0,0,0.12);
    }}
    .bp-header {{
        background-color: #F28425;
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
                <span style="font-size: 10px; margin-left: 6px; background: rgba(255,255,255,0.25); padding: 3px 7px; border-radius: 10px;">{leg_fare_bucket}</span>
            </div>
            <div style="font-weight: bold; font-size: 14px;">SX #{active_leg['Flight']}</div>
        </div>
        <div class="bp-body">
            <!-- PASSENGER & WI-FI -->
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #eee; padding-bottom: 10px; margin-bottom: 10px;">
                <div>
                    <div class="bp-field">Passenger Name</div>
                    <div class="bp-value">John Bowman</div>
                    <div style="font-size: 11px; color: #F28425; font-weight: 700; margin-top: 3px;">👑 Rewards #: 6827165938</div>
                </div>
                <div style="text-align: right;">
                    <div class="bp-field">Leg Fare (All-In)</div>
                    <div class="bp-value" style="color: #F28425;">${leg_all_in:.2f}</div>
                    {wifi_html}
                </div>
            </div>
            
            <!-- ROUTE -->
            <div style="display: flex; justify-content: space-between; align-items: center; margin: 12px 0;">
                <div>
                    <div style="font-size: 30px; font-weight: 900; color: #111;">{active_leg['Origin']}</div>
                    <div class="bp-field">Departure</div>
                </div>
                <div style="font-size: 22px; color: #F28425;">✈️</div>
                <div style="text-align: right;">
                    <div style="font-size: 30px; font-weight: 900; color: #111;">{active_leg['Destination']}</div>
                    <div class="bp-field">Arrival</div>
                </div>
            </div>

            <!-- FLIGHT GRID -->
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
                    <div class="bp-value">{boarding_zone}</div>
                </div>
                <div>
                    <div class="bp-field">Seat</div>
                    <div class="bp-value" style="color: #F28425;">{assigned_seat}</div>
                </div>
            </div>

            <!-- BAGGAGE ALLOWANCE -->
            <div style="display: flex; justify-content: space-between; background: #F8F9FA; padding: 10px; border-radius: 8px; text-align: center; margin-top: 10px;">
                <div style="flex: 1;">
                    <div class="bp-field">Checked Bags</div>
                    <div class="bp-value" style="font-size: 13px;">{checked_str}</div>
                </div>
                <div style="border-left: 1px solid #ddd;"></div>
                <div style="flex: 1;">
                    <div class="bp-field">Carry-On</div>
                    <div class="bp-value" style="font-size: 13px;">{carryon_str}</div>
                </div>
            </div>

            <!-- AIRCRAFT & PASSENGER LOAD -->
            <div style="display: flex; justify-content: space-between; background: #F8F9FA; padding: 10px; border-radius: 8px; text-align: center; margin-top: 10px;">
                <div style="flex: 1;">
                    <div class="bp-field">Aircraft / Reg</div>
                    <div class="bp-value" style="font-size: 13px;">✈️ {flight_info['aircraft_name']} <span style="font-size: 11px; color: #F28425;">({flight_info['tail_number']})</span></div>
                </div>
                <div style="border-left: 1px solid #ddd;"></div>
                <div style="flex: 1;">
                    <div class="bp-field">Est. Flight Load</div>
                    <div class="bp-value" style="font-size: 13px;">👥 {live_pax} / {flight_info['capacity']} ({live_lf}%)</div>
                </div>
            </div>

            <!-- BARCODE -->
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

    st.components.v1.html(card_html, height=540)