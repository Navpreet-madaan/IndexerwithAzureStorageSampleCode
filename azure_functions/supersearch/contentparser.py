"""Content Parser module to extract HTML content from
a nested dictionary or list"""


# Content Parser class
class ContentParser:
    """Content Parser class to extract HTML content
    from a nested dictionary or list"""

    # Recursive function to extract all 'html' values
    def extract_html_content(self, data, html_values=None):
        """Extract HTML content from a nested dictionary or list

        Args:
            data (_type_): data to extract HTML content from
            html_values (list, optional): html values . Defaults to [].

        Returns:
            _type_: returns the html values
        """
        if html_values is None:
            html_values = []
        if isinstance(data, dict):
            for key, value in data.items():
                if value is not None:
                    if key == "html":  # Check if the key is 'html'
                        html_values.append(value)
                    else:
                        self.extract_html_content(value, html_values)
                        # Recursive call
        elif isinstance(data, list):
            for item in data:
                self.extract_html_content(item, html_values)
        return html_values
