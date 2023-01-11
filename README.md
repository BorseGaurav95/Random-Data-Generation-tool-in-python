# Random-Data-Generation-tool-in-python
The tool is used for fake data generation using Faker and SDV (Synthetic data vault) library. This tool auto-fetched the table column name from BigQuery and based that generates the fake data and stores the data in the BigQuery table / CSV file.


Prequisite :
create and download JSON key file of GCP service account. It is required for accessing the GCP project.

Use this keyword while creating a table in BigQuery.

phone_number() → str  

building_number() → str  
                                                     
postcode() → str   

credit_card_number(card_type: Optional[CardType] = None) → str

---------------------------------------------------------------------------------------------------------------------------------------
cryptocurrency_code() → str

name() → str

first_name() → str  

last_name() → str

address() → str

city() → str

country() → str

company_email() → str

email(safe: bool = True, domain: Optional[str] = None) → str

street_address() → str

license_plate() → str

color_name() → str

company() → str


paragraph(nb_sentences: int = 3, variable_nb_sentences: bool = True, ext_word_list: Optional[Sequence[str]] = None) → st

------------------------------------------------------------------------------------------------------------------------------------------

date(pattern: str = '%Y-%m-%d', end_datetime: Union[datetime.date, datetime.datetime, datetime.timedelta, str, int, None] = None) → str

date_time(tzinfo: Optional[datetime.tzinfo] = None, end_datetime: Union[datetime.date, datetime.datetime, datetime.timedelta, str, int, None] = None) → datetime.datetime

month_name() → str


time(pattern: str = '%H:%M:%S', end_datetime: Union[datetime.date, datetime.datetime, datetime.timedelta, str, int, None] = None) → str
