import smtplib

try:
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()  # Upgrade the connection to secure
    server.login("sha_put_your_email@gmail.com", "nor_forget_app_password")  # wink
    print("✅ Login successful!")
except smtplib.SMTPAuthenticationError as e:
    print("❌ Authentication error:", e)
except smtplib.SMTPException as e:
    print("❌ SMTP error:", e)
finally:
    server.quit()
