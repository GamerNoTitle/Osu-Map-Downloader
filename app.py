import requests as r
from flask import Flask, send_from_directory, request, redirect, abort
from bs4 import BeautifulSoup
import json
import os
from tqdm import tqdm

app = Flask(__name__)

cookie = os.environ.get('cookie')

@app.route('/beatmapsets/<mapid>', methods=['GET'])
def LongPathParser(mapid):
    return MapDownloader(mapid)

@app.route('/map/<mapid>', methods=['GET'])
def MapDownloader(mapid):
    url = f'https://osu.ppy.sh/beatmapsets/{mapid}'
    html = r.get(url)
    # with open('./test.html', 'wt', encoding='utf8') as f:
    #     f.write(html.text)
    soup = BeautifulSoup(html.text, 'lxml')
    data = soup.find_all(
        'script', id='json-beatmapset')
    result = json.loads(data[0].text)
    # with open('./data.json', 'wt', encoding='utf8') as f:
    #     f.write(json.dumps(result))
    title = result['title_unicode']
    artist = result['artist_unicode']
    novideo = True if request.args.get('novideo') == '1' else False
    if novideo:
        Downloadurl = f'https://osu.ppy.sh/d/{mapid}n'
    else:
        Downloadurl = f'https://osu.ppy.sh/d/{mapid}'
    topicid = result["legacy_thread_url"].replace('https://osu.ppy.sh/community/forums/topics/','')
    headers = {
        'Host': 'osu.ppy.sh',
        'Connection': 'close',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="101", "Microsoft Edge";v="101"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Upgrade-Insecure-Requests': '1',
        'DNT': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36 Edg/101.0.1210.32',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Referer': f'https://osu.ppy.sh/community/forums/topics/{topicid}?n=1',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cookie': cookie
        }
    download(Downloadurl, f'./.cache/{mapid}.osz', headers)
    # content = response.content
    # with open(f'./.cache/{mapid}.osz', 'wb') as f:
    #     f.write(content)
    return send_from_directory('./.cache', f'{mapid}.osz', as_attachment=True, download_name=f'{title} - {artist}.osz')

def download(url: str, fname: str, headers: dict):
    # ??????stream???????????????url?????????
    resp = r.get(url, stream=True, headers=headers)
    # ??????????????????????????????total????????????0
    total = int(resp.headers.get('content-length', 0))
    # ?????????????????????fname??????(??????????????????)
    # ?????????tqdm??????????????????????????????????????????????????????????????????????????????
    with open(fname, 'wb') as file, tqdm(
        desc=fname,
        total=total,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in resp.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)