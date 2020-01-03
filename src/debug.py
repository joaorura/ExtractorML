import json
import multiprocessing
import requests
import re
from copy import deepcopy
from tqdm import tqdm


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
            "treatment": self._treatment()
        }

        self.regex_list = []
        temp = list(self.regex_dict.items())[0][1:]
        for a in temp:
            for b in a:
                self.regex_list.append(b)

    def _methods(self):
        regex_list = []

        for i in self._data['methods']:
            aux = re.compile(rf"({i}\((([_A-Za-z0-9](\[*'*[- _A-Za-z0-9]'*\]*)*, *)*"
                             rf"( *[ _A-Za-z0-9](\[*'*[- _A-Za-z0-9]'*\]*)* *)+)*\))+")
            regex_list.append(aux)

        return regex_list

    def _lines(self):
        return []

    def _imports(self):
        return []

    def _exceptions(self):
        return []

    def _treatment(self):
        return []





def findMatch(file, regex):
    result = []
    count = 0
    for line in file.splitlines():
        matches = re.search(regex, line)
        if matches is not None:
            to_append = (count, line)
            result.append(to_append)
        count += 1

    return result


def process(data, regex_data, bar, results):
    for file in data:
        file_data = download_file(file[2]).decode('utf-8')

        for a in regex_data:
            search = findMatch(file_data, a)

            finders = []
            for b in search:
                finders.append(b)

            to_append = deepcopy(file)
            to_append.append(finders)
            results.append(to_append)

        # bar.update(1)


def main():
    conf_path = 'conf.json'
    regex_data = Regex(json_process(conf_path)).regex_list

    dir = 'data'
    data = []
    aux = json_process(f'{dir}/tensorflow_data.json')['list']
    for i in aux:
        aux_1 = list(i.values())[1]['items']

        for j in aux_1:
            full_name = j['repository']['full_name']
            name = j['name']
            url = j['html_url'].replace('github.com', 'raw.githubusercontent.com') \
                .replace('/blob', '')
            aux_2 = [full_name, name, url]
            data.append(aux_2)

    cpu_amount = multiprocessing.cpu_count() * 2
    size = len(data) // cpu_amount
    print(len(data), cpu_amount, size)
    begin = end = 0
    the_process = []
    bar = tqdm(max=len(data))
    with multiprocessing.Manager() as manager:
        results = manager.list()

        for a in range(1, cpu_amount + 1):
            begin = size * (a - 1)
            end = size * a
            p = multiprocessing.Process(target=process, args=(data[begin:end], regex_data, bar, results))
            p.start()
            the_process.append(p)

        if end < len(data):
            p = multiprocessing.Process(target=process, args=(data[end + 1:], regex_data, bar, results))
            p.start()
            the_process.append(p)

        for a in the_process:
            a.join()

    print(results)


if __name__ == '__main__':
    main()
