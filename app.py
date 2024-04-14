import os
import pathlib
from flask import Flask, render_template, request, abort, redirect, url_for, session,jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import PassiveAggressiveClassifier
import pickle
import pandas as pd
from sklearn.model_selection import train_test_split
import re
import string
from sklearn.decomposition import TruncatedSVD
# from authlib.integrations.flask_client import OAuth
from datetime import datetime
import time
current_time = datetime.now()
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
import requests
# from pyvi import ViTokenizer
from transformers import T5ForConditionalGeneration,T5Tokenizer
import torch
import cloudinary
from cloudinary.utils import cloudinary_url
from cloudinary.uploader import upload
import cloudinary.api
from googlesearch import search
from pymongo import MongoClient
from bson.objectid import ObjectId
import random
from werkzeug.utils import secure_filename
from bs4 import BeautifulSoup
import threading
from newspaper import Article




tfvect = TfidfVectorizer(analyzer='word', max_features=4189, ngram_range=(1, 2))
loaded_model = pickle.load(open('model/model.pkl', 'rb'))
dataframe = pd.read_csv('data_new.csv',on_bad_lines='skip')

# dataframe = pd.read_csv('data_new.csv',error_bad_lines=False)
dataframe.reset_index(inplace = True)
dataframe.drop(["index"], axis = 1, inplace = True)

def wordopt(text):
    text = text.lower()
    text = re.sub('\[.*?\]', '', text)
    text = re.sub("\\W"," ",text) 
    text = re.sub('https?://\S+|www\.\S+', '', text)
    text = re.sub('<.*?>+', '', text)
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub('\n', '', text)
    text = re.sub('\w*\d\w*', '', text)    
    return text

dataframe["data"] = dataframe["data"].apply(wordopt)
x = dataframe['data']
y = dataframe['label']
name = ""
picture = ""
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=0)

def fake_news_det(news):
    tfid_x_train = tfvect.fit_transform(x_train)
    tfid_x_test = tfvect.transform(x_test)
    input_data = [news]
    vectorized_input_data = tfvect.transform(input_data)
    prediction = loaded_model.predict(vectorized_input_data)
    return prediction


cloudinary.config(
    cloud_name="dz9j1pqvk",
    api_key="738714684352559",
    api_secret="BTs_rShwlDvWSABA5M553OLn4pY"
)


app = Flask("Fake News Detection App")  # naming our application
UPLOAD_FOLDER = 'static/uploads/'
client = MongoClient(
    "mongodb+srv://quocdat51930:4c2xgsPcWejZlyqM@webdetectfakenews.z898ahe.mongodb.net/?retryWrites=true&w=majority")
db = client.fakenews
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = 'static/uploads/'


app.secret_key = "secret key"
GOOGLE_CLIENT_ID = "410564700513-0qlmt8cg5qt6pjihuf6us28j1q7e09mv.apps.googleusercontent.com"
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
client_secrets_file = os.path.join(
    pathlib.Path(__file__).parent, "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"
)
#rồi
@app.route('/predict_news', methods=['GET', 'POST'])
def predict_news():
     if ((request.method == 'POST') and (request.form['message'] != "")):
        message = request.form['message']
        proba = fake_news_det(message)
        if proba > 0.41:
            res = f'<h3 style="color:green; font-weight:bold;">Tin thật</h3>'
        else:
            res = f'<h3 style="color:red; font-weight:bold;">Tin giả</h3>'
        return res  # Return the concatenated HTML code

        
def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)
        else:
            return function()
    return wrapper


@app.route('/')
def home():
    name_session = session.get('name')
    if name_session is None:
        return render_template('index.html', names="", pictures="")
    else:
        return render_template('index.html', names=session["name"], pictures=session["picture"])


@app.route('/index')
def index():
    name_session = session.get('name')
    if name_session is None:
        return render_template('index.html', names="", pictures="")
    else:
        return render_template('index.html', names=session["name"], pictures=session["picture"])


@app.route("/user-manual")
def manual():
    student = db.admin.find({})
    return render_template("user-manual.html", details=student)


@app.route('/reflect', methods=['GET', 'POST'])
def reflect():
    if (request.method == 'POST'):
        iduser = request.form.get('iduser')
        pictures = request.form.get('pictures')
        nameuser = request.form.get('nameuser')
        title = request.form.get('title')
        link = request.form.get('link')
        type = request.form.get('type')
        label = request.form.get('label')
        content = request.form.get('content')
        phone = request.form.get('phone')
        todays = current_time.strftime("%d-%m-%Y %H:%M:%S")
        file = request.files['image_upload']
        upload_result = upload(file)
        # Lấy URL công khai của hình ảnh tải lên
        image_url = upload_result['secure_url']
        db.forum_report.insert_one(
            {
                'Title': title,
                'Summary': content,
                'Status': 0,
                'Category': type,
                'Label': int(label),
                'Content': content,
                'Link': link,
                'GoogleId': iduser,
                'NameGoogle': nameuser,
                'GooglePicture': pictures,
                'Phone': phone,
                'ImageUpload': image_url,
                'DatePost': todays
            }
        )
        return redirect('/check')
    else:
        return redirect('/check')


@app.route('/newspost', methods=['GET', 'POST'])
def newspost():
    if (request.method == 'POST'):
        iduser = request.form.get('iduser')
        pictures = request.form.get('pictures')
        nameuser = request.form.get('nameuser')
        title = request.form.get('title')
        link = request.form.get('link')
        type = request.form.get('type')
        label = request.form.get('label')
        content = request.form.get('content')
        phone = request.form.get('phone')
        todays = current_time.strftime("%d-%m-%Y %H:%M:%S")
        file = request.files['image_upload']
        upload_result = upload(file)
        # Lấy URL công khai của hình ảnh tải lên
        image_url = upload_result['secure_url']
        db.forum_report.insert_one(
            {
                'Title': title,
                'Summary': content,
                'Status': 0,
                'Category': type,
                'Label': int(label),
                'Content': content,
                'Link': link,
                'GoogleId': iduser,
                'NameGoogle': nameuser,
                'GooglePicture': pictures,
                'Phone': phone,
                'ImageUpload': image_url,
                'DatePost': todays
            }
        )
        return redirect('/post')
    else:
        return redirect('/post')



@app.route('/display/<filename>')
def display_image(filename):
    #print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)


@app.route("/uncensoreds/<id>/<value>", methods=['POST'])
def uncensoreds(id,value):
# Update the document in MongoDB
    result = db.forum_report.update_one({"_id": ObjectId(id)}, {'$set': {'Status': int(value)}})
    # Return a response
    if result.modified_count > 0:
        return redirect('/admin/dashboard/')
    else:
        return redirect('/admin/dashboard/')

@app.route("/view/<id>")
def view(id):
    # student = db.admin.find({})
    news = db.forum_report.find_one({"_id": ObjectId(id)})
    newtop3 = db.forum_report.find({}).limit(12)
    newtop5 = db.forum_report.find({"Status": 1}).limit(3).sort('_id', 1)
    name_session = session.get('name')
    if name_session is None:
        return render_template("view.html", details=news, newtop3=newtop3,newtop5=newtop5,names="", pictures="")
    else:
        return render_template("view.html", details=news, newtop3=newtop3,newtop5=newtop5,names=session["name"], pictures=session["picture"])


@app.route("/update_record/<id>", methods=["POST"])
def update_record(id):

    name = request.form.get('Fname')
    mobile = request.form.get('mobile')
    address = request.form.get('address')
    comment = request.form.get('comment')

    db.admin.update_one(
        {"_id": id},
        {'$set':
            {
                'name': name,
                'mobile': mobile,
                'address': address,
                'comment': comment
            }
         })

    return redirect('/show')


@app.errorhandler(404)
def error_404(e):
    return render_template('404.html')


@app.route('/predicts', methods=['GET', 'POST'])
def predicts():
    if ((request.method == 'POST') and (request.form['message'] != "")):
        query = request.form['message']
        domains = ['thethao247.vn', 'chinhphu.vn', 'nld.com.vn', 'plo.vn', 'vtc.vn', 'tienphong.vn', 'quochoi.vn', 'baochinhphu.vn', 'laodong.vn',  'vietnamnet.vn', 'suckhoedoisong.vn', 'tuoitre.vn', 'thanhnien.vn', 'vov.vn', 'doisongphapluat.vn', 'hanoimoi.com.vn', 'tapchicongsan.org', 'hochiminh.org', 'nhandan.com.vn','baophapluat.vn', 'baodautu.vn', 'vnmedia.vn', 'giaoducthoidai.vn', 'baodansinh.vn', 'vanhien.vn', 'dantri.com.vn', 'baomoi.com', 'bnews.vn', 'dantocmiennui.vn', 'vnanet.vn', 'vietnam.vnanet.vn', 'cucnghethuatbieudien.gov.vn', 'moh.gov.vn', 'covid19.gov.vn']
        random.shuffle(domains)
        site_query = ' OR '.join([f'site:{domain}' for domain in domains])
        search_query = query.replace(" ", "+") + " " + site_query

        links = []
        for i, link in enumerate(search(search_query)):
            if link.endswith('/'):
                link = link[:-1]
            links.append(f'<tr><td>{i+1}</td><td><a href="{link}">{link}</a></td></tr>')
            if i == 4:
                break

        links_html = ''.join(links)
        return links_html


# @app.route('/searchurl', methods=['GET', 'POST'])
# def searchurl():
#     if ((request.method == 'POST') and (request.form['message'] != "")):
#         query = request.form['message']
#         domains = ['thethao247.vn', 'chinhphu.vn', 'nld.com.vn', 'plo.vn', 'vtc.vn', 'tienphong.vn', 'quochoi.vn', 'baochinhphu.vn', 'laodong.vn',  'vietnamnet.vn', 'suckhoedoisong.vn', 'tuoitre.vn', 'thanhnien.vn', 'vov.vn', 'doisongphapluat.vn', 'hanoimoi.com.vn', 'tapchicongsan.org', 'hochiminh.org', 'nhandan.com.vn','baophapluat.vn', 'baodautu.vn', 'vnmedia.vn', 'giaoducthoidai.vn', 'baodansinh.vn', 'vanhien.vn', 'dantri.com.vn', 'baomoi.com', 'bnews.vn', 'dantocmiennui.vn', 'vnanet.vn', 'vietnam.vnanet.vn', 'cucnghethuatbieudien.gov.vn', 'moh.gov.vn', 'covid19.gov.vn']
#         random.shuffle(domains)
#         site_query = ' OR '.join([f'site:{domain}' for domain in domains])
#         search_query = query.replace(" ", "+") + " " + site_query

#         links = []
#         for i, link in enumerate(search(search_query)):
#             if link.endswith('/'):
#                 link = link[:-1]
#             links.append(f'<tr><td>{i+1}</td><td><a href="{link}">{link}</a></td></tr>')
#             if i == 4:
#                 break

#         links_html = ''.join(links)
#     return links_html

# @app.route('/searchurl', methods=['GET', 'POST'])
# def searchurl():
#     if ((request.method == 'POST') and (request.form['message'] != "")):
#         query = request.form['message']
#         headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'}
#         domains = ['thethao247.vn', 'chinhphu.vn', 'nld.com.vn', 'plo.vn', 'vtc.vn', 'tienphong.vn', 'quochoi.vn', 'baochinhphu.vn', 'laodong.vn',  'vietnamnet.vn', 'suckhoedoisong.vn', 'tuoitre.vn', 'thanhnien.vn', 'vov.vn', 'doisongphapluat.vn', 'hanoimoi.com.vn', 'tapchicongsan.org', 'hochiminh.org', 'nhandan.com.vn','baophapluat.vn', 'baodautu.vn', 'vnmedia.vn', 'giaoducthoidai.vn', 'baodansinh.vn', 'vanhien.vn', 'dantri.com.vn', 'baomoi.com', 'bnews.vn', 'dantocmiennui.vn', 'vnanet.vn', 'vietnam.vnanet.vn', 'cucnghethuatbieudien.gov.vn', 'moh.gov.vn', 'covid19.gov.vn']
#         random.shuffle(domains)
#         site_query = ' OR '.join([f'site:{domain}' for domain in domains])
#         search_query = query.replace(" ", "+") + " " + site_query
#         links = []
#         for i, link in enumerate(search(search_query)):
#             if link.endswith('/'):
#                 link = link[:-1]
#             links.append(f'<tr><td>{i+1}</td><td><a href="{link}">{link}</a></td></tr>')
#             if i == 4:
#                 break

#         article_data_list = []

#         session = requests.Session()

#         for article_url in links:
#             try:
#                 response = session.get(article_url, headers=headers, timeout=10)
                
#                 if response.status_code == 200:
#                     article = Article(article_url)
#                     article.download()
#                     article.parse()
                    
#                     article_data = {
#                         'url': article_url,
#                         'title': article.title,
#                         'text': article.text
#                     }
                    
#                     article_data_list.append(article_data)
                    
#                     print(f"Title: {article.title}")
#                     print(f"Text: {article.text}")
                    
#                 else:
#                     print(f"Failed to fetch article at {article_url}")
#             except Exception as e:
#                 print(f"Error occurred while fetching article at {article_url}: {e}")

#             # Introduce a delay between requests to avoid being detected as a bot
#             time.sleep(10)  # Adjust the delay time as needed
#             # Now you have a list of dictionaries, where each dictionary represents the data of one article
#         linkss = []
#         for i, article_data in enumerate(article_data_list):
#             linkss.append(f'<tr><td>{i+1}</td><td><a href="{article_data["url"]}">{article_data["url"]}</a></td><td><a href="{article_data["url"]}">{article_data["text"]}</a></td></tr>')
#         links_html = ''.join(linkss)
    
#     return links_html

# @app.route('/searchurl', methods=['GET', 'POST'])
# def searchurl():
#     if ((request.method == 'POST') and (request.form['message'] != "")):
#         query = request.form['message']
#         headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'}
#         domains = ['thethao247.vn', 'chinhphu.vn', 'nld.com.vn', 'plo.vn', 'vtc.vn', 'tienphong.vn', 'quochoi.vn', 'baochinhphu.vn', 'laodong.vn',  'vietnamnet.vn', 'suckhoedoisong.vn', 'tuoitre.vn', 'thanhnien.vn', 'vov.vn', 'doisongphapluat.vn', 'hanoimoi.com.vn', 'tapchicongsan.org', 'hochiminh.org', 'nhandan.com.vn','baophapluat.vn', 'baodautu.vn', 'vnmedia.vn', 'giaoducthoidai.vn', 'baodansinh.vn', 'vanhien.vn', 'dantri.com.vn', 'baomoi.com', 'bnews.vn', 'dantocmiennui.vn', 'vnanet.vn', 'vietnam.vnanet.vn', 'cucnghethuatbieudien.gov.vn', 'moh.gov.vn', 'covid19.gov.vn']
#         random.shuffle(domains)
#         site_query = ' OR '.join([f'site:{domain}' for domain in domains])
#         search_query = query.replace(" ", "+") + " " + site_query
#         links = []
#         for i, link in enumerate(search(search_query)):
#             if link.endswith('/'):
#                 link = link[:-1]
#             links.append(link)
#             if i == 4:
#                 break

#         article_data_list = []

#         session = requests.Session()

#         for article_url in links:
#             try:
#                 response = session.get(article_url, headers=headers, timeout=10)
                
#                 if response.status_code == 200:
#                     article = Article(article_url)
#                     article.download()
#                     article.parse()
                    
#                     article_data = {
#                         'url': article_url,
#                         'title': article.title,
#                         'text': article.text
#                     }
                    
#                     article_data_list.append(article_data)
                    
#                     print(f"Title: {article.title}")
#                     print(f"Text: {article.text}")
                    
#                 else:
#                     print(f"Failed to fetch article at {article_url}")
#             except Exception as e:
#                 print(f"Error occurred while fetching article at {article_url}: {e}")

#             # Introduce a delay between requests to avoid being detected as a bot
#             time.sleep(10)  # Adjust the delay time as needed
#             # Now you have a list of dictionaries, where each dictionary represents the data of one article
#         linkss = []
#         for i, article_data in enumerate(article_data_list):
#            linkss.append(f'<tr> <td>{i+1}</td> <td><a href="{article_data["url"]}">{article_data["url"]}</a> </td> </tr>')
#         links_html = ''.join(linkss)
    
#         return links_html

#     return ""


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'}
domains = ['thethao247.vn', 'chinhphu.vn', 'nld.com.vn', 'plo.vn', 'vtc.vn', 'tienphong.vn', 'quochoi.vn', 'baochinhphu.vn', 'laodong.vn',  'vietnamnet.vn', 'suckhoedoisong.vn', 'tuoitre.vn', 'thanhnien.vn', 'vov.vn', 'doisongphapluat.vn', 'hanoimoi.com.vn', 'tapchicongsan.org', 'hochiminh.org', 'nhandan.com.vn','baophapluat.vn', 'baodautu.vn', 'vnmedia.vn', 'giaoducthoidai.vn', 'baodansinh.vn', 'vanhien.vn', 'dantri.com.vn', 'baomoi.com', 'bnews.vn', 'dantocmiennui.vn', 'vnanet.vn', 'vietnam.vnanet.vn', 'cucnghethuatbieudien.gov.vn', 'moh.gov.vn', 'covid19.gov.vn']
random.shuffle(domains)

def extract_domain(url):
    domain = re.sub(r"https?://", "", url)
    slash_index = domain.find("/")
    return domain[:slash_index]


article_data_list = []
def fetch_article_data(article_url):
    session = requests.Session()

    response = session.get(article_url, headers=headers, timeout=10)

    if response.status_code == 200:
        article = Article(article_url)
        article.download()
        article.parse()

    return article_url, article.title, article.text

def calculate_similarity_percentage(string_input, string):
    words_input = set(string_input.lower().split())
    words_string = set(string.lower().split())
    
    common_words = words_input.intersection(words_string)
    similarity_percentage = len(common_words) / len(words_input) * 100 if len(words_input) > 0 else 0
    
    return similarity_percentage

def find_most_similar_strings(string_input, list_of_strings, n=3):
    similarities = []
    
    for string in list_of_strings:
        similarity_percentage = calculate_similarity_percentage(string_input, string)
        similarities.append((string, similarity_percentage))
    
    sorted_similarities = sorted(similarities, key=lambda x: x[1], reverse=True)
    most_similar_strings = [string for string, _ in sorted_similarities[:n]]
    
    return most_similar_strings


@app.route('/searchurl', methods=['POST'])
def searchurl():
        data = request.get_json()  # Lấy nội dung body dưới dạng JSON
        query = data.get('value')  # Truy cập giá trị 'value' trong JSON
        print(query)
        site_query = ' OR '.join([f'site:{domain}' for domain in domains])
        search_query = query.replace(" ", "+") + " " + site_query
        links = []
        for i, link in enumerate(search(search_query)):
            if link.endswith('/'):
                link = link[:-1]
            links.append(link)
            if i == 4:
                break
        response_data = []
        for i in range(0, 3):
            link, title, content = fetch_article_data(links[i])
            link_domain  = extract_domain(link)
            x = find_most_similar_strings(query, content.replace("\n\n", ".").split("."), 3)
            list_content = find_most_similar_strings(query, content.replace("\n\n", ".").split("."), 3)
            similarity = calculate_similarity_percentage(query, x[0])
            simi = round(similarity)
           
            time.sleep(10)

            completion = client.chat.completions.create(
            model="model-identifier",
            messages=[
                        {"role": "system", "content": "Bạn là một trợ lí phân tích tin tức. Tôi sẽ đưa cho bạn một tin tức và các nguồn thông tin để xác minh tin tức đó. Bạn hãy giúp tôi trả lời giúp tôi xem tin tức đó là đúng hoặc là sai và Tiếp theo trả lời xem Tin đó thuộc phân loại nào trong các phân loại (Hủy hoại hoạt động tình báo, Tuyên truyền phản động,  Thông tin sai lệch, Phản động, Thiên vị chính trị, Lừa dối, Gây rối, Bôi nhọ, Kích động, Thách thức,  Nhảm nhí, Gây sợ hãi, Nhòm ngó, Phân biệt chủng tộc, Phỉ báng, Tạo rối, Lừa đảo) sau đó Cuối cùng Đưa ra lập luận lấy từ các nguồn và cho ra câu trả lời cuối cùng."},
                        {"role": "user", "content": f'''
                        Bạn là một trợ lí phân tích tin tức. Tôi sẽ đưa cho bạn một tin tức và các nguồn thông tin để xác minh tin tức đó. Bạn hãy giúp tôi trả lời giúp tôi xem tin tức đó là đúng hoặc là sai và Tiếp theo trả lời xem Tin đó thuộc phân loại nào trong các phân loại (Hủy hoại hoạt động tình báo, Tuyên truyền phản động,  Thông tin sai lệch, Phản động, Thiên vị chính trị, Lừa dối, Gây rối, Bôi nhọ, Kích động, Thách thức,  Nhảm nhí, Gây sợ hãi, Nhòm ngó, Phân biệt chủng tộc, Phỉ báng, Tạo rối, Lừa đảo) sau đó Cuối cùng Đưa ra lập luận lấy từ các nguồn và cho ra câu trả lời cuối cùng.
                        Tôi có 1 thông tin cần xác minh rằng "{query}". Nhưng tôi sử dụng search engine ở 3 nguồn khác nhau cho ra 3 câu trả lời:
                        - Nguồn {i+1}: "{list_content[0]}"
                        
                        '''}
                    ],
            temperature=0.7,
            )
            
            response_data.append({
            "rank": i+1,
            "domain": link_domain,
            "link": link,
            "title": title,
            "content": list_content,
            "similarity_percentage": simi,
            "result":completion.choices[0].message.content
             })
        # print(json.dumps(response_data, indent=4))
       
        return jsonify(response_data)



@app.route("/login/")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(
        session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    session["email"] = id_info.get("email")
    session["picture"] = id_info.get("picture")
    return redirect("/protected_area")


@app.route("/logout")
def logout():
    session.clear()
    session["google_id"] = ""
    session["name"] = ""
    session["email"] = ""
    session["picture"] = ""
    return redirect("/")


@app.route("/protected_area")
@login_is_required
def protected_area():
    name_session = session.get('name')
    if name_session is None:
        return render_template('index.html', names="", pictures="")
    else:
        return render_template('index.html', names=session["name"], pictures=session["picture"])


@app.route('/detectfakenews')
def detectfakenews():
    name_session = session.get('name')
    if name_session is None:
        return render_template('detect-fake-news.html', names="", pictures="")
    else:
        return render_template('detect-fake-news.html', names=session["name"], pictures=session["picture"])


@app.route('/preventfakenews')
def preventfakenews():
    name_session = session.get('name')
    if name_session is None:
        return render_template('prevent-fake-news.html', names="", pictures="")
    else:
        return render_template('prevent-fake-news.html', names=session["name"], pictures=session["picture"])


@app.route('/usermanual')
def usermanual():
    realnews = db.realnews.find({})
    name_session = session.get('name')
    if name_session is None:
        return render_template('user-manual.html', names="", pictures="", reals=realnews)
    else:
        return render_template('user-manual.html', names=session["name"], pictures=session["picture"], reals=realnews)

@app.route('/deleteforum', methods=['POST'])
def deleteforum():
    # Lấy ID của đối tượng cần xóa từ yêu cầu của client
    itemId = request.form.get('itemId')
    userId = request.form.get('userId')
    page = request.form.get('page')
    db.forum_report.delete_one({"_id": ObjectId(itemId)})
    return redirect("/history/"+userId+"/"+page)


@app.route("/history/<id_user>/<pages>")
def history(id_user, pages):
    page = int(pages)
    page_size = 20
    offset = page * page_size
    # condition1 = {'Status': 1}  # Điều kiện 1
    # condition2 = {'GoogleId': id_user}  # Điều kiện 2
    # {"$and": [condition1, condition2]}
    forums = db.forum_report.find({'GoogleId': id_user}).skip(
        offset).limit(page_size).sort('_id', -1)
    forums_list = []
    for forum in forums:
        forum_info = {
            'Title': forum['Title'],
            'GooglePicture': forum['GooglePicture'],
            'Status': forum['Status'],
            'Label': forum['Label'],
            'GoogleId': forum['GoogleId'],
            'Category': forum['Category'],
            'Summary': forum['Summary'],
            'Title': forum['Title'],
            "_id": forum['_id'],
            'Link': forum['Link'],
            'NameGoogle': forum['NameGoogle'],
            'Phone': forum['Phone'],
            'DatePost': forum['DatePost'],
            'ImageUpload': forum['ImageUpload']

        }
        forums_list.append(forum_info)
    name_session = session.get('name')
    if name_session is None:
        return redirect('index.html')
    else:
        return render_template('history.html', names=session["name"], google_id=session["google_id"], pictures=session["picture"], forums_list=forums_list, page=page, id_user=id_user)

@app.route('/forum')
def forum():
    newtop3 = db.forum_report.find({"Status": 1}).limit(3).sort('_id', 1)
    newtop5 = db.forum_report.find({"Status": 1}).limit(5).sort('_id', 1)
    newtop5s = db.forum_report.find({"Status": 1}).limit(5).sort('_id', -1)
    page = request.args.get('page', 0, type=int)
    page_size = 20
    offset = page * page_size
    forums = db.forum_report.find({"Status": 1}).skip(
        offset).limit(page_size).sort('_id', -1)
    forums_list = []
    for forum in forums:
        forum_info = {
            'Title': forum['Title'],
            'GooglePicture': forum['GooglePicture'],
            'Status': forum['Status'],
            'Label': forum['Label'],
            'GoogleId': forum['GoogleId'],
            'Category': forum['Category'],
            'Summary': forum['Summary'],
            'Title': forum['Title'],
            "_id": forum['_id'],
            'Link': forum['Link'],
            'NameGoogle': forum['NameGoogle'],
            'Phone': forum['Phone'],
            'DatePost': forum['DatePost'],
            'ImageUpload': forum['ImageUpload']

        }
        forums_list.append(forum_info)
    name_session = session.get('name')
    if name_session is None:
        return render_template('forum.html', names="", pictures="", forums_list=forums_list, page=page, newtop3=newtop3, newtop5=newtop5, newtop5s=newtop5s)
    else:
        return render_template('forum.html', names=session["name"], google_id=session["google_id"], pictures=session["picture"], forums_list=forums_list, page=page, newtop3=newtop3, newtop5=newtop5, newtop5s=newtop5s)

@app.route('/post')
def post():
    # realnews = db.realnews.find({"label":1})
    law = db.forum_report.find({"Category": "law", "Status": 1}).limit(12)
    disaster = db.forum_report.find(
        {"Category": "disaster", "Status": 1}).limit(12)
    ecomomy = db.forum_report.find(
        {"Category": "ecomomy", "Status": 1}).limit(12)
    health = db.forum_report.find(
        {"Category": "health", "Status": 1}).limit(12)
    seciurity = db.forum_report.find(
        {"Category": "seciurity", "Status": 1}).limit(12)
    other = db.forum_report.find({"Category": "other", "Status": 1}).limit(12)

    name_session = session.get('name')
    if name_session is None:
        return render_template('index.html', names="", pictures="")
    else:
        return render_template('post.html', names=session["name"], google_id=session["google_id"], pictures=session["picture"], law=law, disaster=disaster, ecomomy=ecomomy, health=health, seciurity=seciurity, other=other)
    

@app.route('/admin/mangeforum')
def mangeforum():
    law = db.forum_report.find({"Category": "law", "Status": 1}).limit(100)
    disaster = db.forum_report.find(
        {"Category": "disaster", "Status": 1}).limit(100)
    ecomomy = db.forum_report.find(
        {"Category": "ecomomy", "Status": 1}).limit(100)
    health = db.forum_report.find(
        {"Category": "health", "Status": 1}).limit(100)
    seciurity = db.forum_report.find(
        {"Category": "seciurity", "Status": 1}).limit(100)
    other = db.forum_report.find({"Category": "other", "Status": 1}).limit(100)
    return render_template('mangeforum.html', law=law, disaster=disaster, ecomomy=ecomomy, health=health, seciurity=seciurity, other=other)


@app.route('/check')
def check():
    name_session = session.get('name')
    if name_session is None:
        return render_template('check.html', names="", pictures="")
    else:
        return render_template('check.html', names=session["name"], google_id=session["google_id"], pictures=session["picture"])


@app.route('/admin/login/')
def loginAdmin():
    return render_template('login.html')



@app.route('/admin/fake_news_published/')
def fake_news_published():
    page = request.args.get('page', 0, type=int)
    page_size = 20
    offset = page * page_size
    forums = db.forum_report.find({"Status": 1, "Label": 0}).skip(offset).limit(page_size).sort('_id', -1)
    forums_list = []
    for forum in forums:
            forum_info = {
                'Title': forum['Title'],
                'GooglePicture': forum['GooglePicture'],
                'Status': forum['Status'],
                'Label': forum['Label'],
                'GoogleId': forum['GoogleId'],
                'Category': forum['Category'],
                'Summary': forum['Summary'],
                'Title': forum['Title'],
                "_id": forum['_id'],
                'Link': forum['Link'],
                'NameGoogle': forum['NameGoogle'],
                'Phone': forum['Phone'],
                'DatePost': forum['DatePost'],
                'ImageUpload': forum['ImageUpload']

            }
            forums_list.append(forum_info)
    name_session = session.get('name')
    if name_session is None:
        return render_template('fake_news_published.html', names="", pictures="", forums_list=forums_list, page=page)
    else:
         return render_template('fake_news_published.html', names=session["name"], google_id=session["google_id"], pictures=session["picture"], forums_list=forums_list, page=page)


@app.route('/admin/real_news_published/')
def real_news_published():
    page = request.args.get('page', 0, type=int)
    page_size = 20
    offset = page * page_size
    forums = db.forum_report.find({"Status": 1, "Label": 1}).skip(offset).limit(page_size).sort('_id', -1)
    forums_list = []
    for forum in forums:
            forum_info = {
                'Title': forum['Title'],
                'GooglePicture': forum['GooglePicture'],
                'Status': forum['Status'],
                'Label': forum['Label'],
                'GoogleId': forum['GoogleId'],
                'Category': forum['Category'],
                'Summary': forum['Summary'],
                'Title': forum['Title'],
                "_id": forum['_id'],
                'Link': forum['Link'],
                'NameGoogle': forum['NameGoogle'],
                'Phone': forum['Phone'],
                'DatePost': forum['DatePost'],
                'ImageUpload': forum['ImageUpload']

            }
            forums_list.append(forum_info)
    name_session = session.get('name')
    if name_session is None:
        return render_template('real_news_published.html', names="", pictures="", forums_list=forums_list, page=page)
    else:
         return render_template('real_news_published.html', names=session["name"], google_id=session["google_id"], pictures=session["picture"], forums_list=forums_list, page=page)



@app.route('/admin/uncensored_new/')
def uncensored_new():
    page = request.args.get('page', 0, type=int)
    page_size = 20
    offset = page * page_size
    forums = db.forum_report.find({"Status": 0}).skip(
        offset).limit(page_size).sort('_id', -1)
    forums_list = []
    for forum in forums:
        forum_info = {
            'Title': forum['Title'],
            'GooglePicture': forum['GooglePicture'],
            'Status': forum['Status'],
            'Label': forum['Label'],
            'GoogleId': forum['GoogleId'],
            'Category': forum['Category'],
            'Summary': forum['Summary'],
            'Title': forum['Title'],
            "_id": forum['_id'],
            'Link': forum['Link'],
            'NameGoogle': forum['NameGoogle'],
            'Phone': forum['Phone'],
            'DatePost': forum['DatePost'],
            'ImageUpload': forum['ImageUpload']

        }
        forums_list.append(forum_info)
    name_session = session.get('name')
    if name_session is None:
        return render_template('uncensored_new.html', names="", pictures="", forums_list=forums_list, page=page)
    else:
        return render_template('uncensored_new.html', names=session["name"], google_id=session["google_id"], pictures=session["picture"], forums_list=forums_list, page=page)


@app.route('/admin/censored_new/')
def censored_new():
    page = request.args.get('page', 0, type=int)
    page_size = 20
    offset = page * page_size
    forums = db.forum_report.find({"Status": 1}).skip(
        offset).limit(page_size).sort('_id', -1)
    forums_list = []
    for forum in forums:
        forum_info = {
            'Title': forum['Title'],
            'GooglePicture': forum['GooglePicture'],
            'Status': forum['Status'],
            'Label': forum['Label'],
            'GoogleId': forum['GoogleId'],
            'Category': forum['Category'],
            'Summary': forum['Summary'],
            'Title': forum['Title'],
            "_id": forum['_id'],
            'Link': forum['Link'],
            'NameGoogle': forum['NameGoogle'],
            'Phone': forum['Phone'],
            'DatePost': forum['DatePost'],
            'ImageUpload': forum['ImageUpload']

        }
        forums_list.append(forum_info)
    name_session = session.get('name')
    if name_session is None:
        return render_template('censored_new.html', names="", pictures="", forums_list=forums_list, page=page)
    else:
        return render_template('censored_new.html', names=session["name"], google_id=session["google_id"], pictures=session["picture"], forums_list=forums_list, page=page)


@app.route('/admin/deny_new/')
def deny_new():
    page = request.args.get('page', 0, type=int)
    page_size = 20
    offset = page * page_size
    forums = db.forum_report.find({"Status": 2}).skip(
        offset).limit(page_size).sort('_id', -1)
    forums_list = []
    for forum in forums:
        forum_info = {
            'Title': forum['Title'],
            'GooglePicture': forum['GooglePicture'],
            'Status': forum['Status'],
            'Label': forum['Label'],
            'GoogleId': forum['GoogleId'],
            'Category': forum['Category'],
            'Summary': forum['Summary'],
            'Title': forum['Title'],
            "_id": forum['_id'],
            'Link': forum['Link'],
            'NameGoogle': forum['NameGoogle'],
            'Phone': forum['Phone'],
            'DatePost': forum['DatePost'],
            'ImageUpload': forum['ImageUpload']

        }
        forums_list.append(forum_info)
    name_session = session.get('name')
    if name_session is None:
        return render_template('deny_new.html', names="", pictures="", forums_list=forums_list, page=page)
    else:
        return render_template('deny_new.html', names=session["name"], google_id=session["google_id"], pictures=session["picture"], forums_list=forums_list, page=page)


@app.route("/loginadmin", methods=['POST'])
def loginadmin():
    if request.method == "POST":
        user = request.form.get("user")
        password = request.form.get("password")
        user_found = db.admin.find_one({"user": user})
        if user_found:
            user_val = user_found['user']
            passwordcheck = user_found['password']
            if password == passwordcheck:
                session["user"] = user_val
                global users, name
                users = session["user"]
                name = user_found['name']
                return redirect('/admin/dashboard/')
            else:
                return redirect('/admin/login/')
        else:
                return redirect('/admin/login/')
    else:
                return redirect('/admin/login/')


@app.route('/admin/dashboard/')
def dashboard():
    count_uncensored = db.forum_report.count_documents({"Status": 0})
    count_censored = db.forum_report.count_documents({"Status": 1})
    count_real = db.forum_report.count_documents({"Status": 1, "Label": 1})
    count_fake = db.forum_report.count_documents({"Status": 1, "Label": 0})
    uncensored = db.forum_report.find({"Status": 0})
    pipeline = [
        {
            '$group': {
                '_id': '$GoogleId',  # Trường để nhóm theo, ở đây là trường 'field'
                'count': {'$sum': 1},  # Đếm số lượng bản ghi trong mỗi nhóm
                'NameGoogle': {'$first': '$NameGoogle'},
                'GooglePicture': {'$first': '$GooglePicture'},
                'Phone':{'$first':'$Phone'}
            }
        },
        {
            '$sort': {'count': -1}
        },
        {
            '$limit': 3
        }
    ]
        # Thực thi pipeline để đếm số lượng bản ghi và nhóm chúng
    result = list(db.forum_report.aggregate(pipeline))
    name_session = session.get('user')
    if name_session is None:
           return redirect(url_for('index'))
    else:
        return render_template('dashboard.html', uncensored=uncensored, result=result, count_uncensored=count_uncensored, count_censored=count_censored, count_real=count_real, count_fake=count_fake)

@app.route('/category/<categories>/<pages>')
def category(categories,pages):
    newtop3 = db.forum_report.find({"Status": 1}).limit(3).sort('_id', 1)
    newtop5 = db.forum_report.find({"Status": 1}).limit(5).sort('_id', 1)
    newtop1 = db.forum_report.find({"Status": 1}).limit(1).sort('_id', -1)
    page =int(pages)
    page_size = 20
    offset = page * page_size
    forums = db.forum_report.find({"Status": 1,"Category":categories}).skip(
        offset).limit(page_size).sort('_id', -1)
    forums_list = []
    for forum in forums:
        forum_info = {
            'Title': forum['Title'],
            'GooglePicture': forum['GooglePicture'],
            'Status': forum['Status'],
            'Label': forum['Label'],
            'GoogleId': forum['GoogleId'],
            'Category': forum['Category'],
            'Summary': forum['Summary'],
            'Title': forum['Title'],
            "_id": forum['_id'],
            'Link': forum['Link'],
            'NameGoogle': forum['NameGoogle'],
            'Phone': forum['Phone'],
            'DatePost': forum['DatePost'],
            'ImageUpload': forum['ImageUpload']

        }
        forums_list.append(forum_info)
    name_session = session.get('name')
    if name_session is None:
        return render_template('category.html', names="", pictures="", forums_list=forums_list, page=page, newtop3=newtop3, newtop5=newtop5,newtop1=newtop1,categories=categories)
    else:
        return render_template('category.html', names=session["name"], google_id=session["google_id"], pictures=session["picture"], forums_list=forums_list, page=page, newtop3=newtop3, newtop5=newtop5,newtop1=newtop1,categories=categories)

# def run_flask():
#     app.run(debug=True, host="0.0.0.0", port="5000")
    
# if __name__ == '__main__':
#     flask_thread = threading.Thread(target=run_flask)
#     flask_thread.start()

# if __name__ == '__main__':
#     app.run(debug=True)

# if __name__ == '__main__':
#     app.run(debug=True, port=5001)
 
if __name__ == '__main__':  
   app.run()