from flask import Flask, request, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
import random
import string

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class ShortenedUrls(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    longUrl = db.Column(db.String(200), nullable=False)
    shortUrl = db.Column(db.String(10), unique=True, nullable=False)

def generate_short_url(length=6):
    chars = string.ascii_letters + string.digits
    while True:
        short_url = "".join(random.choice(chars) for _ in range(length))
        existing_url = db.session.query(ShortenedUrls.shortUrl).filter_by(shortUrl=short_url).first()
        if not existing_url:
            return short_url

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        long_url = request.form['long_url'].strip()
        short_url = generate_short_url()

        
        try:
            url_entry=ShortenedUrls.query.filter_by(longUrl=long_url).first()
            if url_entry:
              url_entry.shortUrl=short_url
            else:
                new_url = ShortenedUrls(longUrl=long_url, shortUrl=short_url)
                db.session.add(new_url)
            db.session.commit()
            return redirect('/')
        except:
            return "There was an issue creating the shortened URL"

    shortened_urls = ShortenedUrls.query.all()
    return render_template('index.html', shortened_urls=shortened_urls)

@app.route('/<short_url>')
def redirect_url(short_url):
    url_entry = ShortenedUrls.query.filter_by(shortUrl=short_url).first_or_404()
    return redirect(url_entry.longUrl)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  
    app.run(debug=True)
