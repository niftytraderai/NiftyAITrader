"""Download Upstox option contracts and save them as a CSV file."""

from collections.abc import Mapping

import pandas as pd
import upstox_client

from option_chain import get_option_contracts


def _is_option_contract_response(response):
    """Return whether *response* is the Upstox option-contract response wrapper."""
    response_class = getattr(upstox_client, "GetOptionContractResponse", None)

    if isinstance(response_class, type):
        return isinstance(response, response_class)

    # Keeps the script compatible with SDK versions that do not expose the
    # response model at the package root.
    return type(response).__name__ == "GetOptionContractResponse"


def _contract_to_dict(contract):
    """Convert one SDK contract model or mapping to a plain dictionary."""
    to_dict = getattr(contract, "to_dict", None)
    if callable(to_dict):
        converted = to_dict()
        if isinstance(converted, Mapping):
            return dict(converted)
        raise TypeError("The contract's to_dict() method did not return a dictionary.")

    try:
        return dict(contract)
    except (TypeError, ValueError) as error:
        raise TypeError(
            f"Cannot convert contract of type {type(contract).__name__} to a dictionary."
        ) from error


def main():
    try:
        response = get_option_contracts()  # Call the API exactly once.
        print(f"Response type: {type(response).__name__}")

        contracts = response.data if _is_option_contract_response(response) else response
        if contracts is None:
            raise ValueError("The option-contract response contained no data.")
        if isinstance(contracts, (str, bytes, Mapping)):
            raise TypeError("Expected a collection of contracts in the response data.")

        contract_records = [_contract_to_dict(contract) for contract in contracts]
        dataframe = pd.DataFrame(contract_records)

        print(f"Number of contracts: {len(dataframe)}")
        print(f"DataFrame columns: {dataframe.columns.tolist()}")
        print("First 5 rows:")
        print(dataframe.head())

        dataframe.to_csv("option_contracts.csv", index=False)
        print("Saved option_contracts.csv successfully.")
    except ImportError as error:
        print(f"Import error: {error}")
    except (ConnectionError, TimeoutError) as error:
        print(f"API request failed: {error}")
    except (TypeError, ValueError) as error:
        print(f"Response processing error: {error}")
    except OSError as error:
        print(f"Could not save option_contracts.csv: {error}")
    except Exception as error:
        print(f"Unexpected error while downloading option contracts: {error}")


if __name__ == "__main__":
    main()
