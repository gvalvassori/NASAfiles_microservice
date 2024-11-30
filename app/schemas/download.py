from pydantic import BaseModel, Field

class DownloadRequest(BaseModel):
    base_url: str = Field(..., description="Base URL to download the products", examples=["https://oceandata.sci.gsfc.nasa.gov/cgi/getfile/A"])
    filter_list: list = Field(..., description="List of products to download", examples=[["A20151822015184.L3m_MO_CHL_chlor_a_4km.nc", "A20151822015184.L3m_MO_SST_sst_4km.nc"]])
    filter_date: str = Field(..., description="Date to download the products", examples=['2018-01-01'])
