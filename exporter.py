import csv
import json


class ExportSpiderData:
    def export(self, file_name: str, data):
        raise NotImplementedError


class ExportCsv(ExportSpiderData):

    def export(self, file_name: str, data):
        if data and data[0]:
            fields = data[0]._fields
            with open(f'{file_name}.csv', 'w', newline='') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(fields)
                writer.writerows(data)


class ExportJson(ExportSpiderData):

    def export(self, file_name: str, data):
        with open(f'{file_name}.json', 'w', encoding='utf-8') as f:
            # for row in data:
            json.dump([row._asdict() for row in data],
                      f, ensure_ascii=False, indent=4)


class ExportGoogleSheet(ExportSpiderData):
    pass
