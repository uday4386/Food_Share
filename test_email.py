import smtplib
from email.mime.text import MIMEText

def test_gmail_smtp():
    sender = "harshanani576@gmail.com"
    password = "gfwo qhlv uqha lapi"
    receiver = "harshanani576@gmail.com" # Send to self for test

    msg = MIMEText("This is a test email from the debugging script.")
    msg['Subject'] = "SMTP Test"
    msg['From'] = sender
    msg['To'] = receiver

    try:
        print(f"Connecting to smtp.gmail.com:587...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.set_debuglevel(1) # Show full communication
        server.starttls()
        print("Logging in...")
        server.login(sender, password)
        print("Login success! Sending email...")
        server.sendmail(sender, receiver, msg.as_string())
        print("Email sent successfully!")
        server.quit()
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    test_gmail_smtp()
