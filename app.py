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
# ----------------------------------------------------
# ----------------------------------------------------
   # PAFA Bridge Spokes (1300 Block - Alaska Hub)
    # ----------------------------------------------------
    (1300, "PAFA", "PAJN", "Daily"),  # Juneau, AK
    (1302, "PAFA", "PAKT", "Tue, Thu, Sat"),  # Ketchikan, AK
    (1304, "PAFA", "PABR", "Mon, Wed, Fri"),  # Utqiaġvik (Barrow), AK
    (1306, "PAFA", "PAOT", "Tue, Thu, Sat"),  # Kotzebue, AK
    (1308, "PAFA", "PASC", "Daily"),  # Deadhorse / Prudhoe Bay, AK
    (1310, "PAFA", "PADQ", "Mon, Wed, Fri"),  # Kodiak, AK
    (1312, "PAFA", "PAOM", "Tue, Thu, Sat"),  # Nome, AK
    (1314, "PAFA", "PAPG", "Tue, Thu, Sat"),  # Petersburg, AK
    (1316, "PAFA", "PASI", "Mon, Wed, Fri"),  # Sitka, AK
    (1318, "PAFA", "PAYA", "Tue, Thu, Sat"),  # Yakutat, AK
    (1320, "PAFA", "PAVD", "Mon, Fri"),  # Valdez, AK
    (1322, "PAFA", "PAEN", "Daily"),  # Kenai, AK
    (1324, "PAFA", "PAKW", "Tue, Thu, Sat"),  # Wrangell, AK
    (1326, "PAFA", "PAHO", "Mon, Wed, Fri, Sun"),  # Homer, AK
    (1328, "PAFA", "PHNL", "Daily"),  # Honolulu, HI (Oahu)
    (1330, "PAFA", "PHOG", "Thu, Sun"),  # Kahului, HI (Maui)
    (1332, "PAFA", "PHKO", "Wed, Sat"),  # Kona, HI (Big Island)
    (1334, "PAFA", "PAGS", "Tue, Thu, Sat"),  # Gustavus, AK
    (1336, "PAFA", "PADL", "Mon, Wed, Fri"),  # Dillingham, AK
    (1338, "PAFA", "PAKN", "Mon, Wed, Fri, Sun"),  # King Salmon, AK

    # ----------------------------------------------------
    # KPVU Bridge Spokes (1400 Block - Intermountain West Hub)
    # ----------------------------------------------------
    (1400, "KPVU", "KBOI", "Daily"),  # Boise, ID
    (1402, "KPVU", "KSGU", "Mon, Wed, Fri, Sun"),  # St. George, UT
    (1404, "KPVU", "KIFP", "Thu, Sun"),  # Bullhead City / Laughlin, AZ
    (1406, "KPVU", "KJAC", "Daily"),  # Jackson Hole, WY
    (1408, "KPVU", "KGEG", "Daily"),  # Spokane, WA
    (1410, "KPVU", "KEUG", "Mon, Fri"),  # Eugene, OR 
    (1412, "KPVU", "KFLG", "Tue, Thu, Sat"),  # Flagstaff, AZ
    (1414, "KPVU", "KCPR", "Mon, Wed, Fri"),  # Casper, WY
    (1416, "KPVU", "KGJT", "Tue, Thu, Sat"),  # Grand Junction, CO
    (1418, "KPVU", "KIDA", "Daily"),  # Idaho Falls, ID
    (1420, "KPVU", "KBZN", "Daily"),  # Bozeman, MT
    (1422, "KPVU", "KMSO", "Mon, Wed, Fri, Sun"),  # Missoula, MT
    (1424, "KPVU", "KTWF", "Tue, Thu, Sat"),  # Twin Falls, ID
    (1426, "KPVU", "KPIH", "Mon, Wed, Fri"),  # Pocatello, ID
    (1428, "KPVU", "KRNO", "Daily"),  # Reno / Tahoe, NV
    (1430, "KPVU", "PHNL", "Daily"),  # Honolulu, HI (Oahu)
    (1432, "KPVU", "PHOG", "Thu, Sun"),  # Kahului, HI (Maui)
    (1434, "KPVU", "KYKM", "Tue, Thu, Sat"),  # Yakima, WA
    (1436, "KPVU", "KPSC", "Mon, Wed, Fri, Sun"),  # Pasco / Tri-Cities, WA
    (1438, "KPVU", "KMFR", "Mon, Fri"),  # Rogue Valley / Medford, OR
    (1440, "KPVU", "KRDM", "Mon, Wed, Fri, Sun"),  # Bend / Redmond, OR
    (1442, "KPVU", "KOTH", "Thu, Sun"),  # North Bend / Coos Bay, OR
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

    # ----------------------------------------------------
    # KIWA Bridge Spokes (300 Block - Southwest Hub)
    # ----------------------------------------------------
    (300, "KIWA", "KSGU", "Mon, Wed, Fri, Sun"),  # St. George, UT
    (302, "KIWA", "KIFP", "Thu, Sun"),  # Bullhead City / Laughlin, AZ
    (304, "KIWA", "KELP", "Daily"),  # El Paso, TX
    (306, "KIWA", "KCLD", "Mon, Fri"),  # Carlsbad / San Diego North, CA
    (308, "KIWA", "KFLG", "Tue, Thu, Sat"),  # Flagstaff, AZ
    (310, "KIWA", "KMAF", "Daily"),  # Midland / Odessa, TX
    (312, "KIWA", "KABQ", "Daily"),  # Albuquerque, NM
    (314, "KIWA", "KTUS", "Daily"),  # Tucson, AZ
    (316, "KIWA", "KPSP", "Mon, Wed, Fri, Sun"),  # Palm Springs, CA
    (318, "KIWA", "KROW", "Tue, Thu, Sat"),  # Roswell, NM
    (320, "KIWA", "KPRC", "Mon, Wed, Fri"),  # Prescott, AZ
    (322, "KIWA", "KDRO", "Mon, Wed, Fri, Sun"),  # Durango, CO
    (324, "KIWA", "KEKO", "Tue, Thu, Sat"),  # Elko, NV
    (326, "KIWA", "KSBP", "Thu, Sun"),  # San Luis Obispo, CA
    (330, "KIWA", "PHNL", "Daily"),  # Honolulu, HI (Oahu)
    (332, "KIWA", "PHOG", "Thu, Sun"),  # Kahului, HI (Maui)
    (334, "KIWA", "PHKO", "Wed, Sat"),  # Kona, HI (Big Island)
    (336, "KIWA", "KSBA", "Daily"),  # Santa Barbara, CA
    (338, "KIWA", "KMRY", "Mon, Wed, Fri, Sun"),  # Monterey, CA
    (340, "KIWA", "KFAT", "Daily"),  # Fresno, CA
    (342, "KIWA", "KBFL", "Mon, Wed, Fri"),  # Bakersfield, CA
    (344, "KIWA", "KCDC", "Thu, Sun"),  # Cedar City, UT
    (346, "KIWA", "KACV", "Tue, Thu, Sat"),  # Arcata / Eureka, CA

    # ----------------------------------------------------
    # KBLI Bridge Spokes (400 Block - Pacific Northwest Hub)
    # ----------------------------------------------------
    (400, "KBLI", "PAJN", "Daily"),  # Juneau, AK
    (402, "KBLI", "PAKT", "Mon, Wed, Fri, Sun"),  # Ketchikan, AK
    (404, "KBLI", "KBOI", "Daily"),  # Boise, ID
    (406, "KBLI", "KGEG", "Daily"),  # Spokane, WA
    (408, "KBLI", "KEUG", "Mon, Wed, Fri, Sun"),  # Eugene, OR
    (410, "KBLI", "KYKM", "Tue, Thu, Sat"),  # Yakima, WA
    (412, "KBLI", "KPSC", "Mon, Wed, Fri"),  # Pasco / Tri-Cities, WA
    (414, "KBLI", "KMFR", "Mon, Fri"),  # Rogue Valley / Medford, OR
    (416, "KBLI", "KRDM", "Mon, Wed, Fri, Sun"),  # Bend / Redmond, OR
    (418, "KBLI", "KOTH", "Thu, Sun"),  # North Bend / Coos Bay, OR
    (420, "KBLI", "KALW", "Tue, Thu, Sat"),  # Walla Walla, WA
    (422, "KBLI", "KEAT", "Mon, Wed, Fri"),  # Wenatchee, WA
    (424, "KBLI", "KLWS", "Tue, Thu, Sat"),  # Lewiston, ID
    (426, "KBLI", "KTWF", "Mon, Wed, Fri"),  # Twin Falls, ID
    (428, "KBLI", "KCLM", "Daily"),  # Port Angeles, WA
    (430, "KBLI", "PHNL", "Daily"),  # Honolulu, HI (Oahu)
    (432, "KBLI", "PHOG", "Thu, Sun"),  # Kahului, HI (Maui)
    (434, "KBLI", "PHKO", "Wed, Sat"),  # Kona, HI (Big Island)
    (436, "KBLI", "PHLI", "Mon, Fri"),  # Lihue, HI (Kauai)
    (438, "KBLI", "KJAC", "Daily"),  # Jackson Hole, WY
    (440, "KBLI", "KCPR", "Tue, Thu, Sat"),  # Casper, WY
    (442, "KBLI", "KIDA", "Mon, Wed, Fri, Sun"),  # Idaho Falls, ID
    (444, "KBLI", "KBZN", "Daily"),  # Bozeman, MT
    (446, "KBLI", "KMSO", "Mon, Wed, Fri"),  # Missoula, MT
    (448, "KBLI", "KPIH", "Tue, Thu, Sat"),  # Pocatello, ID
    (450, "KBLI", "KRNO", "Daily"),  # Reno / Tahoe, NV
    (452, "KBLI", "KACV", "Mon, Wed, Fri, Sun"),  # Arcata / Eureka, CA
    (454, "KBLI", "KRDD", "Tue, Thu, Sat"),  # Redding, CA
    (456, "KBLI", "KHLN", "Thu, Sun"),  # Helena, MT
    (458, "KBLI", "KGTF", "Mon, Fri"),  # Great Falls, MT
    (460, "KBLI", "KMRY", "Mon, Wed, Fri"),  # Monterey, CA
    (462, "KBLI", "PAGS", "Tue, Thu, Sat"),  # Gustavus, AK
    
    # ----------------------------------------------------
    # KMSY Bridge Spokes (500 Block - Gulf Coast Hub)
    # ----------------------------------------------------
    (500, "KMSY", "KELP", "Daily"),  # El Paso, TX
    (502, "KMSY", "KSGF", "Mon, Wed, Fri, Sun"),  # Springfield, MO
    (504, "KMSY", "KLIT", "Daily"),  # Little Rock, AR
    (506, "KMSY", "KPNS", "Daily"),  # Pensacola, FL
    (508, "KMSY", "KMOB", "Mon, Wed, Fri"),  # Mobile, AL
    (510, "KMSY", "KVPS", "Thu, Sun"),  # Eglin / Destin, FL
    (512, "KMSY", "KMAF", "Daily"),  # Midland / Odessa, TX
    (514, "KMSY", "KBTR", "Daily"),  # Baton Rouge, LA
    (516, "KMSY", "KGPT", "Daily"),  # Gulfport / Biloxi, MS
    (518, "KMSY", "KLFT", "Mon, Wed, Fri, Sun"),  # Lafayette, LA
    (520, "KMSY", "KMLU", "Tue, Thu, Sat"),  # Monroe, LA
    (522, "KMSY", "KHBG", "Mon, Fri"),  # Hattiesburg, MS
    (524, "KMSY", "KAEX", "Tue, Thu, Sat"),  # Alexandria, LA
    (526, "KMSY", "KLCH", "Mon, Wed, Fri"),  # Lake Charles, LA
    (528, "KMSY", "KTYR", "Mon, Wed, Fri, Sun"),  # Tyler, TX
    (530, "KMSY", "KAVL", "Thu, Sun"),  # Asheville, NC
    (532, "KMSY", "KTRI", "Tue, Thu, Sat"),  # Tri-Cities / Bristol, TN
    (534, "KMSY", "KCRP", "Daily"),  # Corpus Christi, TX
    (536, "KMSY", "KBPT", "Mon, Wed, Fri"),  # Beaumont / Port Arthur, TX
    (538, "KMSY", "KSHV", "Daily"),  # Shreveport, LA
    (540, "KMSY", "KECP", "Thu, Sun"),  # Panama City Beach, FL
    (542, "KMSY", "KMGM", "Tue, Thu, Sat"),  # Montgomery, AL
    (544, "KMSY", "KBHM", "Tue, Thu, Sat"),  # Birmingham, AL
    (546, "KMSY", "KPGD", "Tue, Thu, Sat"),  # Punta Gorda / Ft. Myers, FL
    (548, "KMSY", "KTYS", "Tue, Thu, Sat"),  # Knoxville, TN

    # ----------------------------------------------------
    # KOMA Bridge Spokes (600 Block - Midwest Hub)
    # ----------------------------------------------------
    (600, "KOMA", "KMLI", "Daily"),  # Moline / Quad Cities, IL
    (602, "KOMA", "KSGF", "Mon, Wed, Fri, Sun"),  # Springfield, MO
    (604, "KOMA", "KLIT", "Daily"),  # Little Rock, AR
    (606, "KOMA", "KFSD", "Daily"),  # Sioux Falls, SD
    (608, "KOMA", "KCID", "Daily"),  # Cedar Rapids, IA
    (610, "KOMA", "KPIA", "Mon, Wed, Fri"),  # Peoria, IL
    (612, "KOMA", "KDSM", "Daily"),  # Des Moines, IA
    (614, "KOMA", "KLNK", "Daily"),  # Lincoln, NE
    (616, "KOMA", "KICT", "Daily"),  # Wichita, KS
    (618, "KOMA", "KBIS", "Mon, Wed, Fri, Sun"),  # Bismarck, ND
    (620, "KOMA", "KFAR", "Mon, Wed, Fri, Sun"),  # Fargo, ND
    (622, "KOMA", "KGRI", "Tue, Thu, Sat"),  # Grand Island, NE
    (624, "KOMA", "KSUX", "Mon, Wed, Fri"),  # Sioux City, IA
    (626, "KOMA", "KCOU", "Tue, Thu, Sat"),  # Columbia, MO
    (628, "KOMA", "KALO", "Mon, Fri"),  # Waterloo, IA
    (630, "KOMA", "KELP", "Daily"),  # El Paso, TX
    (632, "KOMA", "KMAF", "Daily"),  # Midland / Odessa, TX
    (634, "KOMA", "KABQ", "Daily"),  # Albuquerque, NM
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
    (662, "KOMA", "KMKE", "Daily"),  # Milwaukee, WI
    (664, "KOMA", "KBMI", "Mon, Wed, Fri, Sun"),  # Bloomington / Normal, IL
    (666, "KOMA", "KDBQ", "Tue, Thu, Sat"),  # Dubuque, IA
    (668, "KOMA", "KRST", "Daily"),  # Rochester, MN
    (670, "KOMA", "KDLH", "Mon, Wed, Fri, Sun"),  # Duluth, MN
    (672, "KOMA", "KCRP", "Thu, Sun"),  # Corpus Christi, TX
    (674, "KOMA", "KSHV", "Mon, Fri"),  # Shreveport, LA
    (676, "KOMA", "KMQT", "Tue, Thu, Sat"),  # Marquette, MI
    (678, "KOMA", "KPLN", "Mon, Wed, Fri"),  # Pellston / Mackinac, MI
    (680, "KOMA", "KMGM", "Tue, Thu, Sat"),  # Montgomery, AL
    (682, "KOMA", "KBHM", "Tue, Thu, Sat"),  # Birmingham, AL
    
    # ----------------------------------------------------
    # KGRR Bridge Spokes (700 Block - Great Lakes Hub)
    # ----------------------------------------------------
    (700, "KGRR", "KMLI", "Daily"),  # Moline / Quad Cities, IL
    (702, "KGRR", "KPNS", "Thu, Sun"),  # Pensacola, FL
    (704, "KGRR", "KPIT", "Daily"),  # Pittsburgh, PA
    (706, "KGRR", "KCAK", "Mon, Wed, Fri, Sun"),  # Akron / Canton, OH
    (708, "KGRR", "KTVC", "Daily"),  # Traverse City, MI
    (710, "KGRR", "KHTS", "Tue, Thu, Sat"),  # Huntington, WV
    (712, "KGRR", "KCID", "Daily"),  # Cedar Rapids, IA
    (714, "KGRR", "KPIA", "Mon, Wed, Fri"),  # Peoria, IL
    (716, "KGRR", "KSBN", "Daily"),  # South Bend, IN
    (718, "KGRR", "KMKE", "Daily"),  # Milwaukee, WI
    (720, "KGRR", "KFWA", "Daily"),  # Fort Wayne, IN
    (722, "KGRR", "KLAN", "Daily"),  # Lansing, MI
    (724, "KGRR", "KAZO", "Daily"),  # Kalamazoo, MI
    (726, "KGRR", "KFNT", "Daily"),  # Flint, MI
    (728, "KGRR", "KTOL", "Mon, Wed, Fri, Sun"),  # Toledo, OH
    (730, "KGRR", "KMQT", "Mon, Wed, Fri, Sun"),  # Marquette, MI
    (732, "KGRR", "KPLN", "Daily"),  # Pellston / Mackinac, MI
    (734, "KGRR", "KERI", "Mon, Wed, Fri"),  # Erie, PA
    (736, "KGRR", "KBMI", "Thu, Sun"),  # Bloomington, IL
    (738, "KGRR", "KDBQ", "Mon, Fri"),  # Dubuque, IA
    (740, "KGRR", "KIPT", "Tue, Thu, Sat"),  # Williamsport, PA
    (742, "KGRR", "KTYS", "Tue, Thu, Sat"),  # Knoxville, TN

    # ----------------------------------------------------
    # International Flights (800 Block - Skybus Network)
    # ----------------------------------------------------
    (800, "TJBQ", "TNCM", "Mon, Wed, Fri, Sun"),  # St. Maarten
    (802, "TJBQ", "TKPK", "Tue, Thu, Sat"),  # St. Kitts
    (804, "TJBQ", "TFFR", "Tue, Thu, Sat"),  # Guadeloupe
    (806, "TJBQ", "TFFF", "Mon, Wed, Fri"),  # Martinique
    (808, "TJBQ", "TAPA", "Thu, Sun"),  # Antigua
    (810, "TJBQ", "TNCA", "Mon, Wed, Fri, Sun"),  # Aruba
    (812, "TJBQ", "TNCB", "Tue, Thu, Sat"),  # Bonaire
    (814, "TJBQ", "TNCC", "Mon, Wed, Fri, Sun"),  # Curaçao
    (816, "TJBQ", "TLPL", "Thu, Sun"),  # St. Lucia
    (818, "TJBQ", "TBPB", "Mon, Wed, Fri"),  # Barbados
    (820, "TJBQ", "TVSA", "Tue, Thu, Sat"),  # St. Vincent
    (822, "TJBQ", "MDPC", "Daily"),  # Punta Cana, Dominican Republic
    (824, "KSFB", "MDPC", "Daily"),  # Punta Cana, Dominican Republic
    (826, "KSFB", "MBPV", "Thu, Sun"),  # Providenciales, Turks & Caicos
    (828, "KSFB", "MKJS", "Daily"),  # Montego Bay, Jamaica
    (830, "KSFB", "MYNN", "Daily"),  # Nassau, Bahamas
    (832, "KSFB", "MROC", "Mon, Wed, Fri, Sun"),  # San José, Costa Rica
    (834, "PAFA", "CYXY", "Tue, Thu, Sat"),  # Whitehorse, YT, Canada
    (836, "PAFA", "CYVR", "Daily"),  # Vancouver, BC, Canada
    (838, "KBLI", "CYYJ", "Daily"),  # Victoria, BC, Canada
    (840, "KBLI", "CYYC", "Daily"),  # Calgary, AB, Canada
    (842, "KBLI", "MMSD", "Thu, Sun"),  # Los Cabos, Mexico
    (844, "KIWA", "MMSD", "Daily"),  # Los Cabos, Mexico
    (846, "KIWA", "MMPR", "Mon, Wed, Fri, Sun"),  # Puerto Vallarta, Mexico
    (848, "KIWA", "MMMZ", "Tue, Thu, Sat"),  # Mazatlán, Mexico
    (850, "KIWA", "MMGL", "Mon, Wed, Fri, Sun"),  # Guadalajara, Mexico
    (852, "KMSY", "MMUN", "Daily"),  # Cancún, Mexico
    (854, "KMSY", "MMCZ", "Thu, Sun"),  # Cozumel, Mexico
    (856, "KMSY", "MZBZ", "Mon, Wed, Fri"),  # Belize City, Belize
    (858, "KGRR", "CYHM", "Daily"),  # Hamilton / Toronto South, ON, Canada
    (860, "KGRR", "CYUL", "Daily"),  # Montréal, QC, Canada
    (862, "KGRR", "MMUN", "Mon, Wed, Fri, Sun"),  # Cancún, Mexico
    (864, "KBGR", "CYHZ", "Mon, Wed, Fri, Sun"),  # Halifax, NS, Canada
    (866, "KBGR", "BIKF", "Thu, Sun"),  # Reykjavik / Keflavik, Iceland
    (868, "KBGR", "EINN", "Mon, Wed, Fri"),  # Shannon, Ireland
    (870, "KSWF", "CYUL", "Daily"),  # Montréal, QC, Canada
    (872, "KSWF", "BIKF", "Mon, Wed, Fri, Sun"),  # Reykjavik / Keflavik, Iceland
    (874, "KSWF", "EINN", "Thu, Sun"),  # Shannon, Ireland
    (876, "KSWF", "EIDW", "Daily"),  # Dublin, Ireland
    (878, "KBGR", "EIDW", "Mon, Wed, Fri, Sun"),  # Dublin, Ireland
    (880, "KMSY", "MGGT", "Thu, Sun"),  # Guatemala City, Guatemala
    (882, "KIWA", "MRLB", "Thu, Sun"),  # Liberia / Guanacaste, Costa Rica
    (884, "KBLI", "MMPR", "Mon, Wed, Fri"),  # Puerto Vallarta, Mexico
    (886, "KGRR", "MDPC", "Thu, Sun"),  # Punta Cana, Dominican Republic
    (888, "KSFB", "SKCG", "Mon, Fri"),  # Cartagena, Colombia
    (890, "PAFA", "CYEG", "Tue, Thu, Sat"),  # Edmonton, AB, Canada
    
    # ----------------------------------------------------
    # TJBQ Caribbean Regional Spokes (1500 Block - Caribbean Hub)
    # ----------------------------------------------------
    (1500, "TJBQ", "TJPS", "Daily"),  # Ponce, PR
    (1502, "TJBQ", "TIST", "Daily"),  # St. Thomas, USVI
    (1504, "TJBQ", "TISX", "Tue, Thu, Sat"),  # St. Croix, USVI
    (1506, "TJBQ", "TJSJ", "Daily"),  # San Juan, PR
    (1508, "TJBQ", "KMYR", "Thu, Sun"),  # Myrtle Beach, SC
    (1510, "TJBQ", "KILM", "Mon, Fri"),  # Wilmington, NC
    (1512, "TJBQ", "KPVD", "Mon, Wed, Fri, Sun"),  # Providence, RI
    (1514, "TJBQ", "KABE", "Tue, Thu, Sat"),  # Allentown / Lehigh Valley, PA
    (1516, "TJBQ", "KPIT", "Mon, Wed, Fri, Sun"),  # Pittsburgh, PA
    (1518, "TJBQ", "KPNS", "Thu, Sun"),  # Pensacola, FL

    # ----------------------------------------------------
    # KSWF Bridge Spokes (900 Block - Northeast / Hudson Valley Hub)
    # ----------------------------------------------------
    (900, "KSWF", "KABE", "Daily"),  # Allentown, PA
    (902, "KSWF", "KMDT", "Daily"),  # Harrisburg, PA
    (904, "KSWF", "KPWM", "Daily"),  # Portland, ME
    (906, "KSWF", "KCAK", "Mon, Wed, Fri, Sun"),  # Akron / Canton, OH
    (908, "KSWF", "KPVD", "Daily"),  # Providence, RI
    (910, "KSWF", "KCRW", "Tue, Thu, Sat"),  # Charleston, WV
    (912, "KSWF", "KBTV", "Daily"),  # Burlington, VT
    (914, "KSWF", "KORH", "Mon, Wed, Fri"),  # Worcester, MA
    (916, "KSWF", "KSYR", "Daily"),  # Syracuse, NY
    (918, "KSWF", "KBGM", "Mon, Fri"),  # Binghamton, NY
    (920, "KSWF", "KITH", "Tue, Thu, Sat"),  # Ithaca, NY
    (922, "KSWF", "KART", "Mon, Wed, Fri"),  # Watertown, NY
    (924, "KSWF", "KAVP", "Daily"),  # Wilkes-Barre / Scranton, PA
    (926, "KSWF", "KELM", "Tue, Thu, Sat"),  # Elmira / Corning, NY
    (928, "KSWF", "KHVN", "Daily"),  # New Haven, CT
    (930, "KSWF", "KMHT", "Daily"),  # Manchester, NH
    (932, "KSWF", "KACK", "Thu, Sun"),  # Nantucket, MA
    (934, "KSWF", "KMVY", "Thu, Sun"),  # Martha's Vineyard, MA
    (936, "KSWF", "KLEB", "Mon, Wed, Fri"),  # Lebanon, NH
    (938, "KSWF", "KPBG", "Tue, Thu, Sat"),  # Plattsburgh, NY
    (940, "KSWF", "KSLK", "Mon, Fri"),  # Saranac Lake, NY
    (942, "KSWF", "KFMH", "Thu, Sun"),  # Falmouth / Cape Cod, MA
    (944, "KSWF", "KIPT", "Mon, Wed, Fri, Sun"),  # Williamsport, PA
    (946, "KSWF", "KALB", "Daily"),  # Albany, NY
    (948, "KSWF", "KERI", "Thu, Sun"),  # Erie, PA
    (950, "KSWF", "KCHO", "Tue, Thu, Sat"),  # Charlottesville, VA
    (952, "KSWF", "KMQT", "Tue, Thu, Sat"),  # Marquette, MI
    (954, "KSWF", "KPLN", "Mon, Wed, Fri"),  # Pellston / Mackinac, MI
    (956, "KSWF", "KGSO", "Tue, Thu, Sat"),  # Greensboro, NC
    (958, "KSWF", "KJQF", "Tue, Thu, Sat"),  # Concord / Charlotte, NC
    (960, "KSWF", "KPGV", "Tue, Thu, Sat"),  # Greenville, NC
    (962, "KSWF", "KTYS", "Tue, Thu, Sat"),  # Knoxville, TN

    # ----------------------------------------------------
    # KBGR Bridge Spokes (1000 Block - Northern New England Hub)
    # ----------------------------------------------------
    (1000, "KBGR", "KPWM", "Daily"),  # Portland, ME
    (1002, "KBGR", "KMHT", "Daily"),  # Manchester, NH
    (1004, "KBGR", "KPVD", "Daily"),  # Providence, RI
    (1006, "KBGR", "KBTV", "Daily"),  # Burlington, VT
    (1008, "KBGR", "KACK", "Thu, Sun"),  # Nantucket, MA
    (1010, "KBGR", "KMVY", "Thu, Sun"),  # Martha's Vineyard, MA
    (1012, "KBGR", "KPQB", "Mon, Wed, Fri"),  # Presque Isle, ME
    (1014, "KBGR", "KORH", "Tue, Thu, Sat"),  # Worcester, MA
    (1016, "KBGR", "KHVN", "Daily"),  # New Haven, CT
    (1018, "KBGR", "KRKD", "Mon, Fri"),  # Rockland, ME
    (1020, "KBGR", "KBHB", "Mon, Wed, Fri, Sun"),  # Bar Harbor, ME
    (1022, "KBGR", "KLEB", "Tue, Thu, Sat"),  # Lebanon, NH
    (1024, "KBGR", "KPBG", "Mon, Wed, Fri"),  # Plattsburgh, NY
    (1026, "KBGR", "KSLK", "Mon, Fri"),  # Saranac Lake, NY
    (1028, "KBGR", "KFMH", "Thu, Sun"),  # Falmouth / Cape Cod, MA
    (1030, "KBGR", "KALB", "Mon, Wed, Fri"),  Albany, NY
    (1032, "KBGR", "KSYR", "Daily"),  # Syracuse, NY
    (1034, "KBGR", "KERI", "Mon, Wed, Fri"),  # Erie, PA
    (1036, "KBGR", "KMQT", "Tue, Thu, Sat"),  # Marquette, MI
    (1038, "KBGR", "KPLN", "Mon, Wed, Fri"),  # Pellston / Mackinac, MI

    # ----------------------------------------------------
    # KRIC Bridge Spokes (1100 Block - Mid-Atlantic Hub)
    # ----------------------------------------------------
    (1100, "KRIC", "KCHS", "Daily"),  # Charleston, SC
    (1102, "KRIC", "KILM", "Daily"),  # Wilmington, NC
    (1104, "KRIC", "KABE", "Daily"),  # Allentown, PA
    (1106, "KRIC", "KMDT", "Daily"),  # Harrisburg, PA
    (1108, "KRIC", "KPIT", "Daily"),  # Pittsburgh, PA
    (1110, "KRIC", "KROA", "Mon, Wed, Fri"),  # Roanoke, VA
    (1112, "KRIC", "KHTS", "Tue, Thu, Sat"),  # Huntington, WV
    (1114, "KRIC", "KCRW", "Tue, Thu, Sat"),  # Charleston, WV
    (1116, "KRIC", "KSAV", "Daily"),  # Savannah, GA
    (1118, "KRIC", "KAVL", "Mon, Wed, Fri, Sun"),  # Asheville, NC
    (1120, "KRIC", "KTRI", "Tue, Thu, Sat"),  # Tri-Cities / Bristol, TN
    (1122, "KRIC", "KEWN", "Mon, Fri"),  # New Bern, NC
    (1124, "KRIC", "KFAY", "Mon, Wed, Fri"),  # Fayetteville, NC
    (1126, "KRIC", "KPHF", "Daily"),  # Newport News / Williamsburg, VA
    (1128, "KRIC", "KLYH", "Tue, Thu, Sat"),  # Lynchburg, VA
    (1130, "KRIC", "KSBN", "Mon, Wed, Fri"),  # South Bend, IN
    (1132, "KRIC", "KFWA", "Tue, Thu, Sat"),  # Fort Wayne, IN
    (1134, "KRIC", "KTOL", "Mon, Fri"),  # Toledo, OH
    (1136, "KRIC", "KBQK", "Thu, Sun"),  # Brunswick, GA
    (1138, "KRIC", "KMYR", "Daily"),  # Myrtle Beach, SC
    (1140, "KRIC", "KCHO", "Daily"),  # Charlottesville, VA
    (1142, "KRIC", "KIPT", "Thu, Sun"),  # Williamsport, PA
    (1144, "KRIC", "KMLB", "Mon, Wed, Fri"), # Melbourne, FL
    (1146, "KRIC", "KECP", "Tue, Thu, Sat"),  # Panama City Beach, FL
    (1148, "KRIC", "KALB", "Mon, Wed, Fri"),  Albany, NY
    (1150, "KRIC", "KERI", "Mon, Wed, Fri"),  # Erie, PA
    (1152, "KRIC", "KGSO", "Tue, Thu, Sat"),  # Greensboro, NC
    (1154, "KRIC", "KJQF", "Tue, Thu, Sat"),  # Concord / Charlotte, NC
    (1156, "KRIC", "KPGV", "Tue, Thu, Sat"),  # Greenville, NC
    (1158, "KRIC", "KMGM", "Tue, Thu, Sat"),  # Montgomery, AL
    (1160, "KRIC", "KBHM", "Tue, Thu, Sat"),  # Birmingham, AL
    (1162, "KRIC", "KPGD", "Tue, Thu, Sat"),  # Punta Gorda / Ft. Myers, FL
    (1164, "KRIC", "KTYS", "Tue, Thu, Sat"),  # Knoxville, TN

    # ----------------------------------------------------
    # KSFB Bridge Spokes (1200 Block - Florida / Southeast Hub)
    # ----------------------------------------------------
    (1200, "KSFB", "KCHS", "Daily"),  # Charleston, SC
    (1202, "KSFB", "KILM", "Daily"),  # Wilmington, NC
    (1204, "KSFB", "KPNS", "Daily"),  # Pensacola, FL
    (1206, "KSFB", "KEYW", "Daily"),  # Key West, FL
    (1208, "KSFB", "KSAV", "Daily"),  # Savannah, GA
    (1210, "KSFB", "KMOB", "Mon, Wed, Fri, Sun"),  # Mobile, AL
    (1212, "KSFB", "KVPS", "Thu, Sun"),  # Eglin / Destin, FL
    (1214, "KSFB", "KTLH", "Daily"),  # Tallahassee, FL
    (1216, "KSFB", "KMYR", "Daily"),  # Myrtle Beach, SC
    (1218, "KSFB", "KGPT", "Mon, Wed, Fri, Sun"),  # Gulfport / Biloxi, MS
    (1220, "KSFB", "KBQK", "Thu, Sun"),  # Brunswick, GA
    (1222, "KSFB", "KGNV", "Daily"),  # Gainesville, FL
    (1224, "KSFB", "KVRB", "Mon, Wed, Fri"),  # Vero Beach, FL
    (1226, "KSFB", "KAVL", "Mon, Wed, Fri, Sun"),  # Asheville, NC
    (1228, "KSFB", "KTRI", "Tue, Thu, Sat"),  # Tri-Cities / Bristol, TN
    (1230, "KSFB", "KEWN", "Mon, Fri"),  # New Bern, NC
    (1232, "KSFB", "KFAY", "Mon, Wed, Fri"),  # Fayetteville, NC
    (1234, "KSFB", "KPHF", "Daily"),  # Newport News / Williamsburg, VA
    (1236, "KSFB", "KLYH", "Tue, Thu, Sat"),  # Lynchburg, VA
    (1238, "KSFB", "KMLB", "Daily"),  # Melbourne, FL
    (1240, "KSFB", "KECP", "Daily"),  # Panama City Beach, FL
    (1242, "KSFB", "KCHO", "Thu, Sun"),  # Charlottesville, VA
    (1244, "KSFB", "KGSO", "Tue, Thu, Sat"),  # Greensboro, NC
    (1246, "KSFB", "KJQF", "Tue, Thu, Sat"),  # Concord / Charlotte, NC
    (1248, "KSFB", "KPGV", "Tue, Thu, Sat"),  # Greenville, NC
    (1250, "KSFB", "KMGM", "Tue, Thu, Sat"),  # Montgomery, AL
    (1252, "KSFB", "KBHM", "Tue, Thu, Sat"),  # Birmingham, AL
    (1254, "KSFB", "KPGD", "Tue, Thu, Sat"),  # Punta Gorda / Ft. Myers, FL
    (1256, "KSFB", "KTYS", "Tue, Thu, Sat"),  # Knoxville, TN
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

    # Alaska/Hawaii Spokes
    "PAJN": "Juneau, AK",
    "PAKT": "Ketchikan, AK",
    "PABR": "Utqiaġvik (Barrow), AK",
    "PAOT": "Kotzebue, AK",
    "PASC": "Deadhorse / Prudhoe Bay, AK",
    "PADQ": "Kodiak, AK",
    "PAOM": "Nome, AK",
    "PAPG": "Petersburg, AK",
    "PASI": "Sitka, AK",
    "PAYA": "Yakutat, AK",
    "PAVD": "Valdez, AK",
    "PAEN": "Kenai, AK",
    "PAKW": "Wrangell, AK",
    "PAHO": "Homer, AK",
    "PAGS": "Gustavus, AK",
    "PADL": "Dillingham, AK",
    "PAKN": "King Salmon, AK",
    "PHNL": "Honolulu, HI",
    "PHOG": "Kahului, HI (Maui)",
    "PHKO": "Kona, HI",
    "PHLI": "Lihue, HI",

    # Intermountain West Spokes
    "KBOI": "Boise, ID",
    "KSGU": "St. George, UT",
    "KIFP": "Bullhead City / Laughlin, AZ",
    "KJAC": "Jackson Hole, WY",
    "KGEG": "Spokane, WA",
    "KEUG": "Eugene, OR",
    "KFLG": "Flagstaff, AZ",
    "KCPR": "Casper, WY",
    "KGJT": "Grand Junction, CO",
    "KIDA": "Idaho Falls, ID",
    "KBZN": "Bozeman, MT",
    "KMSO": "Missoula, MT",
    "KTWF": "Twin Falls, ID",
    "KPIH": "Pocatello, ID",
    "KRNO": "Reno / Tahoe, NV",
    "KHLN": "Helena, MT",
    "KGTF": "Great Falls, MT",
    "KVEL": "Vernal, UT",
    "KCDC": "Cedar City, UT",

    # Southwest Spokes
    "KELP": "El Paso, TX",
    "KCLD": "Carlsbad / San Diego North, CA",
    "KMAF": "Midland / Odessa, TX",
    "KABQ": "Albuquerque, NM",
    "KTUS": "Tucson, AZ",
    "KPSP": "Palm Springs, CA",
    "KROW": "Roswell, NM",
    "KPRC": "Prescott, AZ",
    "KDRO": "Durango, CO",
    "KEKO": "Elko, NV",
    "KSBP": "San Luis Obispo, CA",

    # Pacific Northwest Spokes
    "KYKM": "Yakima, WA",
    "KPSC": "Pasco / Tri-Cities, WA",
    "KMFR": "Medford / Rogue Valley, OR",
    "KRDM": "Bend / Redmond, OR",
    "KOTH": "North Bend / Coos Bay, OR",
    "KALW": "Walla Walla, WA",
    "KEAT": "Wenatchee, WA",
    "KLWS": "Lewiston, ID",
    "KCLM": "Port Angeles, WA",
    "KACV": "Arcata / Eureka, CA",
    "KRDD": "Redding, CA",
    "KMRY": "Monterey, CA",
    "KSBA": "Santa Barbara, CA",
    "KFAT": "Fresno, CA",
    "KBFL": "Bakersfield, CA",

    # Gulf Coast Spokes
    "KSGF": "Springfield, MO",
    "KLIT": "Little Rock, AR",
    "KPNS": "Pensacola, FL",
    "KMOB": "Mobile, AL",
    "KVPS": "Eglin / Destin, FL",
    "KBTR": "Baton Rouge, LA",
    "KGPT": "Gulfport / Biloxi, MS",
    "KLFT": "Lafayette, LA",
    "KMLU": "Monroe, LA",
    "KHBG": "Hattiesburg, MS",
    "KAEX": "Alexandria, LA",
    "KLCH": "Lake Charles, LA",
    "KTYR": "Tyler, TX",
    "KCRP": "Corpus Christi, TX",
    "KSHV": "Shreveport, LA",
    "KBPT": "Beaumont / Port Arthur, TX",
    "KMGM": "Montgomery, AL",
    "KBHM": "Birmingham, AL",

    # Midwest Spokes
    "KMLI": "Moline / Quad Cities, IL",
    "KFSD": "Sioux Falls, SD",
    "KCID": "Cedar Rapids, IA",
    "KPIA": "Peoria, IL",
    "KDSM": "Des Moines, IA",
    "KLNK": "Lincoln, NE",
    "KICT": "Wichita, KS",
    "KBIS": "Bismarck, ND",
    "KFAR": "Fargo, ND",
    "KGRI": "Grand Island, NE",
    "KSUX": "Sioux City, IA",
    "KCOU": "Columbia, MO",
    "KALO": "Waterloo, IA",

    # Great Lakes Spokes
    "KPIT": "Pittsburgh, PA",
    "KCAK": "Akron / Canton, OH",
    "KTVC": "Traverse City, MI",
    "KHTS": "Huntington, WV",
    "KSBN": "South Bend, IN",
    "KMKE": "Milwaukee, WI",
    "KFWA": "Fort Wayne, IN",
    "KLAN": "Lansing, MI",
    "KAZO": "Kalamazoo, MI",
    "KFNT": "Flint, MI",
    "KTOL": "Toledo, OH",
    "KMQT": "Marquette, MI",
    "KPLN": "Pellston / Mackinac, MI",
    "KBMI": "Bloomington, IL",
    "KDBQ": "Dubuque, IA",
    "KRST": "Rochester, MN",
    "KDLH": "Duluth, MN",

    # Northeast / Hudson Valley Spokes
    "KABE": "Allentown / Lehigh Valley, PA",
    "KMDT": "Harrisburg, PA",
    "KPWM": "Portland, ME",
    "KCRW": "Charleston, WV",
    "KBTV": "Burlington, VT",
    "KORH": "Worcester, MA",
    "KSYR": "Syracuse, NY",
    "KBGM": "Binghamton, NY",
    "KITH": "Ithaca, NY",
    "KART": "Watertown, NY",
    "KAVP": "Wilkes-Barre / Scranton, PA",
    "KELM": "Elmira / Corning, NY",
    "KHVN": "New Haven, CT",
    "KIPT": "Williamsport, PA",
    "KALB": "Albany, NY",
    "KERI": "Erie, PA",

    # Northern New England Spokes
    "KMHT": "Manchester, NH",
    "KPVD": "Providence, RI",
    "KACK": "Nantucket, MA",
    "KMVY": "Martha's Vineyard, MA",
    "KPQB": "Presque Isle, ME",
    "KRKD": "Rockland, ME",
    "KBHB": "Bar Harbor, ME",
    "KLEB": "Lebanon, NH",
    "KPBG": "Plattsburgh, NY",
    "KSLK": "Saranac Lake, NY",
    "KFMH": "Falmouth / Cape Cod, MA",

    # Mid-Atlantic Spokes
    "KCHS": "Charleston, SC",
    "KILM": "Wilmington, NC",
    "KROA": "Roanoke, VA",
    "KSAV": "Savannah, GA",
    "KAVL": "Asheville, NC",
    "KTRI": "Tri-Cities / Bristol, TN",
    "KEWN": "New Bern, NC",
    "KFAY": "Fayetteville, NC",
    "KPHF": "Newport News / Williamsburg, VA",
    "KLYH": "Lynchburg, VA",
    "KCHO": "Charlottesville, VA",
    "KGSO": "Greensboro, NC",
    "KJQF": "Concord / Charlotte, NC",
    "KPGV": "Greenville, NC",

    # Florida Spokes
    "KEYW": "Key West, FL",
    "KTLH": "Tallahassee, FL",
    "KMYR": "Myrtle Beach, SC",
    "KBQK": "Brunswick, GA",
    "KGNV": "Gainesville, FL",
    "KVRB": "Vero Beach, FL",
    "KMLB": "Melbourne, FL",
    "KECP": "Panama City Beach, FL",
    "KPGD": "Punta Gorda / Ft. Myers, FL",

    # Caribbean Spokes
    "TJPS": "Ponce, PR",
    "TIST": "St. Thomas, USVI",
    "TISX": "St. Croix, USVI",
    "TJSJ": "San Juan, PR",

    # International
    "TNCM": "St. Maarten",
    "TKPK": "St. Kitts",
    "TFFR": "Guadeloupe",
    "TFFF": "Martinique",
    "TAPA": "Antigua",
    "TNCA": "Aruba",
    "TNCB": "Bonaire",
    "TNCC": "Curaçao",
    "TLPL": "St. Lucia",
    "TBPB": "Barbados",
    "TVSA": "St. Vincent",
    "MDPC": "Punta Cana, Dominican Republic",
    "MBPV": "Providenciales, Turks & Caicos",
    "MKJS": "Montego Bay, Jamaica",
    "MYNN": "Nassau, Bahamas",
    "MROC": "San José, Costa Rica",
    "CYXY": "Whitehorse, YT, Canada",
    "CYVR": "Vancouver, BC, Canada",
    "CYYJ": "Victoria, BC, Canada",
    "CYYC": "Calgary, AB, Canada",
    "MMSD": "Los Cabos, Mexico",
    "MMPR": "Puerto Vallarta, Mexico",
    "MMMZ": "Mazatlán, Mexico",
    "MMGL": "Guadalajara, Mexico",
    "MMUN": "Cancún, Mexico",
    "MMCZ": "Cozumel, Mexico",
    "MZBZ": "Belize City, Belize",
    "CYHM": "Hamilton / Toronto South, ON, Canada",
    "CYUL": "Montréal, QC, Canada",
    "CYHZ": "Halifax, NS, Canada",
    "BIKF": "Reykjavik / Keflavik, Iceland",
    "EINN": "Shannon, Ireland",
    "EIDW": "Dublin, Ireland",
    "MGGT": "Guatemala City, Guatemala",
    "MRLB": "Liberia / Guanacaste, Costa Rica",
    "SKCG": "Cartagena, Colombia",
    "CYEG": "Edmonton, AB, Canada",
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
    # ALASKA SPOKES (PAFA Block)
    # --------------------------------------------------------------------------
    "PAJN": (58.3594, -134.5762),  # Juneau International, AK
    "PAKT": (55.3556, -131.7137),  # Ketchikan International, AK
    "PABR": (71.2854, -156.7660),  # Utqiaġvik (Barrow / Wiley Post-Will Rogers), AK
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
    "PADL": (59.0454, -158.5033), # Dillingham Airport, AK
    "PAKN": (58.6768, -156.6492), # King Salmon Airport, AK

    # --------------------------------------------------------------------------
    # HAWAII SPOKES
    # --------------------------------------------------------------------------
    "PHNL": (21.3187, -157.9224),  # Daniel K. Inouye Intl (Honolulu), HI
    "PHOG":  (20.8986, -156.4305),  # Kahului Airport (Maui), HI
    "PHKO":  (19.7388, -155.9874),  # Ellison Onizuka Kona Intl, HI
    "PHLI":  (21.9760, -159.3390),  # Lihue Airport (Kauai), HI

    # --------------------------------------------------------------------------
    # INTERMOUNTAIN & PACIFIC NORTHWEST SPOKES (KPVU & KBLI Blocks)
    # --------------------------------------------------------------------------
    "KBOI": (43.5644, -116.2228),  # Boise Air Terminal, ID
    "KSGU": (37.0364, -113.5103),  # St. George Regional, UT
    "KIFP": (35.1561, -114.5595),  # Laughlin/Bullhead International, AZ
    "KJAC": (43.6073, -110.7377),  # Jackson Hole Airport, WY
    "KGEG": (47.6199, -117.5338),  # Spokane International, WA
    "KEUG": (44.1238, -123.2186),  # Eugene Airport (Mahlon Sweet Field), OR
    "KFLG": (35.1384, -111.6713),  # Flagstaff Pulliam, AZ
    "KCPR": (42.9080, -106.4644),  # Casper/Natrona County Intl, WY
    "KGJT": (39.1224, -108.5267),  # Grand Junction Regional, CO
    "KIDA": (43.5146, -112.0702),  # Idaho Falls Regional, ID
    "KBZN": (45.7775, -111.1530),  # Bozeman Yellowstone Intl, MT
    "KMSO": (46.9163, -114.0917),  # Missoula Montana Airport, MT
    "KTWF": (42.4818, -114.4877),  # Magic Valley Regional (Twin Falls), ID
    "KPIH": (42.9113, -112.5959),  # Pocatello Regional, ID
    "KRNO": (39.4991, -119.7681),  # Reno/Tahoe International, NV
    "KYKM": (46.5682, -120.5441),  # Yakima Air Terminal, WA
    "KPSC": (46.2647, -119.1190),  # Tri-Cities Airport (Pasco), WA
    "KMFR": (42.3742, -122.8735),  # Rogue Valley Intl-Medford, OR
    "KRDM": (44.2541, -121.1500),  # Roberts Field (Redmond/Bend), OR
    "KOTH": (43.4171, -124.2460),  # Southwest Oregon Regional (North Bend), OR
    "KALW": (46.0944, -118.2881),  # Walla Walla Regional, WA
    "KEAT": (47.3999, -120.2068),  # Pangborn Memorial (Wenatchee), WA
    "KLWS": (46.3745, -117.0156),  # Lewiston-Nez Perce County, ID
    "KCLM": (48.1202, -123.4997),  # William R. Fairchild (Port Angeles), WA
    "KCDC": (37.7009, -113.0988), # Cedar City Regional Airport, UT
    "KVEL": (40.4409, -109.5099), # Vernal Regional Airport, UT

    # --------------------------------------------------------------------------
    # SOUTHWEST SPOKES (KIWA Block)
    # --------------------------------------------------------------------------
    "KELP": (31.8066, -106.3778),  # El Paso International, TX
    "KCLD": (33.1272, -117.2787),  # McClellan-Palomar (Carlsbad), CA
    "KMAF": (31.9425, -102.2019),  # Midland International, TX
    "KABQ": (35.0402, -106.6091),  # Albuquerque International Sunport, NM
    "KTUS": (32.1161, -110.9410),  # Tucson International, AZ
    "KPSP": (33.8297, -116.5067),  # Palm Springs International, CA
    "KROW": (33.3015, -104.5306),  # Roswell Air Center, NM
    "KPRC": (34.6544, -112.4196),  # Prescott Regional (Ernest A. Love Field), AZ
    "KDRO": (37.1515, -107.7538),  # Durango-La Plata County, CO
    "KEKO": (40.8249, -115.7917),  # Elko Regional, NV
    "KSBP": (35.2371, -120.6424),  # San Luis Obispo County Regional, CA
    "KFLT": (34.8486, -111.7886),  # Sedona / Flagstaff Region, AZ
    "KBFL": (35.4336, -119.0567), # Meadows Field Airport (Bakersfield), CA
    "KFAT": (36.7762, -119.7181), # Fresno Yosemite International Airport, CA
    "KSBA": (34.4262, -119.8403), # Santa Barbara Municipal Airport, CA

    # --------------------------------------------------------------------------
    # GULF COAST & MIDWEST SPOKES (KMSY & KOMA Blocks)
    # --------------------------------------------------------------------------
    "KSGF": (37.2457, -93.3886),   # Springfield-Branson National, MO
    "KLIT": (34.7294, -92.2243),   # Bill and Hillary Clinton National (Little Rock), AR
    "KPNS": (30.4734, -87.1866),   # Pensacola International, FL
    "KMOB": (30.6914, -88.2428),   # Mobile Regional, AL
    "KVPS": (30.4832, -86.5254),   # Destin-Fort Walton Beach / Eglin AFB, FL
    "KBTR": (30.5332, -91.1496),   # Baton Rouge Metropolitan, LA
    "KGPT": (30.4073, -89.0701),   # Gulfport-Biloxi International, MS
    "KLFT": (30.2053, -91.9876),   # Lafayette Regional, LA
    "KMLU": (32.5109, -92.0376),   # Monroe Regional, LA
    "KHBG": (31.2829, -89.2530),   # Hattiesburg-Laurel Regional, MS
    "KAEX": (31.3274, -92.5498),   # Alexandria International, LA
    "KLCH": (30.1261, -93.2233),   # Lake Charles Regional, LA
    "KTYR": (32.3541, -95.4024),   # Tyler Pounds Regional, TX
    "KMLI": (41.4485, -90.5075),   # Quad Cities International (Moline), IL
    "KFSD": (43.5820, -96.7418),   # Sioux Falls Regional, SD
    "KCID": (41.8847, -91.7108),   # The Eastern Iowa Airport (Cedar Rapids), IA
    "KPIA": (40.6642, -89.6933),   # General Wayne A. Downing Peoria Intl, IL
    "KDSM": (41.5340, -93.6631),   # Des Moines International, IA
    "KLNK": (40.8510, -96.7592),   # Lincoln Airport, NE
    "KICT": (37.6499, -97.4331),   # Wichita Dwight D. Eisenhower National, KS
    "KBIS": (46.7727, -100.7460),  # Bismarck Municipal, ND
    "KFAR": (46.9197, -96.8157),   # Hector International (Fargo), ND
    "KGRI": (40.9675, -98.3096),   # Central Nebraska Regional (Grand Island), NE
    "KSUX": (42.4026, -96.3844),   # Sioux Gateway Airport, IA
    "KCOU": (38.8181, -92.2196),   # Columbia Regional, MO
    "KALO": (42.5571, -92.4003),   # Waterloo Regional, IA
    "KMGM": (32.3006, -86.3940),  # Montgomery Regional Airport, AL
    "KBHM": (33.5629, -86.7535),  # Birmingham-Shuttlesworth International Airport, AL
    "KBMI": (40.4771, -88.9159),  # Central Illinois Regional Airport (Bloomington), IL
    "KDBQ": (42.4020, -90.7095),  # Dubuque Regional Airport, IA
    "KCRP": (27.7704, -97.5012),  # Corpus Christi International Airport, TX
    "KSHV": (32.4466, -93.8256),  # Shreveport Regional Airport, LA
    "KBPT": (29.9508, -94.0207),  # Jack Brooks Regional Airport (Beaumont), TX

    # --------------------------------------------------------------------------
    # GREAT LAKES SPOKES (KGRR Block)
    # --------------------------------------------------------------------------
    "KPIT": (40.4915, -80.2329),   # Pittsburgh International, PA
    "KCAK": (40.9161, -81.4422),   # Akron-Canton Airport, OH
    "KTVC": (44.7414, -85.5822),   # Cherry Capital Airport (Traverse City), MI
    "KHTS": (38.3667, -82.5580),   # Tri-State Airport (Huntington), WV
    "KSBN": (41.7086, -86.3173),   # South Bend International, IN
    "KMKE": (42.9472, -87.8966),   # Milwaukee Mitchell International, WI
    "KFWA": (40.9785, -85.1951),   # Fort Wayne International, IN
    "KLAN": (42.7787, -84.5874),   # Capital Region Intl (Lansing), MI
    "KAZO": (42.2349, -85.5521),   # Kalamazoo/Battle Creek Intl, MI
    "KFNT": (42.9654, -83.7436),   # Bishop International (Flint), MI
    "KTOL": (41.5868, -83.8078),   # Toledo Express Airport, OH
    "KMQT": (46.3536, -87.3953),  # Sawyer International Airport (Marquette), MI
    "KPLN": (45.5708, -84.7967),  # Pellston Regional Airport, MI
    "KERI": (42.0820, -80.1762),  # Erie International Airport, PA
    "KRST": (43.9083, -92.4980),  # Rochester International Airport, MN
    "KDLH": (46.8421, -92.1936),  # Duluth International Airport, MN

    # --------------------------------------------------------------------------
    # NORTHEAST & NORTHERN NEW ENGLAND SPOKES (KSWF & KBGR Blocks)
    # --------------------------------------------------------------------------
    "KABE": (40.6521, -75.4408),   # Lehigh Valley International (Allentown), PA
    "KMDT": (40.1935, -76.7634),   # Harrisburg International, PA
    "KPWM": (43.6462, -70.3088),   # Portland International Jetport, ME
    "KPVD": (41.7240, -71.4282),   # Rhode Island T.F. Green Intl (Providence), RI
    "KCRW": (38.3731, -81.5932),   # West Virginia International Yeager (Charleston), WV
    "KBTV": (44.4730, -73.1533),   # Patrick Leahy Burlington International, VT
    "KORH": (42.2673, -71.8757),   # Worcester Regional, MA
    "KSYR": (43.1112, -76.1063),   # Syracuse Hancock International, NY
    "KBGM": (42.2086, -75.9797),   # Greater Binghamton Airport, NY
    "KITH": (42.4913, -76.4585),   # Tompkins Cortland Community (Ithaca), NY
    "KART": (44.0022, -75.7217),   # Watertown International, NY
    "KAVP": (41.3385, -75.7234),   # Wilkes-Barre/Scranton International, PA
    "KELM": (42.1599, -76.8914),   # Elmira/Corning Regional, NY
    "KHVN": (41.2638, -72.8868),   # Tweed-New Haven Airport, CT
    "KMHT": (42.9326, -71.4357),   # Manchester-Boston Regional, NH
    "KACK": (41.2531, -70.0602),   # Nantucket Memorial, MA
    "KMVY": (41.3931, -70.6143),   # Martha's Vineyard Airport, MA
    "KPQB": (46.6889, -68.0448),   # Presque Isle International, ME
    "KRKD": (44.0601, -69.0992),   # Knox County Regional (Rockland), ME
    "KBHB": (44.4498, -68.3616),   # Hancock County-Bar Harbor, ME
    "KLEB": (43.6261, -72.3042),   # Lebanon Municipal, NH
    "KPBG": (44.6509, -73.4681),   # Plattsburgh International, NY
    "KSLK": (44.3853, -74.2062),   # Adirondack Regional (Saranac Lake), NY
    "KFMH": (41.6585, -70.5215),   # Cape Cod Coast Guard Air Station / Falmouth, MA
    "KIPT": (41.2419, -76.9211),  # Williamsport Regional Airport, PA
    "KALB": (42.7483, -73.8017),  # Albany International Airport, NY

    # --------------------------------------------------------------------------
    # MID-ATLANTIC & SOUTHEAST SPOKES (KRIC & KSFB Blocks)
    # --------------------------------------------------------------------------
    "KCHS": (32.8986, -80.0405),   # Charleston International, SC
    "KILM": (34.2706, -77.9026),   # Wilmington International, NC
    "KROA": (37.3255, -79.9754),   # Roanoke-Blacksburg Regional, VA
    "KSAV": (32.1276, -81.2021),   # Savannah/Hilton Head International, GA
    "KAVL": (35.4362, -82.5418),   # Asheville Regional, NC
    "KTRI": (36.4752, -82.4074),   # Tri-Cities Airport (Blountville), TN
    "KEWN": (35.0730, -77.0429),   # Coastal Carolina Regional (New Bern), NC
    "KFAY": (34.9912, -78.8803),   # Fayetteville Regional, NC
    "KPHF": (37.1319, -76.4930),   # Newport News/Williamsburg Intl, VA
    "KLYH": (37.3267, -79.2004),   # Lynchburg Regional, VA
    "KEYW": (24.5557, -81.7596),   # Key West International, FL
    "KTLH": (30.3965, -84.3503),   # Tallahassee International, FL
    "KMYR": (33.6797, -78.9283),   # Myrtle Beach International, SC
    "KBQK": (31.2590, -81.4663),   # Brunswick Golden Isles, GA
    "KGNV": (29.6901, -82.2718),   # Gainesville Regional, FL
    "KVRB": (27.6556, -80.4179),   # Vero Beach Regional, FL
    "KCHO": (38.1386, -78.4529),  # Charlottesville-Albemarle Airport, VA
    "KMLB": (28.1028, -80.6453),  # Melbourne Orlando International Airport, FL
    "KECP": (30.3571, -85.7956),  # Northwest Florida Beaches International Airport, FL
    "KGSO": (36.0978, -79.9373),  # Piedmont Triad International Airport (Greensboro), NC
    "KJQF": (35.3878, -80.7092),  # Concord-Padgett Regional Airport, NC
    "KPGV": (35.6353, -77.3853),  # Pitt-Greenville Airport, NC
    "KPGD": (26.9163, -82.0006),  # Punta Gorda Airport, FL
    "KTYS": (35.8110, -83.9940),  # McGhee Tyson Airport (Knoxville), TN

    # --------------------------------------------------------------------------
    # CARIBBEAN SPOKES (TJBQ Regional Block)
    # --------------------------------------------------------------------------
    "TJPS": (18.0083, -66.5630),   # Mercedita Airport (Ponce), PR
    "TIST": (18.3373, -64.9734),   # Cyril E. King Airport (St. Thomas), USVI
    "TISX": (17.7019, -64.7986),   # Henry E. Rohlsen Airport (St. Croix), USVI
    "TJSJ": (18.4394, -66.0018),   # Luis Muñoz Marín Intl (San Juan), PR

    # --------------------------------------------------------------------------
    # INTERNATIONAL ROUTES (Skybus / 800 Block)
    # --------------------------------------------------------------------------
    "TNCM": (18.0410, -63.1089),   # Princess Juliana Intl, St. Maarten
    "TKPK": (17.3112, -62.7187),   # Robert L. Bradshaw Intl, St. Kitts
    "TFFR": (16.2653, -61.5318),   # Pointe-à-Pitre International, Guadeloupe
    "TFFF": (14.5910, -61.0032),   # Martinique Aimé Césaire Intl, Martinique
    "TAPA": (17.1367, -61.7927),   # V.C. Bird International, Antigua
    "TNCA": (12.5014, -70.0152),   # Queen Beatrix International, Aruba
    "TNCB": (12.1310, -68.2685),   # Flamingo International, Bonaire
    "TNCC": (12.1889, -68.9598),   # Curaçao International, Curaçao
    "TLPL": (13.7332, -60.9526),   # Hewanorra International, St. Lucia
    "TBPB": (13.0746, -59.4925),   # Grantley Adams International, Barbados
    "TVSA": (13.1569, -61.1481),   # Argyle International, St. Vincent
    "MDPC": (18.5674, -68.3634),   # Punta Cana International, Dominican Republic
    "MBPV": (21.7736, -72.2659),   # Providenciales Intl, Turks & Caicos
    "MKJS": (18.5037, -77.9134),   # Sangster International (Montego Bay), Jamaica
    "MYNN": (25.0390, -77.4662),   # Lynden Pindling International (Nassau), Bahamas
    "MROC": (9.9939,  -84.2088),   # Juan Santamaría Intl (San José), Costa Rica
    "CYXY": (60.7095, -135.0673),  # Erik Nielsen Whitehorse Intl, YT, Canada
    "CYVR": (49.1967, -123.1815),  # Vancouver International, BC, Canada
    "CYYJ": (48.6469, -123.4258),  # Victoria International, BC, Canada
    "CYYC": (51.1139, -114.0203),  # Calgary International, AB, Canada
    "CYEG": (53.3097, -113.5797),  # Edmonton International, AB, Canada
    "CYHM": (43.1736, -79.9350),   # John C. Munro Hamilton Intl, ON, Canada
    "CYUL": (45.4706, -73.7408),   # Montréal-Trudeau International, QC, Canada
    "CYHZ": (44.8808, -63.5086),   # Halifax Stanfield International, NS, Canada
    "MMSD": (23.1518, -109.7210),  # Los Cabos International, Mexico
    "MMPR": (20.6801, -105.2541),  # Lic. Gustavo Díaz Ordaz Intl (Puerto Vallarta), Mexico
    "MMMZ": (23.1614, -106.3712),  # General Rafael Buelna Intl (Mazatlán), Mexico
    "MMGL": (20.5218, -103.3112),  # Miguel Hidalgo y Costilla Intl (Guadalajara), Mexico
    "MMUN": (21.0365, -86.8771),   # Cancún International, Mexico
    "MMCZ": (20.5224, -86.9255),   # Cozumel International, Mexico
    "MZBZ": (17.5391, -88.3082),   # Philip S. W. Goldson Intl (Belize City), Belize
    "MGGT": (14.5833, -90.5275),   # La Aurora International (Guatemala City), Guatemala
    "MRLB": (10.5933, -85.5444),   # Daniel Oduber Quirós Intl (Liberia), Costa Rica
    "SKCG": (10.4424, -75.5130),   # Rafael Núñez Intl (Cartagena), Colombia
    "BIKF": (63.9850, -22.6056),   # Keflavík International, Iceland
    "EINN": (52.7020, -8.9248),    # Shannon Airport, Ireland
    "EIDW": (53.4213, -6.2701),    # Dublin Airport, Ireland
}

def haversine_miles(coord1, coord2):
    """Calculates distance between two lat/lon points in miles."""
    if not coord1 or not coord2:
        return 0
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    R = 3958.8  # Earth radius in miles
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
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
            total_miles += 800  # Fallback estimate if airport coordinates are unlisted
            
    # Add a 150-mile penalty per layover connection to prefer efficient transfers
    layover_penalty = (len(path) - 1) * 150
    return total_miles + layover_penalty


# ==========================================
# 3. GEOGRAPHICALLY OPTIMIZED ROUTE ENGINE
# ==========================================

from datetime import datetime

def leg_operates_today(days_str):
    """
    Checks if a flight leg operates today based on standard codes:
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

def find_routes(network, origin, destination, exact_connections=None, max_connections=10, max_display=75):
    origin = origin.strip().upper()
    destination = destination.strip().upper()

    if origin == destination:
        return []

    # =========================================================
    # REAL-TIME DAY FILTER: Keep only flights operating TODAY
    # =========================================================
    active_network = [leg for leg in network if leg_operates_today(leg.get("Days", "Daily"))]

    # 1. PRE-BUILD ADJACENCY MAP (Using active flights only)
    adj_map = defaultdict(list)
    for leg in active_network:
        adj_map[leg["Origin"]].append(leg)

    if origin not in adj_map:
        return []

    # Determine target flight leg depth (Legs = Connections + 1)
    if exact_connections is not None:
        target_legs_list = [exact_connections + 1]
    else:
        max_depth = min(max_connections if max_connections is not None else 10, 6) + 1
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
                    sig = tuple((leg["Flight"], leg["Origin"], leg["Destination"]) for leg in path)
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

# ==========================================
# SEARCH CONTROLS WITH SAFE RANDOM CALLBACK
# ==========================================

st.subheader("🔍 Search Any Route on Network Map")

# 1. State Initialization
if "dest_select_val" not in st.session_state:
    st.session_state["dest_select_val"] = "PAFA" if "PAFA" in all_airports else (all_airports[1] if len(all_airports) > 1 else all_airports[0])

# 2. Callback function executed BEFORE UI reruns
def set_random_destination():
    current_orig = st.session_state.get("orig_select_val", all_airports[0])
    current_dest = st.session_state.get("dest_select_val", None)
    
    # Exclude both origin AND current destination so every click changes the selection
    available = [a for a in all_airports if a != current_orig and a != current_dest]
    
    if available:
        # SystemRandom uses OS entropy, preventing random.seed() calls elsewhere from hijacking selection
        st.session_state["dest_select_val"] = random.SystemRandom().choice(available)

col1, col2, col3, col4 = st.columns([1, 1.3, 1, 1])

# Origin Dropdown
with col1:
    orig_select = st.selectbox(
        "Origin Airport",
        options=all_airports,
        index=all_airports.index("KRIC") if "KRIC" in all_airports else 0,
        key="orig_select_val",
        format_func=lambda code: f"{code} - {AIRPORT_NAMES.get(code, 'Unknown Airport')}"
    )

# Destination Dropdown + Random Button (with Callback)
with col2:
    st.markdown("<label style='font-size: 14px; font-weight: 500;'>Destination Airport</label>", unsafe_allow_html=True)
    d_col1, d_col2 = st.columns([2.2, 1])
    
    with d_col1:
        dest_select = st.selectbox(
            "Destination Airport",
            options=all_airports,
            key="dest_select_val",
            label_visibility="collapsed",
            format_func=lambda code: f"{code} - {AIRPORT_NAMES.get(code, 'Unknown Airport')}"
        )
        
    with d_col2:
        st.button(
            "🎲 Random", 
            on_click=set_random_destination,
            help="Pick a random destination from the network"
        )

# Connections Allowed Dropdown
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

# Max Options Dropdown
with col4:
    max_display_count = st.selectbox(
        "Max Options to Show",
        options=[15, 25, 35, 50, 75],
        index=4, # Defaults to 75
    )

# Map dropdown string to exact connection count integer
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
    if orig_select == dest_select:
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

    # ✅ INDENTED: Now inside the 'if' block
    st.components.v1.html(card_html, height=460)
