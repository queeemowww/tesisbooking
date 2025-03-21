import asyncio
import re

a = """FFR/6 
555-08392193ISTSVO/T95K861MC6/SPP 
/100/GCR 
SU2139/11MAR/ISTSVO/NN 
SSR/GCR 
REF/FFIST 
CUS//0000000//GSA 
/TESIS 
/ISTANBUL"""

ffr_pattern = 'FFR/6\s+\d{3}-\d{8}.{6}/T\d+K\d+,?\d{0,2}?MC\d+,?\d{0,2}/\w+\s+/\d{3}/\w{3}\s+SU\d{4}/\d{1,2}\w{3}/\w{6}/NN\s+\w{3}/\w{3}\s+REF/\w+\s+\w+//\d+//GSA\s+/TESIS\s+/\w+'
awb_pattern = '\d{8}'
from_pattern = '\d{8}.{6}'
to_pattern = '\d{8}.{6}'
pcs_pattern = 'T\d+'
weight_pattern = 'K\d+,?\d{0,2}'
vol_pattern = 'MC\d+,?\d{0,2}'
cargo_pattern = '/\w+\s+'
flight_pattern = 'SU\d{4}'
day_pattern = 'SU\d{4}/\d{1,2}'
month_pattern = 'SU\d{4}/\d{1,2}\w{3}'


async def is_ffr(s):
    return re.match(rf'{ffr_pattern}', s)

async def get_info(s):
    return (re.search(rf'{awb_pattern}', s).group(), re.search(rf'{from_pattern}', s).group()[8:11], re.search(rf'{to_pattern}', s).group()[11:14], 
            re.search(rf'{pcs_pattern}', s).group()[1:], re.search(rf'{weight_pattern}', s).group()[1:], re.search(rf'{vol_pattern}', s).group()[2:],
            re.findall(rf'{cargo_pattern}', s)[1][1:][:3], re.search(rf'{flight_pattern}', s).group()[2:], re.search(rf'{day_pattern}', s).group()[7:],
            re.search(rf'{month_pattern}', s).group()[9:])

