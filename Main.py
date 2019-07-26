import praw
from queue import Queue
import threading
import os
import time

from Subreddit import Subreddit
import ProcessComment
import MessageManager

# PRAW Instance
r = praw.Reddit("InstaMod")
# List of subreddits
sub_list = []
# Queue for users to be analyzed
comment_queue = Queue()
# Queue for users to be flaired
flair_queue = Queue()
# Queue for notifying users of new permissions
perm_queue = Queue()
# Lock for shared resources
lock = threading.Lock()


def read_pms():
    for message in r.inbox.messages():
        if not message.was_comment:
            MessageManager.process_pm(message, sub_list)


# Create all subreddit objects and return multisub for comment stream
def get_multisub():
    # Get all folder names (subreddit names)
    folder_names = [name for name in os.listdir(".")
                    if name.startswith("r-") and os.path.isdir(name)]
    
    # Create subreddit objects and multisub
    multisub_str = ""
    for folder_name in folder_names:
        sub_name = folder_name[2:]
        sub_list.append(Subreddit(folder_name, r))
        multisub_str += sub_name + "+"
        
    return r.subreddit(multisub_str[:-1])
        

def flair_users():
    while not flair_queue.empty():
        flair_data = flair_queue.get()
        flair_queue.task_done()
        
        username = flair_data[0]
        flair_txt = flair_data[1]
        flair_css = flair_data[2]

        print("Flair results..."
              + "\n\tUser: " + username
              + "\n\tFlair: " + flair_txt
              + "\n\tCSS: " + flair_css + "\n")
        

def notify_permission_change():
    while not perm_queue.empty():
        perm_data = perm_queue.get()
        perm_queue.task_done()
        
        username = perm_data[0]
        new_perm = perm_data[1]
        print("Permission results..."
              + "\n\tUser: " + username
              + "\n\tPermission: " + new_perm + "\n")


# Main Method
all_subs = get_multisub()
# Child thread for processing comments
process_thread = threading.Thread(target=ProcessComment.fetch_queue,
                                  args=(comment_queue, flair_queue, perm_queue, sub_list))
process_thread.setDaemon(True)
process_thread.start()

while True:
    try:
        for comment in all_subs.stream.comments(pause_after=1, skip_existing=True):
            if comment is None:
                print("At none")
                flair_users()
                print("Past flair")
                notify_permission_change()
                print("Past perm")
                read_pms()
                print("Past pm")
                continue
            print("Got a comment")
            comment_queue.put(comment)
    except Exception as e:
        print("Error: " + str(e) + "\nSleeping for 1 min")
        time.sleep(60)
