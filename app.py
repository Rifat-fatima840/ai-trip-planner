from flask import Flask, render_template, request, redirect, session
import sqlite3
import datetime

app = Flask(__name__)
app.secret_key = "tripplanner_secret"

# ---------- Database ----------
def get_db():
    conn = sqlite3.connect("database.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT,
            created_at TEXT,
            last_login TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            destination TEXT,
            budget INTEGER,
            days INTEGER,
            hotel TEXT,
            created_at TEXT
        )
    """)
    return conn
def get_db():
    conn = sqlite3.connect("database.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT,
            created_at TEXT,
            last_login TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            destination TEXT,
            budget INTEGER,
            days INTEGER,
            hotel TEXT,
            created_at TEXT
        )
    """)
    return conn

def create_admin():
    db = get_db()
    db.execute(
        "INSERT OR IGNORE INTO users (username, password, role, created_at) VALUES (?, ?, ?, ?)",
        ("admin", "admin123", "admin", str(datetime.datetime.now()))
    )
    db.commit()
    db.close()

# Call this once at app start
create_admin()

# ---------- Home redirects ----------
@app.route("/")
def home():
    
    return render_template("index.html")

@app.route("/next")
def next_page():
    
    return render_template("index1.html")

# ---------- Register ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        try:
            # ✅ Correct: insert into users table
            db.execute(
                "INSERT INTO users (username, password, role, created_at) VALUES (?, ?, ?, ?)",
                (username, password, "user", str(datetime.datetime.now()))
            )
            db.commit()
            db.close()
            return redirect("/login")
        except sqlite3.IntegrityError:
            return "Username already exists. Try another."
    return render_template("register.html")


# ---------- Login ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        cursor = db.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        db.close()

        if user:
            session["user"] = username
            return redirect("/dashboard")
        else:
            return "Invalid login credentials"
    return render_template("login.html")



# ---------- Admin / All Users & Trips ----------
@app.route("/admin_history")
def admin_history():
    if "user" not in session:
        return redirect("/login")

    username = session["user"]

    db = get_db()
    # Check if current user is admin
    user = db.execute("SELECT role FROM users WHERE username=?", (username,)).fetchone()
    if not user or user[0] != "admin":
        db.close()
        return "Access Denied. Only admin can view this page."

    # Fetch all users
    users = db.execute("SELECT id, username, role, created_at, last_login FROM users").fetchall()

    # Fetch all trips
    trips = db.execute("SELECT id, username, destination, budget, days, hotel, created_at FROM trips").fetchall()
    db.close()

    return render_template("admin_history.html", users=users, trips=trips)

# ---------- Dashboard / Trip Planner ----------
@app.route("/dashboard", methods=["GET", "POST"])          
def dashboard():
    if "user" not in session:
        return redirect("/login")

    username = session["user"]

    if request.method == "POST":       
        budget = int(request.form["budget"])
        days = int(request.form["days"])
        interest = request.form["interest"]

        area=request.form["area"]
        crowd=request.form["crowd"]


        offline_support=False
        if area=="rural":
            offline_support=True

        # AI Destination Logic
        if interest == "nature":
            destination = "Manali / Ooty Hill Station"
        elif interest == "beach":
            destination = "Goa / Pondicherry Beach"
        else:
            destination = "Delhi / Mumbai City Tour"

        # AI Explanation
        if interest == "nature":
            reason = "This destination was selected because it offers scenic beauty, fresh air, and peaceful environments ideal for nature lovers."
        elif interest == "beach":
            reason = "This destination is ideal for relaxation, beach activities, and a calm vacation experience."
        else:
            reason = "This destination is suitable for city exploration, shopping, cultural places, and urban lifestyle."
            

        # Day-wise Itinerary
        itinerary = []

        for day in range(1, days + 1):
            if crowd == "low":
                plan = f"Day {day}: Early morning sightseeing, less crowded spots, nature walk"
            elif crowd == "medium":
                plan = f"Day {day}: Standard sightseeing with flexible timing"
            else:
                plan = f"Day {day}: Popular tourist attractions and shopping areas"
            itinerary.append(plan)

        #------------------
       

        # Budget-based Hotel
        hotels = []
        restaurants = []
        conveyance = []

        # ================== NATURE PLACES ==================
        if "Manali" in destination or "Ooty" in destination:
            # ---- Hotels ----
            if offline_support:
                
                hotel = "Budget Nature Stay"
                hotels = [
                    {"name": "Local Homestay", "rate": "₹1,200 / night"},
                    {"name": "Nature View Lodge", "rate": "₹1,500 / night"},
                    {"name": "Village Guest House", "rate": "₹900 / night"}
                ]
                
                   

                # ---- Restaurants ----
                restaurants = [
                    {"name": "Local Dhaba", "type": "Traditional Food"},
                    {"name": "Village Canteen", "type": "Home Style Meals"},
                    
                ]

                # ---- Conveyance ----
                conveyance = [
                    {"mode": "Local Bus", "rate": "₹20-₹40"},
                    
                    {"mode": "Shared Jeep", "rate": "₹50–₹100 per ride"}
            
               ]
            else:
                if budget < 10000:
                    hotel = "Budget Nature Stay"
                    hotels = [
                        {"name": "Green Hills Guest House", "rate": "₹1,200 / night"},
                        {"name": "Nature View Lodge", "rate": "₹1,500 / night"},
                        {"name": "Hilltop Budget Inn", "rate": "₹1,800 / night"}
                    ]
                elif budget <= 20000:
                    hotel = "Standard Nature Stay"
                    hotels = [
                        {"name": "Mountain Retreat", "rate": "₹3,500 / night"},
                        {"name": "Forest Breeze Resort", "rate": "₹4,000 / night"},
                        {"name": "Nature Bliss Hotel", "rate": "₹4,500 / night"}
                    ]
                else:
                    hotel = "Luxury Nature Stay"
                    hotels = [
                        {"name": "The Himalayan Resort", "rate": "₹8,000 / night"},
                        {"name": "Savoy Hill Resort", "rate": "₹9,500 / night"},
                        {"name": "Luxury Valley View", "rate": "₹11,000 / night"}
                    ]

                # ---- Restaurants ----
                restaurants = [
                    {"name": "Cafe 1947", "type": "Cafe & Continental"},
                    {"name": "Garden Restaurant", "type": "Indian & Chinese"},
                    {"name": "Hill View Cafe", "type": "Local Cuisine"}
                ]

                # ---- Conveyance ----
                conveyance = [
                    {"mode": "Local Taxi", "rate": "₹1,200/day"},
                    {"mode": "Bike Rental", "rate": "₹700/day"},
                    {"mode": "Auto Rickshaw", "rate": "₹50–₹100 per ride"}
            
               ]

        # ================== BEACH PLACES ==================
        elif "Goa" in destination or "Pondicherry" in destination:
            # ---- Hotels ----
            if offline_support:
                
                hotel = "Budget Nature Stay"
                hotels = [
                    {"name": "Beach Village Homestay", "rate": "₹1,200 / night"},
                    {"name": "Coastal Guest House", "rate": "₹1,500 / night"},
                    
                ]
                
                   

                # ---- Restaurants ----
                restaurants = [
                    {"name": "VIallage Cafe", "type": "Traditional Food"},
                    {"name": "Beachside Dhaba", "type": "Home Style Meals"},
                    
                ]

                # ---- Conveyance ----
                conveyance = [
                    {"mode": "Scooter Rental", "rate": "₹300/day"},
                    
                    {"mode": "Shared Rickshaw", "rate": "₹20–₹50 per ride"}
            
               ]
            else:
                if budget < 10000:
                    hotel = "Budget Beach Stay"
                    hotels = [
                    {"name": "Beach Hut Stay", "rate": "₹1,500 / night"},
                    {"name": "Ocean Breeze Lodge", "rate": "₹1,800 / night"},
                    {"name": "Sunny Sands Inn", "rate": "₹2,000 / night"}
                ]
                elif budget <= 20000:
                    hotel = "Standard Beach Stay"
                    hotels = [
                    {"name": "Sea View Resort", "rate": "₹4,000 / night"},
                    {"name": "Blue Waves Hotel", "rate": "₹4,500 / night"},
                    {"name": "Palm Tree Retreat", "rate": "₹5,000 / night"}
                ]
                else:
                    hotel = "Luxury Beach Stay"
                    hotels = [
                    {"name": "Taj Beach Resort", "rate": "₹12,000 / night"},
                    {"name": "Leela Palace Beach", "rate": "₹15,000 / night"},
                    {"name": "Grand Ocean Resort", "rate": "₹18,000 / night"}
                ]

            # ---- Restaurants ----
                restaurants = [
                    {"name": "Fisherman’s Wharf", "type": "Seafood"},
                    {"name": "Cafe des Arts", "type": "French & Cafe"},
                    {"name": "Beach Shack Grill", "type": "Goan Cuisine"}
                ]

                # ---- Conveyance ----
                conveyance = [
                    {"mode": "Scooter Rental", "rate": "₹400/day"},
                    {"mode": "Local Taxi", "rate": "₹2,000/day"},
                    {"mode": "Bus", "rate": "₹20–₹50 per ride"}
                ]

        # ================== CITY PLACES ==================
        else:  # Delhi / Mumbai
            # ---- Hotels ----
            if offline_support:
                
                hotel = "Budget Nature Stay"
                hotels = [
                    {"name": "Community Guest House", "rate": "₹1,800 / night"},
                    {"name": "Local Budget Inn", "rate": "₹1,500 / night"},
                    
                ]
                
                   

                # ---- Restaurants ----
                restaurants = [
                    {"name": "Local Dhaba", "type": "Indian Food"},
                    {"name": "Community Cafe", "type": "Home Style Meals"},
                    
                ]

                # ---- Conveyance ----
                conveyance = [
                    {"mode": "Scooter Rental", "rate": "₹300/day"},
                    
                    {"mode": "Shared Rickshaw", "rate": "₹20–₹50 per ride"}
            
               ]
            else:
                if budget < 10000:
                    hotel = "Budget City Stay"
                    hotels = [
                    {"name": "City Comfort Inn", "rate": "₹2,000 / night"},
                    {"name": "Urban Budget Hotel", "rate": "₹2,500 / night"},
                    {"name": "Metro Stay Lodge", "rate": "₹3,000 / night"}
                ]
                elif budget <= 20000:
                    hotel = "Standard City Stay"
                    hotels = [
                    {"name": "Hotel City Pride", "rate": "₹4,500 / night"},
                    {"name": "Urban Residency", "rate": "₹5,000 / night"},
                    {"name": "Central Park Hotel", "rate": "₹5,500 / night"}
                ]
                else:
                    hotel = "Luxury City Stay"
                    hotels = [
                    {"name": "Taj City Palace", "rate": "₹12,000 / night"},
                    {"name": "The Oberoi", "rate": "₹15,000 / night"},
                    {"name": "ITC Grand Central", "rate": "₹18,000 / night"}
                ]

                # ---- Restaurants ----
                restaurants = [
                    {"name": "Barbeque Nation", "type": "Multi-Cuisine"},
                    {"name": "Bukhara", "type": "North Indian"},
                    {"name": "Leopold Cafe", "type": "Cafe & Continental"}
                ]

                # ---- Conveyance ----
                conveyance = [
                    {"mode": "Metro", "rate": "₹30–₹80 per ride"},
                    {"mode": "App Cab (Uber/Ola)", "rate": "₹15/km"},
                    {"mode": "Auto Rickshaw", "rate": "₹30–₹60 per ride"}
                ]

        if budget < 10000:
            hotel_category = "2 Star ⭐⭐"
        elif budget <= 20000:
            hotel_category = "3 Star ⭐⭐⭐"
        else:
            hotel_category = "5 Star ⭐⭐⭐⭐⭐"   



        # ---------------- Insert trip into trips table ----------------
        print("saving trips",username,destination,budget,days,hotel)

        db = get_db()
        db.execute(
            "INSERT INTO trips (username, destination, budget, days, hotel, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (username, destination, budget, days, hotel, str(datetime.datetime.now()))
        )
        
        db.commit()
        db.close()
        return render_template("result.html",
                               destination=destination,
                               budget=budget,
                               days=days,
                               itinerary=itinerary,
                               hotel_category=hotel_category,
                               hotel=hotel,
                               hotels=hotels,
                               restaurants=restaurants,
                               conveyance=conveyance,
                               crowd=crowd,
                               reason=reason,
                               offline_support=offline_support,
                               username=username)
    return render_template("dashboard.html", username=username)

# ---------- Logout ----------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

@app.route("/welcome")
def welcome():
    return render_template("welcome.html")

# ---------- Run App ----------


@app.route("/history")
def history():
    if "user" not in session:
        return redirect("/login")

    db = get_db()
    trips = db.execute(
        "SELECT destination, budget, days, hotel FROM trips WHERE username=?",
        (session["user"],)
    ).fetchall()
    db.close()

    return render_template("history.html", trips=trips)
# ---------- Run App ----------
if __name__ == "__main__":
    app.run()