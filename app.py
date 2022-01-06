from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.exchange-rates.org/history/IDR/USD/T')
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
table = soup.find('table', attrs={'class':'table table-striped table-hover table-hover-solid-row table-simple history-data'})
row = table.find_all('td')

row_length = len(row)

# temp = [] #initiating a list
date_temp = []
day_temp = []
price_temp = [] 

for i in range(0, row_length):
#insert the scrapping process here
	if i in range(0, row_length, 4):
		date_temp.append(row[i].get_text())
	if i in range(1, row_length, 4):
		day_temp.append(row[i].get_text())
	if i in range(2, row_length, 4):
		price_temp.append(row[i].get_text())
    # temp.append((____,____,____)) 

# temp = temp[::-1]

#change into dataframe
df = pd.DataFrame()
df['Date'] = date_temp
df['Day'] = day_temp
df['Price'] = price_temp

#insert data wrangling here
df['Date'] = df['Date'].astype('datetime64')

df['Price'] = df['Price'].apply(lambda x: x.replace('IDR', ''))
df['Price'] = df['Price'].apply(lambda x: x.replace(',', ''))
df['Price'] = df['Price'].astype('float')

start = min(df['Date'])
end = max(df['Date'])
quarter = pd.date_range(start=start, end=end)
df = df.set_index('Date')
df = df.reindex(quarter)
df['Price'] = df['Price'].fillna(method='ffill')
df = df.reset_index().rename(columns={'index':'Date'})
df['Date'] = df['Date'].astype('datetime64')
#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'{df["Price"][0].round(2)}' #be careful with the " and ' 
	card_data = "Rp " + format(float(card_data), ',')

	# generate plot
	ax = plt.figure(figsize = (9,3), dpi=300) 
	ax.add_subplot()

	x = df['Date'].values
	y = df['Price'].values
	# plt.title('Daily Price USD-Indonesia')
	plt.xlabel('Date')
	plt.ylabel('Price (in IDR)')
	plt.plot(x, y, color='green', linewidth=2)
	plt.tight_layout()
	# plt.show()
	plt.savefig('daily_price.png',bbox_inches="tight") 
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result,
		start_date=start.to_period('D'),
		end_date=end.to_period('D')
		)


if __name__ == "__main__": 
    app.run(debug=True)