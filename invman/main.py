from flask import (
    Blueprint,
    render_template,
    request,
    url_for,
    g,
    redirect,
    session,
    jsonify,
)
from invman.db import get_db
from invman.start import login_required

bp = Blueprint("main", __name__, url_prefix="/main")

# Required functions.


def product_list(id):
    """ Retrieves products which are in the product table. """

    db = get_db()
    product_list = db.execute(
        "SELECT product_id, product_name, quantity FROM product WHERE for_business = ? AND quantity > -1",
        (id,),
    ).fetchall()
    return product_list


def get_product(location, product_id, quantity):
    """ Used by the movement route to get a product from a location. """

    product_array = []
    db = get_db()
    b_id = session.get("user_id")
    if location == "product_factory":
        # Get product from product table, deduct the quantity.
        ogquantity = db.execute(
            "SELECT quantity FROM product WHERE product_id = ? AND for_business = ?",
            (product_id, b_id,),
        ).fetchone()[0]
        newquantity = ogquantity - quantity
        if int(newquantity) < 0:
            raise Exception("Invalid quantity.")
        query = (
            "UPDATE product SET quantity = ? WHERE product_id = ? AND for_business = ?"
        )
        db.execute(query, (newquantity, product_id, b_id))
        p = db.execute(
            "SELECT product_id FROM product WHERE for_business = ? AND product_id = ?",
            (b_id, product_id,),
        ).fetchone()
        product_array = list(p)
        product_array.append(quantity)
        db.commit()
        return product_array
    else:
        ogquantity = db.execute(
            "SELECT qty FROM warehouse WHERE loc_id = ? AND prod_id = ? AND b_id = ?",
            (location, product_id, b_id,),
        ).fetchone()[0]
        newquantity = ogquantity - quantity
        if int(newquantity) < 0:
            raise Exception("Invalid quantity.")
        query = (
            "UPDATE warehouse SET qty = ? where loc_id = ? AND prod_id = ? AND b_id = ?"
        )
        db.execute(query, (newquantity, location, product_id, b_id,))
        p = db.execute(
            "SELECT prod_id FROM warehouse WHERE prod_id = ? AND loc_id = ? AND b_id = ?",
            (product_id, location, b_id,),
        ).fetchone()
        if int(newquantity) == 0:
            db.execute(
                "DELETE FROM warehouse WHERE b_id = ? AND prod_id = ? AND loc_id = ?",
                (b_id, product_id, location,),
            )
        product_array = list(p)
        product_array.append(quantity)
        db.commit()
        return product_array


def set_product(location, product_array):
    """ Used by the movement route to set a product to a location. """
    # Sets the product to a location, updates quantity if the product already exists
    db = get_db()
    b_id = session.get("user_id")
    product_id = product_array[0]
    quantity = product_array[1]
    if location != "Move out":
        product_exists = db.execute(
            "SELECT * FROM warehouse WHERE prod_id = ? AND loc_id = ? AND b_id = ?",
            (product_id, location, b_id),
        ).fetchone()
        if product_exists:
            ogquantity = db.execute(
                "SELECT qty FROM warehouse WHERE loc_id = ? AND prod_id = ? AND b_id = ?",
                (location, product_id, b_id,),
            ).fetchone()[0]
            newquantity = ogquantity + quantity
            query = "UPDATE warehouse SET qty = ? WHERE loc_id = ? AND prod_id = ? AND b_id = ?"
            db.execute(query, (newquantity, location, product_id, b_id,))
            db.commit()
        else:
            db.execute(
                "INSERT INTO warehouse (b_id, prod_id, qty, loc_id) values (?, ?, ?, ?)",
                (b_id, product_id, quantity, location),
            )
            db.commit()


def balance_quantity(quantity, product_id, location):
    """ Used by the product route to add or subtract quantity of a product."""

    db = get_db()
    if location == "product_factory":
        ogquantity = db.execute(
            "SELECT quantity from product WHERE product_id = ?", (product_id,)
        ).fetchone()
        ogquantity = ogquantity["quantity"]
        newquantity = ogquantity + quantity
        if int(newquantity) < 0:
            raise Exception("Invalid quantity.")
        query = "UPDATE product SET quantity = ? where product_id = ?"
        db.execute(query, (newquantity, product_id))
        db.commit()


def check_warehouse():
    """ Returns a list of location IDs which has products stored """
    db = get_db()
    b_id = session.get("user_id")
    query = "SELECT loc_id FROM warehouse where b_id = ?"
    warehouses = db.execute(query, (b_id,)).fetchall()
    loc_list = []
    for lids in warehouses:
        if lids[0] not in loc_list:
            loc_list.append(lids[0])
    return loc_list


def products_at_locations():
    """ Creates a dictionary with loc IDs as keys and products stored there as values """
    db = get_db()
    b_id = session.get("user_id")
    locs = check_warehouse()
    warehouse = {}
    for ids in locs:
        l = []
        prods = db.execute(
            "SELECT prod_id, qty FROM warehouse where b_id = ? AND loc_id = ?",
            (b_id, ids,),
        ).fetchall()
        locname = db.execute(
            "SELECT location_name FROM location WHERE location_id = ? AND for_business = ?",
            (ids, b_id,),
        ).fetchone()["location_name"]
        for data in prods:
            prodname = db.execute(
                "SELECT product_name FROM product WHERE for_business = ? AND product_id = ?",
                (b_id, data["prod_id"],),
            ).fetchone()["product_name"]
            l.append([data["prod_id"] + " " + prodname, data["qty"]])
        warehouse[locname] = l
    return warehouse


def logmovements(
    movement_id, from_location, to_location, prod_id, qty,
):
    """ Used by the movement route to log movements. """
    db = get_db()
    b_id = session.get("user_id")
    db.execute(
        "INSERT INTO movement (movement_id, from_location, to_location, prod_id, qty, b_id)"
        "VALUES (?, ?, ?, ?, ?, ?)",
        (movement_id, from_location, to_location, prod_id, qty, b_id,),
    )
    db.commit()


# Dynamic routes


@bp.route("/_getquantity/<prd>/<loc>", methods=("GET",))
def getquantity(prd, loc):
    """ Used by the movement page to get the quantity of a product."""
    db = get_db()
    b_id = session.get("user_id")
    qty = {}
    if loc == "Product Factory":
        if prd != "None":
            q = db.execute(
                "SELECT quantity FROM product WHERE product_id = ? AND for_business = ?",
                (prd, b_id,),
            ).fetchone()
            qty["qty"] = str(q["quantity"])
        else:
            pass
    else:
        q = db.execute(
            "SELECT qty FROM warehouse WHERE prod_id = ? AND b_id = ? AND loc_id = ?",
            (prd, b_id, loc,),
        ).fetchone()
        qty["qty"] = str(q["qty"])
    return qty


@bp.route("/_loadproducts/<lid>", methods=("GET",))
def loadproducts(lid):
    """ Used by the movement page to retrieve products at a particular location. """
    db = get_db()

    b_id = session.get("user_id")
    product_list = {}

    if lid == "Product Factory":
        query = "SELECT product_id, product_name FROM product WHERE for_business = ? AND quantity > 0"
        warehouses = db.execute(query, (b_id,)).fetchall()
        for products in warehouses:
            product_list[products[0]] = products[1]
    else:
        query = "SELECT prod_id FROM warehouse where loc_id = ? AND b_id = ?"
        warehouses = db.execute(query, (lid, b_id,)).fetchall()
        for products in warehouses:
            product_name = db.execute(
                "SELECT product_name FROM product WHERE product_id = ? AND for_business = ?",
                (products["prod_id"], b_id,),
            ).fetchone()
            product_list[products["prod_id"]] = product_name["product_name"]

    return jsonify(product_list)


@bp.route("/<lid>/deleteloc", methods=("GET",))
def delete_loc(lid):
    """ Used by the location page to delete a location. Also deletes any products at that location. """

    db = get_db()
    b_id = session.get("user_id")
    db.execute(
        "DELETE FROM location WHERE location_id = ? AND for_business = ?", (lid, b_id,)
    )
    db.commit()
    db.execute("DELETE FROM warehouse WHERE loc_id = ? AND b_id = ?", (lid, b_id,))
    db.commit()
    return redirect(url_for("main.locations"))


@bp.route("/<id>/delete", methods=("GET",))
def delete(id):
    """ Used by the product page to delete a product. """

    db = get_db()
    b_id = session.get("user_id")
    query = "UPDATE product SET quantity = -1 WHERE product_id = ? AND for_business = ?"
    db.execute(query, (id, b_id,))
    db.commit()
    return redirect(url_for("main.products"))


# Routes


@bp.route("/")
def root():
    return redirect(url_for("main.products"))


@bp.route("/products", methods=("GET", "POST"))
@login_required
def products():
    """ The product route. """

    db = get_db()  # Get the database connection.
    b_id = session.get("user_id")

    error = None
    # Request to add/update a product to the product table.
    if request.method == "POST":
        if "submit_product" in request.form:
            try:
                prod_id = request.form["insert_product_id"]
                prod_name = request.form["insert_product_name"]
                prod_qty = int(request.form["insert_product_qty"])
                if prod_qty < 0:
                    raise Exception("Invalid quantity.")
                db.execute(
                    "INSERT INTO product (product_id, product_name, quantity, for_business) values (?, ?, ?, ?)",
                    (prod_id, prod_name, prod_qty, b_id,),
                )
                db.commit()
                return redirect(url_for("main.products"))
            except Exception as e:
                if "UNIQUE constraint failed" in str(e):
                    error = "Error adding product: A product with that ID already exists or has been created before."
                elif "invalid literal for int() with base 10:" in str(e):
                    error = "Invalid quantity."
                else:
                    error = str(e)
        if "update_product" in request.form:
            try:
                prod_selected = request.form["select_product"].split(",")[0]
                prod_name = request.form["update_product_name"]
                prod_qty = int(request.form["update_product_qty"])

                if prod_name:
                    query = "UPDATE product SET product_name = ? WHERE product_id = ?"
                    db.execute(query, (prod_name, prod_selected))
                    db.commit()
                balance_quantity(
                    prod_qty, prod_selected, location="product_factory",
                )
                db.commit()
                return redirect(url_for("main.products"))
            except Exception as e:
                if "invalid literal for int() with base 10:" in str(e):
                    error = "Invalid quantity."
                else:
                    error = str(e)
        else:
            pass
    # Retrieve and display products on the page.
    prod_list = product_list(b_id)
    return render_template(
        "products.html", products=prod_list, title="Products", error=error
    )


@bp.route("/locations", methods=("GET", "POST"))
@login_required
def locations():
    """ The location route. """

    db = get_db()  # Get the database connection
    b_id = session.get("user_id")
    error = None

    # Request to add a location to the location table.
    if request.method == "POST":
        if "submit_location" in request.form:
            try:
                loc_id = request.form["insert_location_id"]
                loc_name = request.form["insert_location_name"]
                db.execute(
                    "INSERT INTO location (location_id, location_name, for_business) values(?, ?, ?)",
                    (loc_id, loc_name, b_id,),
                )
                db.commit()
                return redirect(url_for("main.locations"))
            except Exception as e:
                if "UNIQUE constraint failed:" in str(e):
                    error = "Location with that ID already exists."
                else:
                    error = str(e)
        if "update_location" in request.form:
            try:
                loc_selected = request.form["select-location"].split(",")[0]
                new_locname = request.form["location-name-update"]
                db.execute(
                    "UPDATE location SET location_name = ? WHERE location_id = ?",
                    (new_locname, loc_selected,),
                )
                db.commit()
                return redirect(url_for("main.locations"))
            except Exception as e:
                error = str(e)
        else:
            pass

    # Retrieve locations and render the page.
    location_list = db.execute(
        "SELECT location_id, location_name FROM location where for_business = ?",
        (b_id,),
    ).fetchall()
    return render_template(
        "locations.html", title="Locations", locations=location_list, error=error
    )


@bp.route("/movement", methods=("GET", "POST",))
@login_required
def movements():
    """ Movement route. """

    db = get_db()
    b_id = session.get("user_id")

    error = None

    if request.method == "POST":
        # movement request - move product to a location
        try:
            if "movement-operation" in request.form:
                move_from = request.form["move-from"].split(",")[0]
                prod = request.form["product-to-move"].split(",")[0]
                quantity = int(request.form["quantity-to-move"])
                if quantity < 0:
                    raise Exception("Invalid quantity.")
                move_to = request.form["move-to"].split(",")[0]
                product_array = get_product(move_from, prod, quantity)
                set_product(move_to, product_array)
                logmovements("Movement", move_from, move_to, prod, quantity)
            if "sales-operation" in request.form:
                move_from = request.form["sales-location"].split(",")[0]
                prod = request.form["sales-product"].split(",")[0]
                quantity = int(request.form["quantity-to-sell"])
                if quantity < 0:
                    raise Exception("Invalid quantity.")
                product_array = get_product(move_from, prod, quantity)
                logmovements("Sales", move_from, " ", prod, quantity)
            if "purchase-operation" in request.form:
                move_from = "product_factory"
                prod = request.form["purchase-product"].split(",")[0]
                quantity = int(request.form["quantity-to-purchase"])
                if quantity < 0:
                    raise Exception("Invalid quantity.")
                move_to = request.form["move-purchase"].split(",")[0]
                product_array = get_product(move_from, prod, quantity)
                set_product(move_to, product_array)
                logmovements("Purchase", " ", move_to, prod, quantity)
            return redirect(url_for("main.movements"))
        except Exception as e:
            if "'NoneType' object is not subscriptable" in str(e):
                error = "Error moving: Invalid product."
            else:
                error = "Error moving: " + str(e)

    all_products = product_list(b_id)  # All products in the product table
    all_locations = db.execute(
        "SELECT location_id, location_name FROM location WHERE for_business = ?",
        (b_id,),
    ).fetchall()  # All the locations

    warehouses = []  # Locations which have products stored there.
    lids = check_warehouse()
    for ids in lids:
        query = "SELECT location_id, location_name FROM location WHERE location_id = ?"
        l = db.execute(query, (ids,)).fetchone()
        warehouses.append(l)

    locations_with_products = products_at_locations()

    return render_template(
        "movement.html",
        title="Movement",
        warehouses=warehouses,
        allproducts=all_products,
        alllocations=all_locations,
        locationmap=locations_with_products,
        error=error,
    )


@bp.route("/movementlogs", methods=("GET", "POST",))
@login_required
def movementlogs():
    """ Movement logs route. """
    db = get_db()
    b_id = session.get("user_id")

    logtable = db.execute("SELECT * FROM movement WHERE b_id = ?", (b_id,)).fetchall()
    business_name = db.execute(
        "SELECT business_name FROM business WHERE business_id = ?", (b_id,)
    ).fetchone()

    return render_template(
        "movementlogs.html",
        logtable=logtable,
        business_name=business_name,
        title="Logs",
    )


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("start.index"))
