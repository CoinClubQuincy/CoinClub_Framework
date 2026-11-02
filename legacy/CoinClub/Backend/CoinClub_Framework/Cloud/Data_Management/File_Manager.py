import json

class Files:
    def __init__(self):
        print("Initialize File Class")

    def JSON(file_name,Data):
        print("Write Json File")
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(Data, f, ensure_ascii=False, indent=4)

    def READ_JSON(FILE):
        print("Read Json File")
        with open('%s' % FILE) as f:
          data = json.load(f)

        print(data)
        return data

    def CSV(self):
        print("Write CSV")

    def READ_CSV(self):
        print("Read CSV")


#
