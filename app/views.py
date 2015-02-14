from flask import render_template, request, redirect, send_from_directory, session, flash, url_for
from flask import make_response # untuk sitemap
from app import app
# untuk find_one based on data id => db.freewaredata.find_one({'_id': ObjectId(file_id)})
# atom feed
from werkzeug.contrib.atom import AtomFeed
from bson.objectid import ObjectId 
from filters import slugify, splitter, onlychars, get_first_part, get_last_part, formattime, cleanurl
from functools import wraps
from forms import AdminLoginForm, UserLoginForm, UserRegisterForm
import datetime
import pymongo
from flask.ext.mail import Message, Mail


# setup database mongo
c = pymongo.Connection()
dbentity = c["entities"]  # nanti ada dbentity.user, dbentity.admin, dll


@app.template_filter()
def slug(s):
    """ 
    transform words into slug 
    usage: {{ string|slug }}
    """
    return slugify(s)

@app.template_filter("humanize")
def jinja2_filter_humanize(date):
    """
    convert datetime object into human readable
    usage humanize(dateobject) or if in template
    {{ dateobject|humanize }}
    """
    import humanize
    secs = datetime.datetime.now() - date
    secs = int(secs.total_seconds())
    date = humanize.naturaltime(datetime.datetime.now() - datetime.timedelta(seconds=secs))  # 10 seconds ago
    return date


# handle robots.txt file
@app.route("/robots.txt")
def robots():
    # point to robots.txt files
    return send_from_directory(app.static_folder, request.path[1:])


def user_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("username") is not None:
            return f(*args, **kwargs)
        else:
            flash("Please log in first...", "error")
            next_url = request.url
            login_url = "%s?next=%s" % (url_for("users_login"), next_url)
            return redirect(login_url)
    return decorated_function


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/sitemap.xml")
def sitemap():
    # data = db.freewaredata.find()
    # sitemap_xml = render_template("sitemap.xml", data=data)
    # response = make_response(sitemap_xml)
    # response.headers['Content-Type'] = 'application/xml'

    # return response
    pass

@app.route('/recent.atom')
def recent_feed():
    # http://werkzeug.pocoo.org/docs/contrib/atom/ 
    # wajibun: id(link) dan updated
    # feed = AtomFeed('Recent Articles',
    #                feed_url = request.url, url=request.url_root)
    # data = datas
    # for d in data:
    #    feed.add(d['nama'], content_type='html', id=d['id'], updated=datetime.datetime.now())
    # return feed.get_response()
    pass
