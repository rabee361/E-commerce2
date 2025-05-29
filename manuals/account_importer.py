import os
from .dat_reader import DatReader
from DatabaseOperations import DatabaseOperations

class AccountImporter:
    def __init__(self, sql_connector):
        self.dat_reader = DatReader()
        self.database_operations = DatabaseOperations(sql_connector)
        
    def import_accounts_from_dat(self, dat_file_path):
        """
        Import accounts from a DAT file into the database
        
        Args:
            dat_file_path (str): Path to the DAT file
            
        Returns:
            int: Number of accounts imported
        """
        # Convert DAT to XML
        xml_file_path = self.dat_reader.convert_dat_to_xml(dat_file_path, output_dir='manuals/xml/')
        if not xml_file_path:
            print(f"Failed to convert DAT file to XML: {dat_file_path}")
            return 0
            
        # Import accounts from XML
        imported_count = self.import_accounts_from_xml(xml_file_path)
        
        # Clean up temporary XML file
        try:
            os.remove(xml_file_path)
        except:
            pass
            
        return imported_count
        
    def import_accounts_from_xml(self, xml_file_path):
        """
        Import accounts from an XML file into the database
        
        Args:
            xml_file_path (str): Path to the XML file
            
        Returns:
            int: Number of accounts imported
        """
        # Read the XML file
        if not self.dat_reader.read_xml_file(xml_file_path):
            print(f"Failed to read XML file: {xml_file_path}")
            return 0
            
        # Get the XML content
        xml_content = self.dat_reader.xml_content
        if xml_content is None:
            print("No XML content available")
            return 0
            
        # Find accounts root element
        accounts_root = xml_content.find(".//accounts")
        if accounts_root is None:
            print("No accounts element found in XML")
            return 0
            
        # Create a dictionary to store account codes and their corresponding database IDs
        account_map = {}
        imported_count = 0
        
        # Process each account hierarchically
        imported_count = self._process_accounts_hierarchy(accounts_root, "", account_map)
            
        return imported_count
    
    def _process_accounts_hierarchy(self, parent_element, parent_code, account_map):
        """
        Process accounts hierarchy recursively
        
        Args:
            parent_element: The parent XML element containing account elements
            parent_code: The code of the parent account
            account_map: Dictionary mapping account codes to their database IDs
            
        Returns:
            int: Number of accounts imported in this branch
        """
        imported_count = 0
        print(account_map)
        
        # Process all direct child accounts
        for account in parent_element.findall("./account"):
            account_name = account.get("name")
            account_code = account.get("code", "")
            account_type = account.get("type_col", "normal")
            
            if not account_name:
                print("Account tag missing name attribute, skipping")
                continue
                
            # Determine parent account ID based on parent_code
            parent_account_id = account_map.get(parent_code, "")
                
            # Create account in database
            try:
                account_id = self.database_operations.addAccount(
                    name=account_name,
                    details="Imported from XML", #TODO: change to details
                    code=account_code,
                    parent_account=str(parent_account_id),
                    account_type=account_type,
                    final_account='',
                    financial_statement="",
                    financial_statement_block="",
                    force_cost_center=0,
                    default_cost_center="",
                    auto=True
                )
                
                # Store the account ID in the map using its code
                if account_code:
                    account_map[account_code] = account_id
                    
                imported_count += 1
                print(f"Imported account: {account_name} (Code: {account_code}, Parent: {parent_code})")
                
                # Process children recursively
                imported_count += self._process_accounts_hierarchy(account, account_code, account_map)
            
            except Exception as e:
                print(f"Failed to import account {account_name}: {str(e)}")
                
        return imported_count


def import_accounts(sql_connector, dat_file_path):
    """
    Convenience function to import accounts from a DAT file
    
    Args:
        sql_connector: Database connection
        dat_file_path (str): Path to the DAT file
        
    Returns:
        int: Number of accounts imported
    """
    importer = AccountImporter(sql_connector)
    return importer.import_accounts_from_dat(dat_file_path) 