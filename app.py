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
url_get = requests.get('https://www.boxofficemojo.com/year/world/')
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
table = soup.find('div', attrs={'class':'a-section imdb-scroll-table-inner'}).find('table')
content = table.find_all('tr')[0:]

row_length = len(content)

temp = [] #initiating a list 

for i in range(1, row_length):
#insert the scrapping process here

    # Ranking Movie
    rank = content[i].find_all('td')[0].text

    # Release Group Title
    title = content[i].find_all('td')[1].text

    # Worldwide
    world = content[i].find_all('td')[2].text
    world = world.strip()

    # Domestic
    domestic = content[i].find_all('td')[3].text
    domestic = domestic.strip()

    # % Domestic
    p_domestic = content[i].find_all('td')[4].text
    p_domestic = p_domestic.strip()

    # Foreign
    foreign = content[i].find_all('td')[5].text
    foreign = foreign.strip()

    # % Foreign
    p_foreign = content[i].find_all('td')[6].text
    p_foreign = p_foreign.strip()

    temp.append((rank, title, world, domestic, p_domestic, foreign, p_foreign)) 

temp = temp[::-1]

#change into dataframe
df = pd.DataFrame(temp, columns = ('Rank','Title','Worldwide','Domestic','p_Domestic','Foreign','p_Foreign'))

#insert data wrangling here
df.Rank = df.Rank.astype('int64')
df.Worldwide = df.Worldwide.str.replace('$', '').str.replace(',', '').astype('int64')
df.Domestic = df.Domestic.str.replace('$', '').str.replace(',', '').str.replace('-','0').astype('int64')
df.Foreign = df.Foreign.str.replace('$', '').str.replace(',', '').str.replace('-','0').astype('int64')
df.p_Domestic = df.p_Domestic.str.replace('%','').str.replace('-','0').astype('float64')
df.p_Foreign = df.p_Foreign.str.replace('%','').str.replace('-','0').astype('float64')

top10 = df.drop(columns= ['Domestic','p_Domestic','Foreign','p_Foreign']).head(10)

movieforeign = df[df.Domestic == 0].drop(columns = ['Worldwide', 'Domestic', 'p_Domestic', 'p_Foreign'])

top10foreign = df.sort_values('Foreign', ascending= False).drop(columns = ['Worldwide', 'Domestic', 'p_Domestic', 'p_Foreign']).head(10)

moviedomestic = df[df.Foreign == 0].drop(columns = ['Worldwide', 'Foreign', 'p_Domestic', 'p_Foreign'])

top10domestic = df.sort_values('Domestic', ascending= False).drop(columns = ['Worldwide', 'Foreign', 'p_Domestic', 'p_Foreign']).head(10)

domoverfor = df[df.Domestic > df.Foreign]
domoverfor['Difference'] = domoverfor.Domestic - domoverfor.Foreign

top10plot = top10.drop(columns = 'Rank').set_index('Title').sort_values(by='Worldwide',ascending=True)

#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'{top10plot["Worldwide"].mean().round(2)}' #be careful with the " and ' 

	# generate plot
	ax = top10plot.plot(figsize = (20,9)).barh(y= "Worldwide", width="Title") 
	
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
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)