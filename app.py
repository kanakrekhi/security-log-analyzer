from flask import Flask, render_template, request
import re
import os
from collections import defaultdict

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Create uploads folder automatically
os.makedirs("uploads", exist_ok=True)

def analyze_logs(file_path):
    failed_attempts = defaultdict(int)
    ip_pattern = r'(?:\d{1,3}\.){3}\d{1,3}'

    with open(file_path, "r", errors="ignore") as file:
        for line in file:
            line_lower = line.lower()

            if ("failed" in line_lower or 
                "invalid" in line_lower or 
                "authentication failure" in line_lower):

                ip_match = re.search(ip_pattern, line)
                if ip_match:
                    ip = ip_match.group()
                    failed_attempts[ip] += 1

    return dict(failed_attempts)


@app.route("/", methods=["GET", "POST"])
def home():
    results = None
    labels = []
    values = []

    if request.method == "POST":
        file = request.files["logfile"]

        if file and file.filename != "":
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            results = analyze_logs(filepath)

            labels = list(results.keys())
            values = list(results.values())

    return render_template("index.html", results=results, labels=labels, values=values)


if __name__ == "__main__":
    app.run(debug=True)