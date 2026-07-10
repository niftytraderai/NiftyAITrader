from option_chain import get_option_chain
from pprint import pprint

response = get_option_chain()

pprint(response.to_dict())