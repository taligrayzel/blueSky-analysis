from flask import Flask, render_template, request
from analyze_user import analyze_user
from pathlib import Path
import re

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None

    if request.method == "POST":
        username = re.sub(r'[\u200e\u200f\u202a-\u202e]', '', request.form.get("username", "").strip())
        try:
            result = analyze_user(username)
            if result:
                result["username"] = username
                result["viz_path"] = f"/static/visualizations/{username.replace('.', '_')}_analysis.png"
        except ValueError as ve:
            error = str(ve)
        except Exception:
            error = "An unexpected error occurred. Please try again later."

    return render_template("index.html", result=result, error=error)

if __name__ == "__main__":
    app.run(debug=True)
