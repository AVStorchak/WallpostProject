def load_posts(query_id, query_date):
    all_posts = []
    parsing_counter = 0

    with requests.Session() as s:
        while True:
            url = f'https://api.vk.com/method/wall.get?owner_id={query_id}&count=100&offset={parsing_counter*100}&v=5.103&access_token={token}'

            resp = s.get(url)
            resp_text = json.loads(resp.text)
            parsing_counter += 1

            all_posts.extend(resp_text['response']['items'])
            if all_posts[-1]['date'] < query_date:
                return all_posts
            if len(all_posts) == resp_text['response']['count']:
                return all_posts
