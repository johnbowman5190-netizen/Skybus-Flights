import random
from datetime import datetime
from collections import deque, defaultdict
import math
import streamlit as st
import streamlit.components.v1 as components

# ==========================================
# 1. PAGE CONFIG & COLOR SETTINGS
# ==========================================
st.set_page_config(
    page_title="Skybus Route & Boarding System",
    page_icon="✈️",
    layout="wide"
)

# Custom accent color matching the logo (#F28425)
ACCENT_COLOR = "#F28425"

# Styling using your custom accent color
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
    # I. INTER-HUB DIRECT EXPRESS ROUTES (SX 100 - SX 208)
    # Full Mesh Network Across All 12 Hubs
    # ----------------------------------------------------
    (100, "PAFA", "KBLI", "Daily"),  # SX 100 / SX 101
    (102, "PAFA", "KIWA", "Daily"),  # SX 102 / SX 103
    (104, "PAFA", "KPVU", "Daily"),  # SX 104 / SX 105
    (106, "PAFA", "KBGR", "Daily"),  # SX 106 / SX 107
    (108, "KBLI", "KIWA", "Daily"),  # SX 108 / SX 109
    (110, "KBLI", "KPVU", "Daily"),  # SX 110 / SX 111
    (112, "KBLI", "KOMA", "Daily"),  # SX 112 / SX 113
    (114, "KBLI", "KMSY", "Daily"),  # SX 114 / SX 115
    (116, "KBLI", "KGRR", "Daily"),  # SX 116 / SX 117
    (118, "KBLI", "KSWF", "Daily"),  # SX 118 / SX 119
    (120, "KBLI", "KBGR", "Daily"),  # SX 120 / SX 121
    (122, "KBLI", "KRIC", "Daily"),  # SX 122 / SX 123
    (124, "KBLI", "KSFB", "Daily"),  # SX 124 / SX 125
    (126, "KIWA", "KPVU", "Daily"),  # SX 126 / SX 127
    (128, "KIWA", "KOMA", "Daily"),  # SX 128 / SX 129
    (130, "KIWA", "KMSY", "Daily"),  # SX 130 / SX 131
    (132, "KIWA", "KGRR", "Daily"),  # SX 132 / SX 133
    (134, "KIWA", "KSWF", "Daily"),  # SX 134 / SX 135
    (136, "KIWA", "KBGR", "Daily"),  # SX 136 / SX 137
    (138, "KIWA", "KRIC", "Daily"),  # SX 138 / SX 139
    (140, "KIWA", "KSFB", "Daily"),  # SX 140 / SX 141
    (142, "KPVU", "KOMA", "Daily"),  # SX 142 / SX 143
    (144, "KPVU", "KMSY", "Daily"),  # SX 144 / SX 145
    (146, "KPVU", "KGRR", "Daily"),  # SX 146 / SX 147
    (148, "KPVU", "KSWF", "Daily"),  # SX 148 / SX 149
    (150, "KPVU", "KBGR", "Daily"),  # SX 150 / SX 151
    (152, "KPVU", "KRIC", "Daily"),  # SX 152 / SX 153
    (154, "KPVU", "KSFB", "Daily"),  # SX 154 / SX 155
    (156, "KOMA", "KMSY", "Daily"),  # SX 156 / SX 157
    (158, "KOMA", "KGRR", "Daily"),  # SX 158 / SX 159
    (160, "KOMA", "KSWF", "Daily"),  # SX 160 / SX 161
    (162, "KOMA", "KBGR", "Daily"),  # SX 162 / SX 163
    (164, "KOMA", "KRIC", "Daily"),  # SX 164 / SX 165
    (166, "KOMA", "KSFB", "Daily"),  # SX 166 / SX 167
    (168, "KMSY", "KGRR", "Daily"),  # SX 168 / SX 169
    (170, "KMSY", "KSWF", "Daily"),  # SX 170 / SX 171
    (172, "KMSY", "KBGR", "Daily"),  # SX 172 / SX 173
    (174, "KMSY", "KRIC", "Daily"),  # SX 174 / SX 175
    (176, "KMSY", "KSFB", "Daily"),  # SX 176 / SX 177
    (178, "KMSY", "TJBQ", "Daily"),  # SX 178 / SX 179
    (180, "KGRR", "KSWF", "Daily"),  # SX 180 / SX 181
    (182, "KGRR", "KBGR", "Daily"),  # SX 182 / SX 183
    (184, "KGRR", "KRIC", "Daily"),  # SX 184 / SX 185
    (186, "KGRR", "KSFB", "Daily"),  # SX 186 / SX 187
    (188, "KGRR", "TJBQ", "Daily"),  # SX 188 / SX 189
    (190, "KSWF", "KBGR", "Daily"),  # SX 190 / SX 191
    (192, "KSWF", "KRIC", "Daily"),  # SX 192 / SX 193
    (194, "KSWF", "KSFB", "Daily"),  # SX 194 / SX 195
    (196, "KSWF", "TJBQ", "Daily"),  # SX 196 / SX 197
    (198, "KBGR", "KRIC", "Daily"),  # SX 198 / SX 199
    (200, "KBGR", "KSFB", "Daily"),  # SX 200 / SX 201
    (202, "KBGR", "TJBQ", "Daily"),  # SX 202 / SX 203
    (204, "KRIC", "KSFB", "Daily"),  # SX 204 / SX 205
    (206, "KRIC", "TJBQ", "Daily"),  # SX 206 / SX 207
    (208, "KSFB", "TJBQ", "Daily"),  # SX 208 / SX 209
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
    (2834, "KGRR", "SPIM", "Wed, Sat"),  # Lima, Peru
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

    # ----------------------------------------------------
    # KRIC International Spokes (Richmond, VA Hub)
    # ----------------------------------------------------
    (3830, "KRIC", "EGCC", "Mon, Wed, Fri"),  # Manchester, UK
    (3832, "KRIC", "LOWW", "Tue, Thu, Sat"),  # Vienna, Austria
    (3834, "KRIC", "EKCH", "Mon, Wed, Fri"),  # Copenhagen, Denmark
    (3836, "KRIC", "SEQM", "Thu, Sun"),  # Quito, Ecuador
    (3838, "KRIC", "SAEZ", "Wed, Sat"),  # Buenos Aires, Argentina

    # ----------------------------------------------------
    # KPVU International Spokes (Provo, UT Hub)
    # ----------------------------------------------------
    (3850, "KPVU", "CYYC", "Mon, Wed, Fri, Sun"),  # Calgary, AB, Canada
    (3852, "KPVU", "CYEG", "Tue, Thu, Sat"),  # Edmonton, AB, Canada
    (3854, "KPVU", "CYZF", "Thu, Sun"),  # Yellowknife, NT, Canada
    
    # ----------------------------------------------------
    # TJBQ Caribbean Regional Spokes (1500 Block - Caribbean Hub)
    # ----------------------------------------------------
    (1500, "TJBQ", "TJPS", "Tue, Thu, Sat"),  # Ponce, PR
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
    "KEKO": "Elko, NV",
    "KEUG": "Eugene, OR",
    "KFAT": "Fresno, CA",
    "KFLG": "Flagstaff, AZ",
    "KGEG": "Spokane, WA",
    "KGJT": "Grand Junction, CO",
    "KGPI": "Kalispell, MT",
    "KGTF": "Great Falls, MT",
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
    "KMWH": "Moses Lake, WA",
    "KOGD": "Ogden, UT",
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
    "KSGU": "St. George, UT",
    "KSLE": "Salem, OR",
    "KSMF": "Sacramento, CA",
    "KSUN": "Sun Valley, ID",
    "KTWF": "Twin Falls, ID",
    "KVEL": "Vernal, UT",
    "KYKM": "Yakima, WA",

    # Southwest & South Central
    "KABI": "Abilene, TX",
    "KABQ": "Albuquerque, NM",
    "KACT": "Waco, TX",
    "KAMA": "Amarillo, TX",
    "KBPT": "Beaumont / Port Arthur, TX",
    "KCRP": "Corpus Christi, TX",
    "KELP": "El Paso, TX",
    "KHRL": "Harlingen, TX",
    "KLAW": "Lawton, OK",
    "KLBB": "Lubbock, TX",
    "KLRD": "Laredo, TX",
    "KMAF": "Midland / Odessa, TX",
    "KMFE": "McAllen, TX",
    "KOKC": "Oklahoma City, OK",
    "KROW": "Roswell, NM",
    "KSAF": "Santa Fe, NM",
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
    "KGRI": "Grand Island, NE",
    "KICT": "Wichita, KS",
    "KINL": "International Falls, MN",
    "KJEF": "Jefferson City, MO",
    "KJMS": "Jamestown, ND",
    "KLNK": "Lincoln, NE",
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
    "KISQ": "Sault Ste. Marie, MI",
    "KJVY": "Jeffersonville, IN",
    "KLAN": "Lansing, MI",
    "KLSE": "La Crosse, WI",
    "KMBS": "Saginaw, MI",
    "KMKE": "Milwaukee, WI",
    "KMQT": "Marquette, MI",
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

AIRPORT_COORDS = {
    # --------------------------------------------------------------------------
    # HUB AIRPORTS
    # --------------------------------------------------------------------------
    "PAFA": (64.8151, -147.8564),  # Fairbanks International, AK
    "KPVU": (40.2192, -111.7233),  # Provo Municipal, UT
    "KIWA": (33.3078, -111.6550),  # Phoenix-Mesa Gateway, AZ
    "KBLI": (48.7927, -122.5375),  # Bellingham International, WA
    "KMSY": (29.9934, -90.2580),   # Louis Armstrong New Orleans Intl, LA
    "KOMA": (41.3025, -95.8942),   # Eppley Airfield (Omaha), NE
    "KGRR": (42.8808, -85.5228),   # Gerald R. Ford Intl (Grand Rapids), MI
    "TJBQ": (18.4949, -67.1294),   # Rafael Hernández Intl (Aguadilla), PR
    "KSWF": (41.5041, -74.1048),   # New York Stewart Intl, NY
    "KBGR": (44.8074, -68.8281),   # Bangor International, ME
    "KRIC": (37.5052, -77.3197),   # Richmond International, VA
    "KSFB": (28.7776, -81.2375),   # Orlando Sanford Intl, FL


    # --------------------------------------------------------------------------
    # ALASKA SPOKES
    # --------------------------------------------------------------------------
    "PAJN": (58.3594, -134.5762),  # Juneau International, AK
    "PAKT": (55.3556, -131.7137),  # Ketchikan International, AK
    "PABR": (71.2854, -156.7660),  # Utqiaġvik (Barrow), AK
    "PAOT": (66.8847, -162.5986),  # Ralph Wien Memorial (Kotzebue), AK
    "PASC": (70.1947, -148.4652),  # Deadhorse / Prudhoe Bay, AK
    "PADQ": (57.7499, -152.4939),  # Kodiak Airport, AK
    "PAOM": (64.5122, -165.4453),  # Nome Airport, AK
    "PAPG": (56.8017, -132.9453),  # Petersburg James A. Johnson, AK
    "PASI": (57.0471, -135.3616),  # Sitka Rocky Gutierrez, AK
    "PAYA": (59.5033, -139.6602),  # Yakutat Airport, AK
    "PAVD": (61.1339, -146.2483),  # Valdez Airport, AK
    "PAEN": (60.5731, -151.2450),  # Kenai Municipal, AK
    "PAKW": (56.4843, -132.3698),  # Wrangell Airport, AK
    "PAHO": (59.6456, -151.4766),  # Homer Airport, AK
    "PADL": (59.0454, -158.5033),  # Dillingham Airport, AK
    "PAKN": (58.6768, -156.6492),  # King Salmon Airport, AK
    "PAGS": (58.4244, -135.7075),  # Gustavus Airport, AK

    # --------------------------------------------------------------------------
    # HAWAII SPOKES
    # --------------------------------------------------------------------------
    "PHNL": (21.3187, -157.9224),  # Daniel K. Inouye Intl (Honolulu), HI
    "PHOG": (20.8986, -156.4305),  # Kahului Airport (Maui), HI
    "PHKO": (19.7388, -155.9874),  # Ellison Onizuka Kona Intl, HI
    "PHLI": (21.9760, -159.3390),  # Lihue Airport (Kauai), HI

    # --------------------------------------------------------------------------
    # INTERMOUNTAIN & PACIFIC NORTHWEST SPOKES
    # --------------------------------------------------------------------------
    "KALW": (46.0944, -118.2881),  # Walla Walla Regional Airport, WA
    "KBOI": (43.5644, -116.2228),  # Boise Airport, ID
    "KBZN": (45.7775, -111.1531),  # Bozeman Yellowstone International Airport, MT
    "KCDC": (37.7010, -113.0988),  # Cedar City Regional Airport, UT
    "KCLM": (48.1202, -123.4997),  # William R. Fairchild (Port Angeles), WA
    "KCNY": (38.7550, -109.7548),  # Canyonlands Regional Airport (Moab), UT
    "KCPR": (42.9080, -106.4644),  # Casper/Natrona County Intl, WY
    "KEAT": (47.3999, -120.2068),  # Pangborn Memorial Airport (Wenatchee), WA
    "KEUG": (44.1233, -123.2186),  # Eugene Airport, OR
    "KGEG": (47.6199, -117.5338),  # Spokane International Airport, WA
    "KGJT": (39.1224, -108.5267),  # Grand Junction Regional, CO
    "KGTF": (47.4820, -111.3707),  # Great Falls International Airport, MT
    "KHLN": (46.6068, -111.9827),  # Helena Regional Airport, MT
    "KIDA": (43.5146, -112.0702),  # Idaho Falls Regional Airport, ID
    "KJAC": (43.6073, -110.7377),  # Jackson Hole Airport, WY
    "KLWS": (46.3745, -117.0154),  # Lewiston-Nez Perce County Airport, ID
    "KMFR": (42.3742, -122.8735),  # Rogue Valley International-Medford Airport, OR
    "KMSO": (46.9163, -114.0906),  # Missoula Montana Airport, MT
    "KOTH": (43.4171, -124.2460),  # Southwest Oregon Regional (North Bend), OR
    "KPIH": (42.9113, -112.5959),  # Pocatello Regional, ID
    "KPSC": (46.2647, -119.1190),  # Tri-Cities Airport (Pasco), WA
    "KRDM": (44.2541, -121.1500),  # Roberts Field (Redmond), OR
    "KRNO": (39.4991, -119.7681),  # Reno/Tahoe International Airport, NV
    "KSGU": (37.0364, -113.5103),  # St. George Regional Airport, UT
    "KTWF": (42.4818, -114.4877),  # Magic Valley Regional Airport (Twin Falls), ID
    "KVEL": (40.4409, -109.5099),  # Vernal Regional Airport, UT
    "KYKM": (46.5682, -120.5440),  # Yakima Air Terminal, WA

    # --------------------------------------------------------------------------
    # SOUTHWEST SPOKES
    # --------------------------------------------------------------------------
    "KABQ": (35.0402, -106.6091),  # Albuquerque International Sunport, NM
    "KACV": (40.9781, -124.1086),  # California Redwood Coast-Humboldt County Airport, CA
    "KBFL": (35.4336, -119.0567),  # Meadows Field Airport (Bakersfield), CA
    "KDRO": (37.1515, -107.7538),  # Durango-La Plata County Airport, CO
    "KDVT": (33.6883, -112.0825),  # Phoenix Deer Valley Airport, AZ
    "KEKO": (40.8249, -115.7917),  # Elko Regional, NV
    "KELP": (31.8066, -106.3778),  # El Paso International, TX
    "KFAT": (36.7762, -119.7181),  # Fresno Yosemite International Airport, CA
    "KFLG": (35.1384, -111.6712),  # Flagstaff Pulliam Airport, AZ
    "KSEZ": (34.8486, -111.7886),  # Sedona Airport, AZ
    "KIFP": (35.1561, -114.5595),  # Laughlin/Bullhead International Airport, AZ
    "KMAF": (31.9425, -102.2019),  # Midland International, TX
    "KMRY": (36.5870, -121.8430),  # Monterey Regional Airport, CA
    "KPRC": (34.6545, -112.4196),  # Prescott Regional Airport, AZ
    "KPSP": (33.8297, -116.5067),  # Palm Springs International Airport, CA
    "KRDD": (40.5090, -122.2934),  # Redding Regional Airport, CA
    "KROW": (33.3015, -104.5306),  # Roswell Air Center, NM
    "KSBA": (34.4262, -119.8403),  # Santa Barbara Municipal Airport, CA
    "KSBD": (34.0953, -117.2349),  # San Bernardino International Airport, CA
    "KSBP": (35.2371, -120.6424),  # San Luis Obispo County Regional, CA
    "KSMF": (38.6954, -121.5908),  # Sacramento International Airport, CA
    "KTUS": (32.1161, -110.9410),  # Tucson International, AZ

    # --------------------------------------------------------------------------
    # GULF COAST & MIDWEST SPOKES
    # --------------------------------------------------------------------------
    "KABI": (32.4163, -99.6804),   # Abilene, TX
    "KACT": (31.6113, -97.2293),   # Waco, TX
    "KAEX": (31.3274, -92.5498),   # Alexandria International, LA
    "KALO": (42.5571, -92.4003),   # Waterloo Regional, IA
    "KAMA": (35.2194, -101.7059),  # Amarillo, TX
    "KATW": (44.2575, -88.5192),   # Appleton / Fox Cities, WI
    "KBHM": (33.5629, -86.7535),   # Birmingham-Shuttlesworth Intl Airport, AL
    "KBIS": (46.7727, -100.7460),  # Bismarck Municipal, ND
    "KBJI": (47.5098, -94.9333),   # Bemidji, MN
    "KBLV": (38.5451, -89.8458),   # Belleville / St. Louis area, IL
    "KBMI": (40.4771, -88.9159),   # Central Illinois Regional Airport (Bloomington), IL
    "KBPT": (29.9508, -94.0207),   # Jack Brooks Regional Airport (Beaumont), TX
    "KBTR": (30.5332, -91.1496),   # Baton Rouge Metropolitan, LA
    "KBWG": (36.9696, -86.4137),   # Bowling Green, KY
    "KCHA": (35.0353, -85.2038),   # Chattanooga, TN
    "KCID": (41.8847, -91.7108),   # The Eastern Iowa Airport (Cedar Rapids), IA
    "KCOU": (38.8181, -92.2196),   # Columbia Regional, MO
    "KCRP": (27.7704, -97.5012),   # Corpus Christi International Airport, TX
    "KCSG": (32.5163, -84.9388),   # Columbus, GA
    "KCWA": (44.7776, -89.6661),   # Central Wisconsin, WI
    "KDBQ": (42.4020, -90.7095),   # Dubuque Regional Airport, IA
    "KDIK": (46.7979, -102.8023),  # Dickinson, ND
    "KDSM": (41.5340, -93.6631),   # Des Moines International, IA
    "KDVL": (48.1158, -98.9036),   # Devils Lake, ND
    "KESC": (45.7445, -87.0988),   # Escanaba, MI
    "KFAR": (46.9197, -96.8157),   # Hector International (Fargo), ND
    "KFSD": (43.5820, -96.7418),   # Sioux Falls Regional, SD
    "KFSM": (35.3364, -94.3687),   # Fort Smith, AR
    "KGCK": (37.9275, -100.7244),  # Garden City, KS
    "KGPT": (30.4073, -89.0701),   # Gulfport-Biloxi International, MS
    "KGRI": (40.9675, -98.3096),   # Central Nebraska Regional (Grand Island), NE
    "KGTR": (33.4547, -88.5912),   # Columbus / Starkville, MS
    "KGYY": (41.6163, -87.4139),   # Gary / Chicago area, IN
    "KHBG": (31.2829, -89.2530),   # Hattiesburg-Laurel Regional, MS
    "KHEZ": (31.7915, -91.2991),   # Natchez, MS
    "KHSV": (34.6404, -86.7756),   # Huntsville, AL
    "KICT": (37.6499, -97.4331),   # Wichita Dwight D. Eisenhower National, KS
    "KIMT": (45.8184, -88.1143),   # Iron Mountain, MI
    "KINL": (48.5682, -93.4003),   # International Falls, MN
    "KISQ": (45.9744, -86.1714),   # Schoolcraft County Airport (Manistique), MI
    "KJEF": (38.5962, -92.1578),   # Jefferson City, MO
    "KJKA": (30.2882, -87.6713),   # Gulf Shores, AL
    "KJMS": (46.9298, -98.6782),   # Jamestown, ND
    "KJVY": (38.2731, -85.7397),   # Jeffersonville / Louisville area, IN
    "KLAW": (34.5676, -98.4153),   # Lawton, OK
    "KLBB": (33.6636, -101.8228),  # Lubbock, TX
    "KLCH": (30.1261, -93.2233),   # Lake Charles Regional, LA
    "KLFT": (30.2053, -91.9876),   # Lafayette Regional, LA
    "KLIT": (34.7294, -92.2243),   # Bill and Hillary Clinton National (Little Rock), AR
    "KLNK": (40.8510, -96.7592),   # Lincoln Airport, NE
    "KLSE": (43.8794, -91.2567),   # La Crosse, WI
    "KMCN": (32.6939, -83.6431),   # Macon, GA
    "KMEI": (32.3432, -88.7554),   # Meridian, MS
    "KMGM": (32.3006, -86.3940),   # Montgomery Regional Airport, AL
    "KMLI": (41.4485, -90.5075),   # Quad Cities International (Moline), IL
    "KMLU": (32.5109, -92.0376),   # Monroe Regional, LA
    "KMOB": (30.6914, -88.2428),   # Mobile Regional, AL
    "KMOT": (48.2575, -101.2803),  # Minot, ND
    "KOWB": (37.7408, -87.1656),   # Owensboro, KY
    "KPIA": (40.6642, -89.6933),   # General Wayne A. Downing Peoria Intl, IL
    "KPIB": (31.4673, -89.3374),   # Hattiesburg / Laurel, MS
    "KPIR": (44.3845, -100.2862),  # Pierre, SD
    "KPNS": (30.4734, -87.1866),   # Pensacola International, FL
    "KRAP": (44.0453, -103.0572),  # Rapid City, SD
    "KRFD": (42.1954, -89.0982),   # Rockford, IL
    "KSGF": (37.2457, -93.3886),   # Springfield-Branson National, MO
    "KSHV": (32.4466, -93.8256),   # Shreveport Regional Airport, LA
    "KSJT": (31.3564, -100.4963),  # San Angelo, TX
    "KSLN": (38.7911, -97.6519),   # Salina, KS
    "KSPI": (39.8441, -89.6779),   # Springfield, IL
    "KSTC": (45.5456, -94.0699),   # St. Cloud, MN
    "KSTJ": (39.7733, -94.9056),   # St. Joseph, MO
    "KSUX": (42.4026, -96.3844),   # Sioux Gateway Airport, IA
    "KTOP": (39.0706, -95.6258),   # Topeka, KS
    "KTRI": (36.4752, -82.4074),   # Tri-Cities, TN/VA
    "KTUL": (36.1984, -95.8881),   # Tulsa, OK
    "KTUP": (34.2690, -88.7656),   # Tupelo, MS
    "KTYR": (32.3541, -95.4024),   # Tyler Pounds Regional, TX
    "KVCT": (28.8475, -96.9774),   # Victoria, TX
    "KVPS": (30.4832, -86.5254),   # Destin-Fort Walton Beach / Eglin AFB, FL
    "KXNA": (36.2819, -94.3068),   # Fayetteville / Northwest Arkansas, AR

    # --------------------------------------------------------------------------
    # GREAT LAKES SPOKES
    # --------------------------------------------------------------------------
    "KAPN": (45.0781, -83.5603),   # Alpena, MI
    "KAZO": (42.2349, -85.5521),   # Kalamazoo/Battle Creek Intl, MI
    "KCAK": (40.9161, -81.4422),   # Akron-Canton Airport, OH
    "KCIU": (46.2508, -84.4725),   # Chippewa County Intl (Sault Ste. Marie), MI
    "KCMH": (39.9981, -82.8919),   # Columbus, OH
    "KCMX": (47.1684, -88.4891),   # Houghton, MI
    "KCVG": (39.0461, -84.6622),   # Cincinnati, OH/KY
    "KDAY": (39.9024, -84.2194),   # Dayton, OH
    "KDLH": (46.8421, -92.1936),   # Duluth International Airport, MN
    "KERI": (42.0820, -80.1762),   # Erie International Airport, PA
    "KEVV": (38.0383, -87.5308),   # Evansville, IN
    "KFNT": (42.9654, -83.7436),   # Bishop International (Flint), MI
    "KFWA": (40.9785, -85.1951),   # Fort Wayne International, IN
    "KGRB": (44.4846, -88.1297),   # Green Bay, WI
    "KHTS": (38.3667, -82.5580),   # Tri-State Airport (Huntington), WV
    "KLAN": (42.7787, -84.5874),   # Capital Region Intl (Lansing), MI
    "KLEX": (38.0364, -84.6058),   # Lexington, KY
    "KMBS": (43.5328, -84.0796),   # Saginaw / Bay City / Midland, MI
    "KMKE": (42.9472, -87.8966),   # Milwaukee Mitchell International, WI
    "KMQT": (46.3536, -87.3953),   # Sawyer International Airport (Marquette), MI
    "KPIT": (40.4915, -80.2329),   # Pittsburgh International, PA
    "KPLN": (45.5708, -84.7967),   # Pellston Regional Airport, MI
    "KRST": (43.9083, -92.4980),   # Rochester International Airport, MN
    "KSBN": (41.7086, -86.3173),   # South Bend International, IN
    "KTOL": (41.5868, -83.8078),   # Toledo Express Airport, OH
    "KTVC": (44.7414, -85.5822),   # Cherry Capital Airport (Traverse City), MI

    # --------------------------------------------------------------------------
    # NORTHEAST & NORTHERN NEW ENGLAND SPOKES
    # --------------------------------------------------------------------------
    "KABE": (40.6521, -75.4408),   # Lehigh Valley International (Allentown), PA
    "KACK": (41.2531, -70.0602),   # Nantucket Memorial, MA
    "KALB": (42.7483, -73.8017),   # Albany International Airport, NY
    "KART": (44.0022, -75.7217),   # Watertown International, NY
    "KAUG": (44.3206, -69.7972),   # Augusta State Airport, ME
    "KAVP": (41.3385, -75.7234),   # Wilkes-Barre/Scranton International, PA
    "KBFD": (41.8031, -78.6401),   # Bradford Regional Airport, PA
    "KBGM": (42.2086, -75.9797),   # Greater Binghamton Airport, NY
    "KBHB": (44.4498, -68.3616),   # Hancock County-Bar Harbor, ME
    "KBTV": (44.4730, -73.1533),   # Patrick Leahy Burlington International, VT
    "KBUF": (42.9405, -78.7322),   # Buffalo Niagara International, NY
    "KCON": (43.2028, -71.5022),   # Concord Municipal Airport, NH
    "KDUJ": (41.1783, -78.8986),   # DuBois Regional Airport, PA
    "KELM": (42.1599, -76.8914),   # Elmira/Corning Regional, NY
    "KEWB": (41.6761, -70.9583),   # New Bedford Regional, MA
    "KFMH": (41.6585, -70.5215),   # Cape Cod Coast Guard Air Station / Falmouth, MA
    "KFRG": (40.7288, -73.4134),   # Republic Airport (Farmingdale), NY
    "KGON": (41.3301, -72.0456),   # Groton-New London Airport, CT
    "KHPN": (41.0670, -73.7076),   # Westchester County Airport (White Plains), NY
    "KHVN": (41.2638, -72.8868),   # Tweed-New Haven Airport, CT
    "KHYA": (41.6693, -70.2804),   # Barnstable Municipal (Hyannis), MA
    "KIPT": (41.2419, -76.9211),   # Williamsport Regional Airport, PA
    "KISP": (40.7952, -73.1002),   # Long Island MacArthur Airport (Islip), NY
    "KITH": (42.4913, -76.4585),   # Tompkins Cortland Community (Ithaca), NY
    "KJST": (40.3229, -78.8338),   # Johnstown-Cambria County Airport, PA
    "KLBE": (40.2759, -79.4048),   # Arnold Palmer Regional Airport (Latrobe), PA
    "KLEB": (43.6261, -72.3042),   # Lebanon Municipal, NH
    "KLNS": (40.1217, -76.2960),   # Lancaster Airport, PA
    "KMDT": (40.1935, -76.7634),   # Harrisburg International, PA
    "KMHT": (42.9326, -71.4357),   # Manchester-Boston Regional, NH
    "KMIV": (39.3678, -75.0722),   # Millville Municipal Airport, NJ
    "KMPV": (44.2035, -72.5623),   # Edward F. Knapp State (Montpelier), VT
    "KMSS": (44.9358, -74.8456),   # Massena International Airport, NY
    "KMVY": (41.3931, -70.6143),   # Martha's Vineyard Airport, MA
    "KOGS": (44.6819, -75.4656),   # Ogdensburg International Airport, NY
    "KOQU": (41.5972, -71.4122),   # Quonset State Airport (North Kingstown), RI
    "KORH": (42.2673, -71.8757),   # Worcester Regional, MA
    "KPBG": (44.6509, -73.4681),   # Plattsburgh International, NY
    "KPQB": (46.6889, -68.0448),   # Presque Isle International, ME
    "KPSM": (43.0779, -70.8233),   # Portsmouth International at Pease, NH
    "KPVD": (41.7240, -71.4282),   # Rhode Island T.F. Green Intl (Providence), RI
    "KPWM": (43.6462, -70.3088),   # Portland International Jetport, ME
    "KRDG": (40.3785, -75.9652),   # Reading Regional Airport, PA
    "KRKD": (44.0601, -69.0992),   # Knox County Regional (Rockland), ME
    "KROC": (43.1189, -77.6724),   # Frederick Douglass - Greater Rochester Intl, NY
    "KSBY": (38.3405, -75.5103),   # Salisbury-Ocean City Wicomico Regional, MD
    "KSFM": (43.3939, -70.7075),   # Sanford Seacoast Regional Airport, ME
    "KSLK": (44.3853, -74.2062),   # Adirondack Regional (Saranac Lake), NY
    "KSYR": (43.1112, -76.1063),   # Syracuse Hancock International, NY
    "KTTN": (40.2767, -74.8135),   # Trenton-Mercer Airport, NJ

    # --------------------------------------------------------------------------
    # MID-ATLANTIC & SOUTHEAST SPOKES
    # --------------------------------------------------------------------------
    "KACY": (39.4576, -74.5772),   # Atlantic City International, NJ
    "KAGS": (33.3699, -82.0292),   # Augusta Regional, GA
    "KAVL": (35.4362, -82.5418),   # Asheville Regional, NC
    "KBLF": (37.2934, -81.2155),   # Mercer County Airport (Bluefield), WV
    "KBQK": (31.2590, -81.4663),   # Brunswick Golden Isles, GA
    "KCAE": (33.9388, -81.1195),   # Columbia Metropolitan, SC
    "KCHO": (38.1386, -78.4529),   # Charlottesville-Albemarle Airport, VA
    "KCHS": (32.8986, -80.0405),   # Charleston International, SC
    "KCKB": (39.2965, -80.2280),   # North Central West Virginia (Clarksburg), WV
    "KCRW": (38.3731, -81.5932),   # West Virginia International Yeager (Charleston), WV
    "KECP": (30.3571, -85.7956),   # Northwest Florida Beaches International Airport, FL
    "KEWN": (35.0730, -77.0429),   # Coastal Carolina Regional (New Bern), NC
    "KFAY": (34.9912, -78.8803),   # Fayetteville Regional, NC
    "KFLO": (34.1874, -79.7153),   # Florence Regional, SC
    "KFLL": (26.0726, -80.1527),   # Fort Lauderdale/Hollywood Intl, FL
    "KGNV": (29.6901, -82.2718),   # Gainesville Regional, FL
    "KGSO": (36.0978, -79.9373),   # Piedmont Triad International Airport (Greensboro), NC
    "KGSP": (34.8957, -82.2188),   # Greenville-Spartanburg International, SC
    "KHGR": (39.7077, -77.7297),   # Hagerstown Regional, MD
    "KILG": (39.6787, -75.6065),   # Wilmington Airport, DE
    "KILM": (34.2706, -77.9026),   # Wilmington International, NC
    "KEYW": (24.5557, -81.7596),   # Key West International, FL
    "KJQF": (35.3878, -80.7092),   # Concord-Padgett Regional Airport, NC
    "KLWB": (37.8583, -80.3995),   # Greenbrier Valley Airport (Lewisburg), WV
    "KLYH": (37.3267, -79.2004),   # Lynchburg Regional, VA
    "KMGW": (39.6425, -79.9157),   # Morgantown Municipal, WV
    "KMLB": (28.1028, -80.6453),   # Melbourne Orlando International Airport, FL
    "KMYR": (33.6797, -78.9283),   # Myrtle Beach International, SC
    "KPGD": (26.9163, -82.0006),   # Punta Gorda Airport, FL
    "KPGV": (35.6353, -77.3853),   # Pitt-Greenville Airport, NC
    "KPHF": (37.1319, -76.4930),   # Newport News/Williamsburg Intl, VA
    "KPIE": (27.9105, -82.6874),   # St. Pete-Clearwater International, FL
    "KPKB": (39.3453, -81.4423),   # Mid-Ohio Valley Regional (Parkersburg), WV
    "KRDU": (35.8776, -78.7875),   # Raleigh-Durham International, NC
    "KROA": (37.3255, -79.9754),   # Roanoke-Blacksburg Regional, VA
    "KSAV": (32.1276, -81.2021),   # Savannah/Hilton Head International, GA
    "KSGJ": (29.9593, -81.3397),   # Northeast Florida Regional (St. Augustine), FL
    "KSRQ": (27.3954, -82.5544),   # Sarasota/Bradenton International, FL
    "KTLH": (30.3965, -84.3503),   # Tallahassee International, FL
    "KTYS": (35.8110, -83.9940),   # McGhee Tyson Airport (Knoxville), TN
    "KVRB": (27.6556, -80.4179),   # Vero Beach Regional, FL

    # --------------------------------------------------------------------------
    # CANADA
    # --------------------------------------------------------------------------
    "CYDF": (49.2082, -57.3961),   # Deer Lake Airport, NL
    "CYEG": (53.3097, -113.5800),  # Edmonton International Airport, AB
    "CYFC": (45.8689, -66.5372),   # Fredericton International, NB
    "CYHM": (43.1736, -79.9350),   # John C. Munro Hamilton Intl, ON
    "CYHZ": (44.8808, -63.5086),   # Halifax Stanfield International, NS
    "CYQB": (46.7911, -71.3933),   # Québec City Jean Lesage Intl, QC
    "CYQM": (46.1132, -64.6772),   # Greater Moncton Roméo LeBlanc Intl, NB
    "CYQY": (46.1614, -60.0478),   # Sydney Airport, NS
    "CYSJ": (45.3161, -65.8903),   # Saint John Airport, NB
    "CYUL": (45.4706, -73.7408),   # Montréal-Trudeau International, QC
    "CYVR": (49.1939, -123.1840),  # Vancouver International Airport, BC
    "CYWG": (49.9100, -97.2397),   # Winnipeg Richardson International, MB
    "CYXS": (53.8894, -122.6790),  # Prince George Airport, BC
    "CYXY": (60.7096, -135.0673),  # Erik Nielsen Whitehorse International, YT
    "CYYC": (51.1188, -114.0099),  # Calgary International Airport, AB
    "CYYG": (46.2900, -63.1211),   # Charlottetown Airport, PE
    "CYYJ": (48.6469, -123.4258),  # Victoria International Airport, BC
    "CYYT": (47.6186, -52.7519),   # St. John's International Airport, NL
    "CYZF": (62.4631, -114.4403),  # Yellowknife Airport, NT

    # --------------------------------------------------------------------------
    # MEXICO & CENTRAL AMERICA
    # --------------------------------------------------------------------------
    "MGGT": (14.5833, -90.5275),   # La Aurora Intl (Guatemala City), Guatemala
    "MMBT": (15.7753, -96.2625),   # Bahías de Huatulco Intl, Mexico
    "MMCZ": (20.5224, -86.9255),   # Cozumel International, Mexico
    "MMGL": (20.5218, -103.3112),  # Miguel Hidalgo y Costilla Intl (Guadalajara), Mexico
    "MMHO": (29.0958, -111.0478),  # General Ignacio Pesqueira García Intl (Hermosillo), Mexico
    "MMMZ": (23.1614, -106.3712),  # General Rafael Buelna Intl (Mazatlán), Mexico
    "MMPB": (19.1583, -98.3711),   # Hermanos Serdán Intl (Puebla), Mexico
    "MMPR": (20.6801, -105.2541),  # Lic. Gustavo Díaz Ordaz Intl (Puerto Vallarta), Mexico
    "MMSD": (23.1518, -109.7210),  # Los Cabos International, Mexico
    "MMTJ": (32.5411, -116.9700),  # Tijuana International Airport, Mexico
    "MMUN": (21.0365, -86.8771),   # Cancún International, Mexico
    "MMVR": (19.1458, -96.1897),   # General Heriberto Jara Intl (Veracruz), Mexico
    "MNMG": (12.1444, -86.1683),   # Augusto C. Sandino Intl (Managua), Nicaragua
    "MPPA": (8.9775, -79.5997),    # Panamá Pacífico International, Panama
    "MROC": (9.9939, -84.2088),    # Juan Santamaría Intl (San José), Costa Rica
    "MRLB": (10.5933, -85.5444),   # Daniel Oduber Quirós Intl (Liberia), Costa Rica
    "MZBZ": (17.5391, -88.3082),   # Philip S. W. Goldson Intl (Belize City), Belize

    # --------------------------------------------------------------------------
    # CARIBBEAN & US TERRITORIES
    # --------------------------------------------------------------------------
    "MBPV": (21.7736, -72.2659),   # Providenciales Intl, Turks & Caicos
    "MDPC": (18.5674, -68.3634),   # Punta Cana International, Dominican Republic
    "MKJP": (17.9356, -76.7875),   # Norman Manley Intl (Kingston), Jamaica
    "MKJS": (18.5037, -77.9134),   # Sangster International (Montego Bay), Jamaica
    "MUHA": (22.9892, -82.4092),   # José Martí International (Havana), Cuba
    "MUVR": (23.1592, -81.4328),   # Juan Gualberto Gómez (Varadero), Cuba
    "MWCR": (19.2922, -81.3578),   # Owen Roberts Intl (Grand Cayman), Cayman Islands
    "MYNN": (25.0390, -77.4662),   # Lynden Pindling International (Nassau), Bahamas
    "MYSM": (24.0864, -74.5247),   # San Salvador Airport, Bahamas
    "TAPA": (17.1367, -61.7927),   # V.C. Bird International, Antigua
    "TBPB": (13.0746, -59.4925),   # Grantley Adams International, Barbados
    "TFFF": (14.5910, -61.0032),   # Martinique Aimé Césaire Intl, Martinique
    "TFFR": (16.2653, -61.5318),   # Pointe-à-Pitre International, Guadeloupe
    "TIST": (18.3373, -64.9734),   # Cyril E. King Airport (St. Thomas), USVI
    "TISX": (17.7019, -64.7986),   # Henry E. Rohlsen Airport (St. Croix), USVI
    "TJPS": (18.0083, -66.5630),   # Mercedita Airport (Ponce), PR
    "TJSJ": (18.4394, -66.0018),   # Luis Muñoz Marín Intl (San Juan), PR
    "TKPK": (17.3112, -62.7187),   # Robert L. Bradshaw Intl, St. Kitts
    "TLPL": (13.7332, -60.9526),   # Hewanorra International, St. Lucia
    "TNCA": (12.5014, -70.0152),   # Queen Beatrix International, Aruba
    "TNCB": (12.1310, -68.2685),   # Flamingo International, Bonaire
    "TNCC": (12.1889, -68.9598),   # Curaçao International, Curaçao
    "TNCM": (18.0410, -63.1089),   # Princess Juliana Intl, St. Maarten
    "TVSA": (13.1569, -61.1481),   # Argyle International, St. Vincent

    # --------------------------------------------------------------------------
    # SOUTH AMERICA
    # --------------------------------------------------------------------------
    "SAEZ": (-34.8222, -58.5358),  # Ezeiza International (Buenos Aires), Argentina
    "SCEL": (-33.3930, -70.7858),  # Arturo Merino Benítez Intl (Santiago), Chile
    "SEQM": (-0.1292, -78.3575),   # Mariscal Sucre International (Quito), Ecuador
    "SKBO": (-4.7016, -74.1469),   # El Dorado International (Bogota), Colombia
    "SKCG": (10.4424, -75.5130),   # Rafael Núñez Intl (Cartagena), Colombia
    "SKCL": (3.5433, -76.3814),    # Alfonso Bonilla Aragón Intl (Cali), Colombia
    "SKRG": (6.1645, -75.4233),    # José María Córdova Intl (Medellin), Colombia
    "SMJP": (5.4431, -55.1903),    # Johan Adolf Pengel Intl (Paramaribo), Suriname
    "SPJC": (-12.0219, -77.1143),  # Jorge Chávez International (Lima), Peru
    "SPQU": (-16.3411, -71.5831),  # Rodríguez Ballón Intl (Arequipa), Peru
    "SYCJ": (6.4981, -58.2539),    # Cheddi Jagan Intl (Georgetown), Guyana

    # --------------------------------------------------------------------------
    # EUROPE & ICELAND
    # --------------------------------------------------------------------------
    "BIKF": (63.9850, -22.6056),    # Keflavík International, Iceland
    "EBBR": (50.9014, 4.4844),      # Brussels Airport, Belgium
    "EDDF": (50.0379, 8.5622),      # Frankfurt Airport, Germany
    "EDDM": (48.3538, 11.7861),     # Munich Airport, Germany
    "EFHK": (60.3172, 24.9633),     # Helsinki Airport, Finland
    "EGCC": (53.3537, -2.2750),     # Manchester Airport, United Kingdom
    "EGPK": (55.5094, -4.5867),     # Glasgow Prestwick Airport, Scotland
    "EGLL": (51.4700, -0.4543),     # London Heathrow Airport, United Kingdom
    "EHAM": (52.3105, 4.7683),      # Amsterdam Airport Schiphol, Netherlands
    "EIDW": (53.4213, -6.2701),     # Dublin Airport, Ireland
    "EINN": (52.7020, -8.9248),     # Shannon Airport, Ireland
    "EKCH": (55.6180, 12.6508),     # Copenhagen Airport, Denmark
    "ENGM": (60.1939, 11.1004),     # Oslo Airport Gardermoen, Norway
    "ESSA": (59.6519, 17.9186),     # Stockholm Arlanda Airport, Sweden
    "LEBL": (41.2974, 2.0833),      # Josep Tarradellas Barcelona-El Prat, Spain
    "LEMD": (40.4936, -3.5668),     # Adolfo Suárez Madrid–Barajas, Spain
    "LFPG": (49.0097, 2.5479),      # Paris Charles de Gaulle Airport, France
    "LGAV": (37.9364, 23.9445),     # Athens International Airport, Greece
    "LIRF": (41.8003, 12.2389),     # Rome Fiumicino Airport, Italy
    "LOWW": (48.1103, 16.5697),     # Vienna International Airport, Austria
    "LPPD": (37.7412, -25.6979),    # Ponta Delgada (Azores), Portugal
    "LPPT": (38.7813, -9.1359),     # Humberto Delgado Airport (Lisbon), Portugal
    "LROP": (44.5722, 26.1022),     # Henri Coandă Intl (Bucharest), Romania
    "LSZH": (47.4647, 8.5492),      # Zurich Airport, Switzerland

    # --------------------------------------------------------------------------
    # ASIA & PACIFIC
    # --------------------------------------------------------------------------
    "RKPK": (35.1795, 128.9381),    # Gimhae International (Busan), South Korea
    "ROAH": (26.1958, 127.6458),    # Naha Airport (Okinawa), Japan
    "RORS": (24.8267, 125.1458),    # Shimojishima Airport, Japan
    "RPLC": (15.1878, 120.5606),    # Clark International Airport, Philippines
}

import math
import random
from collections import defaultdict, deque
from datetime import datetime
import streamlit as st


def haversine_miles(coord1, coord2):
    """Calculates distance between two lat/lon points in miles."""
    if not coord1 or not coord2:
        return 0
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    R = 3958.8  # Earth radius in miles
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


def calculate_route_score(path):
    """Calculates total route mileage + minor layover penalty."""
    total_miles = 0
    for leg in path:
        c1 = AIRPORT_COORDS.get(leg["Origin"])
        c2 = AIRPORT_COORDS.get(leg["Destination"])
        if c1 and c2:
            total_miles += haversine_miles(c1, c2)
        else:
            total_miles += (
                800  # Fallback estimate if airport coordinates are unlisted
            )

    # Add a 150-mile penalty per layover connection to prefer efficient transfers
    layover_penalty = (len(path) - 1) * 150
    return total_miles + layover_penalty


# ==========================================
# 3. GEOGRAPHICALLY OPTIMIZED ROUTE ENGINE
# ==========================================


def leg_operates_today(days_str):
    """Checks if a flight leg operates today based on standard codes:

    'Daily', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'
    """
    if not days_str:
        return True

    days_clean = str(days_str).strip()

    # 1. 'Daily' always operates
    if "daily" in days_clean.lower():
        return True

    # 2. Get today's 3-letter day abbreviation (e.g., 'Mon', 'Wed', 'Fri')
    today_code = datetime.now().strftime("%a")

    # 3. Check if today's code is listed in the days string
    if today_code.lower() in days_clean.lower():
        return True

    return False


def get_reachable_destinations(network, origin, max_connections=6):
    """Returns a list of destination airport codes that have active operating flights

    from the specified origin on today's schedule.
    """
    # Keep only flight legs operating TODAY
    active_network = [
        leg
        for leg in network
        if leg_operates_today(leg.get("Days", "Daily"))
    ]

    adj_map = defaultdict(list)
    for leg in active_network:
        adj_map[leg["Origin"]].append(leg["Destination"])

    if origin not in adj_map:
        return []

    # BFS traversal to discover all reachable airports within max connection depth
    reachable = set()
    queue = deque([(origin, 0)])
    visited = {origin}

    while queue:
        curr, depth = queue.popleft()
        if depth >= max_connections + 1:
            continue
        for nxt in adj_map.get(curr, []):
            if nxt not in visited:
                visited.add(nxt)
                reachable.add(nxt)
                queue.append((nxt, depth + 1))

    return sorted(list(reachable))


def find_routes(
    network,
    origin,
    destination,
    exact_connections=None,
    max_connections=10,
    max_display=75,
):
    origin = origin.strip().upper()
    destination = destination.strip().upper()

    if origin == destination:
        return []

    # Keep only flights operating TODAY
    active_network = [
        leg
        for leg in network
        if leg_operates_today(leg.get("Days", "Daily"))
    ]

    # 1. PRE-BUILD ADJACENCY MAP
    adj_map = defaultdict(list)
    for leg in active_network:
        adj_map[leg["Origin"]].append(leg)

    if origin not in adj_map:
        return []

    # Determine target flight leg depth (Legs = Connections + 1)
    if exact_connections is not None:
        target_legs_list = [exact_connections + 1]
    else:
        max_depth = (
            min(max_connections if max_connections is not None else 10, 6) + 1
        )
        target_legs_list = list(range(1, max_depth + 1))

    valid_paths = []
    seen_signatures = set()

    # 2. TARGETED SEARCH FOR SELECTED CONNECTION LEVEL
    for target_legs in target_legs_list:
        if len(valid_paths) >= max_display * 2:
            break

        stack = []
        for leg in adj_map[origin]:
            stack.append(([leg], {origin, leg["Destination"]}))

        while stack:
            path, visited = stack.pop()
            current_node = path[-1]["Destination"]

            if len(path) == target_legs:
                if current_node == destination:
                    sig = tuple(
                        (leg["Flight"], leg["Origin"], leg["Destination"])
                        for leg in path
                    )
                    if sig not in seen_signatures:
                        seen_signatures.add(sig)
                        valid_paths.append(path)
                        if len(valid_paths) >= max_display * 2:
                            break
                continue

            if len(path) < target_legs:
                for nxt in adj_map.get(current_node, []):
                    nxt_dest = nxt["Destination"]
                    if nxt_dest not in visited:
                        new_visited = visited.copy()
                        new_visited.add(nxt_dest)
                        stack.append((path + [nxt], new_visited))

    if not valid_paths:
        return []

    # 3. SORT & RETURN BEST ROUTE OPTIONS
    valid_paths.sort(key=lambda p: calculate_route_score(p))
    return valid_paths[:max_display]


# ==========================================
# 4. APP UI
# ==========================================

network = get_full_network()
all_airports = sorted(list(set([f["Origin"] for f in network])))

st.subheader("🔍 Search Any Route on Network Map")

col1, col2, col3, col4 = st.columns([1, 1.3, 1, 1])

# 1. Origin Dropdown
with col1:
    orig_select = st.selectbox(
        "Origin Airport",
        options=all_airports,
        index=all_airports.index("KRIC") if "KRIC" in all_airports else 0,
        key="orig_select_val",
        format_func=lambda code: f"{code} - {AIRPORT_NAMES.get(code, 'Unknown Airport')}",
    )

# 2. Calculate Active Destinations for Today from selected Origin
valid_destinations = get_reachable_destinations(
    network, orig_select, max_connections=6
)

# Keep dest_select_val valid when Origin changes
if (
    "dest_select_val" not in st.session_state
    or st.session_state["dest_select_val"] not in valid_destinations
):
    if valid_destinations:
        st.session_state["dest_select_val"] = valid_destinations[0]
    else:
        st.session_state["dest_select_val"] = None


# 3. Safe Callback for Random Selection
def set_random_destination():
    current_dest = st.session_state.get("dest_select_val", None)
    # Pick exclusively from today's valid destinations, excluding current selection
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
                options=valid_destinations,  # Hides destinations without active flights today
                key="dest_select_val",
                label_visibility="collapsed",
                format_func=lambda code: f"{code} - {AIRPORT_NAMES.get(code, 'Unknown Airport')}",
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

# ==========================================
# 5. SEARCH RESULTS
# ==========================================

if "search_results" in st.session_state:
    results = st.session_state["search_results"]
    orig = st.session_state["search_orig"]
    dest = st.session_state["search_dest"]
    selected_conn_str = st.session_state.get("search_conn_str", conn_str)

    st.markdown("---")
    st.markdown(
        f"### Possible Routes for **{orig} ➔ {dest}** ({len(results)} option(s) found)"
    )

    if not results:
        st.info(
            f"No routes found connecting {orig} to {dest} with **{selected_conn_str}**."
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

import math
import random
from datetime import datetime

HUBS = {"KRIC", "KSFB", "KSWF", "KBGR", "TJBQ"}
INTL_AIRPORTS = {"TJBQ", "TIST", "TISX"}

# Skybus Fleet Specifications with Tail Registrations
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


def get_flight_capacity_and_pax(leg):
    """Assigns aircraft model, specific tail number registration, and passenger load factor

    based on distance, route classification, flight number, and date.
    """
    flight_num = leg["Flight"]
    orig = leg["Origin"]
    dest = leg["Destination"]

    c1 = AIRPORT_COORDS.get(orig)
    c2 = AIRPORT_COORDS.get(dest)
    distance = haversine_miles(c1, c2) if (c1 and c2) else 600

    today_str = datetime.now().strftime("%Y-%m-%d")
    seed_value = f"{flight_num}-{today_str}"
    rng = random.Random(seed_value)

    is_hub_to_hub = (orig in HUBS) and (dest in HUBS)
    is_international = (orig in INTL_AIRPORTS) or (dest in INTL_AIRPORTS)

    if is_international or is_hub_to_hub or distance >= 1000:
        ac_type = rng.choice(["A321", "A321", "A321", "A321", "A320"])
    elif distance < 450:
        ac_type = rng.choice(["A319", "A319", "A319", "A320"])
    else:
        ac_type = rng.choice(["A320", "A320", "A320", "A319", "A321"])

    spec = FLEET_SPECS[ac_type]
    tail_number = rng.choice(spec["registrations"])
    capacity = spec["capacity"]

    min_pax = int(capacity * 0.72)
    max_pax = int(capacity * 0.98)
    pax_count = rng.randint(min_pax, max_pax)

    return {
        "aircraft_code": ac_type,
        "aircraft_name": spec["name"],
        "tail_number": tail_number,
        "capacity": capacity,
        "pax_count": pax_count,
        "load_factor": round((pax_count / capacity) * 100, 1),
    }


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

    # Calculate aircraft model & passenger load for active leg
    flight_info = get_flight_capacity_and_pax(active_leg["Flight"])

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
                <span style="font-size: 10px; margin-left: 6px; background: rgba(255,255,255,0.25); padding: 3px 7px; border-radius: 10px;">MOBILE PASS</span>
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
                    <div class="bp-field">Wi-Fi Access</div>
                    <div class="bp-value" style="color: #F28425;">High-Speed SkyFly</div>
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
                    <div class="bp-value">Zone 1</div>
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
                    <div class="bp-value" style="font-size: 13px;">🧳 1 Checked</div>
                </div>
                <div style="border-left: 1px solid #ddd;"></div>
                <div style="flex: 1;">
                    <div class="bp-field">Carry-On</div>
                    <div class="bp-value" style="font-size: 13px;">🎒 1 Carry-on</div>
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
                    <div class="bp-value" style="font-size: 13px;">👥 {flight_info['pax_count']} / {flight_info['capacity']} ({flight_info['load_factor']}%)</div>
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

    st.components.v1.html(card_html, height=530)
