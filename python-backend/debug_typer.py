import typer

def main(
    recipient_id: str = typer.Option(
        "recipient-1",
        "--recipient-id",
        "-r",
        help="Your recipient identifier/address",
        show_default=True,
    ),
):
    print(f"Recipient: {recipient_id}")

try:
    typer.run(main)
except Exception as e:
    print(f"Error: {e}")
