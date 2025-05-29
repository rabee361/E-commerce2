import xlrd

from DatabaseOperations import DatabaseOperations

class Importer(object):
	def __init__(self, sqlite, filemanager):
		super().__init__()
		self.filemanager = filemanager
		self.sqlite = sqlite
		self.database_operations = DatabaseOperations(sqlite)

	def importRawsFromExcel(self):
		# Open the workbook and define the worksheet
		file = self.filemanager.openFile("xlsx")
		if file != '':
			excel_work_book = xlrd.open_workbook(file)
			excel_sheet = excel_work_book.sheet_by_index(0)
			for i in range(1,excel_sheet.nrows):
				code = excel_sheet.cell_value(i,0)
				name = excel_sheet.cell_value(i,1)
				quantity = excel_sheet.cell_value(i,2)
				self.database_operations.updateOrAddRawMaterials(code, name, quantity)
		else:
			pass

	def importProductsFromExcel(self):
		# Open the workbook and define the worksheet
		file = self.filemanager.openFile("xlsx")
		if file != '':
			excel_work_book = xlrd.open_workbook(file)
			excel_sheet = excel_work_book.sheet_by_index(0)
			for i in range(1,excel_sheet.nrows):
				code = excel_sheet.cell_value(i,0)
				name = excel_sheet.cell_value(i,1)
				quantity_in_batch = excel_sheet.cell_value(i,2)
				year_require = excel_sheet.cell_value(i,3)
				ready = excel_sheet.cell_value(i,4)
				self.database_operations.updateOrAddProducts(code, name, quantity_in_batch, year_require, ready)
		else:
			pass




