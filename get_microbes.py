import requests

from bs4 import BeautifulSoup
import pandas as pd



base = 'https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/'
tax = ['phylum', 'class', 'order', 'family', 'genus', 'species']
df = pd.DataFrame(columns = tax)



def get_category(base, link, cat_name):
    page = requests.get(base + link)
    soup = BeautifulSoup(page.content, 'html.parser')
    categories = soup.find_all('a', {'title' : cat_name})
    return categories


link ='wwwtax.cgi?mode=Tree&id=2&lvl=1&lin=f&keep=1&srchmode=1&unlock'

phylums = get_category(base, link, tax[0])
for phylum in phylums:
    link = phylum['href']
    classes = get_category(base, link, tax[1])
    phylum_text = phylum.get_text()
    for class_name in classes:
        link = class_name['href']
        orders = get_category(base, link, tax[2])
        class_text = class_name.get_text()
        for order in orders:
            link = order['href']
            families = get_category(base, link, tax[3])
            order_text = order.get_text()
            for family in families:
                link = family['href']
                genuses = get_category(base, link, tax[4])
                family_text = family.get_text()
                for genus in genuses:
                    link = genus['href']
                    species_plural = get_category(base, link, tax[5])
                    genus_text = genus.get_text()
                    for species in species_plural:
                        species_text = species.get_text()
                        row = [phylum_text, class_text, order_text, family_text, genus_text, species_text]
                        print(row)
                        df.loc[len(df)] = row



df.to_csv('microbes.csv')
print(df.head())
