from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from pathlib import Path
from datetime import datetime, date
app=Flask(__name__); app.secret_key="fairshift-demo"
DB=Path(__file__).with_name("fairshift.db")
INDUSTRIES=["Construction","College"]
def connect():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c
def init():
    with connect() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS workers(id INTEGER PRIMARY KEY, name TEXT, role TEXT, industry TEXT, rate REAL);
        CREATE TABLE IF NOT EXISTS shifts(id INTEGER PRIMARY KEY AUTOINCREMENT, worker_id INTEGER, day TEXT, cin TEXT, cout TEXT);
        CREATE TABLE IF NOT EXISTS reports(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, industry TEXT, category TEXT, details TEXT, status TEXT DEFAULT 'Pending', created TEXT);
        """)
        if c.execute("SELECT COUNT(*) FROM workers").fetchone()[0]==0:
            c.executemany("INSERT INTO workers VALUES(?,?,?,?,?)",[
            (1,"Asha Kumar","Site Assistant","Construction",800),(2,"Ravi Sharma","Electrician","Construction",950),
            (3,"Priya Singh","Facility Assistant","College",750),(4,"Arun Das","Maintenance Staff","College",850)])
def worker(wid=1):
    with connect() as c:return c.execute("SELECT * FROM workers WHERE id=?",(wid,)).fetchone()
def shift_for(wid=1):
    with connect() as c:return c.execute("SELECT * FROM shifts WHERE worker_id=? AND day=? ORDER BY id DESC LIMIT 1",(wid,date.today().isoformat())).fetchone()
@app.route("/")
def index():
    view=request.args.get("view","worker"); industry=request.args.get("industry","Construction")
    if industry not in INDUSTRIES: industry="Construction"
    w=worker(1); sh=shift_for()
    hours=0
    if sh and sh["cin"]:
        start=datetime.strptime(sh["cin"],"%Y-%m-%d %H:%M:%S")
        end=datetime.strptime(sh["cout"],"%Y-%m-%d %H:%M:%S") if sh["cout"] else datetime.now()
        hours=max(0,(end-start).total_seconds()/3600)
    ot=max(0,hours-8); rate=w["rate"]/8
    pay=(w["rate"]+ot*rate*1.5) if sh and sh["cin"] else 0
    with connect() as c:
        workers=c.execute("SELECT * FROM workers WHERE industry=?",(industry,)).fetchall()
        attendance=c.execute("SELECT s.*,w.name,w.role,w.industry FROM shifts s JOIN workers w ON w.id=s.worker_id WHERE s.day=? AND w.industry=?",(date.today().isoformat(),industry)).fetchall()
        reports=c.execute("SELECT * FROM reports ORDER BY id DESC").fetchall()
        report_count=c.execute("SELECT COUNT(*) FROM reports").fetchone()[0]
        open_count=c.execute("SELECT COUNT(*) FROM reports WHERE status!='Resolved'").fetchone()[0]
    return render_template("index.html",view=view,industry=industry,industries=INDUSTRIES,w=w,sh=sh,hours=round(hours,2),ot=round(ot,2),pay=round(pay,2),workers=workers,attendance=attendance,reports=reports,report_count=report_count,open_count=open_count)
@app.post("/attendance/<action>")
def attendance(action):
    wid=int(request.form.get("worker_id","1")); w=worker(wid); now=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sh=shift_for(wid)
    with connect() as c:
        if action=="in":
            if sh and sh["cin"] and not sh["cout"]: flash("Already checked in.","error")
            else:c.execute("INSERT INTO shifts(worker_id,day,cin) VALUES(?,?,?)",(wid,date.today().isoformat(),now)); flash("Check-in saved.","success")
        elif action=="out":
            if not sh or not sh["cin"] or sh["cout"]:flash("Check in first.","error")
            else:c.execute("UPDATE shifts SET cout=? WHERE id=?",(now,sh["id"]));flash("Check-out saved.","success")
    return redirect(url_for("index",view="worker",industry=w["industry"]))
@app.post("/reports")
def report():
    name=request.form.get("name","").strip()[:80]; industry=request.form.get("industry","Construction"); category=request.form.get("category","Other"); details=request.form.get("details","").strip()[:1000]
    if industry not in INDUSTRIES:industry="Construction"
    if name and details:
        with connect() as c:c.execute("INSERT INTO reports(name,industry,category,details,status,created) VALUES(?,?,?,?,?,?)",(name,industry,category,details,"Pending",datetime.now().strftime("%d %b %H:%M")))
        flash("Report submitted to the admin dashboard.","success")
    else:flash("Please enter your name and report details.","error")
    return redirect(url_for("index",view="worker",industry=industry))
@app.post("/status/<int:rid>")
def status(rid):
    value=request.form.get("status","Pending")
    if value not in ["Pending","In Progress","Resolved"]:value="Pending"
    with connect() as c:c.execute("UPDATE reports SET status=? WHERE id=?",(value,rid))
    flash("Report status updated.","success")
    return redirect(url_for("index",view="admin",industry=request.form.get("industry","Construction")))
if __name__=="__main__":init();app.run(debug=True)
