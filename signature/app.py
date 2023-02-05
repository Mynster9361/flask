from flask import Flask, render_template
from appfunctions import run
app = Flask(__name__)

@app.route("/<email_input>")
def index(email_input):
    cmd = "Get-Mailbox " + email_input + " | Get-MailboxMessageConfiguration | select SignatureHtml -ExpandProperty SignatureHtml"
    signature = run(cmd)
    
    return render_template("signature.html", signature=signature)

app.run(host="0.0.0.0", port=80)
