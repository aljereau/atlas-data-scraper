import pandas as pd
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class DataPointConfig:
    category: str
    metric: str
    source_name: str
    source_url: str
    area_on_page: str
    method_logic: str
    example_data: str

class ExcelConfigParser:
    def __init__(self, excel_path: str):
        """Initialize the Excel config parser.
        
        Args:
            excel_path: Path to the Excel file containing configuration
        """
        self.excel_path = excel_path
        self.property_links: List[str] = []
        self.data_points: List[DataPointConfig] = []
        self._load_configuration()

    def _load_configuration(self):
        """Load configuration from Excel file."""
        # Read property links - using the specific column name and sheet name
        properties_df = pd.read_excel(self.excel_path, sheet_name='🏡 Property Details')
        # Get links from the 'Link' column
        if 'Link' in properties_df.columns:
            self.property_links = properties_df['Link'].dropna().tolist()

        # Read data point configuration
        config_df = pd.read_excel(self.excel_path, sheet_name='Example Data')
        
        for _, row in config_df.iterrows():
            # Convert NaN values to empty strings
            row = row.fillna('')
            
            data_point = DataPointConfig(
                category=str(row['Category']),
                metric=str(row['Metric']),
                source_name=str(row['Source Name']),
                source_url=str(row['Source URL']),
                area_on_page=str(row['Area on page']),
                method_logic=str(row['Method/Logic']),
                example_data=str(row['Data'])
            )
            self.data_points.append(data_point)

    def get_funda_metrics(self) -> List[DataPointConfig]:
        """Get metrics that should be scraped from Funda."""
        return [dp for dp in self.data_points 
                if 'funda' in str(dp.source_name).lower() 
                and dp.source_url]  # Only include if source_url is not empty

    def get_mock_metrics(self) -> List[DataPointConfig]:
        """Get metrics that should be mocked."""
        return [dp for dp in self.data_points 
                if 'mock' in str(dp.source_name).lower()]

    def get_property_links(self) -> List[str]:
        """Get list of property links to scrape."""
        return self.property_links

    def get_metrics_by_category(self) -> Dict[str, List[DataPointConfig]]:
        """Group metrics by category."""
        categories = {}
        for dp in self.data_points:
            if dp.category not in categories:
                categories[dp.category] = []
            categories[dp.category].append(dp)
        return categories
        
    def get_metrics_by_source(self) -> Dict[str, List[DataPointConfig]]:
        """Group metrics by source."""
        sources = {}
        for dp in self.data_points:
            source = dp.source_name
            if source not in sources:
                sources[source] = []
            sources[source].append(dp)
        return sources 