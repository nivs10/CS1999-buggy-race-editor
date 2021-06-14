from flask import Flask, render_template, request, jsonify
import sqlite3 as sql

# app - The flask application where all the magical things are configured.
app = Flask(__name__)

# Constants - Stuff that we need to know that won't ever change!
DATABASE_FILE = "database.db"
DEFAULT_BUGGY_ID = "1"
BUGGY_RACE_SERVER_URL = "https://rhul.buggyrace.net"

#------------------------------------------------------------
# the index page
#------------------------------------------------------------
@app.route('/')
def home():
    return render_template('index.html', server_url=BUGGY_RACE_SERVER_URL)

#------------------------------------------------------------
# Buggy Cost Calculator
#------------------------------------------------------------

def cost():
    con = sql.connect(DATABASE_FILE)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM buggies")
    record = cur.fetchone()
    
    buggy_cost_file = 'buggy_cost.csv'
    lines = open(buggy_cost_file).readlines()
   
    items = []
    costs = []
    
    for line in lines:
        option, price = line.strip().split(',')
        if 'Cost' in line:
            pass
        else:
            items.append(str(option))
            costs.append(int(price))
    
    qty_wheels = record['qty_wheels']
    power_type = record['power_type']
    power_units = record['power_units']
    aux_power_type = record['aux_power_type']
    aux_power_units = record['aux_power_units']
    hamster_booster = record['hamster_booster']
    flag_color = record['flag_color']
    flag_pattern = record['flag_pattern']
    flag_color_secondary = record['flag_color_secondary']
    tyres = record['tyres']
    qty_tyres = record['qty_tyres']
    armour = record['armour']
    attack = record['attack']
    qty_attacks = record['qty_attacks']
    fireproof = record['fireproof']
    insulated = record['insulated']
    antibiotic = record['antibiotic']
    banging = record['banging']
    algo = record['algo']

    power_type_location = items.index(power_type)
    aux_power_type_location = items.index(aux_power_type)
    hamster_booster_location = items.index('hamster_booster')
    tyres_location = items.index(tyres)
    armour_location = items.index(armour)
    attack_location = items.index(attack)
    fireproof_location = items.index('fireproof') #boolean
    insulated_location = items.index('insulated') #boolean
    antibiotic_location = items.index('antibiotic') #boolean
    banging_location = items.index('banging') #boolean
	
    power_type_cost = costs[power_type_location]
    aux_power_type_cost = costs[aux_power_type_location]
    hamster_booster_cost = costs[hamster_booster_location]
    tyres_cost = costs[tyres_location]
    armour_cost = costs[armour_location]
    attack_cost = costs[attack_location]
    
    power_cost = power_units * power_type_cost
    aux_power_cost = aux_power_units * aux_power_type_cost
    total_hamster_booster_cost = hamster_booster * hamster_booster_cost
    total_tyres_cost = qty_tyres * tyres_cost
    total_attack_cost = qty_attacks * attack_cost
	
    if armour_cost > 4:
	    total_armour_cost = armour_cost * (1 + (0.1 * (qty_tyres - 4)))
    
    if fireproof == 'true':
        fireproof_cost = costs[fireproof_location]
    else:
        fireproof_cost = 0
    
    if insulated == 'true':
        insulated_cost = costs[insulated_location]
    else:
        insulated_cost = 0
    
    if antibiotic == 'true':
        antibiotic_location = items.index('antibiotic')
        antibiotic_cost = costs[antibiotic_location]
    else:
        antibiotic_cost = 0
    
    if banging == 'true':
        banging_location = items.index('banging')
        banging_cost = costs[banging_location]
    else:
        banging_cost = 0
    
    total_buggy_cost = power_cost + aux_power_cost + total_hamster_booster_cost + total_tyres_cost + total_armour_cost + total_attack_cost + fireproof_cost + insulated_cost + antibiotic_cost + banging_cost
	
    return int(total_buggy_cost)

#------------------------------------------------------------
# Rules
#------------------------------------------------------------

    #TBC

#------------------------------------------------------------
# creating a new buggy:
#  if it's a POST request process the submitted data
#  but if it's a GET request, just show the form
#------------------------------------------------------------
@app.route('/new', methods = ['POST', 'GET'])
def create_buggy():
    if request.method == 'GET':
        con = sql.connect(DATABASE_FILE)
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM buggies")
        record = cur.fetchone(); 
        return render_template("buggy-form.html", buggy = record)
    elif request.method == 'POST':
        msg=""
        qty_wheels = request.form['qty_wheels']
        power_type = request.form['power_type']
        power_units = request.form['power_units']
        aux_power_type = request.form['aux_power_type']
        aux_power_units = request.form['aux_power_units']
        hamster_booster = request.form['hamster_booster']
        flag_color = request.form['flag_color']
        flag_pattern = request.form['flag_pattern']
        flag_color_secondary = request.form['flag_color_secondary']
        tyres = request.form['tyres']
        qty_tyres = request.form['qty_tyres']
        armour = request.form['armour']
        attack = request.form['attack']
        qty_attacks = request.form['qty_attacks']
        fireproof = request.form['fireproof']
        insulated = request.form['insulated']
        antibiotic = request.form['antibiotic']
        banging = request.form['banging']
        algo = request.form['algo']

        while qty_wheels.isdigit():
            try:
                with sql.connect(DATABASE_FILE) as con:
                    cur = con.cursor()
                    cur.execute(
                        "UPDATE buggies set qty_wheels=?, power_type=?, power_units=?, aux_power_type=?, aux_power_units=?, hamster_booster=?, flag_color=?, flag_pattern=?, flag_color_secondary=?, tyres=?, qty_tyres=?, armour=?, attack=?, qty_attacks=?, fireproof=?, insulated=?, antibiotic=?, banging=?, algo=? WHERE id=?",
                        (qty_wheels, power_type, power_units, aux_power_type, aux_power_units, hamster_booster, flag_color, flag_pattern, flag_color_secondary, tyres, qty_tyres, armour, attack, qty_attacks, fireproof, insulated, antibiotic, banging, algo, DEFAULT_BUGGY_ID)
                    )
                    con.commit()
                    buggy_cost = cost()
                    msg = f"Record successfully saved - Your current is cost is {buggy_cost}"
            except:
                con.rollback()
                msg = "error in update operation"
            finally:
                con.close()
            return render_template("updated.html", msg = msg)
        else:
            msg = "invalid entry, please try again"
            return render_template("buggy-form.html", msg = msg)

#------------------------------------------------------------
# a page for displaying the buggy
#------------------------------------------------------------
@app.route('/buggy')
def show_buggies():
    con = sql.connect(DATABASE_FILE)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM buggies")
    record = cur.fetchone(); 
    return render_template("buggy.html", buggy = record, buggy_cost = cost())

#------------------------------------------------------------
# a placeholder page for editing the buggy: you'll need
# to change this when you tackle task 2-EDIT
#------------------------------------------------------------
@app.route('/edit')
def edit_buggy():
    return render_template("buggy-form.html")

#------------------------------------------------------------
# Poster
#------------------------------------------------------------
@app.route('/poster')
def poster():
   return render_template('poster.html')

#------------------------------------------------------------
# You probably don't need to edit this... unless you want to ;)
#
# get JSON from current record
#  This reads the buggy record from the database, turns it
#  into JSON format (excluding any empty values), and returns
#  it. There's no .html template here because it's *only* returning
#  the data, so in effect jsonify() is rendering the data.
#------------------------------------------------------------
@app.route('/json')
def summary():
    con = sql.connect(DATABASE_FILE)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM buggies WHERE id=? LIMIT 1", (DEFAULT_BUGGY_ID))

    buggies = dict(zip([column[0] for column in cur.description], cur.fetchone())).items() 
    return jsonify({ key: val for key, val in buggies if (val != "" and val is not None) })

# You shouldn't need to add anything below this!
if __name__ == '__main__':
    app.run(debug = True, host="0.0.0.0")
