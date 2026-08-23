from db import get_db

def seed_database():
    db=get_db()
    if db.execute("SELECT COUNT(*) c FROM inventory").fetchone()["c"]:
        db.close()
        return

    centers=[
        ("Kolkata DC","Kolkata"),("Delhi DC","Delhi"),
        ("Mumbai DC","Mumbai"),("Bangalore DC","Bangalore"),
        ("Chennai DC","Chennai")
    ]
    for name,city in centers:
        db.execute("INSERT INTO distribution_centers(name,city) VALUES(?,?)",(name,city))
    dc={r["name"]:r["id"] for r in db.execute("SELECT * FROM distribution_centers")}

    rows=[
      ("Paracetamol 500mg","PCM-500",dc["Kolkata DC"],"PCM500-A22",500,800,200,12),
      ("Amoxicillin 250mg","AMX-250",dc["Mumbai DC"],"AMX250-B23",200,500,150,18),
      ("Vitamin C 500mg","VTC-500",dc["Delhi DC"],"VTC500-C12",1000,700,150,20),
      ("Azithromycin 500mg","AZI-500",dc["Chennai DC"],"AZI500-D11",300,450,120,22),
      ("Dol 650mg","DOL-650",dc["Bangalore DC"],"DOL650-E09",700,450,100,60),
      ("Cetirizine 10mg","CET-10",dc["Bangalore DC"],"CET10-F10",980,400,100,75)
    ]
    db.executemany("""
      INSERT INTO inventory
      (medicine,sku,dc_id,batch_no,current_stock,min_stock,safety_stock,days_to_expiry)
      VALUES(?,?,?,?,?,?,?,?)
    """,rows)

    demand=[
      ("Paracetamol 500mg","18 May",1400,1350),("Paracetamol 500mg","19 May",2100,1950),
      ("Paracetamol 500mg","20 May",1850,2050),("Paracetamol 500mg","21 May",3100,2800),
      ("Paracetamol 500mg","22 May",2600,2900),("Paracetamol 500mg","23 May",3500,3200),
      ("Paracetamol 500mg","24 May",2500,3600),
      ("Vitamin C 500mg","18 May",800,850),("Vitamin C 500mg","19 May",900,880),
      ("Vitamin C 500mg","20 May",1100,1050),("Vitamin C 500mg","21 May",1150,1100),
      ("Vitamin C 500mg","22 May",1200,1180),("Vitamin C 500mg","23 May",1250,1220),
      ("Vitamin C 500mg","24 May",1300,1280),
      ("Amoxicillin 250mg","18 May",500,480),("Amoxicillin 250mg","19 May",550,530),
      ("Amoxicillin 250mg","20 May",600,580),("Amoxicillin 250mg","21 May",620,600),
      ("Amoxicillin 250mg","22 May",650,630),("Amoxicillin 250mg","23 May",680,650),
      ("Amoxicillin 250mg","24 May",700,670)
    ]
    db.executemany(
      "INSERT INTO demand_history(medicine,day,actual,forecast) VALUES(?,?,?,?)",
      demand
    )

    recs=[
      (1,600,"Kolkata DC","High","Expected demand exceeds available stock"),
      (2,500,"Delhi DC","High","Stock below minimum threshold"),
      (3,500,"Mumbai DC","Medium","Demand trend increasing"),
      (4,300,"Delhi DC","Medium","Safety stock risk"),
      (5,200,"Kolkata DC","Low","Preventive replenishment")
    ]
    db.executemany("""
      INSERT INTO replenishments
      (inventory_id,recommended_qty,source,priority,reason)
      VALUES(?,?,?,?,?)
    """,recs)

    alerts=[
      ("danger","Low stock alert: Paracetamol 500mg at Kolkata DC","Current stock 500 is below minimum 800 units","10 min ago"),
      ("warning","Demand spike detected for Amoxicillin 250mg","Increase of 35% in last 3 days","2 hr ago"),
      ("info","Replenishment completed: Vitamin C 500mg","Received 500 units at Delhi DC","1 hr ago"),
      ("warning","Expiry risk: Paracetamol batch PCM500-A22","12 days remaining; prioritize FEFO allocation","35 min ago"),
      ("success","Inventory healthy: Dol 650mg","Stock is above safety level","3 hr ago")
    ]
    db.executemany(
      "INSERT INTO alerts(type,title,detail,time_text) VALUES(?,?,?,?)",
      alerts
    )
    db.commit()
    db.close()
