# app/services/news_service.py

import requests
from bs4 import BeautifulSoup
import traceback

def get_latest_news():
    try:
        url = "https://news.google.com/rss/search?q=ekonomi+when:1d&hl=tr&gl=TR&ceid=TR:tr"
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, "xml")
        items = soup.find_all("item")
        print(f" Google News item sayısı: {len(items)}")

        news_list = []
        for item in items[:5]:  # sadece ilk 5 haber
            title = item.find("title").text.strip()
            link = item.find("link").text.strip()
            pub_date = item.find("pubDate").text.strip()

            news_list.append({
                "title": title,
                "link": link,
                "pubDate": pub_date,
                "source": "Google News (TR - Ekonomi)"
            })

        return news_list

    except Exception as e:
        print(" HATA:", e)
        traceback.print_exc()
        return [{"error": str(e)}]

# Test etmek için
if __name__ == "__main__":
    news = get_latest_news()
    for i, item in enumerate(news, 1):
        print(f"{i}. {item['title']}\n   {item['link']}")
