from flask import Flask, render_template, jsonify, request
from db import get_db, init_db
from seed import seed_database

app = Flask(__name__)

@app.before_request
def setup():
    init_db()
    seed_database()

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/inventory")
def inventory():
    return render_template("inventory.html")

@app.route("/demand")
def demand():
    return render_template("demand.html")

@app.route("/replenishment")
def replenishment():
    return render_template("replenishment.html")

@app.route("/alerts")
def alerts():
    return render_template("alerts.html")

@app.get("/api/dashboard")
def dashboard_api():
    db = get_db()
    k = lambda q: db.execute(q).fetchone()["c"]
    kpis = {
        "skus": k("SELECT COUNT(*) c FROM inventory"),
        "value": "₹ 15.62 Cr",
        "low_stock": k("SELECT COUNT(*) c FROM inventory WHERE current_stock <= min_stock"),
        "demand_increase": "+18.4%",
        "expiry": k("SELECT COUNT(*) c FROM inventory WHERE days_to_expiry <= 30")
    }
    inv = [dict(r) for r in db.execute("""
        SELECT i.*, d.name dc_name FROM inventory i
        JOIN distribution_centers d ON i.dc_id=d.id ORDER BY i.current_stock ASC
    """).fetchall()]
    recs = [dict(r) for r in db.execute("""
        SELECT r.*, i.medicine, i.sku, i.current_stock, d.name dc_name
        FROM replenishments r JOIN inventory i ON r.inventory_id=i.id
        JOIN distribution_centers d ON i.dc_id=d.id ORDER BY r.id
    """).fetchall()]
    expiry = [dict(r) for r in db.execute("""
        SELECT i.medicine,i.batch_no,i.days_to_expiry,i.current_stock,d.name dc_name
        FROM inventory i JOIN distribution_centers d ON i.dc_id=d.id
        WHERE i.days_to_expiry<=30 ORDER BY i.days_to_expiry
    """).fetchall()]
    alerts = [dict(r) for r in db.execute(
        "SELECT * FROM alerts ORDER BY id DESC LIMIT 8"
    ).fetchall()]
    return jsonify({"kpis":kpis,"inventory":inv,"recs":recs,"expiry":expiry,"alerts":alerts})

@app.get("/api/inventory")
def inventory_api():
    db=get_db()
    return jsonify([dict(r) for r in db.execute("""
        SELECT i.*,d.name dc_name FROM inventory i
        JOIN distribution_centers d ON i.dc_id=d.id ORDER BY i.medicine
    """).fetchall()])

@app.get("/api/demand")
def demand_api():
    db=get_db()
    return jsonify([dict(r) for r in db.execute(
        "SELECT medicine,day,actual,forecast FROM demand_history ORDER BY id"
    ).fetchall()])

@app.get("/api/replenishments")
def replenishments_api():
    db=get_db()
    return jsonify([dict(r) for r in db.execute("""
        SELECT r.*,i.medicine,i.sku,d.name dc_name
        FROM replenishments r JOIN inventory i ON r.inventory_id=i.id
        JOIN distribution_centers d ON i.dc_id=d.id ORDER BY r.id
    """).fetchall()])

@app.post("/api/replenishments/<int:rid>/approve")
def approve(rid):
    db=get_db()
    if not db.execute("SELECT id FROM replenishments WHERE id=?",(rid,)).fetchone():
        return jsonify({"error":"Not found"}),404
    db.execute("UPDATE replenishments SET status='Approved' WHERE id=?",(rid,))
    db.commit()
    return jsonify({"message":"Replenishment approved"})

@app.post("/api/simulate")
def simulate():
    payload=request.get_json(silent=True) or {}
    increase=float(payload.get("increase",20))
    db=get_db()
    rows=db.execute("""
        SELECT i.medicine,i.current_stock,i.safety_stock,AVG(h.forecast) avg_forecast
        FROM inventory i JOIN demand_history h ON i.medicine=h.medicine GROUP BY i.id
    """).fetchall()
    result=[]
    for r in rows:
        base=round(r["avg_forecast"])
        forecast=round(base*(1+increase/100))
        shortage=max(0,forecast+r["safety_stock"]-r["current_stock"])
        result.append({"medicine":r["medicine"],"base":base,"forecast":forecast,"shortage":shortage})
    return jsonify(result)

@app.post("/api/reset")
def reset():
    db=get_db()
    for table in ["alerts","replenishments","demand_history","inventory","distribution_centers"]:
        db.execute(f"DELETE FROM {table}")
    db.commit()
    db.close()
    seed_database()
    return jsonify({"message":"Demo data reset"})

if __name__=="__main__":
    app.run(debug=True)
