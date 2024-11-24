import re
from typing import Dict, Union, Any

class VDFParser:
    def __init__(self):
        self.current_pos = 0
        self.text = ""
        
    def parse_file(self, filename: str) -> Dict[str, Any]:
        """Parse a VDF file and return the data as a nested dictionary."""
        with open(filename, 'r', encoding='utf-8') as f:
            self.text = f.read()
        self.current_pos = 0
        return self.parse()
    
    def parse_string(self, text: str) -> Dict[str, Any]:
        """Parse a VDF string and return the data as a nested dictionary."""
        self.text = text
        self.current_pos = 0
        return self.parse()
    
    def skip_whitespace(self):
        """Skip whitespace and comments."""
        while self.current_pos < len(self.text):
            # Skip whitespace
            while self.current_pos < len(self.text) and self.text[self.current_pos].isspace():
                self.current_pos += 1
                
            # Skip comments
            if self.current_pos < len(self.text) - 1 and self.text[self.current_pos:self.current_pos + 2] == '//':
                while self.current_pos < len(self.text) and self.text[self.current_pos] != '\n':
                    self.current_pos += 1
            else:
                break
    
    def parse_quoted_string(self) -> str:
        """Parse a quoted string."""
        if self.text[self.current_pos] == '"':
            self.current_pos += 1
            start = self.current_pos
            while self.current_pos < len(self.text) and self.text[self.current_pos] != '"':
                self.current_pos += 1
            if self.current_pos >= len(self.text):
                raise ValueError("Unterminated quoted string")
            result = self.text[start:self.current_pos]
            self.current_pos += 1  # Skip closing quote
            return result
        else:
            raise ValueError(f"Expected quote at position {self.current_pos}")
    
    def parse_unquoted_string(self) -> str:
        """Parse an unquoted string."""
        start = self.current_pos
        while (self.current_pos < len(self.text) and 
               not self.text[self.current_pos].isspace() and 
               self.text[self.current_pos] not in '{}"'):
            self.current_pos += 1
        return self.text[start:self.current_pos]
    
    def parse_value(self) -> Union[str, Dict[str, Any]]:
        """Parse a value (either a string or a nested object)."""
        self.skip_whitespace()
        
        if self.current_pos >= len(self.text):
            raise ValueError("Unexpected end of input")
            
        if self.text[self.current_pos] == '{':
            return self.parse_object()
        elif self.text[self.current_pos] == '"':
            return self.parse_quoted_string()
        else:
            return self.parse_unquoted_string()
    
    def parse_object(self) -> Dict[str, Any]:
        """Parse a VDF object."""
        result = {}
        
        # Skip opening brace
        if self.text[self.current_pos] != '{':
            raise ValueError(f"Expected '{{' at position {self.current_pos}")
        self.current_pos += 1
        
        while True:
            self.skip_whitespace()
            
            if self.current_pos >= len(self.text):
                raise ValueError("Unexpected end of input")
                
            # Check for closing brace
            if self.text[self.current_pos] == '}':
                self.current_pos += 1
                break
                
            # Parse key
            key = self.parse_value()
            
            # Parse value
            self.skip_whitespace()
            value = self.parse_value()
            
            result[key] = value
            
        return result
    
    def parse(self) -> Dict[str, Any]:
        """Main parsing function."""
        result = {}
        self.skip_whitespace()
        
        if self.current_pos >= len(self.text):
            return result
        
        # Parse root key
        root_key = self.parse_value()
        
        # Parse root value (should be an object)
        self.skip_whitespace()
        root_value = self.parse_value()
        
        result[root_key] = root_value
        return result

# Example usage
def parse_vdf(text: str) -> Dict[str, Any]:
    parser = VDFParser()
    return parser.parse_string(text)

import sys
import json

if __name__ == "__main__":
    fname = sys.argv[1]
    with open(fname, 'r', encoding='utf-8') as f:
        text = f.read()


    parsed = parse_vdf(text)
    json = json.dumps(parsed, indent=4)
    print(json)
