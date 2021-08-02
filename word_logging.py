import pandas as pd
import re
import json

data = pd.read_csv('/Users/tylerkim/Desktop/SquarePanda/SquareTales Mappings/SquareTales Sets 1-16 - Sheet1.csv')

# internal dicts
word_mappings = {}
new_words = {}
book_pages = {}
word_occurance = {}
words_order = {}

# engineering dicts
eng_pages = {}
eng_word_dict = {}
eng_new_word_dict = {}
eng_new_word_count_book = {}
eng_new_word_count_page = {}

for _, row in data.iterrows():
    title = row['Title']
    book = row["Book #"]
    set = row["SET"]
    # use 'booksets' as an absolute book reference, since books only range from 1-5
    bookset = (set - 1) * 5 + book
    # remove punctuation and convert everything to lowercase so "Name" and "name" are not different words
    words = re.sub(r'[^\w\s]', '', row['Words on Page'].lower())
    # split words string into a list
    w_list = words.split()
    for word in w_list:
        seen = []
        for sets in word_mappings.keys():
            seen.extend(list(word_mappings[sets].keys()))
#
###       ** Depending on if you want ordering by book, set, or title,
###       replace each occurence with the desired attribute (e.g. in line 41,
###       replace 'set' with 'book')**
#
##      Uncomment next two lines to get the new words in each set/book/title
#         if word not in seen:
#           new_words.setdefault(set, []).append(word)

##        Uncomment next two lines to get word counts for each set/book/title
#         word_mappings.setdefault(set, {}).setdefault(word, 0)
#         word_mappings[set][word] += 1
#
##        Uncomment next two lines to get word occurence totals
#         word_occurance.setdefault(word, 0)
#         word_occurance[word] += 1
#
##        Uncomment next 3 lines to get words in order of occurence for each title/book
#         words_order.setdefault(title, [])
#         if word not in words_order[title]:
#             words_order[title].append(word)

if word_occurance:
    # reorder the dictionary in terms of most common word
    word_occurance = {k: v for k, v in sorted(word_occurance.items(), reverse=True, key=lambda item: item[1])}

## Uncomment to get content page values for each bookset
# for _, row in data.iterrows():
#     book = row['Book #']
#     set = row['SET']
#     bookset = (set - 1) * 5 + book
# #   Because Page 2 is the Content page 1, subtract 1 from each page value
#     page = row['Page #'] - 1
#     if page > book_pages[bookset]:
#         book_pages[bookset] = page
#

# constructs dictionaries for engineering
seen = []
for _, row in data.iterrows():
    title = row['Title']
    book = f'book_{row["Book #"]}'
    set = f'set_{row["SET"]}'
    page = row['Page #'] - 1
    track = 'track_2' if row['SET'] <= 8 else 'track_3'
    words = re.sub(r'[^\w\s]', '', row['Words on Page'].lower())
    w_list = words.split()

    eng_pages.setdefault(track, {}).setdefault(set, {}).setdefault(book, 0)
    if page > eng_pages[track][set][book]:
        eng_pages[track][set][book] = page
    new_words = []
    for word in w_list:
        eng_word_dict.setdefault(track, {}).setdefault(set, {}).setdefault(book, {}).setdefault(f'page_{page}', {}).setdefault(word, 0)
        eng_word_dict[track][set][book][f'page_{page}'][word] += 1
        eng_new_word_count_page.setdefault(track, {}).setdefault(set, {}).setdefault(book, {}).setdefault(f'page_{page}', {}).setdefault(word, 0)
        eng_new_word_count_page[track][set][book][f'page_{page}'][word] += 1
        eng_new_word_count_book.setdefault(track, {}).setdefault(set, {}).setdefault(book, {}).setdefault(word, 0)
        eng_new_word_count_book[track][set][book][word] += 1

        if word not in seen:
            new_words.append(word)
            seen.append(word)


    eng_new_word_dict.setdefault(track, {}).setdefault(set, {}).setdefault(book, []).extend(new_words)
    eng_new_word_count_page[track][set][book][f'page_{page}']['new_words'] = new_words
    eng_new_word_count_book[track][set][book].setdefault('new_words', []).extend(new_words)


print(f'nwd: {eng_new_word_dict}')
print(f'nwdp: {eng_new_word_count_page}')
print(f'nwdb: {eng_new_word_count_book}')





all = {'word_dict': eng_word_dict, 'book_pages': eng_pages, 'new_word_with_count_page': eng_new_word_count_page, 'new_words':eng_new_word_dict, 'new_word_with_count_book':eng_new_word_count_book}

# uncomment to save the engineering dictionaries as json
with open('squaretales_page_word_map.json', 'w') as f:
    json.dump(all, f)

## uncomment to save dictionary in the first parameter as a data frame, then to csv
# df = pd.DataFrame.from_dict(words_order, orient='index')
# df.to_csv('/Users/tylerkim/Desktop/SquarePanda/words_order.csv')