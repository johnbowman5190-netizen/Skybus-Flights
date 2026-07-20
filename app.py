import streamlit as st
from datetime import datetime, timedelta
from collections import deque

# Page Configuration for Mobile
st.set_page_config(page_title="SkyLink Airways Booking", page_icon="✈️", layout="centered")

# ==========================================
# 1. ROUTE NETWORK DATA
# ==========================================
ROUTES_DATA = [
    # Inter-Base Trunk Network (100-299)
    (100, "KBGR", "KSFB", 185, "Daily"), (102, "KIWA", "KBLI", 195, "Daily"),
    (104, "TJBQ", "KSFB", 175, "Daily"), (106, "PAFA", "KBLI", 210, "Daily"),
    (108, "KBGR", "TJBQ", 240, "Mon,Wed,Fri,Sun"), (110, "KIWA", "PAFA", 330, "Mon,Tue,Thu,Sat"),
    (200, "KSFB", "KRIC", 110, "Daily"), (202, "KIWA", "KPVU", 85, "Daily"),
    (204, "KGRR", "KSWF", 105, "Mon,Wed,Fri,Sun"), (206, "KMSY", "KOMA", 135, "Tue,Thu,Sat,Sun"),
    (208, "KSFB", "KMSY", 120, "Daily"), (210, "KBLI", "KPVU", 115, "Mon,Wed,Fri"),

    # Hub Spokes & Focus Cities
    (300, "KBGR", "KBOS", 55, "Daily"), (302, "KBGR", "KPWM", 40, "Daily"),
    (304, "KBGR", "KPVD", 65, "Daily"), (306, "KBGR", "KBTV", 60, "Mon,Wed,Fri"),
    (308, "KBGR", "KACK", 50, "Tue,Thu,Sat,Sun"), (310, "KBGR", "KMVY", 50, "Fri,Sat,Sun"),
    (312, "KBGR", "KBDL", 70, "Daily"), (314, "KBGR", "KSYR", 80, "Mon,Wed,Fri"),
    (316, "KBGR", "KROC", 90, "Tue,Thu,Sat"), (318, "KBGR", "KPBG", 60, "Mon,Fri"),

    (400, "KSFB", "KEYW", 70, "Daily"), (402, "KSFB", "KPNS", 75, "Daily"),
    (404, "KSFB", "KTLH", 55, "Daily"), (406, "KSFB", "KCHS", 65, "Daily"),
    (408, "KSFB", "KSAV", 60, "Mon,Wed,Fri,Sun"), (410, "KSFB", "KBHM", 90, "Tue,Thu,Sat"),
    (412, "KSFB", "KGSP", 80, "Mon,Wed,Fri"), (414, "KSFB", "KMYR", 70, "Daily"),
    (416, "KSFB", "KAGS", 75, "Tue,Thu,Sat"), (418, "KSFB", "KCAE", 70, "Mon,Wed,Fri,Sun"),

    (500, "TJBQ", "TJSJ", 35, "Daily"), (502, "TJBQ", "TIST", 50, "Daily"),
    (504, "TJBQ", "TISX", 55, "Daily"), (506, "TJBQ", "TJPS", 30, "Daily"),
    (508, "TJBQ", "TJIG", 35, "Daily"), (510, "TJBQ", "TNCM", 75, "Mon,Wed,Fri,Sun"),
    (512, "TJBQ", "MDPC", 45, "Daily"), (514, "TJBQ", "MDSD", 50, "Daily"),
    (516, "TJBQ", "MBPV", 80, "Tue,Thu,Sat"), (518, "TJBQ", "MYNN", 110, "Mon,Fri"),

    (600, "KIWA", "KLAS", 60, "Daily"), (602, "KIWA", "KSAN", 65, "Daily"),
    (604, "KIWA", "KPSP", 55, "Daily"), (606, "KIWA", "KTUS", 40, "Daily"),
    (608, "KIWA", "KFLG", 40, "Daily"), (610, "KIWA", "KABQ", 70, "Daily"),
    (612, "KIWA", "KSLC", 95, "Daily"), (614, "KIWA", "KRNO", 100, "Mon,Wed,Fri,Sun"),
    (616, "KIWA", "KFAT", 85, "Tue,Thu,Sat"), (618, "KIWA", "KOAK", 115, "Daily"),

    (700, "KBLI", "KGEG", 60, "Daily"), (702, "KBLI", "KYKM", 50, "Mon,Wed,Fri"),
    (704, "KBLI", "KPSC", 55, "Daily"), (706, "KBLI", "KEAT", 45, "Tue,Thu,Sat"),
    (708, "KBLI", "KALW", 60, "Mon,Fri"), (710, "KBLI", "KRDM", 75, "Daily"),
    (712, "KBLI", "KEUG", 70, "Daily"), (714, "KBLI", "KMFR", 85, "Mon,Wed,Fri,Sun"),
    (716, "KBLI", "KOTH", 80, "Tue,Thu,Sat"), (718, "KBLI", "KLWS", 70, "Mon,Wed,Fri"),

    (900, "PAFA", "PANC", 55, "Daily"), (902, "PAFA", "PAJN", 85, "Daily"),
    (904, "PAFA", "PAKT", 115, "Mon,Wed,Fri,Sun"), (906, "PAFA", "PASI", 100, "Tue,Thu,Sat"),
    (908, "PAFA", "PABR", 80, "Daily"), (910, "PAFA", "PAOT", 75, "Mon,Wed,Fri"),
    (912, "PAFA", "PAOM", 80, "Daily"), (914, "PAFA", "PABE", 70, "Mon,Wed,Fri,Sun"),
    (916, "PAFA", "PACV", 65, "Tue,Thu,Sat"), (918, "PAFA", "PAPG", 95, "Mon,Fri"),

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

    # International
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

# Build Full Flight Catalog
@st.cache_data
def get_flight_catalog():
    catalog = []
    base_dep = datetime.strptime("08:00", "%H:%M")
    
    for flt_out, orig, dest, duration, days in ROUTES_DATA:
        # Outbound
        arr_out = base_dep + timedelta(minutes=duration)
        catalog.append({
            "Flight": flt_out, "Origin": orig, "Destination": dest,
            "Dep": base_dep.strftime("%H:%M"), "Arr": arr_out.strftime("%H:%M"),
            "Duration": duration, "Days": days
        })
        
        # Inbound
        in_dep = arr_out + timedelta(minutes=60)
        in_arr = in_dep + timedelta(minutes=duration)
        catalog.append({
            "Flight": flt_out + 1, "Origin": dest, "Destination": orig,
            "Dep": in_dep.strftime("%H:%M"), "Arr": in_arr.strftime("%H:%M"),
            "Duration": duration, "Days": days
        })
    return catalog

flights = get_flight_catalog()
all_airports = sorted(list(set([f["Origin"] for f in flights] + [f["Destination"] for f in flights])))

# ==========================================
# 2. SEARCH ENGINE ALGORITHM
# ==========================================
def search_flights(origin, destination, max_connections):
    queue = deque()
    valid_itineraries = []

    for f in flights:
        if f["Origin"] == origin:
            queue.append([f])

    while queue:
        path = queue.popleft()
        last_leg = path[-1]
        curr_dest = last_leg["Destination"]

        if curr_dest == destination:
            valid_itineraries.append(path)
            continue

        if len(path) - 1 < max_connections:
            last_arr = datetime.strptime(last_leg["Arr"], "%H:%M")
            for next_f in flights:
                if next_f["Origin"] == curr_dest:
                    if next_f["Destination"] in {f["Origin"] for f in path}:
                        continue
                    next_dep = datetime.strptime(next_f["Dep"], "%H:%M")
                    layover = (next_dep - last_arr).total_seconds() / 60
                    if 45 <= layover <= 360:
                        queue.append(path + [next_f])

    return valid_itineraries

# ==========================================
# 3. STREAMLIT MOBILE UI
# ==========================================
st.title("✈️ SkyLink Flight Search")
st.caption("Book routes across your custom Hub & Spoke Network")

col1, col2 = st.columns(2)
with col1:
    origin = st.selectbox("From (Origin)", all_airports, index=0)
with col2:
    destination = st.selectbox("To (Destination)", all_airports, index=1)

max_stops = st.select_slider("Max Connections Allowed", options=[0, 1, 2], value=1)

if st.button("🔍 Search Flights", type="primary", use_container_width=True):
    if origin == destination:
        st.warning("Origin and Destination must be different.")
    else:
        results = search_flights(origin, destination, max_stops)
        
        st.markdown(f"### Results for **{origin}** ➔ **{destination}**")
        st.write(f"Found **{len(results)}** itinerary option(s)")

        if not results:
            st.error("No valid flights found within connection limits.")
        else:
            for idx, itin in enumerate(results, 1):
                stops = len(itin) - 1
                stop_label = "Nonstop" if stops == 0 else f"{stops} Stop(s)"
                
                with st.expander(f"Option {idx}: {stop_label} ({itin[0]['Dep']} ➔ {itin[-1]['Arr']})", expanded=(idx==1)):
                    for leg_i, leg in enumerate(itin, 1):
                        st.markdown(f"**Leg {leg_i}: Flight {leg['Flight']}**")
                        st.write(f"🛫 **{leg['Origin']}** ({leg['Dep']}) ➔ 🛬 **{leg['Destination']}** ({leg['Arr']})")
                        st.caption(f"Duration: {leg['Duration']} mins | Days: {leg['Days']}")
                        
                        if leg_i < len(itin):
                            arr = datetime.strptime(leg['Arr'], "%H:%M")
                            nxt_dep = datetime.strptime(itin[leg_i]['Dep'], "%H:%M")
                            layover = int((nxt_dep - arr).total_seconds() / 60)
                            st.info(f"⏱️ **{layover} min layover** in {leg['Destination']}")
                    
                    st.button(f"Select Option {idx}", key=f"select_{idx}")
