import xlsxwriter

from FileManager import FileManager

class Exporter:
    def __init__(self):
        super().__init__()
        self.filemanager = FileManager()
        print("Exporter class initiated.")


    def exportTableToExcel(self, table):
        file_name = self.filemanager.createEmptyFile('xlsx')
        workbook = xlsxwriter.Workbook(file_name)

        bold_format = workbook.add_format({
            'bold': True,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'})

        yellow_format = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': 'yellow',
            'color': 'black'})

        green_format = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': 'green',
            'color': 'white'})

        red_format = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': 'red',
            'color': 'white'})

        center_format = workbook.add_format({
            'align': 'center'
        })

        worksheet = workbook._add_sheet("Simple Plan Result")

        worksheet.right_to_left()

        columns_count = table.columnCount()
        rows_count = table.rowCount()

        #get headers
        for i in range(0, columns_count):
            header = table.horizontalHeaderItem(i).text()
            worksheet.write(0, i, str(header), center_format)

        workbook.close()
