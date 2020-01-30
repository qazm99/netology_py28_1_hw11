import requests
import os


# Получаем текст из файла по его пути/имени
def get_file_text(file, encoding='utf8'):
    try:
        with open(file, encoding=encoding) as file:
            text_to_translate = file.read()
            print(f'Текст из файла {file.name} получен')
            return text_to_translate
            # print(text_to_translate)
    except FileNotFoundError as e:
        print('Файл не найден')


# Запись текста в файл - передаем текст и путь/имя файла
def text_to_file(text, filename, encoding='utf8'):
    try:
        with open(filename + '.txt', 'w', encoding=encoding) as file:
            file.write(text)
            print(f'Текст перевода в файл {file.name} записан')
            return file.name
    except Exception as e:
        print(f'Не удалось записать файл {filename}: {e}')


# переводим на яндекс переводчике текст, с исходного языка, на целевой язык, указываем ключ
def translate_it(text, lang_text, to_lang, apy_key):
    """
    https://translate.yandex.net/api/v1.5/tr.json/translate ?
    key=<API-ключ>
     & text=<переводимый текст>
     & lang=<направление перевода>
     & [format=<формат текста>]
     & [options=<опции перевода>]
     & [callback=<имя callback-функции>]
    :param to_lang:
    :return:
    """

    URL = 'https://translate.yandex.net/api/v1.5/tr.json/translate'
    try:
        params = {
            'key': apy_key,
            'text': text,
            'lang': (lang_text + '-{}').format(to_lang),
        }

        response = requests.get(URL, params=params)
        # print(response.status_code)
        json_ = response.json()
        print(f'Перевели текст файла с {lang_text} на {to_lang}: {json_.get("text")[0][:40]}...')
        return ''.join(json_['text'][0])
    except Exception as e:
        print(f'Не удалось перевести текст: {e}')
        print(f'Код ответа: {response.status_code}, {json_["code"]} - {json_["message"]}')


# отправить файл на яндексдиск, передаем путь к файлу, путь назначения файла на Ядиске, передаем токен OAuth Ядиска
def go_to_disk(filename, path_to='/', oauth=''):
    url_disk = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
    headers = {
        'Authorization': 'OAuth ' + oauth,
    }
    params = {
        'path': path_to + filename,
        'overwrite': 'true',
    }
    try:
        with open(filename, 'rb', ) as file:
            filedata = file.read()
            files = {
                'file': filedata,
            }
            # по полученной ссылке отправляем данные из файла
            response = requests.get(url_disk, headers=headers, params=params, timeout=10)
            json_response = response.json()
            params['file'] = file.name
            if json_response.get('href') != None:
                response = requests.put(json_response['href'], filedata)
                json2_response = response
                return json2_response.status_code, json2_response.reason
            else:
                print(f'Не удалось получить ссылку на загрузку файла: {json_response.get("message")}')
    except Exception as e:
        print(f'Не получилось отправить файл {filename} на Ядиск: {e}')


# # print(translate_it('В настоящее время доступна единственная опция — признак включения в ответ автоматически определенного языка переводимого текста. Этому соответствует значение 1 этого параметра.', 'no'))

if __name__ == '__main__':
    api_key = 'trnsl.1.1.20200125T113951Z.d376771cc4d168af.1614e80afaec48ec7f1de03eac47de3c5d9f880e'
    oauth = 'AgAAAAA8h00sAAYYxIB99O-YTUbOujGHJ0PR508'
    print('Запущена программа перевода текстовых файлов с наименованием исходного языка для перевода')
    # находим все текстовые файлы с  полной длиной имени файла 6 символов
    for file in os.listdir():
        if file.endswith(".txt") and len(file) == 6:
            leng_original = file[:2]  # получаем исходный язык текста
            text_orig = get_file_text(file)
            # получаем файл и сохраняем на диск из переведенного текста, исходный язык определяем по имени файла, язык назначения русский
            file_to_disk = text_to_file(translate_it(text_orig, leng_original.lower(), 'ru', api_key),
                                        'RUform' + leng_original)
            # Отправляем файл на Ядиск
            # Если все хорошо файлики появятся здесь https://yadi.sk/d/8Z2Rwp3xQyw0yA
            if file_to_disk != None:
                result_put_file = go_to_disk(file_to_disk, '/translate/', oauth=oauth)
                if result_put_file is not None:
                    if result_put_file[0] == 201:
                        print(f'Файл {file_to_disk} успешно отправлен на Ядиск')
                    else:
                        print(f'Не удалось отправить файл на Ядиск: {result_put_file[0]} - {result_put_file[1]}')
                else:
                    print('Не получен ответ от севрера при отправке')
            else:
                print(f'Не сформирован файл для отправки из {file}')
    print('Завершена программа перевода текстовых файлов')
