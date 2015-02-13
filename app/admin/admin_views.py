from flask import render_template, redirect, request, session, flash, url_for
from flask import Blueprint
from functools import wraps
from app.forms import AdminLoginForm, UserLoginForm, UserRegisterForm


admin = Blueprint('admin', __name__, url_prefix="/admin")


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("admin") is not None:
            return f(*args, **kwargs)
        else:
            flash("Please log in first...", "error")
            next_url = request.url
            login_url = "%s?next=%s" % (url_for("admin.admin_login"), next_url)
            return redirect(login_url)
    return decorated_function


@admin.route("/")
@login_required
def admin_index():
    return render_template("admin/index.html")


@admin.route("/login", methods=["GET", "POST"])
def admin_login():
    form = AdminLoginForm()

    # if "admin" in session:
    #     return redirect(url_for("admin.admin_index"))

    if request.method == "POST":
        if form.validate() == False:
            flash("invalid credentials")
            return render_template("admin/login.html", form=form)
        else:
            session["admin"] = form.email.data
            flash("Anda sudah berhasil masuk, selamat!", category="info")
            return redirect(request.args.get("next") or url_for("admin.admin_index"))
    elif request.method == "GET":
        return render_template("/admin/login.html", form=form)



@admin.route("/grabber", methods=["GET", "POST"])
@login_required
def admin_grab():
    """
    admin update database by utilizing google images api.
    1. show the post form
    2. filter the grabbed content
    3. post!

    pake get aja
    jika ada parameter ?query= maka search lah
    else tampilkan form input kosong gitu aje

    method POST dipake ketika insert ke database saje

    guide on ajax.googleapis request
    https://developers.google.com/image-search/v1/jsondevguide
    imgsz = image size
    rsz = results (1-8)
    start = pagination (1-8)

    """

    # if we have query params in url:
    if request.args.get("query"):

        query = request.args.get("query").replace(" ", "%20")
        jumper = range(0, 64, 8)  # [0, 8, ..., 64]

        container = []

        for jump in jumper:
            # build the url
            url = "http://ajax.googleapis.com/ajax/services/search/images?v=1.0&imgsz=large&rsz=8&start=%s&q=%s" % (jump, query)

            # show the search results
            data = json.loads(urllib2.urlopen(url).read())["responseData"]["results"]
            container += data  # appending data

        return render_template("admin_post.html", data=container)

    # if request method is post, ready to insert into database
    if request.method == "POST":
        """
        download the image[s] to some dir [ex: temp_assets]
        and run: python dist_img_to_dir.py temp_assets
        done! :)
        """
        return "sukses"
        
    # else, show template with form and blank table
    print "autoreloaded!"
    return render_template("admin/admin_post.html")


@admin.route("/logout")
def admin_logout():
    if "admin" not in session:
        return redirect(url_for("admin_login"))
    session.pop("admin", None)
    #return redirect(url_for("index"))
    return redirect("/")


@admin.route("/flot")
def flot():
    return render_template("admin/flot.html")

@admin.route("/morris")
def morris():
	return render_template("admin/morris.html")

@admin.route("/tables")
def tables():
	return render_template("admin/tables.html")

@admin.route("/forms")
def forms():
	return render_template("admin/forms.html")

@admin.route("/panels-wells")
def panels_wells():
	return render_template("admin/panels-wells.html")

@admin.route("/buttons")
def buttons():
	return render_template("admin/buttons.html")

@admin.route("/notifications")
def notifications():
	return render_template("admin/notifications.html")

@admin.route("/typography")
def typography():
	return render_template("admin/typography.html")

@admin.route("/grid")
def grid():
	return render_template("admin/grid.html")

@admin.route("/blank")
def blank():
	return render_template("admin/blank.html")

@admin.route("/login")
def login():
	return render_template("admin/login.html")
