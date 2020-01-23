import csv
import io
import matplotlib.pyplot as plt
import vk
from datetime import datetime


token = '41f3b5d941f3b5d941f3b5d984419c87bc441f341f3b5d91fd7d26e4f0bd94fa406d9cf'
vk_id = 'app7287397_184125'
session = vk.Session(access_token=token)
vkapi = vk.API(session, v='5.103')
plot_list = ['posts', 'comments', 'likes', 'reposts']
plt.style.use('seaborn')
title = ', '.join(plot_list[1:])
params = {'axes.labelsize': 'x-large',
          'axes.titlesize':'x-large',
          'xtick.labelsize':'large',
          'ytick.labelsize':'x-large',
          'figure.titlesize':'xx-large'}
plt.rcParams.update(params)


def get_query_id(name):
    """
    Creates a query id from the passed user name
    """
    if name.isnumeric():
        name = 'id' + name
    response = vkapi.utils.resolveScreenName(access_token=token,
                                             screen_name=name)
    if response['type'] == 'group':
        return -response['object_id']
    elif response['type'] == 'user':
        return response['object_id']


def get_query_timestamp(date):
    """
    Converts the passed date to a UNIX timestamp
    """
    stripped_date = datetime.strptime(date, "%Y-%m-%d").timestamp()
    return stripped_date


def load_posts(query_id, query_date):
    """
    Downloads batches of posts from the specified user/group
    wall until the specified date is reached/surpassed or 
    the wall is exhausted.
    """
    all_posts = []
    parsing_counter = 0

    while True:
        posts = vkapi.wall.get(owner_id=query_id,
                               count=100,
                               offset=parsing_counter*100)
        parsing_counter += 1
        all_posts.extend(posts['items'])
        if all_posts[-1]['date'] < query_date:
            return all_posts
        if len(all_posts) == posts['count']:
            return all_posts


def cleanup_counts(post):
    """
    For eligible fields (i.e. likes, reposts, etc.), converts 
    nested dicts with 'count' keys to the corresponding
    count values.
    """
    for k, v in iter(post.items()):
        try:
            post[k] = v['count']
        except TypeError:
            post[k] = v
    return post


def filter_posts(all_posts, query_date):
    """
    Eliminates posts that do not fall within the specified time period
    and strips the post data from unnecessary fields.
    Converts reposted text to post text.
    Reduces application data to the 'apps' and 'app_count' fields.
    """
    fields = ['id', 'text', 'comments', 'likes', 'reposts']
    filtered_posts = []
    for post in all_posts:
        app_list = []
        app_count = 0

        if post['date'] > query_date:
            filtered_post = {k: v for k, v in iter(post.items()) if k in fields}

            try:
                filtered_post['text'] = post['copy_history'][0]['text']
            except KeyError:
                pass

            try:
                for i in post['attachments']:
                    if i['type'] == 'link' and i['link']['caption'] == 'Application':
                        app_list.append(i['link']['url'])
                        app_count += 1
            except KeyError:
                pass

            filtered_post['apps'] = ', '.join(app_list)
            filtered_post['app_count'] = app_count
            filtered_post['date'] = datetime.fromtimestamp(post['date'])
            filtered_post = cleanup_counts(filtered_post)
            filtered_posts.append(filtered_post)
    return filtered_posts


def plot_year_stats(data):
    """
    Plots dataframe with stats per year.
    """
    post_stats = data.groupby([data["date"].dt.year]).mean()
    post_stats['posts'] = data.groupby([data["date"].dt.year]).size()
    year_title = f'Number of posts and average amount of {title} per year'

    axes = post_stats[plot_list].plot(kind="bar", alpha=0.7, figsize=(15, 20),
                                      title=year_title, legend=False,
                                      subplots=True, sharex=False)
    for ax in axes:
        ax.set_xlabel('')
        ax.set_ylabel('Count')
        for p in ax.patches:
            ax.annotate(str(round(p.get_height(), 2)),
                        (p.get_x(), p.get_height() * 1.005))

    output = io.BytesIO()
    plt.savefig(output)
    return output.getvalue()


def plot_month_stats(data):
    """
    Plots dataframe with stats per month.
    """
    month_map = {'1': 'JAN', '2': 'FEB', '3': 'MAR', '4': 'APR',
                 '5': 'MAY', '6': 'JUN', '7': 'JUL', '8': 'AUG',
                 '9': 'SEP', '10': 'OCT', '11': 'NOV', '12': 'DEC'}

    post_stats = data.groupby([data["date"].dt.month]).mean()
    post_stats['posts'] = data.groupby([data["date"].dt.month]).size()
    month_title = f'Number of posts and average amount of {title} per month'

    axes = post_stats[plot_list].plot(kind="bar", alpha=0.7, figsize=(15, 20),
                                      title=month_title, legend=False,
                                      subplots=True, sharex=False)
    for ax in axes:
        ax.set_xlabel('')
        ax.set_ylabel('Count')
        labels = [item.get_text() for item in ax.get_xticklabels()]
        ax.set_xticklabels([month_map[month] for month in labels])
        for p in ax.patches:
            ax.annotate(str(round(p.get_height(), 2)),
                        (p.get_x(), p.get_height() * 1.005))

    output = io.BytesIO()
    plt.savefig(output)
    return output.getvalue()


def plot_weekday_stats(data):
    """
    Plots dataframe with stats per weekday.
    """
    weekday_map = {'0': 'MON', '1': 'TUE', '2': 'WED', '3': 'THU',
                   '4': 'FRI', '5': 'SAT', '6': 'SUN'}

    post_stats = data.groupby([data["date"].dt.weekday]).mean()
    post_stats['posts'] = data.groupby([data["date"].dt.weekday]).size()
    week_title = f'Number of posts and average amount of {title} per weekday'

    axes = post_stats[plot_list].plot(kind="bar", alpha=0.7, figsize=(15, 20),
                                      title=week_title, legend=False,
                                      subplots=True, sharex=False)
    for ax in axes:
        ax.set_xlabel('')
        ax.set_ylabel('Count')
        labels = [item.get_text() for item in ax.get_xticklabels()]
        ax.set_xticklabels([weekday_map[weekday] for weekday in labels])
        for p in ax.patches:
            ax.annotate(str(round(p.get_height(), 2)),
                        (p.get_x(), p.get_height() * 1.005))

    output = io.BytesIO()
    plt.savefig(output)
    return output.getvalue()


def plot_hour_stats(data):
    """
    Plots dataframe with stats per hour.
    """
    post_stats = data.groupby([data["date"].dt.hour]).mean()
    post_stats['posts'] = data.groupby([data["date"].dt.hour]).size()
    hour_title = f'Number of posts and average amount of {title} per hour'

    axes = post_stats[plot_list].plot(kind="bar", alpha=0.7, figsize=(15, 20),
                                      title=hour_title, legend=False,
                                      subplots=True, sharex=False)
    for ax in axes:
        ax.set_xlabel('')
        ax.set_ylabel('Count')
        for p in ax.patches:
            ax.annotate(str(round(p.get_height(), 2)),
                        (p.get_x(), p.get_height() * 1.005))

    output = io.BytesIO()
    plt.savefig(output)
    return output.getvalue()


def compose_csv(data, requested_fields):
    """
    Creates an IO object to be passed as csv data.
    """
    output = io.StringIO()

    with output as file:
        vk_writer = csv.writer(file, delimiter=',', quotechar='"',
                               quoting=csv.QUOTE_MINIMAL)
        vk_writer.writerow(requested_fields)
        for row in data:
            adjusted_row = [v for k, v in row.items() if k in requested_fields]
            vk_writer.writerow(adjusted_row)
        csv_data = output.getvalue()

    return csv_data
