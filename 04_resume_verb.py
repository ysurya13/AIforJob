#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from bs4 import BeautifulSoup
import requests



# In[18]:

def get_action_verbs(url):
    """
    Fetches action verbs from the specified URL and returns them as a list of dictionaries.
    Each dictionary contains a summary and a list of verbs associated with that summary.
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    #print(soup.prettify())

    # get all list items under summary tags
    data = []
    for summary in soup.find_all('summary'):
        list_items = summary.find_next('ul').find_all('li')
        verbs = []
        for item in list_items:
            verbs.append(item.get_text(strip=True))
        data.append({summary.get_text(strip=True):verbs})



    # save the data to a text file
    with open('action_verbs.txt', 'w') as f:
        for entry in data:
            for key, verbs in entry.items():
                f.write(f"{key}:\n")
                for verb in verbs:
                    f.write(f" - {verb}\n")
                f.write("\n")



if __name__ == "__main__":
    url = "https://www.careereducation.columbia.edu/resources/200-action-verbs-spice-your-resume"
    get_action_verbs(url)
    print("Action verbs have been fetched and saved to 'action_verbs.txt'.")

