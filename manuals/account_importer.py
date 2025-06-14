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
        
        # Find root element - handle both direct root and nested root
        root = xml_content
        if xml_content.tag != "root":
            root = xml_content.find("root")
            if root is None:
                print(f"No root element found in XML: {xml_file_path}")
                return 0
        
        # Process all accounts
        imported_count = self._process_accounts_from_rows(root)
        
        return imported_count
    
    def _process_accounts_from_rows(self, root_element):
        """
        Process accounts from row elements

        Args:
            root_element: The root XML element containing row elements

        Returns:
            int: Number of accounts imported
        """
        imported_count = 0
        account_map = {}  # Maps account names to their database IDs

        # First pass: collect all accounts
        accounts = []
        for row in root_element.findall("./row"):
            # Use Arabic tag names
            account_name = row.find("./account").text if row.find("./account") is not None else None
            account_code = row.find("./code").text if row.find("./code") is not None else ""
            final_account = row.find("./final_account").text if row.find("./final_account") is not None else ""
            parent_account_name = row.find("./main_account").text if row.find("./main_account") is not None else ""

            if not account_name:
                print("Row missing account element, skipping")
                continue

            accounts.append({
                "name": account_name,
                "code": account_code,
                "final_account": final_account,
                "parent_account_name": parent_account_name.strip() if parent_account_name else ""
            })

        # Sort accounts to ensure parents are created before children
        # Main accounts (without parent) should be created first
        accounts.sort(key=lambda x: (len(x["parent_account_name"]), len(x["code"])))

        # Second pass: create accounts in order
        for account in accounts:
            account_name = account["name"]
            account_code = account["code"]
            final_account = account["final_account"]
            parent_account_name = account["parent_account_name"]

            # Determine parent account based on main_account tag
            parent_account_id = ""
            if parent_account_name:
                # Look up parent account ID by name
                if parent_account_name in account_map:
                    parent_account_id = account_map[parent_account_name]
                else:
                    print(f"Warning: Parent account '{parent_account_name}' not found for account '{account_name}'")

            # Determine parent account based on main_account tag
            final_account_id = ""
            if final_account:
                # Look up parent account ID by name
                if final_account in account_map:
                    final_account_id = account_map[final_account]
                else:
                    print(f"Warning: Parent account '{final_account}' not found for account '{account_name}'")

            # Create account in database
            try:
                account_id = self.database_operations.addAccount(
                    name=account_name,
                    details="Imported from XML",
                    code=account_code,
                    parent_account=str(parent_account_id),
                    account_type="normal",
                    final_account=final_account_id,
                    financial_statement="",
                    financial_statement_block="",
                    force_cost_center=0,
                    default_cost_center="",
                    auto=True
                )

                # Store the account ID in the map using its name for parent lookup
                account_map[account_name] = account_id

                imported_count += 1
                parent_info = f"Parent: {parent_account_name} (ID: {parent_account_id})" if parent_account_name else "No parent (main account)"
                print(f"Imported account: {account_name} (Code: {account_code}, {parent_info})")

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
