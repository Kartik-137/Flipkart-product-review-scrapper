from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup
import pymongo

import logging
logging.basicConfig(filename="scrap_log_file.log" , level=logging.INFO)

my_app = Flask(__name__)

# First page (index.html)
@my_app.route('/', methods=['GET'])
@cross_origin()
def search_page():
    return render_template('index.html')

# Second page (result.html)
@my_app.route("/review", methods=['GET', 'POST'])  # To handle both GET, POST simultaneously
@cross_origin()
def final_page():
    if request.method == 'POST':
        try:
            ### Scrapping code here  ###
            
            # Get the product name to search for from index.html
            search_string = request.form['content']

            # Main page url, where all products are present
            main_url = "https://www.flipkart.com/search?q=" + search_string
            main_source = requests.get(main_url).text

            # bs4 object for main page
            main_soup = BeautifulSoup(main_source, 'lxml')

            # list of the first result on page 1 of 24
            first_prod = "https://www.flipkart.com" + main_soup.find(name='a', class_='_1fQZEK')['href']

            # bs4 object of first_prod
            first_prod_html = requests.get(first_prod).text
            soup_first_prod = BeautifulSoup(first_prod_html, 'lxml')

            # all the comment boxes on the searched product page
            lst_commentboxes = soup_first_prod.find_all(name="div",class_="col _2wzgFH")

            # Empty list to hold the scrapped data
            review_lst = []
            sr_no = 0

            for i in lst_commentboxes:
                
                # Fetch the name of the Customer
                try:
                    name = i.find(name='div', class_='row _3n8db9').p.text
                except:
                    logging.info(f"name unknown")

                # Fetch the rating by the customer
                try:
                    rating = i.find(name="div",class_='_3LWZlK _1BLPMq').text
                except:
                    logging.info(f"NOT rated")

                # Fetch the comment highlight
                try:
                    comm_tag = i.div.p.text
                except:
                    logging.info(f"comment exception")

                # Fetch the customers comment description
                try:
                    comm_para = i.find(name='div', class_='t-ZTKy').text
                    comm_para = comm_para[:(len(comm_para)-9)]
                except:
                    logging.info("Exception occurred")
                
                sr_no = sr_no + 1

                data_dict = {"Product": search_string, "Name": name, "Rating": rating,
                             "Comment Highlight": comm_tag, "Comment": comm_para, "Sr. No.":sr_no}
                review_lst.append(data_dict)

            logging.info("logging scrapped result {}".format(review_lst))

            return render_template('result.html', reviews= review_lst)

        except Exception as e:
            logging.info(e)
            return "See log file"
    else:  
        # Redirect to first_page 
        return render_template("index.html")

if __name__ == "__main__":
    my_app.run(host="0.0.0.0", debug=False)