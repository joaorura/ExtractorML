import json
import multiprocessing
import sys
import token
import tokenize

import requests
import re
import os
from tqdm import tqdm

multiprocessing.freeze_support()


def json_process(file):
    with open(file) as jf:
        json_data = json.load(jf)
    return json_data


def download_file(url):
    answer = requests.get(url)
    if answer.status_code == requests.codes.OK:
        return answer.content
    else:
        answer.raise_for_status()


class Regex:
    def __init__(self, data):
        self._data = data
        self.regex_dict = {
            "methods": self._methods(),
            "lines": self._lines(),
            "imports": self._imports(),
            "exceptions": self._exceptions(),
        }

        self.regex_list = []
        temp = list(self.regex_dict.items())
        for a in temp:
            aux = a[1:]
            for b in aux:
                for c in b:
                    self.regex_list.append(c)

    def _methods(self):
        regex_list = []

        for i in self._data['methods']:
            aux = re.compile(rf"({i}\(( *(([_A-Za-z0-9](\[*[- _A-Za-z0-9'\"]\]*)* *, *)*"
                             rf"[_A-Za-z0-9](\[*[- _A-Za-z0-9'\"]*\]*)* *)+)*)\)")
            regex_list.append(aux)

        return regex_list

    def _lines(self):
        return self._data['lines']

    def _imports(self):
        regex_list = []
        for i in self._data['imports']:
            aux = re.compile(rf"((from|import)+ +)+{i}( +(as|import))* *[a-zA-Z0-9_]*")
            regex_list.append(aux)

        return regex_list

    def _exceptions(self):
        regex_list = []
        for i in self._data['exceptions']:
            aux = re.compile(rf"raise +{i}(\(*( *(([_A-Za-z0-9](\[*[- _A-Za-z0-9'\"]\]*)* *, *)*"
                             rf"( *[_A-Za-z0-9](\[*[- _A-Za-z0-9'\"]\]*)* *)+)*)\)*)")
            regex_list.append(aux)

            aux = re.compile(rf"except +{i}:")
            regex_list.append(aux)

        return regex_list


def find_match(file, regex):
    result = []
    count = 1
    for line in file.splitlines():
        matches = re.search(regex, line)
        if matches is not None:
            to_append = {"number_line": count, "line": line}
            result.append(to_append)
        count += 1

    return result


def remove_comments(source):
    source = re.sub(re.compile(r"# *[#_\-'\"A-Za-z0-9 ]*", re.DOTALL), "", source)
    source = re.sub(re.compile(r'(""")[\n\t#_\-\'"A-Za-z0-9 ]*(""")'), "", source)

    return source


def get_super(line, aux_file_0, aux_file_1):
    start = end = 0
    for start in range(line - 1, -1, -1):

        search = re.search(r"(def|class) *[_A-Za-z0-9]+", aux_file_0[start])

        if search is not None:
            break

    for end in range(line - 1, len(aux_file_0)):
        search = re.search(r"^\n(?!\t)", aux_file_0[end])
        if search is not None:
            break

    if start != 0 or end != len(aux_file_0):
        result = aux_file_1[start:end]
        for i in range(0, len(result)):
            result[i] += "\n"

        return result
    else:
        return None


def process(data, regex_data, results, n):
    for file in tqdm(data, desc=f'Processor {n}'):
        aux_0 = file["http_file"].replace('github.com', 'raw.githubusercontent.com') \
            .replace('/blob', '')

        try:
            file_data = download_file(aux_0).decode('utf-8')
        except UnicodeDecodeError:
            print(f"Error in decode file. Link: {file['http_file']}")
            continue

        file_data = remove_comments(file_data)
        aux_file_0 = file_data.replace("\n", "'~\n").split("~")
        aux_file_1 = file_data.splitlines()

        list_of_data = {
            "info": file,
            "results": {}
        }
        for a in regex_data:
            list_of_data["results"][a] = {
                "items": []
            }
            aux = list_of_data["results"][a]["items"]

            for b in regex_data[a]:
                search = find_match(file_data, b)

                finders = []
                for c in search:
                    finders.append({"method": get_super(c["number_line"], aux_file_0, aux_file_1), "data_line": c})

                if len(finders) != 0:
                    for i in finders:
                        aux.append(i)

            list_of_data["results"][a]["amount_items"] = len(aux)

        results.append(list_of_data)


def main():
    conf_path = 'system/conf.json'
    regex_data = Regex(json_process(conf_path)).regex_dict

    _dir = 'data'
    data = []

    for file in os.listdir(_dir):
        if re.search('.json', file) is None:
            raise SystemError("Todos os arquivos dentro de data devem ser json.")

        aux = json_process(f'{_dir}/{file}')['list']

        for i in aux:
            aux_1 = list(i.values())[1]['items']

            for j in aux_1:
                aux_2 = {
                    "name_repositories": j['repository']['full_name'],
                    "file_name": j['name'],
                    "http_file": j['html_url']
                }

                data.append(aux_2)

    cpu_amount = multiprocessing.cpu_count()
    if len(data) < cpu_amount:
        cpu_amount = len(data)
    if cpu_amount * 10 < len(data):
        cpu_amount *= 10

    size = len(data) // cpu_amount
    print(len(data), cpu_amount, size, len(regex_data))
    end = 0
    the_process = []

    with multiprocessing.Manager() as manager:
        results = manager.list()

        for a in range(1, cpu_amount + 1):
            begin = size * (a - 1)
            end = size * a
            p = multiprocessing.Process(target=process, args=(data[begin:end], regex_data, results, a))
            p.start()
            the_process.append(p)

        if end < len(data):
            p = multiprocessing.Process(target=process, args=(data[end + 1:], regex_data, results, a + 1))
            p.start()
            the_process.append(p)

        for a in the_process:
            a.join()

        results = {"results": list(results)}
        for i in regex_data:
            results['amount_' + i] = 0

        for i in results['results']:
            for j in i["results"]:
                results["amount_" + j] += i["results"][j]['amount_items']

        try:
            test = int(sys.argv[1] != 1)
        except IndexError:
            test = False

        if test:
            with open('system/result.json', 'w', encoding='utf-8') as write:
                json.dump(results, write, ensure_ascii=False, indent=4)
        else:
            print(json.dumps(results, indent=4))


if __name__ == '__main__':
    main()
