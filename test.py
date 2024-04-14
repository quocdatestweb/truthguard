import requests
from bs4 import BeautifulSoup
import random
from googlesearch import search
from newspaper import Article
import re
import requests
import time
import json
from flask import Flask, request, jsonify
from openai import OpenAI
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")


app = Flask(__name__)

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


    

    

if __name__ == '__main__':
    app.run()