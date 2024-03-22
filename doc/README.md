# Coles Sales Notifier

This python script allows you to get an email when the prices of items that you are interested in go below a price that you specify. The script is set to email you a maximum of once a day, and will email you every morning as long as at least one of the specified items is below it's target price. It is designed to be run on something like a raspberry pi that can run the script indefinitely.

<div align="center">
  ***SETUP***
</div>

+ For all the items that you want to be notified about, find their url's on the Coles website
+ Add the url's into Items.csv
+ Add whatever short and long name you want for each item in Items.csv
+ Decide at what price you want to be alerted at for each item and add to Items.csv
+ Fill in your email credentials in the email.env file
