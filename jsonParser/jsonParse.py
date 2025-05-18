import json
import datetime

def jsonParse(nameOfFile, dateStart, dateEnd, nameOfChat, nameOfExit="example.json"):
    try:
        with open(nameOfFile, 'r', encoding="UTF-8") as file:
            loadedData = json.load(file)
            partToParse = -1;
            for i in loadedData["chats"]["list"]:
                if i['name'] == nameOfChat:
                    partToParse = i
                    break
            ans = []
            for message in partToParse["messages"]:
                date = message["date"]
                messageDate = datetime.date(int(date[:4]), int(date[5:7]), int(date[8:10]))
                if messageDate >= dateStart and messageDate <= dateEnd:
                    ans.append(message)
        with open(nameOfExit, "w", encoding="UTF-8") as f:
            f.write(json.dumps(ans))
        with open(nameOfExit, "r", encoding="UTF-8") as f:
            load = json.load(f)
            for i in load:
                print(i["text"])
    except (KeyError, TypeError) as chatNotFound:
        print("Такого чата, вероятно, нет, или даты заданы неправильно")
    except Exception:
        print("Что-то пошло не так")
    