import socket
import sys
import argparse
import requests
import re
from bs4 import BeautifulSoup


def print_welcome(lang_list):
    print("Hello, you're welcome to the translator. Translator supports: ")
    for k, v in lang_list.items():
        print(f'{k} : {v}')


def parse_args():
    parser = argparse.ArgumentParser(description="Choose language to to translate")
    parser.add_argument('source', choices=['all', 'arabic', 'german', 'english', 'spanish', 'french', 'hebrew', 'japanese',
                                           'dutch', 'polish', 'portuguese', 'romanian', 'russian', 'turkish'],
                        help='Language to convert from')
    parser.add_argument('target', help='Language to convert to')
    parser.add_argument('word', help='word to translate')
    all_args = parser.parse_args()
    return all_args


def connect(translator, base_word):
    url = f'https://context.reverso.net/translation/{translator}/{base_word}'
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    except socket.error as e:
        print('Something wrong with your internet connection')
        sys.exit()
    if r.status_code == 404:
        print(f"Sorry, unable to find {word}")
        sys.exit()
    return r


def get_translations(conn):
    soup = BeautifulSoup(conn.content, 'html.parser')
    translation_soup = soup.find_all('a', {'class': re.compile('translation ... dict')})
    return [each.text.strip() for each in translation_soup]


def get_source_examples(conn):
    soup = BeautifulSoup(conn.content, 'html.parser')
    example_soup = soup.find_all('div', {'class': 'src ltr'})
    return [each.text.strip() for each in example_soup]


def get_target_examples(conn):
    soup = BeautifulSoup(conn.content, 'html.parser')
    example_soup = soup.find_all('div', {'class': re.compile('trg ...')})
    return [each.text.strip() for each in example_soup]


def print_translations(t_list):
    if multi_flag:
        num_results = 1
    else:
        num_results = 5
    if len(t_list) > num_results:
        for i in range(num_results):
            print(t_list[i])
            save.write(f'{t_list[i]}\n')
    else:
        for t in t_list:
            print(t)
            save.write(f'{t}\n')


def output_examples(src, trg):
    if multi_flag:
        num_results = 1
    else:
        num_results = 5
    if len(src) > num_results or len(trg) > num_results:
        for i in range(num_results):
            try:
                print(f'{src[i]}')
                save.write(f'{src[i]}\n')
                print(f'{trg[i]}\n')
                save.write(f'{trg[i]}\n\n')
            except IndexError as e:
                print(f'No examples found\n')
                save.write(f'No examples found\n\n')
    else:
        for s in src:
            print(s)
            save.write(s)
        for t in trg:
            print(t)
            save.write(t)


def single_translation():
    lang_pair = source_lang + '-' + target_lang
    web_connection = connect(lang_pair, word)

    words = get_translations(web_connection)
    src_examples = get_source_examples(web_connection)
    trg_examples = get_target_examples(web_connection)

    print(f"{target_lang.title()} Translations:")
    save.write(f"{target_lang.title()} Translations:\n")
    print_translations(words)

    print(f'\n{target_lang.title()} Examples:')
    save.write(f'\n{target_lang.title()} Examples:\n')
    output_examples(src_examples, trg_examples)


def all_translations():
    for target in supported.values():
        if target.lower() in source_lang:
            continue
        lang_pair = source_lang + '-' + target.lower()
        web_connection = connect(lang_pair, word)

        words = get_translations(web_connection)
        src_examples = get_source_examples(web_connection)
        trg_examples = get_target_examples(web_connection)

        print(f"{target.title()} Translations:")
        save.write(f"{target.title()} Translations:\n")
        print_translations(words)

        print(f'\n{target.title()} Examples:')
        save.write(f'\n{target.title()} Examples:\n')
        output_examples(src_examples, trg_examples)


supported = {1: 'Arabic', 2: 'German', 3: 'English', 4: 'Spanish', 5: 'French', 6: 'Hebrew', 7: 'Japanese',
             8: 'Dutch', 9: 'Polish', 10: 'Portuguese', 11: 'Romanian', 12: 'Russian', 13: 'Turkish'}


args = parse_args()

try:
    assert str(args.target).title() in supported.values() or "All" in str(args.target).title()
except AssertionError as e:
    print(f"Sorry, the program doesn't support {str(args.target).title()}")
    sys.exit()

source_lang = args.source
target_lang = args.target
word = args.word
multi_flag = False

save = open(f'{word}.txt', 'a', encoding='utf-8')

if target_lang == 'all':
    multi_flag = True
    all_translations()
elif target_lang != 'all':
    single_translation()

save.close()
