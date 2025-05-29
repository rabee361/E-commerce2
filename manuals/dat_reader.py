import os
import base64
from lxml import etree


class DatReader:
    def __init__(self):
        self.xml_content = None
        
    def read_dat_file(self, file_path):
        """
        Read an encrypted XML content from a .dat file and decrypt it
        
        Args:
            file_path (str): Path to the .dat file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check if file exists and has .dat extension
            if not os.path.exists(file_path) or not file_path.lower().endswith('.dat'):
                print(f"Error: Invalid file path or not a .dat file: {file_path}")
                return False
            
            # Read the encrypted content
            with open(file_path, 'rb') as f:
                encrypted_content = f.read()
            
            # Decrypt the content (assuming base64 encoding)
            try:
                decrypted_content = base64.b64decode(encrypted_content)
                # Try to parse as XML to verify it's valid
                self.xml_content = etree.fromstring(decrypted_content)
                return True
            except base64.binascii.Error:
                print("Error: File content is not valid base64 encoded data")
                return False
            except etree.XMLSyntaxError as e:
                print(f"Error: Decrypted content is not valid XML: {e}")
                return False
                
        except Exception as e:
            print(f"Error reading DAT file: {e}")
            return False
    
    def read_xml_file(self, file_path):
        """
        Read an XML file to be converted to .dat format
        
        Args:
            file_path (str): Path to the XML file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check if file exists and has .xml extension
            if not os.path.exists(file_path) or not file_path.lower().endswith('.xml'):
                print(f"Error: Invalid file path or not an XML file: {file_path}")
                return False
            
            # Parse the XML file
            self.xml_content = etree.parse(file_path).getroot()
            return True
        
        except Exception as e:
            print(f"Error reading XML file: {e}")
            return False
    
    def save_as_xml(self, output_path=None):
        """
        Save the decrypted XML content to a file
        
        Args:
            output_path (str, optional): Path where to save the XML file.
                                       If None, uses the same name as input file with .xml extension
            
        Returns:
            str: Path to the saved XML file or None if failed
        """
        if self.xml_content is None:
            print("No XML content to save. Call read_dat_file() first.")
            return None
        
        try:
            # Create XML tree
            tree = etree.ElementTree(self.xml_content)
            
            # Write XML to file with proper encoding and formatting
            tree.write(
                output_path,
                encoding="utf-8",
                xml_declaration=True,
                pretty_print=True
            )
            
            print(f"XML file saved to: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error saving XML file: {e}")
            return None
    
    def save_as_dat(self, output_path=None):
        """
        Save the XML content as an encrypted .dat file
        
        Args:
            output_path (str, optional): Path where to save the .dat file.
                                       If None, uses the same name as input file with .dat extension
            
        Returns:
            str: Path to the saved .dat file or None if failed
        """
        if self.xml_content is None:
            print("No XML content to save. Load XML content first.")
            return None
        
        try:
            # Convert XML to string with proper formatting
            xml_string = etree.tostring(
                self.xml_content,
                encoding="utf-8",
                xml_declaration=True,
                pretty_print=True
            )
            
            # Encrypt the content using base64
            encrypted_content = base64.b64encode(xml_string)
            
            # Write to .dat file
            with open(output_path, 'wb') as f:
                f.write(encrypted_content)
            
            print(f"DAT file saved to: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error saving DAT file: {e}")
            return None
    
    def convert_dat_to_xml(self, dat_file_path, output_dir=None):
        """
        Convenience method to convert a .dat file to XML in one step
        
        Args:
            dat_file_path (str): Path to the .dat file
            output_dir (str, optional): Directory to save the XML file
            
        Returns:
            str: Path to the saved XML file or None if failed
        """
        if self.read_dat_file(dat_file_path):
            # Determine output path
            if output_dir:
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                base_name = os.path.splitext(os.path.basename(dat_file_path))[0]
                output_path = os.path.join(output_dir, f"{base_name}.xml")
            else:
                output_path = os.path.splitext(dat_file_path)[0] + ".xml"
                
            return self.save_as_xml(output_path)
        return None
    
    def convert_xml_to_dat(self, xml_file_path, output_dir=None):
        """
        Convenience method to convert an XML file to .dat in one step
        
        Args:
            xml_file_path (str): Path to the XML file
            output_dir (str, optional): Directory to save the .dat file
            
        Returns:
            str: Path to the saved .dat file or None if failed
        """
        if self.read_xml_file(xml_file_path):
            # Determine output path
            if output_dir:
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                base_name = os.path.splitext(os.path.basename(xml_file_path))[0]
                output_path = os.path.join(output_dir, f"{base_name}.dat")
            else:
                output_path = os.path.splitext(xml_file_path)[0] + ".dat"
                
            return self.save_as_dat(output_path)
        return None


def dat_to_xml(dat_file_path, output_dir=None):
    """
    Convenience function to convert a .dat file to XML in one step
    
    Args:
        dat_file_path (str): Path to the .dat file
        output_dir (str, optional): Directory to save the XML file
        
    Returns:
        str: Path to the saved XML file or None if failed
    """
    reader = DatReader()
    return reader.convert_dat_to_xml(dat_file_path, output_dir)


def xml_to_dat(xml_file_path, output_dir=None):
    """
    Convenience function to convert an XML file to .dat in one step
    
    Args:
        xml_file_path (str): Path to the XML file
        output_dir (str, optional): Directory to save the .dat file
        
    Returns:
        str: Path to the saved .dat file or None if failed
    """
    reader = DatReader()
    return reader.convert_xml_to_dat(xml_file_path, output_dir)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python dat_reader.py <command> <file_path> [output_directory]")
        print("Commands:")
        print("  toxml  - Convert .dat file to XML")
        print("  todat  - Convert XML file to .dat")
        sys.exit(1)
        
    command = sys.argv[1].lower()
    file_path = sys.argv[2]
    output_dir = sys.argv[3] if len(sys.argv) > 3 else None
    
    if command == "toxml":
        dat_to_xml(file_path, output_dir)
    elif command == "todat":
        xml_to_dat(file_path, output_dir)
    else:
        print(f"Unknown command: {command}")
        print("Valid commands: toxml, todat")