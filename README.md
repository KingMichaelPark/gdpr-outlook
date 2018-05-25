# GDPR Outlook CSV Export Parser and Organizer
This simple parser will iterate through your Microsoft Outlook email and contact csv exports,
identifying all the unique pairs of phone numbers, email addresses, and full names, and tries
to predict/label whether the email address identified is a personal email or a corporate email
address. It goes through every csv in a directory or an individual csv export.

It then saves all the records to one SQLite Database .db file so if you want to apply any
cryptopgraphy on the information that you possess, you can simply create a new table that is
protected and hashed. It works in all the testing that I did but hopefully it should be pretty resiliant.

