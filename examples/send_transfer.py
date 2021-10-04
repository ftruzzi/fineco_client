import argparse
import logging

from fineco_client import FinecoClient, FinecoBankTransfer

logging.basicConfig(level=logging.INFO)

def main(args):
    client = FinecoClient()
    transfer = FinecoBankTransfer(
        amount=args.amount,
        description=args.description,
        recipient_country=args.country,
        recipient_iban=args.iban,
        recipient_name=args.name,
    )
    client.send_transfer(transfer)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to send a bank transfer through finecobank.com")
    parser.add_argument("--amount", type=float, required=True, help="Amount to send")
    parser.add_argument("--country", type=str, required=True, help="Destination country")
    parser.add_argument("--description", type=str, required=True, help="Transfer description")
    parser.add_argument("--iban", type=str, required=True, help="IBAN of the recipient")
    parser.add_argument("--name", type=str, required=True, help="Name of the recipient")

    args = parser.parse_args()
    main(args)