from transformers import pipeline
from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class summary_text(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(2000), nullable=False)
    summary = db.Column(db.String(2000), nullable=False)
    completed = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id

@app.route("/", methods=['POST', 'GET'])
def index():
    with app.app_context():
        db.create_all()

    if request.method == "POST":
        task_content = request.form['content']
        summarizer = pipeline("summarization")
        summary_result = summarizer(task_content)
        new_summary_task = summary_text(content = task_content, summary = summary_result[0]["summary_text"])

        try:
            db.session.add(new_summary_task)
            db.session.commit()
            return redirect("/")
        except:
            return "Error happens in your code"

    else:
        tasks = summary_text.query.order_by(summary_text.date_created).all()
        return render_template("index.html", tasks=tasks)#, summary=summary)
    
@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = summary_text.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return "Error happens in deleting code"

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task_to_update =  summary_text.query.get_or_404(id)

    if request.method == 'POST':
        task_to_update.content = request.form['content']
        
        try:
            db.session.commit()
            return redirect('/')
        except:
            return "There was an issue with update feature"
    else:
        return render_template("update.html", task=task_to_update)

if __name__ == "__main__":
    app.run(port=8001, debug=True)
