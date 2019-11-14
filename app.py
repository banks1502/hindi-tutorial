from flask import Flask, render_template, redirect, \
    url_for, request, session, flash, g, make_response, send_file
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from functools import wraps
from pymysql import escape_string as thwart
from datetime import datetime,timedelta
from time import mktime
import os
import time
from wtforms import Form, BooleanField, TextField, PasswordField, validators
from passlib.hash import sha256_crypt
from dbconnect import connection
import gc
# Dictates urls and linkage
from content_management import Content
from flask_mail import Mail, Message


app = Flask(__name__)
app.secret_key = 'hindi-tutorial'

app.config.update(
	DEBUG=False,
	#EMAIL SETTINGS
	MAIL_SERVER='mail.cloudaccess.net',#'smtp.gmail.com',
	MAIL_PORT=587,#465,
    #MAIL_USE_SSL=True,
    MAIL_USE_TSL=True,
    MAIL_USERNAME = 'info@bitesofjoy.in',
	MAIL_PASSWORD = '3idiots@123'
	)
mail = Mail(app)


# list of topics by {TOPIC:["TITLE", "URL"]}
TOPIC_DICT = Content()

class User:
    def username(self):
        try:
            email = str(session['email'])
            return str(session['email'])
        except:
            return("guest")

user = User()

def userinformation():
    try:
        #client_name = (session['username'])
        client_email =(session['email'])
        client_name = client_email
        guest = False
    except:
        guest = True
        client_name = "Guest"
        
    if not guest:
        try:
            c,conn = connection()
            c.execute("SELECT * FROM users WHERE email = (%s)",
                    (thwart(client_email)))
            data = c.fetchone()
            settings = data[3]
            tracking = data[4]
            rank = data[5]
        except Exception as e:
            pass

    else:
        settings = [0,0]
        tracking = [0,0]
        rank = [0,0]
        
    return client_name, settings, tracking, rank

def update_user_tracking():
    try:
        completed = str(request.args['completed'])
        if completed in str(TOPIC_DICT.values()):
            client_name, settings, tracking, rank = userinformation()
            if tracking == None:
                tracking = completed
            else:
                if completed not in tracking:
                    tracking = tracking+","+completed
            
            c,conn = connection()
            c.execute("UPDATE users SET tracking = %s WHERE email = %s",
                    (thwart(tracking),thwart(client_name)))
            conn.commit()
            c.close()
            conn.close()
            client_name, settings, tracking, rank = userinformation()

        else:
            pass

            
    except Exception as e:
        pass


class RegistrationForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=20)])
    email = TextField('Email Address', [validators.Length(min=6, max=50)])
    password = PasswordField('New Password', [
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the <a href="/about/tos" target="blank" of Service> Terms of Use </a> and <a href="/about/privacy-policy" target="blank">Privacy Notice</a>', [validators.Required()])
    
class ChangePasswordForm(Form):
    email = TextField('Email Address', [validators.Length(min=6, max=50)])
    password = PasswordField('Current Password')
    npassword = PasswordField('New Password',[
        validators.EqualTo('rnpassword', message='Passwords must match')
    ])
    rnpassword = PasswordField('Re-enter New Password')

## LIVE VERSION ####
@app.route('/robots.txt/')
def robots():
    return("User-agent: *\nDisallow: /register/\nDisallow: /login/\nDisallow: /donation-success/")

###### DEV VERSION #####
##@app.route('/robots.txt/')
##def robots():
##    return("User-agent: *\nDisallow: /")
##

@app.route('/sitemap.xml', methods=['GET'])
def sitemap():
    try:
      """Generate sitemap.xml. Makes a list of urls and date modified."""
      pages=[]
      ten_days_ago=(datetime.now() - timedelta(days=7)).date().isoformat()
      # static pages
      for rule in app.url_map.iter_rules():
          if "GET" in rule.methods and len(rule.arguments)==0:
              pages.append(
                           ["learn-hindi.herokuapp.com"+str(rule.rule),ten_days_ago]
                           )

      sitemap_xml = render_template('sitemap_template.xml', pages=pages)
      response= make_response(sitemap_xml)
      response.headers["Content-Type"] = "application/xml"    
    
      return response
    except Exception as e:
        return(str(e))

    
@app.route('/', methods=['GET', 'POST'])
def main():
    form = RegistrationForm(request.form)
    try:
        c,conn = connection()
        error = None
        if request.method == 'POST':
            try:
                data = c.execute("SELECT * FROM users WHERE email = (%s)",
                        thwart(request.form['email']))
                data = c.fetchone()[1]
                
                if sha256_crypt.verify(request.form['password'], data):
                    session['logged_in'] = True
                    session['email'] = request.form['email']
                    message = request.form['email'] + ', You are now logged in. '
                    flash( message ,'error')

                    #msg = Message('User Creation', sender='contact@example.com', recipients=['bitesofjoy03@gmail.com'])
                    #msg.body = """
                    #        From: %s <%s>
                    #        %s
                    #        """ % (request.form['username'], request.form['email'], message)
                    #mail.send(msg)"""

                    return redirect(url_for('dashboard'))
            except Exception as e:
                flash("What are you doing?")

            try:                
                if request.method == 'POST' and form.validate():
                    username = form.username.data
                    email = form.email.data

                    password = sha256_crypt.encrypt((str(form.password.data)))
                    c,conn = connection()

                    x = c.execute("SELECT * FROM users WHERE email = (%s)",
                        (thwart(email)))

                    if int(x) > 0:
                        flash("That email is already taken, please choose another")
                        return render_template('register.html', form=form)

                    else:
                        c.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
                            (thwart(username), thwart(password), thwart(email)))
                        conn.commit()
                        flash('Thanks for registering')
                        c.close()
                        conn.close()
                        gc.collect()
                        session['logged_in'] = True
                        session['username'] = username
                        session['email'] = email
                        return redirect(url_for('dashboard'))

            except Exception as e:
                return(str(e))
  
            else:
                flash('Invalid credentials. Try again')
        gc.collect()
        return render_template("main.html", error=error, form=form, page_type = "main")
    except Exception as e:
        return(str(e))


#@app.route('/jinjaman/')
def jinjaman():
    try:
        gc.collect()
        data = [15, '15', 'Python is good','Python, Java, php, SQL, C++','<p><strong>Hey there!</strong></p>']
        return render_template("jinja-templating.html", data = data)
    except Exception as e:
        return(str(e))

'''@app.route('/search/')
def search_results():
    results = []
    search_string = str(request.args['q'])
    #print(request.url,'\n',request.referrer)

    import re

    f = open('sitemap.xml','r')
    res = f.readlines()
    for d in res:
        data = re.findall(search_string,d)
        for i in data:
            flash(re.findall('>(http:\/\/.+)<',i))


    flash("No matching result")
    return redirect(request.referrer)
 
    '''



@app.route('/contact/')
def contact():
    try:
        return render_template("contact.html")
    except Exception as e:
        return(str(e))



@app.route('/email_sent/' , methods=['GET', 'POST'])
def email_sent():
    try:
       if request.method == 'POST':
           name = request.form.get("name")
           email = request.form.get("email")
           subject = request.form.get("subject")
           message = request.form.get("message")
           msg = Message(subject, sender = 'no-reply@bitesofjoy.in', recipients = ['info@bitesofjoy.in'])
           msg.body = 'From:' + email + '\n' + message
           mail.send(msg)
           flash('Thanks !! We have received your message.')
           return redirect(url_for('main'))
    except Exception as e:
        return str(e)


#@app.route('/include_example/')
def include_example():
    try:
        replies = {'Jack':'Cool post',
                   'Jane':'+1',
                   'Erika':'Most definitely',
                   'Bob':'wow',
                   'Carl':'amazing!',}
        return render_template("includes_tutorial.html", replies = replies)
    except Exception as e:
        return(str(e))

#@app.route('/header.py')
def headerpython():
    try:
        gc.collect()
        return render_template("header.py")
    except Exception as e:
        return(str(e))


@app.errorhandler(404)
def page_not_found(e):
    try:
        gc.collect()
        rule = request.path
        if "feed" in rule or "favicon" in rule or "wp-content" in rule or "wp-login" in rule or "wp-login" in rule or "wp-admin" in rule or "xmlrpc" in rule or "tag" in rule or "wp-include" in rule or "style" in rule or "apple-touch" in rule or "genericons" in rule or "topics" in rule or "category" in rule or "index" in rule or "include" in rule or "trackback" in rule or "download" in rule or "viewtopic" in rule or "browserconfig" in rule:
            pass
        else:
            pass
        #flash(str(rule))
        return render_template('404.html'), 404
    except Exception as e:
        return(str(e))

@app.errorhandler(500)
def page_not_found(e):
    return ("Ouch, looks like we're knocked out"), 500


# login required decorator
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap


@app.route('/change-password/', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm(request.form)
    try:
        c,conn = connection()
        
        error = None
        if request.method == 'POST':

            data = c.execute("SELECT * FROM users WHERE email = (%s)",
                    thwart(request.form['email']))
            data = c.fetchone()[1]

            if sha256_crypt.verify(request.form['password'], data):
                #flash('Authentication Successful.')
                if len(request.form['npassword']) > 0:
                    #flash("You wanted to change password")
                    
                    if request.form['npassword'] == request.form['rnpassword'] and len(request.form['npassword']) > 0:
                        try:
                            #flash("new passwords matched")
                            password = sha256_crypt.encrypt((str(request.form['npassword'])))
                            
                            c,conn = connection()
                            
                            data = c.execute("UPDATE users SET password = %s where email = %s",
                            (password,thwart(request.form['email'])))

                            conn.commit()
                            c.close()
                            conn.close()
                            flash("Your password was successfully changed.'")
                        except Exception as e:
                            return(str(e))
                    else:
                        flash("New Passwords do not match!")

                return render_template('change-password.html', form=form)
            else:
                flash('Invalid credentials. Try again')
                error = 'Invalid credentials. Try again'
        gc.collect()          
        return render_template('change-password.html', form=form)
    except Exception as e:
        return(str(e))


@app.route('/login/', methods=['GET','POST'])
def login():
    try:
        c,conn = connection()
        
        error = None
        if request.method == 'POST':

            data = c.execute("SELECT * FROM users WHERE email = (%s)",
                    thwart(request.form['email']))
            data = c.fetchone()[1]
            
            if sha256_crypt.verify(request.form['password'], data):
                session['logged_in'] = True
                session['email'] = request.form['email']
                flash('You are now logged in.')
                return redirect(url_for('dashboard'))

            else:
                error = 'Invalid credentials. Try again'
        gc.collect()
        return render_template('login.html', error=error)
    except Exception as e:
        error = 'Invalid credentials. Try again'
        return render_template('login.html', error=error)

    

@app.route('/logout/')
def logout():
	session.pop('logged_in', None)
	session.clear()
	flash('You have been logged out.')
	gc.collect()
	return redirect(url_for('main'))


@app.route('/register/', methods=['GET', 'POST'])
def register():

    try:
        form = RegistrationForm(request.form)
        if request.method == 'POST' and form.validate():
            #flash("register attempted")

            username = form.username.data
            email = form.email.data

            password = sha256_crypt.encrypt((str(form.password.data)))
            c,conn = connection()

            x = c.execute("SELECT * FROM users WHERE email = (%s)",
                (thwart(email)))

            if int(x) > 0:
                flash("That email is already registered, please choose another")
                return render_template('register.html', form=form)

            else:
                c.execute("INSERT INTO users (username, password, email, tracking) VALUES (%s, %s, %s, %s)",
                    (thwart(username), thwart(password), thwart(email), thwart("/introduction-to-python-programming/")))
                conn.commit()
                flash('Thanks for registering')
                c.close()
                conn.close()
                gc.collect()
                session['email'] = email
                session['logged_in'] = True
                return redirect(url_for('dashboard'))
        gc.collect()
        #flash("hi there.")
        return render_template('register.html', form=form)
    except Exception as e:
        return(str(e))


def topic_completion_percent():
    try:
        client_name, settings, tracking, rank = userinformation()

        try:
            tracking = tracking.split(",")
        except:
            pass

        if tracking == None:
            tracking = []
            #flash("tracking is none")

        completed_percentages = {}
        
        for each_topic in TOPIC_DICT:
            total = 0
            total_complete = 0
            
            for each in TOPIC_DICT[each_topic]:
                total += 1
                for done in tracking:
                    if done == each[1]:
                        total_complete += 1

            percent_complete = int(((total_complete*100)/total))
            completed_percentages[each_topic] = percent_complete


        return completed_percentages
    except:
        for each_topic in TOPIC_DICT:
            total = 0
            total_complete = 0
       
            completed_percentages[each_topic] = 0.0

        return completed_percentages

    pass
    #return basics,pygame,pyopengl,kivy,flask,django,mysql,sqlite,datamanip,dataviz,nltk,svm,clustering,imagerec,forexalgo,robotics,supercomp,tkinter
    
@app.route('/guided-tutorials/', methods=['GET', 'POST'])
@app.route('/topics/', methods=['GET', 'POST'])
@app.route('/begin/', methods=['GET', 'POST'])
@app.route('/dashboard/', methods=['GET', 'POST'])
#@login_required
def dashboard():
    try:
        try:
            client_name, settings, tracking, rank = userinformation()
            gc.collect()

            if client_name == "Guest":
                flash("Welcome Guest, feel free to browse content. Progress tracking is only available for Logged-in users.")
                tracking = ['None']

            update_user_tracking()
            completed_percentages = topic_completion_percent()
            
            return render_template("dashboard.html",topics = TOPIC_DICT,tracking = tracking, completed_percentages=completed_percentages)
        except Exception as e:
            return((str(e), "please report errors to bitesofjoy03@gmail.com"))
    except Exception as e:
        return((str(e), "please report errors to bitesofjoy03@gmail.com"))

@app.route('/about/tos/', methods=['GET', 'POST'])
def terms_of_service():
    return render_template("tos.html")

@app.route('/about/privacy-policy/', methods=['GET', 'POST'])
def privacy_policy():
    return render_template("privacy_policy.html")



@app.route(TOPIC_DICT["Common Things"][0][1], methods=['GET', 'POST'])
def पक्षियों_का_नाम():
    update_user_tracking()
    completed_percentages = topic_completion_percent()
    return render_template("tutorials/Common Things/birds-pakshiyon-naam.html",all_topics =TOPIC_DICT,completed_percentages=completed_percentages, curLink = TOPIC_DICT["Common Things"][0][1], curTitle=TOPIC_DICT["Common Things"][0][0],  nextLink = TOPIC_DICT["Common Things"][1][1], nextTitle = TOPIC_DICT["Common Things"][1][0])



@app.route(TOPIC_DICT["Common Things"][1][1], methods=['GET', 'POST'])
def सरीसृप_और_जलीय_जानवर():
    update_user_tracking()
    completed_percentages = topic_completion_percent()
    return render_template("tutorials/Common Things/reptiles-aquartic-sarisrip-jaliya-janwar.html",all_topics =TOPIC_DICT,completed_percentages=completed_percentages, curLink = TOPIC_DICT["Common Things"][1][1], curTitle=TOPIC_DICT["Common Things"][1][0],  nextLink = TOPIC_DICT["Common Things"][2][1], nextTitle = TOPIC_DICT["Common Things"][2][0])



@app.route(TOPIC_DICT["Common Things"][2][1], methods=['GET', 'POST'])
def पालतू_जानवर():
    update_user_tracking()
    completed_percentages = topic_completion_percent()
    return render_template("tutorials/Common Things/pet-paltu-janwar.html",all_topics =TOPIC_DICT,completed_percentages=completed_percentages, curLink = TOPIC_DICT["Common Things"][2][1], curTitle=TOPIC_DICT["Common Things"][2][0],  nextLink = TOPIC_DICT["Common Things"][3][1], nextTitle = TOPIC_DICT["Common Things"][3][0])



@app.route(TOPIC_DICT["Common Things"][3][1], methods=['GET', 'POST'])
def जंगली_जानवर():
    update_user_tracking()
    completed_percentages = topic_completion_percent()
    return render_template("tutorials/Common Things/wild-jangli-janwar.html",all_topics =TOPIC_DICT,completed_percentages=completed_percentages, curLink = TOPIC_DICT["Common Things"][3][1], curTitle=TOPIC_DICT["Common Things"][3][0],  nextLink = TOPIC_DICT["Common Things"][4][1], nextTitle = TOPIC_DICT["Common Things"][4][0])



@app.route(TOPIC_DICT["Common Things"][4][1], methods=['GET', 'POST'])
def रंग():
    update_user_tracking()
    completed_percentages = topic_completion_percent()
    return render_template("tutorials/Common Things/colour-colour.html",all_topics =TOPIC_DICT,completed_percentages=completed_percentages, curLink = TOPIC_DICT["Common Things"][4][1], curTitle=TOPIC_DICT["Common Things"][4][0],  nextLink = TOPIC_DICT["Common Things"][5][1], nextTitle = TOPIC_DICT["Common Things"][5][0])



@app.route(TOPIC_DICT["Common Things"][5][1], methods=['GET', 'POST'])
def लोग_और_संबंध():
    update_user_tracking()
    completed_percentages = topic_completion_percent()
    return render_template("tutorials/Common Things/people-relationship-log-sambandh.html",all_topics =TOPIC_DICT,completed_percentages=completed_percentages, curLink = TOPIC_DICT["Common Things"][5][1], curTitle=TOPIC_DICT["Common Things"][5][0],  nextLink = TOPIC_DICT["Common Things"][6][1], nextTitle = TOPIC_DICT["Common Things"][6][0])



@app.route(TOPIC_DICT["Common Things"][6][1], methods=['GET', 'POST'])
def शरीर_के_अंग():
    update_user_tracking()
    completed_percentages = topic_completion_percent()
    return render_template("tutorials/Common Things/body-parts-sarir-angg.html",all_topics =TOPIC_DICT,completed_percentages=completed_percentages, curLink = TOPIC_DICT["Common Things"][6][1], curTitle=TOPIC_DICT["Common Things"][6][0],  nextLink = TOPIC_DICT["Common Things"][7][1], nextTitle = TOPIC_DICT["Common Things"][7][0])



@app.route(TOPIC_DICT["Common Things"][7][1], methods=['GET', 'POST'])
def सब्जियां():
    update_user_tracking()
    completed_percentages = topic_completion_percent()
    return render_template("tutorials/Common Things/vegetables-sabjiyan.html",all_topics =TOPIC_DICT,completed_percentages=completed_percentages, curLink = TOPIC_DICT["Common Things"][7][1], curTitle=TOPIC_DICT["Common Things"][7][0],  nextLink = TOPIC_DICT["Common Things"][8][1], nextTitle = TOPIC_DICT["Common Things"][8][0])



@app.route(TOPIC_DICT["Common Things"][8][1], methods=['GET', 'POST'])
def फल():
    update_user_tracking()
    completed_percentages = topic_completion_percent()
    return render_template("tutorials/Common Things/fruits-fal.html",all_topics =TOPIC_DICT,completed_percentages=completed_percentages, curLink = TOPIC_DICT["Common Things"][8][1], curTitle=TOPIC_DICT["Common Things"][8][0],  nextLink = TOPIC_DICT["Common Things"][9][1], nextTitle = TOPIC_DICT["Common Things"][9][0])



@app.route(TOPIC_DICT["Common Things"][9][1], methods=['GET', 'POST'])
def दिन_और_महीने():
    update_user_tracking()
    completed_percentages = topic_completion_percent()
    return render_template("tutorials/Common Things/day-month-din-mahine.html",all_topics =TOPIC_DICT,completed_percentages=completed_percentages, curLink = TOPIC_DICT["Common Things"][9][1], curTitle=TOPIC_DICT["Common Things"][9][0],  nextLink = TOPIC_DICT["Common Things"][10][1], nextTitle = TOPIC_DICT["Common Things"][10][0])



@app.route(TOPIC_DICT["Common Things"][10][1], methods=['GET', 'POST'])
def संख्या():
    update_user_tracking()
    completed_percentages = topic_completion_percent()
    return render_template("tutorials/Common Things/numbers-sankhya.html",all_topics =TOPIC_DICT,completed_percentages=completed_percentages, curLink = TOPIC_DICT["Common Things"][10][1], curTitle=TOPIC_DICT["Common Things"][10][0],  nextLink = TOPIC_DICT["Common Things"][11][1], nextTitle = TOPIC_DICT["Common Things"][11][0])


@app.route(TOPIC_DICT["Common Things"][11][1], methods=['GET', 'POST'])
def मसाले():
    update_user_tracking()
    completed_percentages = topic_completion_percent()
    return render_template("tutorials/Common Things/spices-masale.html",all_topics =TOPIC_DICT,completed_percentages=completed_percentages, curLink = TOPIC_DICT["Common Things"][11][1], curTitle=TOPIC_DICT["Common Things"][11][0],  nextLink = TOPIC_DICT["Common Things"][12][1], nextTitle = TOPIC_DICT["Common Things"][12][0])



@app.route(TOPIC_DICT["Common Things"][12][1], methods=['GET', 'POST'])
def आकार():
    update_user_tracking()
    completed_percentages = topic_completion_percent()
    return render_template("tutorials/Common Things/aakar-shape.html",all_topics =TOPIC_DICT,completed_percentages=completed_percentages, curLink = TOPIC_DICT["Common Things"][12][1], curTitle=TOPIC_DICT["Common Things"][12][0])



@app.route(TOPIC_DICT["Stories"][0][1], methods=['GET', 'POST'])
def कौआ_और_लोमड़ी():
    update_user_tracking()
    completed_percentages = topic_completion_percent()
    return render_template("tutorials/Stories/crow-fox-kaua-lomri.html",all_topics =TOPIC_DICT,completed_percentages=completed_percentages, curLink = TOPIC_DICT["Stories"][0][1], curTitle=TOPIC_DICT["Stories"][0][0],  nextLink = TOPIC_DICT["Stories"][1][1], nextTitle = TOPIC_DICT["Stories"][1][0])



@app.route(TOPIC_DICT["Stories"][1][1], methods=['GET', 'POST'])
def सच्चे_मित्र():
    update_user_tracking()
    completed_percentages = topic_completion_percent()
    return render_template("tutorials/Stories/true-friend-sache-mitra.html",all_topics =TOPIC_DICT,completed_percentages=completed_percentages, curLink = TOPIC_DICT["Stories"][1][1], curTitle=TOPIC_DICT["Stories"][1][0])


@app.route(TOPIC_DICT["General"][0][1], methods=['GET', 'POST'])
def अल्पप्राण_और_महाप्राण_वर्ण():
    update_user_tracking()
    completed_percentages = topic_completion_percent()
    return render_template("tutorials/General/least-aspiring-alppraan-mahapraan-alphabets.html",all_topics =TOPIC_DICT,completed_percentages=completed_percentages, curLink = TOPIC_DICT["General"][0][1], curTitle=TOPIC_DICT["General"][0][0],  nextLink = TOPIC_DICT["General"][1][1], nextTitle = TOPIC_DICT["General"][1][0])



@app.route(TOPIC_DICT["General"][1][1], methods=['GET', 'POST'])
def अन्विति():
    update_user_tracking()
    completed_percentages = topic_completion_percent()
    return render_template("tutorials/General/discovery-anviti.html",all_topics =TOPIC_DICT,completed_percentages=completed_percentages, curLink = TOPIC_DICT["General"][1][1], curTitle=TOPIC_DICT["General"][1][0],  nextLink = TOPIC_DICT["General"][2][1], nextTitle = TOPIC_DICT["General"][2][0])



@app.route(TOPIC_DICT["General"][2][1], methods=['GET', 'POST'])
def लिंग():
    update_user_tracking()
    completed_percentages = topic_completion_percent()
    return render_template("tutorials/General/gender-ling.html",all_topics =TOPIC_DICT,completed_percentages=completed_percentages, curLink = TOPIC_DICT["General"][2][1], curTitle=TOPIC_DICT["General"][2][0])



@app.route(TOPIC_DICT["Basics"][0][1], methods=['GET', 'POST'])
def वर्णमाला():
    update_user_tracking()
    completed_percentages = topic_completion_percent()
    return render_template("tutorials/Basics/alphabet-varnmala.html",all_topics =TOPIC_DICT,completed_percentages=completed_percentages, curLink = TOPIC_DICT["Basics"][0][1], curTitle=TOPIC_DICT["Basics"][0][0],  nextLink = TOPIC_DICT["Basics"][1][1], nextTitle = TOPIC_DICT["Basics"][1][0])



@app.route(TOPIC_DICT["Basics"][1][1], methods=['GET', 'POST'])
def स्वर():
    update_user_tracking()
    completed_percentages = topic_completion_percent()
    return render_template("tutorials/Basics/vowel-swar.html",all_topics =TOPIC_DICT,completed_percentages=completed_percentages, curLink = TOPIC_DICT["Basics"][1][1], curTitle=TOPIC_DICT["Basics"][1][0],  nextLink = TOPIC_DICT["Basics"][2][1], nextTitle = TOPIC_DICT["Basics"][2][0])



@app.route(TOPIC_DICT["Basics"][2][1], methods=['GET', 'POST'])
def व्यंजन():
    update_user_tracking()
    completed_percentages = topic_completion_percent()
    return render_template("tutorials/Basics/consonent-vyanjan.html",all_topics =TOPIC_DICT,completed_percentages=completed_percentages, curLink = TOPIC_DICT["Basics"][2][1], curTitle=TOPIC_DICT["Basics"][2][0],  nextLink = TOPIC_DICT["Basics"][3][1], nextTitle = TOPIC_DICT["Basics"][3][0])



@app.route(TOPIC_DICT["Basics"][3][1], methods=['GET', 'POST'])
def मात्राएँ():
    update_user_tracking()
    completed_percentages = topic_completion_percent()
    return render_template("tutorials/Basics/punctuation-matraye.html",all_topics =TOPIC_DICT,completed_percentages=completed_percentages, curLink = TOPIC_DICT["Basics"][3][1], curTitle=TOPIC_DICT["Basics"][3][0],  nextLink = TOPIC_DICT["Basics"][4][1], nextTitle = TOPIC_DICT["Basics"][4][0])



@app.route(TOPIC_DICT["Basics"][4][1], methods=['GET', 'POST'])
def संयुक्ताक्षर():
    update_user_tracking()
    completed_percentages = topic_completion_percent()
    return render_template("tutorials/Basics/ligature-sanyutakshar.html",all_topics =TOPIC_DICT,completed_percentages=completed_percentages, curLink = TOPIC_DICT["Basics"][4][1], curTitle=TOPIC_DICT["Basics"][4][0])


@app.route(TOPIC_DICT["Grammer"][0][1], methods=['GET', 'POST'])
def संज्ञा():
    update_user_tracking()
    completed_percentages = topic_completion_percent()
    return render_template("tutorials/Grammer/noun-sangya.html",all_topics =TOPIC_DICT,completed_percentages=completed_percentages, curLink = TOPIC_DICT["Grammer"][0][1], curTitle=TOPIC_DICT["Grammer"][0][0],  nextLink = TOPIC_DICT["Grammer"][1][1], nextTitle = TOPIC_DICT["Grammer"][1][0])



@app.route(TOPIC_DICT["Grammer"][1][1], methods=['GET', 'POST'])
def सर्वनाम():
    update_user_tracking()
    completed_percentages = topic_completion_percent()
    return render_template("tutorials/Grammer/pronoun-sarvnaam.html",all_topics =TOPIC_DICT,completed_percentages=completed_percentages, curLink = TOPIC_DICT["Grammer"][1][1], curTitle=TOPIC_DICT["Grammer"][1][0],  nextLink = TOPIC_DICT["Grammer"][2][1], nextTitle = TOPIC_DICT["Grammer"][2][0])



@app.route(TOPIC_DICT["Grammer"][2][1], methods=['GET', 'POST'])
def क्रिया():
    update_user_tracking()
    completed_percentages = topic_completion_percent()
    return render_template("tutorials/Grammer/verb-kriya.html",all_topics =TOPIC_DICT,completed_percentages=completed_percentages, curLink = TOPIC_DICT["Grammer"][2][1], curTitle=TOPIC_DICT["Grammer"][2][0],  nextLink = TOPIC_DICT["Grammer"][3][1], nextTitle = TOPIC_DICT["Grammer"][3][0])



@app.route(TOPIC_DICT["Grammer"][3][1], methods=['GET', 'POST'])
def विशेषण():
    update_user_tracking()
    completed_percentages = topic_completion_percent()
    return render_template("tutorials/Grammer/adjective-viseshan.html",all_topics =TOPIC_DICT,completed_percentages=completed_percentages, curLink = TOPIC_DICT["Grammer"][3][1], curTitle=TOPIC_DICT["Grammer"][3][0],  nextLink = TOPIC_DICT["Grammer"][4][1], nextTitle = TOPIC_DICT["Grammer"][4][0])



@app.route(TOPIC_DICT["Grammer"][4][1], methods=['GET', 'POST'])
def कारक():
    update_user_tracking()
    completed_percentages = topic_completion_percent()
    return render_template("tutorials/Grammer/factor-kaarak.html",all_topics =TOPIC_DICT,completed_percentages=completed_percentages, curLink = TOPIC_DICT["Grammer"][4][1], curTitle=TOPIC_DICT["Grammer"][4][0],  nextLink = TOPIC_DICT["Grammer"][5][1], nextTitle = TOPIC_DICT["Grammer"][5][0])



@app.route(TOPIC_DICT["Grammer"][5][1], methods=['GET', 'POST'])
def काल():
    update_user_tracking()
    completed_percentages = topic_completion_percent()
    return render_template("tutorials/Grammer/tense-kaal.html",all_topics =TOPIC_DICT,completed_percentages=completed_percentages, curLink = TOPIC_DICT["Grammer"][5][1], curTitle=TOPIC_DICT["Grammer"][5][0],  nextLink = TOPIC_DICT["Grammer"][6][1], nextTitle = TOPIC_DICT["Grammer"][6][0])



@app.route(TOPIC_DICT["Grammer"][6][1], methods=['GET', 'POST'])
def अव्यय():
    update_user_tracking()
    completed_percentages = topic_completion_percent()
    return render_template("tutorials/Grammer/inexhaustible-avyay.html",all_topics =TOPIC_DICT,completed_percentages=completed_percentages, curLink = TOPIC_DICT["Grammer"][6][1], curTitle=TOPIC_DICT["Grammer"][6][0],  nextLink = TOPIC_DICT["Grammer"][7][1], nextTitle = TOPIC_DICT["Grammer"][7][0])



@app.route(TOPIC_DICT["Grammer"][7][1], methods=['GET', 'POST'])
def उपसर्ग():
    update_user_tracking()
    completed_percentages = topic_completion_percent()
    return render_template("tutorials/Grammer/prefix-upsarg.html",all_topics =TOPIC_DICT,completed_percentages=completed_percentages, curLink = TOPIC_DICT["Grammer"][7][1], curTitle=TOPIC_DICT["Grammer"][7][0],  nextLink = TOPIC_DICT["Grammer"][8][1], nextTitle = TOPIC_DICT["Grammer"][8][0])



@app.route(TOPIC_DICT["Grammer"][8][1], methods=['GET', 'POST'])
def प्रत्यय():
    update_user_tracking()
    completed_percentages = topic_completion_percent()
    return render_template("tutorials/Grammer/suffix-pratyay.html",all_topics =TOPIC_DICT,completed_percentages=completed_percentages, curLink = TOPIC_DICT["Grammer"][8][1], curTitle=TOPIC_DICT["Grammer"][8][0],  nextLink = TOPIC_DICT["Grammer"][9][1], nextTitle = TOPIC_DICT["Grammer"][9][0])



@app.route(TOPIC_DICT["Grammer"][9][1], methods=['GET', 'POST'])
def संधि():
    update_user_tracking()
    completed_percentages = topic_completion_percent()
    return render_template("tutorials/Grammer/treaty-sandhi.html",all_topics =TOPIC_DICT,completed_percentages=completed_percentages, curLink = TOPIC_DICT["Grammer"][9][1], curTitle=TOPIC_DICT["Grammer"][9][0],  nextLink = TOPIC_DICT["Grammer"][10][1], nextTitle = TOPIC_DICT["Grammer"][10][0])



@app.route(TOPIC_DICT["Grammer"][10][1], methods=['GET', 'POST'])
def संधि_विच्छेद():
    update_user_tracking()
    completed_percentages = topic_completion_percent()
    return render_template("tutorials/Grammer/disjoining-sandhi-visched.html",all_topics =TOPIC_DICT,completed_percentages=completed_percentages, curLink = TOPIC_DICT["Grammer"][10][1], curTitle=TOPIC_DICT["Grammer"][10][0],  nextLink = TOPIC_DICT["Grammer"][11][1], nextTitle = TOPIC_DICT["Grammer"][11][0])



@app.route(TOPIC_DICT["Grammer"][11][1], methods=['GET', 'POST'])
def समास():
    update_user_tracking()
    completed_percentages = topic_completion_percent()
    return render_template("tutorials/Grammer/compound-samas.html",all_topics =TOPIC_DICT,completed_percentages=completed_percentages, curLink = TOPIC_DICT["Grammer"][11][1], curTitle=TOPIC_DICT["Grammer"][11][0],  nextLink = TOPIC_DICT["Grammer"][12][1], nextTitle = TOPIC_DICT["Grammer"][12][0])



@app.route(TOPIC_DICT["Grammer"][12][1], methods=['GET', 'POST'])
def मुहावरा():
    update_user_tracking()
    completed_percentages = topic_completion_percent()
    return render_template("tutorials/Grammer/idiom-muhawara.html",all_topics =TOPIC_DICT,completed_percentages=completed_percentages, curLink = TOPIC_DICT["Grammer"][12][1], curTitle=TOPIC_DICT["Grammer"][12][0],  nextLink = TOPIC_DICT["Grammer"][13][1], nextTitle = TOPIC_DICT["Grammer"][13][0])



@app.route(TOPIC_DICT["Grammer"][13][1], methods=['GET', 'POST'])
def वचन():
    update_user_tracking()
    completed_percentages = topic_completion_percent()
    return render_template("tutorials/Grammer/promise-vachan.html",all_topics =TOPIC_DICT,completed_percentages=completed_percentages, curLink = TOPIC_DICT["Grammer"][13][1], curTitle=TOPIC_DICT["Grammer"][13][0],  nextLink = TOPIC_DICT["Grammer"][14][1], nextTitle = TOPIC_DICT["Grammer"][14][0])


@app.route(TOPIC_DICT["Grammer"][14][1], methods=['GET', 'POST'])
def अलंकार():
    update_user_tracking()
    completed_percentages = topic_completion_percent()
    return render_template("tutorials/Grammer/ornamental-alankar.html",all_topics =TOPIC_DICT,completed_percentages=completed_percentages, curLink = TOPIC_DICT["Grammer"][14][1], curTitle=TOPIC_DICT["Grammer"][14][0])



if __name__ == "__main__":
    app.run(debug=True)

    
