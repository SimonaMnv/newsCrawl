import os
from flask import Flask, jsonify

app = Flask("scrapy-start")


@app.route('/scrape')
def scrape():
    print(os.system('scrapy crawl newsbomb'))

    return jsonify({'scraped_finished': True}, 200)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)