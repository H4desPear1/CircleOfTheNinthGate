import os
from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)

# ------------------------------------------------------------------
# IMPORTANT: Change this to a long random string before deploying.
# You can generate one with: python -c "import secrets; print(secrets.token_hex(32))"
# ------------------------------------------------------------------
app.secret_key = os.environ.get("SECRET_KEY", "CHANGE_ME_BEFORE_DEPLOYING")

# ------------------------------------------------------------------
# Set your password here. Replace the placeholder before deploying.
# ------------------------------------------------------------------
PORTAL_PASSWORD = os.environ.get("PORTAL_PASSWORD", "test")


@app.route("/", methods=["GET"])
def index():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        password = request.form.get("password", "")

        if password == PORTAL_PASSWORD:
            session["authenticated"] = True
            return redirect(url_for("secret"))
        else:
            error = "ACCESS DENIED — INVALID CREDENTIALS"

    return render_template("login.html", error=error)


@app.route("/secret")
def secret():
    if not session.get("authenticated"):
        return redirect(url_for("login"))
    return render_template("secret.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=False)
