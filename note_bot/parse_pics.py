import os
from note_bot.models import add_card, add_topic, get_topics_ids


def parse_topics():
    have = get_topics_ids()
    print(have)
    # todo: изменить бекслеш на слеш для линукса - там путь через обычный слеш
    for root, dirs, files in os.walk("static"):
        if root == 'static' or int(root.split('\\')[-1]) in have:
            if root != 'static':
                print("тема", int(root.split('\\')[-1]), "уже есть в таблице")
            else:
                print('static')
            continue
        topic_id = int(root.split('\\')[-1])
        pics_paths = {}
        pics_descriptions = {}
        topic = []  #['name', 'description']    #todo: переписать через датакласс/именованный кортеж
        for file in files:
            if file.split('.')[-1] == 'txt':
                topic.append(file.split('.')[0])    #запоминаем название темы
                with open(os.path.join(root, file), 'r', encoding="utf-8") as f:
                    topic.append(f.readline().rstrip())      #запоминаем описание темы
                    a = f.readlines()
                    for i in range(len(a)):
                        pics_descriptions[i+1] = a[i].rstrip()
            else:
                num = int(file.split('.')[0])
                pics_paths[num] = os.path.join(root, file)

        add_topic(topic_id, topic[0], topic[1], len(pics_paths))

        for key in sorted(pics_paths.keys()):
            add_card(topic_id, key, pics_paths[key], pics_descriptions[key])
