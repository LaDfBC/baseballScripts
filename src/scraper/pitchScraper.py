from src.scraper.Post import Post

# TODO: This absolutely needs to be refactored into a class, but I suck.  Please don't judge me.

# Uses the PRAW instance of Reddit
def sync_all_posts(reddit):
    posts = reddit.subreddit("BaseballbytheNumbers").hot(limit = 25)

    for post in posts:
        if post.link_flair_text == None:
            continue

        current_post = Post(post)
        # try:
        pitches = current_post.get_pitches()
        print(pitches)
        # except:
        #     print("Failed to parse post: " + post.title)



def sync_posts_since(time):
    return None
