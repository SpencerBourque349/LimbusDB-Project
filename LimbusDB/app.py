from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)

# databse connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="limbus_db"
)

cursor = db.cursor(dictionary=True)

# Landing page

@app.route("/")
def landing():
    return render_template("landing.html")
    
# homepage
@app.route("/home")
def home():
    return render_template("home.html")

# View Identities
@app.route("/identities")
def identities():
    cursor.execute("""
    SELECT 
        i.identity_id,
        i.identity_name,
        s.sinner_id,
        s.sinner_name AS sinner,
        i.rarity, i.season_released,
        GROUP_CONCAT(DISTINCT ia.affinity_name) AS affinities,
        GROUP_CONCAT(DISTINCT ise.keyword_name) AS statuses
    FROM identity i
    JOIN sinner s ON i.sinner_id = s.sinner_id
    LEFT JOIN IdentityAffinity ia ON i.identity_id = ia.identity_id
    LEFT JOIN IdentityStatusEffect ise ON i.identity_id = ise.identity_id
    GROUP BY i.identity_id
""")
    data = cursor.fetchall()
    return render_template("identities.html", identities=data)

# Add Identity
@app.route("/add_identity", methods=["GET", "POST"])
def add_identity():
    if request.method == "POST":
        name = request.form["identity_name"]
        sinner_id = request.form["sinner_id"]
        rarity = request.form["rarity"]
        season = request.form["season_released"]
        acquisition = request.form["acquisition"]

        affinities = request.form.getlist("affinities")
        statuses = request.form.getlist("statuses")

        # Insert into Identity
        cursor.execute("""
            INSERT INTO Identity (identity_name, sinner_id, rarity, season_released, acquisition)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, sinner_id, rarity, season, acquisition))

        db.commit()

        identity_id = cursor.lastrowid  # IMPORTANT

        # insert affinities
        for aff in affinities:
            cursor.execute("""
                INSERT INTO IdentityAffinity (identity_id, affinity_name)
                VALUES (%s, %s)
            """, (identity_id, aff))

        # insert statuses
        for stat in statuses:
            cursor.execute("""
                INSERT INTO IdentityStatusEffect (identity_id, keyword_name)
                VALUES (%s, %s)
            """, (identity_id, stat))

        db.commit()
        return redirect("/identities")

    # get request
    cursor.execute("SELECT * FROM Sinner")
    sinners = cursor.fetchall()

    cursor.execute("SELECT * FROM Affinity")
    affinities = cursor.fetchall()

    cursor.execute("SELECT * FROM statuseffect")
    statuses = cursor.fetchall()

    return render_template(
        "add_identity.html",
        sinners=sinners,
        affinities=affinities,
        statuses=statuses
    )

# Delete Identity
@app.route("/delete_identity/<int:id>")
def delete_identity(id):
    cursor.execute("DELETE FROM Identity WHERE identity_id = %s", (id,))
    db.commit()
    return redirect("/identities")
    
# edit Identity
@app.route("/edit_identity/<int:id>", methods=["GET", "POST"])
def edit_identity(id):

    if request.method == "POST":
        name = request.form["identity_name"]
        sinner_id = request.form["sinner_id"]
        rarity = request.form["rarity"]
        season = request.form["season_released"]
        acquisition = request.form["acquisition"]

        affinities = request.form.getlist("affinities")
        statuses = request.form.getlist("statuses")

        # Update main Identity table
        cursor.execute("""
            UPDATE Identity
            SET identity_name=%s, sinner_id=%s, rarity=%s,
                season_released=%s, acquisition=%s
            WHERE identity_id=%s
        """, (name, sinner_id, rarity, season, acquisition, id))

        #  Clear old relationships
        cursor.execute("DELETE FROM IdentityAffinity WHERE identity_id=%s", (id,))
        cursor.execute("DELETE FROM IdentityStatusEffect WHERE identity_id=%s", (id,))

        #  Insert new affinities
        for aff in affinities:
            cursor.execute("""
                INSERT INTO IdentityAffinity (identity_id, affinity_name)
                VALUES (%s, %s)
            """, (id, aff))

        #  Insert new statuses
        for stat in statuses:
            cursor.execute("""
                INSERT INTO IdentityStatusEffect (identity_id, keyword_name)
                VALUES (%s, %s)
            """, (id, stat))

        db.commit()
        return redirect("/identities")

    # get request

    # Identity info
    cursor.execute("SELECT * FROM Identity WHERE identity_id=%s", (id,))
    identity = cursor.fetchone()

    # Dropdown data
    cursor.execute("SELECT * FROM Sinner")
    sinners = cursor.fetchall()

    cursor.execute("SELECT * FROM Affinity")
    affinities = cursor.fetchall()

    cursor.execute("SELECT * FROM statuseffect")  
    statuses = cursor.fetchall()

    # Current selections
    cursor.execute("SELECT affinity_name FROM IdentityAffinity WHERE identity_id=%s", (id,))
    current_aff = [row["affinity_name"] for row in cursor.fetchall()]

    cursor.execute("SELECT keyword_name FROM IdentityStatusEffect WHERE identity_id=%s", (id,))
    current_stat = [row["keyword_name"] for row in cursor.fetchall()]

    return render_template(
        "edit_identity.html",
        identity=identity,
        sinners=sinners,
        affinities=affinities,
        statuses=statuses,
        current_aff=current_aff,
        current_stat=current_stat
    )
    
    # EGOS
@app.route("/egos")
def egos():
    cursor.execute("""
    SELECT 
        e.ego_id,
        e.ego_name,
        e.class,
        e.season_released,
        s.sinner_id,
        s.sinner_name AS sinner,
        GROUP_CONCAT(DISTINCT ea.affinity_name) AS affinities,
        GROUP_CONCAT(DISTINCT es.keyword_name) AS statuses
    FROM EGO e
    JOIN Sinner s ON e.sinner_id = s.sinner_id
    LEFT JOIN EGOAffinity ea ON e.ego_id = ea.ego_id
    LEFT JOIN EGOStatusEffect es ON e.ego_id = es.ego_id
    GROUP BY e.ego_id
""")
    data = cursor.fetchall()
    return render_template("egos.html", egos=data)

    
# ego insert
@app.route("/add_ego", methods=["GET", "POST"])
def add_ego():
    if request.method == "POST":
        name = request.form["ego_name"]
        sinner_id = request.form["sinner_id"]
        rarity = request.form["class"]
        season = request.form["season_released"]
        acquisition = request.form["acquisition"]

        affinities = request.form.getlist("affinities")
        statuses = request.form.getlist("statuses")

        # Insert into ego
        cursor.execute("""
            INSERT INTO EGO (ego_name, sinner_id, class, season_released, acquisition)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, sinner_id, rarity, season, acquisition))

        db.commit()

        ego_id = cursor.lastrowid

        # Insert affinities
        for aff in affinities:
            cursor.execute("""
                INSERT INTO EGOAffinity (ego_id, affinity_name)
                VALUES (%s, %s)
            """, (ego_id, aff))

        # Insert statuses
        for stat in statuses:
            cursor.execute("""
                INSERT INTO EGOStatusEffect (ego_id, keyword_name)
                VALUES (%s, %s)
            """, (ego_id, stat))

        db.commit()
        return redirect("/egos")

    # get request
    cursor.execute("SELECT * FROM Sinner")
    sinners = cursor.fetchall()

    cursor.execute("SELECT * FROM Affinity")
    affinities = cursor.fetchall()

    cursor.execute("SELECT * FROM statuseffect")
    statuses = cursor.fetchall()

    return render_template(
        "add_ego.html",
        sinners=sinners,
        affinities=affinities,
        statuses=statuses
    )
    
   # ego deletion 
@app.route("/delete_ego/<int:id>")
def delete_ego(id):
    cursor.execute("DELETE FROM EGO WHERE ego_id = %s", (id,))
    db.commit()
    return redirect("/egos")    
    
    # edit ego
@app.route("/edit_ego/<int:id>", methods=["GET", "POST"])
def edit_ego(id):

    if request.method == "POST":
        name = request.form["ego_name"]
        sinner_id = request.form["sinner_id"]
        ego_class = request.form["class"]
        season = request.form["season_released"]
        acquisition = request.form["acquisition"]

        affinities = request.form.getlist("affinities")
        statuses = request.form.getlist("statuses")

        cursor.execute("""
            UPDATE EGO
            SET ego_name=%s, sinner_id=%s, class=%s,
                season_released=%s, acquisition=%s
            WHERE ego_id=%s
        """, (name, sinner_id, ego_class, season, acquisition, id))

        # Clear old
        cursor.execute("DELETE FROM EGOAffinity WHERE ego_id=%s", (id,))
        cursor.execute("DELETE FROM EGOStatusEffect WHERE ego_id=%s", (id,))

        # Insert new
        for aff in affinities:
            cursor.execute("""
                INSERT INTO EGOAffinity (ego_id, affinity_name)
                VALUES (%s, %s)
            """, (id, aff))

        for stat in statuses:
            cursor.execute("""
                INSERT INTO EGOStatusEffect (ego_id, keyword_name)
                VALUES (%s, %s)
            """, (id, stat))

        db.commit()
        return redirect("/egos")

    # get request
    cursor.execute("SELECT * FROM EGO WHERE ego_id=%s", (id,))
    ego = cursor.fetchone()

    cursor.execute("SELECT * FROM Sinner")
    sinners = cursor.fetchall()

    cursor.execute("SELECT * FROM Affinity")
    affinities = cursor.fetchall()

    cursor.execute("SELECT * FROM statuseffect")
    statuses = cursor.fetchall()

    cursor.execute("SELECT affinity_name FROM EGOAffinity WHERE ego_id=%s", (id,))
    current_aff = [row["affinity_name"] for row in cursor.fetchall()]

    cursor.execute("SELECT keyword_name FROM EGOStatusEffect WHERE ego_id=%s", (id,))
    current_stat = [row["keyword_name"] for row in cursor.fetchall()]

    return render_template(
        "edit_ego.html",
        ego=ego,
        sinners=sinners,
        affinities=affinities,
        statuses=statuses,
        current_aff=current_aff,
        current_stat=current_stat
    )
 # report of number of identities per sinner
@app.route("/report_identities")
def report_identities():
    cursor.execute("""
        SELECT s.sinner_id, s.sinner_name, COUNT(i.identity_id) AS total
        FROM Sinner s
        LEFT JOIN Identity i ON s.sinner_id = i.sinner_id
        GROUP BY s.sinner_id, s.sinner_name
    """)
    data = cursor.fetchall()
    return render_template("report1.html", data=data)
    
 # Identity details  
@app.route("/identity/<int:id>")
def identity_detail(id):
    cursor.execute("""
        SELECT 
            i.*, 
            s.sinner_name,
            GROUP_CONCAT(DISTINCT ia.affinity_name) AS affinities,
            GROUP_CONCAT(DISTINCT ise.keyword_name) AS statuses
        FROM Identity i
        JOIN Sinner s ON i.sinner_id = s.sinner_id
        LEFT JOIN IdentityAffinity ia ON i.identity_id = ia.identity_id
        LEFT JOIN IdentityStatusEffect ise ON i.identity_id = ise.identity_id
        WHERE i.identity_id = %s
        GROUP BY i.identity_id
    """, (id,))

    identity = cursor.fetchone()
    return render_template("identity_detail.html", i=identity)
#sinner page
@app.route("/sinners")
def sinners():
    cursor.execute("SELECT * FROM Sinner")
    data = cursor.fetchall()
    return render_template("sinners.html", sinners=data)
    
 # ego details   
@app.route("/egos/<int:id>")
def ego_detail(id):
    cursor.execute("""
        SELECT 
            e.*, 
            s.sinner_name,
            GROUP_CONCAT(DISTINCT ea.affinity_name) AS affinities,
            GROUP_CONCAT(DISTINCT ese.keyword_name) AS statuses
        FROM EGO e
        JOIN Sinner s ON e.sinner_id = s.sinner_id
        LEFT JOIN EGOAffinity ea ON e.ego_id = ea.ego_id
        LEFT JOIN EGOStatusEffect ese ON e.ego_id = ese.ego_id
        WHERE e.ego_id = %s
        GROUP BY e.ego_id
    """, (id,))

    ego = cursor.fetchone()
    return render_template("ego_detail.html", e=ego)
  # sinner details  
@app.route("/sinner/<int:id>")
def sinner_detail(id):

    # get sinner info
    cursor.execute("""
        SELECT *
        FROM Sinner
        WHERE sinner_id = %s
    """, (id,))
    sinner = cursor.fetchone()

    # get identities for this sinner
    cursor.execute("""
        SELECT 
            i.identity_id,
            i.identity_name,
            i.rarity,
            i.season_released
        FROM Identity i
        WHERE i.sinner_id = %s
    """, (id,))
    identities = cursor.fetchall()

    # get egos for this sinner
    cursor.execute("""
        SELECT 
            e.ego_id,
            e.ego_name,
            e.class,
            e.season_released
        FROM EGO e
        WHERE e.sinner_id = %s
    """, (id,))
    egos = cursor.fetchall()

    return render_template(
        "sinner_detail.html",
        sinner=sinner,
        identities=identities,
        egos=egos
    )
    
# report of number of identities and egos released per season    
@app.route("/report_season_counts")
def report_season_counts():
    cursor.execute("""
        SELECT season_released, COUNT(*) AS total
        FROM (
            SELECT season_released FROM Identity
            UNION ALL
            SELECT season_released FROM EGO
        ) AS combined
        GROUP BY season_released
        ORDER BY season_released
    """)
    data = cursor.fetchall()
    return render_template("report_season_counts.html", data=data)

from flask import request

#report where user chooses and affinity and outputs all identities and egos with that affinity
@app.route("/report_affinity", methods=["GET"])
def report_affinity():
    aff = request.args.get("aff")

    data = []

    if aff:  # only run query if something selected
        cursor.execute("""
            SELECT i.identity_id AS item_id, i.identity_name AS name, 'Identity' AS type
            FROM Identity i
            JOIN IdentityAffinity ia ON i.identity_id = ia.identity_id
            WHERE ia.affinity_name = %s

            UNION

            SELECT e.ego_id AS item_id, e.ego_name AS name, 'EGO' AS type
            FROM EGO e
            JOIN EGOAffinity ea ON e.ego_id = ea.ego_id
            WHERE ea.affinity_name = %s
        """, (aff, aff))

        data = cursor.fetchall()

    # get list of affinities for dropdown
    cursor.execute("SELECT affinity_name FROM Affinity")
    affinities = cursor.fetchall()

    return render_template(
        "report_affinity.html",
        data=data,
        aff=aff,
        affinities=affinities
    )

if __name__ == "__main__":
    app.run(debug=True)